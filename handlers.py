"""Chat functions for MetricStream Connector (MetricStream REST API)."""
from __future__ import annotations

import json
import uuid

from imperal_sdk import ActionResult

import metricstream_client as ms
from app import chat
from schemas import (
    AssessmentIdParams, AssessmentList, AuditRiskPostureParams,
    ConnectMetricStreamParams, ConnectionList, ConnectionRefParams,
    ControlIdParams, ControlList, CreateIssueParams, DeleteResult,
    DisconnectMetricStreamParams, IssueIdParams, IssueList,
    ListAssessmentsParams, ListControlsParams, ListIssuesParams,
    ListRisksParams, MetricStreamAssessment, MetricStreamConnection,
    MetricStreamControl, MetricStreamIssue, MetricStreamRisk, NoParams,
    RiskIdParams, RiskList, RiskPostureAudit, UpdateIssueParams,
)

_SECRET_NAME = "metricstream_connections"


async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET_NAME)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return data if isinstance(data, list) else []


async def _save_connections(ctx, connections: list[dict]) -> None:
    await ctx.secrets.set(_SECRET_NAME, json.dumps(connections))


def _connection_entity(c: dict) -> MetricStreamConnection:
    return MetricStreamConnection(
        connection_id=c.get("id", ""),
        label=c.get("label") or "MetricStream tenant",
        base_url=c.get("base_url", ""),
    )


async def _resolve_connection(ctx, connection_id: str) -> dict:
    connections = await _load_connections(ctx)
    if not connections:
        raise ms.MetricStreamError("No MetricStream tenant connected yet. Use connect_metricstream first.")
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                return c
        raise ms.MetricStreamError(f"No connection found with id '{connection_id}'.")
    return connections[0]


def _client_for(c: dict) -> ms.MetricStreamClient:
    return ms.MetricStreamClient(c.get("api_key", ""), c.get("base_url", ""))


def _unwrap(data) -> list[dict]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("data", "items", "results", "records"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


@chat.function("connect_metricstream", "Connect a MetricStream tenant via a static API Key, after verifying connectivity.", action_type="write", chain_callable=True, data_model=MetricStreamConnection, event="metricstream-connector.connect_metricstream", effects=["metricstream.provider.connected"])
async def connect_metricstream(ctx, params: ConnectMetricStreamParams) -> ActionResult:
    """Connect a MetricStream tenant via a static API Key, after verifying connectivity."""
    client = ms.MetricStreamClient(params.api_key, params.base_url)
    try:
        await client.request("GET", "/api/v1/risks", params={"limit": 1})
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)

    connections = await _load_connections(ctx)
    connection_id = str(uuid.uuid4())
    record = {
        "id": connection_id,
        "label": params.label or "MetricStream tenant",
        "api_key": params.api_key,
        "base_url": client.base_url,
    }
    connections.append(record)
    await _save_connections(ctx, connections)
    return ActionResult.success(data=_connection_entity(record), summary="Metricstream connected.")


@chat.function("disconnect_metricstream", "Disconnect a MetricStream tenant: deletes only the saved credentials. Nothing in MetricStream itself is changed.", action_type="write", chain_callable=True, data_model=DeleteResult, event="metricstream-connector.disconnect_metricstream", effects=["metricstream.provider.disconnected"])
async def disconnect_metricstream(ctx, params: DisconnectMetricStreamParams) -> ActionResult:
    """Disconnect a MetricStream tenant: deletes only the saved credentials."""
    connections = await _load_connections(ctx)
    remaining = [c for c in connections if c.get("id") != params.connection_id]
    if len(remaining) == len(connections):
        return ActionResult.error(f"No connection found with id '{params.connection_id}'.")
    await _save_connections(ctx, remaining)
    return ActionResult.success(data=DeleteResult(deleted=True, connection_id=params.connection_id), summary="Metricstream disconnected.")


@chat.function("list_connections", "List the connected MetricStream tenants.", action_type="read", chain_callable=True, data_model=ConnectionList, event="metricstream-connector.list_connections")
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """List the connected MetricStream tenants."""
    connections = await _load_connections(ctx)
    return ActionResult.success(data=ConnectionList(connections=[_connection_entity(c) for c in connections]), summary="Connections listed.")


# ---- Risks ----

def _risk_entity(r: dict) -> MetricStreamRisk:
    return MetricStreamRisk(
        risk_id=str(r.get("id", "")),
        name=r.get("name", r.get("title", "")),
        risk_level=r.get("risk_level", r.get("riskLevel", "")),
    )


@chat.function("list_risks", "List Risks in the GRC Risk Register on the connected MetricStream tenant.", action_type="read", chain_callable=True, data_model=RiskList, event="metricstream-connector.list_risks")
async def list_risks(ctx, params: ListRisksParams) -> ActionResult:
    """List Risks in the GRC Risk Register on the connected MetricStream tenant."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", "/api/v1/risks")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    items = _unwrap(data)
    return ActionResult.success(data=RiskList(risks=[_risk_entity(r) for r in items]), summary="Risks listed.")


@chat.function("get_risk", "Read one Risk in full by id.", action_type="read", chain_callable=True, data_model=MetricStreamRisk, event="metricstream-connector.get_risk")
async def get_risk(ctx, params: RiskIdParams) -> ActionResult:
    """Read one Risk in full by id."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", f"/api/v1/risks/{params.risk_id}")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    return ActionResult.success(data=_risk_entity(data if isinstance(data, dict) else {}), summary="Risk retrieved.")


# ---- Issues ----

def _issue_entity(i: dict) -> MetricStreamIssue:
    return MetricStreamIssue(
        issue_id=str(i.get("id", "")),
        title=i.get("title", i.get("name", "")),
        status=i.get("status", ""),
        severity=i.get("severity", ""),
        risk_id=str(i.get("risk_id", i.get("riskId", ""))) if i.get("risk_id") or i.get("riskId") else "",
    )


@chat.function("list_issues", "List Issues raised against Risks, optionally filtered to one Risk.", action_type="read", chain_callable=True, data_model=IssueList, event="metricstream-connector.list_issues")
async def list_issues(ctx, params: ListIssuesParams) -> ActionResult:
    """List Issues raised against Risks, optionally filtered to one Risk."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    query = {"risk_id": params.risk_id} if params.risk_id else None
    try:
        data, _ = await client.request("GET", "/api/v1/issues", params=query)
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    items = _unwrap(data)
    return ActionResult.success(data=IssueList(issues=[_issue_entity(i) for i in items]), summary="Issues listed.")


@chat.function("get_issue", "Read one Issue in full by id.", action_type="read", chain_callable=True, data_model=MetricStreamIssue, event="metricstream-connector.get_issue")
async def get_issue(ctx, params: IssueIdParams) -> ActionResult:
    """Read one Issue in full by id."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", f"/api/v1/issues/{params.issue_id}")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    return ActionResult.success(data=_issue_entity(data if isinstance(data, dict) else {}), summary="Issue retrieved.")


@chat.function("create_issue", "Create a new Issue, optionally linked to a Risk.", action_type="write", chain_callable=True, data_model=MetricStreamIssue, event="metricstream-connector.create_issue", effects=["metricstream.issue.created"])
async def create_issue(ctx, params: CreateIssueParams) -> ActionResult:
    """Create a new Issue, optionally linked to a Risk."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    body = {"title": params.title, "description": params.description}
    if params.severity:
        body["severity"] = params.severity
    if params.risk_id:
        body["risk_id"] = params.risk_id
    try:
        data, _ = await client.request("POST", "/api/v1/issues", json_body=body)
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    return ActionResult.success(data=_issue_entity(data if isinstance(data, dict) else {}), summary="Issue created.")


@chat.function("update_issue", "Update selected fields of an existing Issue (status and/or severity). Only given fields change.", action_type="write", chain_callable=True, data_model=MetricStreamIssue, event="metricstream-connector.update_issue", effects=["metricstream.issue.updated"])
async def update_issue(ctx, params: UpdateIssueParams) -> ActionResult:
    """Update selected fields of an existing Issue. Only given fields change."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    body = {}
    if params.status:
        body["status"] = params.status
    if params.severity:
        body["severity"] = params.severity
    try:
        data, _ = await client.request("PATCH", f"/api/v1/issues/{params.issue_id}", json_body=body)
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    return ActionResult.success(data=_issue_entity(data if isinstance(data, dict) else {}), summary="Issue updated.")


# ---- Controls ----

def _control_entity(c: dict) -> MetricStreamControl:
    return MetricStreamControl(
        control_id=str(c.get("id", "")),
        name=c.get("name", c.get("title", "")),
        testing_status=c.get("testing_status", c.get("testingStatus", "")),
    )


@chat.function("list_controls", "List Controls and their testing status on the connected MetricStream tenant.", action_type="read", chain_callable=True, data_model=ControlList, event="metricstream-connector.list_controls")
async def list_controls(ctx, params: ListControlsParams) -> ActionResult:
    """List Controls and their testing status on the connected MetricStream tenant."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", "/api/v1/controls")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    items = _unwrap(data)
    return ActionResult.success(data=ControlList(controls=[_control_entity(x) for x in items]), summary="Controls listed.")


@chat.function("get_control", "Read one Control in full by id.", action_type="read", chain_callable=True, data_model=MetricStreamControl, event="metricstream-connector.get_control")
async def get_control(ctx, params: ControlIdParams) -> ActionResult:
    """Read one Control in full by id."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", f"/api/v1/controls/{params.control_id}")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    return ActionResult.success(data=_control_entity(data if isinstance(data, dict) else {}), summary="Control retrieved.")


# ---- Assessments ----

def _assessment_entity(a: dict) -> MetricStreamAssessment:
    return MetricStreamAssessment(
        assessment_id=str(a.get("id", "")),
        name=a.get("name", a.get("title", "")),
        status=a.get("status", ""),
    )


@chat.function("list_assessments", "List compliance/risk Assessments configured on the connected MetricStream tenant.", action_type="read", chain_callable=True, data_model=AssessmentList, event="metricstream-connector.list_assessments")
async def list_assessments(ctx, params: ListAssessmentsParams) -> ActionResult:
    """List compliance/risk Assessments configured on the connected MetricStream tenant."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", "/api/v1/assessments")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    items = _unwrap(data)
    return ActionResult.success(data=AssessmentList(assessments=[_assessment_entity(a) for a in items]), summary="Assessments listed.")


@chat.function("get_assessment", "Read one Assessment in full by id.", action_type="read", chain_callable=True, data_model=MetricStreamAssessment, event="metricstream-connector.get_assessment")
async def get_assessment(ctx, params: AssessmentIdParams) -> ActionResult:
    """Read one Assessment in full by id."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)
    try:
        data, _ = await client.request("GET", f"/api/v1/assessments/{params.assessment_id}")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    return ActionResult.success(data=_assessment_entity(data if isinstance(data, dict) else {}), summary="Assessment retrieved.")


# ---- Aggregated report ----

@chat.function("audit_risk_posture", "Build a lightweight risk posture overview: open Issues by severity, high-risk Risks, Controls failing testing, and Assessment completion rate.", action_type="read", chain_callable=True, data_model=RiskPostureAudit, event="metricstream-connector.audit_risk_posture")
async def audit_risk_posture(ctx, params: AuditRiskPostureParams) -> ActionResult:
    """Build a lightweight risk posture overview."""
    c = await _resolve_connection(ctx, params.connection_id)
    client = _client_for(c)

    try:
        risks_data, _ = await client.request("GET", "/api/v1/risks")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    try:
        issues_data, _ = await client.request("GET", "/api/v1/issues")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    try:
        controls_data, _ = await client.request("GET", "/api/v1/controls")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)
    try:
        assessments_data, _ = await client.request("GET", "/api/v1/assessments")
    except ms.MetricStreamError as exc:
        return ActionResult.error(str(exc), retryable=exc.retryable)

    risks = _unwrap(risks_data)
    issues = _unwrap(issues_data)
    controls = _unwrap(controls_data)
    assessments = _unwrap(assessments_data)

    open_issues = [i for i in issues if str(i.get("status", "")).lower() not in ("closed", "resolved", "done")]
    critical = sum(1 for i in open_issues if str(i.get("severity", "")).lower() == "critical")
    high = sum(1 for i in open_issues if str(i.get("severity", "")).lower() == "high")
    other = len(open_issues) - critical - high

    high_risk = sum(1 for r in risks if str(r.get("risk_level", r.get("riskLevel", ""))).lower() in ("high", "critical"))
    failing_controls = sum(1 for c_ in controls if str(c_.get("testing_status", c_.get("testingStatus", ""))).lower() in ("fail", "failed", "failing"))

    total_assessments = len(assessments)
    completed_assessments = sum(1 for a in assessments if str(a.get("status", "")).lower() in ("complete", "completed"))
    completion_pct = round((completed_assessments / total_assessments * 100), 1) if total_assessments else 0.0

    summary = (
        f"{len(open_issues)} open issue(s) ({critical} critical, {high} high), "
        f"{high_risk} high/critical risk(s), {failing_controls} control(s) failing testing, "
        f"{completion_pct}% assessment completion."
    )

    return ActionResult.success(data=RiskPostureAudit(
        open_issues_critical=critical,
        open_issues_high=high,
        open_issues_other=max(other, 0),
        high_risk_count=high_risk,
        controls_failing=failing_controls,
        assessment_completion_pct=completion_pct,
        summary=summary,
    ), summary="Risk posture audit ready.")
