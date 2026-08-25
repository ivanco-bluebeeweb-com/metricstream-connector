# Pricing History — MetricStream Connector

## 2026-08-25 — initial pricing (build → deploy → save_pricing → submit_for_review)

Same pattern as Vanta/Drata/LogicGate/OneTrust/AuditBoard this build cycle:
pricing set via `developer.save_pricing` BEFORE `submit_for_review`, per the
standing rule ("ты не выставила прайсинги на функции перед заливом на
платформу... это должно быть частью дефолтного поведения всегда для всех
приложений и для всех сессий").

`save_pricing` succeeded on the **first** call — `manifest_json` came back
populated with `pricing_model: "per_action"` and all 11 non-zero tool prices
present. No retry needed.

**Deploy succeeded on the first attempt** (20/21 — the one warning is the
expected missing `@ext.on_install` hook, same as every other app in this
portfolio; non-blocking).

**Category note:** same as every prior GRC app — `category="grc"` does not
exist in the platform's category catalog; filed under `productivity`.

**Open technical debt, disclosed:** `CONNECTOR_DISCOVERY.md` for this app was
written from best-effort platform knowledge of MetricStream's REST API, NOT
from a confirmed live read of MetricStream's developer documentation — the
web-search tool was already failing earlier in this session (Exa 402,
confirmed during the AuditBoard build) so no retry was attempted. Endpoint
paths (`/api/v1/risks`, `/api/v1/issues`, etc.) should be reconciled against
MetricStream's real API spec before being treated as fully verified. This is
flagged directly in CONNECTOR_DISCOVERY.md and IDEAL_ONBOARDING.md — the same
open item as AuditBoard's.

**Architecture note:** MetricStream uses a static Bearer API Key model (like
Drata/LogicGate/AuditBoard) plus a required `base_url` (like OneTrust/
AuditBoard, since MetricStream is a per-tenant hosted instance) — same hybrid
pattern as AuditBoard.

**Prices — fixed platform scale {0, 8, 16, 20, 40, 60}, no exceptions, no
markup:**

| Цена | Функции |
|---|---|
| 0 | `connect_metricstream`, `disconnect_metricstream`, `list_connections` (настройка доступа, не операция с MetricStream API) |
| 8 | `list_risks`, `get_risk`, `list_issues`, `get_issue`, `list_controls`, `get_control`, `list_assessments`, `get_assessment` (лёгкие read-операции) |
| 20 | `create_issue`, `update_issue` (write-операции) |
| 40 | `audit_risk_posture` (агрегированный отчёт по нескольким сущностям) |

## Portfolio status after this app

Six GRC connectors now fully shipped in one continuous build arc: Vanta,
Drata, LogicGate, OneTrust, AuditBoard, MetricStream — all deployed, priced,
and submitted for Marketplace review.
