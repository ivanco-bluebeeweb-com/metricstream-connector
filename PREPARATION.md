# MetricStream Connector — Preparation

**Prepared:** 2026-08-25
**Scope:** Tier 1 (Risks, Issues, Controls, Assessments) — maximum practical
functionality per the user's standing "maximum functionality" instruction.

## 1. Product outcome

MetricStream Connector lets an authorized Imperal user connect their
MetricStream tenant (BYOK static API Key + required base_url), browse the
Risk register, review and manage Issues (including creating/updating them),
check Controls testing status and Assessments, and get an aggregated
risk-posture report — all without leaving the chat. MetricStream remains the
system of record.

## 2. Connection architecture

- **Model:** BYOK, per Imperal account, multi-connection JSON secret
  (`metricstream_connections`).
- **Secret shape:** each record = `{connection_id, label, api_key, base_url}`.
- **Auth:** static Bearer API Key on every request (best-effort assumption;
  flagged for verification in CONNECTOR_DISCOVERY.md).
- **No secret echo:** api_key is never returned in entities, labels, errors,
  panels, or logs.
- **Verification:** `connect_metricstream` performs a bounded single-page
  call (list Risks) before persisting the connection.

## 3. Provider client

`metricstream_client.py` is the single HTTP boundary. It:

1. holds no long-lived state beyond the api_key/base_url passed at construction;
2. builds Bearer authorization headers;
3. maps status codes into safe, user-facing structured errors
   (`MetricStreamError`), marking 429/5xx as retryable;
4. never logs or raises the raw api_key in any exception message;
5. tolerantly unwraps both `{"data": [...], ...}` and bare-list responses.

## 4. Chat functions (Tier 1, complete)

- `connect_metricstream`, `disconnect_metricstream`, `list_connections`
- `list_risks`, `get_risk`
- `list_issues`, `get_issue`, `create_issue`, `update_issue`
- `list_controls`, `get_control`
- `list_assessments`, `get_assessment`
- `audit_risk_posture`

## 5. UI

See UI_COMPONENT_PLAN.md — same conventions as the rest of the GRC portfolio.
