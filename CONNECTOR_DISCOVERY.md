# MetricStream Connector — Discovery

**Prepared:** 2026-08-25
**Source:** Best-effort platform knowledge of MetricStream's API.

> ⚠️ **UNVERIFIED THIS SESSION.** A live web search against MetricStream's
> developer documentation was not attempted this time because the search
> provider was already failing earlier in this session (Exa 402, confirmed
> during the AuditBoard build). The API shape below reflects best-effort
> knowledge of MetricStream's REST API (a generic object-based GRC/IRM data
> model) and MUST be reconciled against the live developer docs before this
> connector is treated as fully verified — same open item already tracked for
> Vanta/Drata/LogicGate/OneTrust/AuditBoard's discovery docs this cycle.

## 1. What MetricStream is

MetricStream is an enterprise Integrated Risk Management (IRM) / GRC platform
covering Risk Management, Audit Management, Compliance Management, Policy
Management, and Incident Management, all built on a shared configurable
object data model (similar in spirit to LogicGate's Applications/Records, but
with MetricStream's own fixed core object types: Risks, Issues, Controls,
Assessments). It is the sixth GRC connector in this portfolio.

## 2. Authentication (best effort — verify before go-live)

- MetricStream's public API is understood to support a static Bearer API Key
  model (generated per-user/per-integration in MetricStream Admin), sent as
  `Authorization: Bearer <api_key>` on every request — same static-token
  shape as Drata/LogicGate/AuditBoard.
- `base_url` is user-supplied and required, since MetricStream is a
  per-tenant hosted instance (no shared default host) — same pattern as
  OneTrust/AuditBoard.

## 3. Core entities (Tier 1)

| Entity | Description | Ops |
|---|---|---|
| Risks | Risk register entries | list, get |
| Issues | Issues/findings raised against risks or controls | list, get, create, update |
| Controls | Control library and their testing status | list, get |
| Assessments | Compliance/risk assessments | list, get |

## 4. Value-add report

`audit_risk_posture` — aggregate: open Issues by severity, high-risk Risks
count, Controls failing testing, Assessment completion rate.

## 5. Architecture decision

Same hybrid as AuditBoard: static Bearer API Key (like Drata/LogicGate) +
required `base_url` (like OneTrust/AuditBoard). Secret:
`metricstream_connections`, each record `{connection_id, label, api_key,
base_url}`.
