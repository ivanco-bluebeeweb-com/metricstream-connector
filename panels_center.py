"""MetricStream Connector -- center panels for Risks/Issues/Controls/Assessments/Overview."""
from __future__ import annotations

from imperal_sdk import ui

import handlers as h
from app import ext


def _first_connection_id(connections: list[dict]) -> str:
    return connections[0].get("id", "") if connections else ""


@ext.panel("metricstream_overview", slot="center", title="Risk posture", center_overlay=True)
async def metricstream_overview(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    if not connections:
        return ui.Empty(message="Nothing to show here", icon="ShieldCheck")
    from schemas import AuditRiskPostureParams
    result = await h.audit_risk_posture(ctx, AuditRiskPostureParams(connection_id=_first_connection_id(connections)))
    if not result.success:
        return ui.Alert(type="error", message=f"Could not load risk posture: {result.error}")
    d = result.data
    return ui.Stack(direction="v", gap=3, align="stretch", children=[
        ui.Header(text="Risk posture overview", level=2),
        ui.Stack(direction="h", gap=4, align="stretch", children=[
            ui.Stat(label="Critical issues", value=str(d.open_issues_critical)),
            ui.Stat(label="High issues", value=str(d.open_issues_high)),
            ui.Stat(label="Other open issues", value=str(d.open_issues_other)),
            ui.Stat(label="High/critical risks", value=str(d.high_risk_count)),
            ui.Stat(label="Controls failing", value=str(d.controls_failing)),
            ui.Stat(label="Assessment completion", value=f"{d.assessment_completion_pct}%"),
        ]),
        ui.Text(d.summary, variant="caption"),
    ])


@ext.panel("metricstream_risks", slot="center", title="Risks", center_overlay=True)
async def metricstream_risks(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    if not connections:
        return ui.Empty(message="Nothing to show here", icon="AlertTriangle")
    from schemas import ListRisksParams
    result = await h.list_risks(ctx, ListRisksParams(connection_id=_first_connection_id(connections)))
    if not result.success:
        return ui.Alert(type="error", message=f"Could not load risks: {result.error}")
    risks = result.data.risks
    if not risks:
        return ui.Empty(message="No risks found", icon="AlertTriangle")
    return ui.DataTable(
        columns=[
            {"key": "risk_id", "label": "ID"},
            {"key": "name", "label": "Name"},
            {"key": "risk_level", "label": "Level"},
        ],
        rows=[r.model_dump() for r in risks],
    )


@ext.panel("metricstream_issues", slot="center", title="Issues", center_overlay=True)
async def metricstream_issues(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    if not connections:
        return ui.Empty(message="Nothing to show here", icon="Flag")
    from schemas import ListIssuesParams
    result = await h.list_issues(ctx, ListIssuesParams(connection_id=_first_connection_id(connections)))
    if not result.success:
        return ui.Alert(type="error", message=f"Could not load issues: {result.error}")
    issues = result.data.issues
    if not issues:
        return ui.Empty(message="No issues found", icon="Flag")
    return ui.DataTable(
        columns=[
            {"key": "issue_id", "label": "ID"},
            {"key": "title", "label": "Title"},
            {"key": "status", "label": "Status"},
            {"key": "severity", "label": "Severity"},
        ],
        rows=[i.model_dump() for i in issues],
    )


@ext.panel("metricstream_controls", slot="center", title="Controls", center_overlay=True)
async def metricstream_controls(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    if not connections:
        return ui.Empty(message="Nothing to show here", icon="CheckSquare")
    from schemas import ListControlsParams
    result = await h.list_controls(ctx, ListControlsParams(connection_id=_first_connection_id(connections)))
    if not result.success:
        return ui.Alert(type="error", message=f"Could not load controls: {result.error}")
    controls = result.data.controls
    if not controls:
        return ui.Empty(message="No controls found", icon="CheckSquare")
    return ui.DataTable(
        columns=[
            {"key": "control_id", "label": "ID"},
            {"key": "name", "label": "Name"},
            {"key": "testing_status", "label": "Testing status"},
        ],
        rows=[c.model_dump() for c in controls],
    )


@ext.panel("metricstream_assessments", slot="center", title="Assessments", center_overlay=True)
async def metricstream_assessments(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    if not connections:
        return ui.Empty(message="Nothing to show here", icon="ClipboardCheck")
    from schemas import ListAssessmentsParams
    result = await h.list_assessments(ctx, ListAssessmentsParams(connection_id=_first_connection_id(connections)))
    if not result.success:
        return ui.Alert(type="error", message=f"Could not load assessments: {result.error}")
    assessments = result.data.assessments
    if not assessments:
        return ui.Empty(message="No assessments found", icon="ClipboardCheck")
    return ui.DataTable(
        columns=[
            {"key": "assessment_id", "label": "ID"},
            {"key": "name", "label": "Name"},
            {"key": "status", "label": "Status"},
        ],
        rows=[a.model_dump() for a in assessments],
    )
