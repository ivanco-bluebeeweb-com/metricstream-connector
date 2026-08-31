"""Pydantic input contracts and SDL result entities for MetricStream Connector."""
from __future__ import annotations

from imperal_sdk import sdl
from pydantic import BaseModel, Field


class NoParams(BaseModel):
    pass


class ConnectionRefParams(BaseModel):
    connection_id: str = Field("", description="Optional saved MetricStream tenant connection ID. Omit to use the first connected tenant.")


class ConnectMetricStreamParams(BaseModel):
    label: str = Field("", description="Friendly tenant label, e.g. 'Acme Corp — Risk & Compliance'.")
    api_key: str = Field(..., description="MetricStream API Key, from MetricStream Admin.")
    base_url: str = Field(..., description="Your MetricStream instance URL, e.g. https://your-instance.metricstream.com.")


class DisconnectMetricStreamParams(ConnectionRefParams):
    connection_id: str = Field(..., description="Saved MetricStream tenant connection ID to remove from Imperal.")


class ListRisksParams(ConnectionRefParams):
    pass


class RiskIdParams(ConnectionRefParams):
    risk_id: str = Field(..., description="MetricStream Risk ID.")


class ListIssuesParams(ConnectionRefParams):
    risk_id: str = Field("", description="Optional MetricStream Risk ID to filter Issues to.")


class IssueIdParams(ConnectionRefParams):
    issue_id: str = Field(..., description="MetricStream Issue ID.")


class CreateIssueParams(ConnectionRefParams):
    title: str = Field(..., description="Issue title.")
    description: str = Field("", description="Issue description.")
    severity: str = Field("", description="Issue severity, e.g. LOW, MEDIUM, HIGH, CRITICAL.")
    risk_id: str = Field("", description="Optional MetricStream Risk ID this Issue relates to.")


class UpdateIssueParams(ConnectionRefParams):
    issue_id: str = Field(..., description="MetricStream Issue ID to update.")
    status: str = Field("", description="New status for the Issue.")
    severity: str = Field("", description="New severity for the Issue.")


class ListControlsParams(ConnectionRefParams):
    pass


class ControlIdParams(ConnectionRefParams):
    control_id: str = Field(..., description="MetricStream Control ID.")


class ListAssessmentsParams(ConnectionRefParams):
    pass


class AssessmentIdParams(ConnectionRefParams):
    assessment_id: str = Field(..., description="MetricStream Assessment ID.")


class AuditRiskPostureParams(ConnectionRefParams):
    pass


# ---- SDL entities ----

class MetricStreamConnection(sdl.Entity):
    id: str = ""
    title: str = ""
    connection_id: str
    label: str
    base_url: str


class ConnectionList(sdl.Entity):
    id: str = ""
    title: str = ""
    connections: list[MetricStreamConnection]


class MetricStreamRisk(sdl.Entity):
    id: str = ""
    title: str = ""
    risk_id: str
    name: str
    risk_level: str = ""


class RiskList(sdl.Entity):
    id: str = ""
    title: str = ""
    risks: list[MetricStreamRisk]


class MetricStreamIssue(sdl.Entity):
    id: str = ""
    issue_id: str
    title: str
    status: str = ""
    severity: str = ""
    risk_id: str = ""


class IssueList(sdl.Entity):
    id: str = ""
    title: str = ""
    issues: list[MetricStreamIssue]


class MetricStreamControl(sdl.Entity):
    id: str = ""
    title: str = ""
    control_id: str
    name: str
    testing_status: str = ""


class ControlList(sdl.Entity):
    id: str = ""
    title: str = ""
    controls: list[MetricStreamControl]


class MetricStreamAssessment(sdl.Entity):
    id: str = ""
    title: str = ""
    assessment_id: str
    name: str
    status: str = ""


class AssessmentList(sdl.Entity):
    id: str = ""
    title: str = ""
    assessments: list[MetricStreamAssessment]


class RiskPostureAudit(sdl.Entity):
    id: str = ""
    title: str = ""
    open_issues_critical: int
    open_issues_high: int
    open_issues_other: int
    high_risk_count: int
    controls_failing: int
    assessment_completion_pct: float
    summary: str


class DeleteResult(sdl.Entity):
    id: str = ""
    title: str = ""
    deleted: bool
    connection_id: str
