# MetricStream Connector — UI Component Plan

Source: `UI_COMPONENT_VOCABULARY.md`. Only primitives from the verified
vocabulary are used below.

## Standing rules applied
- Every input carries its own visible label (`Text(variant="caption")` + input).
- Placeholders are contextually specific.
- Connect form container stretched to full sidebar width, contents stretched
  to fill it (`align="stretch"`).
- Sidebar carries NO instructions duplicated from the "How do I get this?"
  modal.
- No `Card` in the left sidebar — plain `Stack` + `Divider` only.

## 1. Left sidebar (`slot="left"`)

**Not connected:**
- `Button` "How do I get this?" (ghost, opens `metricstream_connect_help` modal)
- `Form(action="connect_metricstream")`:
  - Label `Input` (placeholder: "Acme Corp — Risk & Compliance")
  - Instance URL `Input` (placeholder: "https://your-instance.metricstream.com")
  - API Key `Input` (placeholder: "MetricStream Admin > API Key")
  - Submit button "Connect"

**Connected:**
- `Text` account label, `Divider`
- `Button` list (ghost, full width): Risk posture, Risks, Issues, Controls, Assessments
- `Divider`
- `Button` "App settings" (secondary, always last)

## 2. Center panels (`slot="center"`, `center_overlay=True`)

- `metricstream_overview` — `audit_risk_posture` as `Stat` cards (open issues
  by severity, high-risk Risks, failing Controls, Assessment completion %).
- `metricstream_risks` — `DataTable` of Risks or `Empty`.
- `metricstream_issues` — `DataTable` of Issues, opens create/update forms.
- `metricstream_controls` — `DataTable` of Controls.
- `metricstream_assessments` — `DataTable` of Assessments.

## 3. Modal

- `metricstream_connect_help` — center modal, static explanation of how to
  get an API Key, not duplicated in the sidebar.

## 4. App settings

- `metricstream_settings` — list of connected tenants with a Disconnect
  button per row.
