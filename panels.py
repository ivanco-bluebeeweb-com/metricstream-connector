"""MetricStream Connector panels.

Same conventions as the rest of the GRC portfolio: no Cards in the left
sidebar, disconnect only in App settings, every input has its own visible
label, placeholders are contextually specific, the connect form stretches to
the sidebar's full width with contents stretched to fill it, and the sidebar
carries no instructions duplicated from the "How do I get this?" modal.
"""
from __future__ import annotations

from imperal_sdk import ui

import handlers as h
from app import ext


def _field(label: str, node: ui.UINode) -> ui.UINode:
    return ui.Stack(direction="v", gap=1, align="stretch", children=[
        ui.Text(label, variant="caption"),
        node,
    ])


def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings", variant="secondary", size="sm", icon="Settings", on_click=ui.Call("__panel__metricstream_settings"),
    )


@ext.panel("metricstream_sidebar", slot="left", title="MetricStream")
async def metricstream_sidebar(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    if not connections:
        return ui.Stack(direction="v", gap=3, align="stretch", children=[
            ui.Button("How do I get this?", variant="ghost", size="sm", icon="HelpCircle",
                      on_click=ui.Call("__panel__metricstream_connect_help")),
            ui.Button("Sign in with MetricStream (SSO / OAuth)", variant="primary", size="sm", icon="login"),
            ui.Divider(),
            ui.Text("Or connect via API Key", variant="caption"),
            ui.Form(action="connect_metricstream", submit_label="Connect", children=[
                _field("Account label", ui.Input(param_name="label", placeholder="Acme Corp — Risk & Compliance")),
                _field("Instance URL", ui.Input(param_name="base_url", placeholder="https://your-instance.metricstream.com")),
                _field("API Key", ui.Input(param_name="api_key", placeholder="MetricStream Admin > API Key")),
            ]),
        ])
    label = connections[0].get("label") or "MetricStream tenant"
    return ui.Stack(direction="v", gap=3, align="stretch", children=[
        ui.Text(label, variant="body"),
        ui.Divider(),
        ui.Button("Risk posture", variant="ghost", size="sm", icon="ShieldCheck",
                  on_click=ui.Call("__panel__metricstream_overview")),
        ui.Button("Risks", variant="ghost", size="sm", icon="AlertTriangle",
                  on_click=ui.Call("__panel__metricstream_risks")),
        ui.Button("Issues", variant="ghost", size="sm", icon="Flag",
                  on_click=ui.Call("__panel__metricstream_issues")),
        ui.Button("Controls", variant="ghost", size="sm", icon="CheckSquare",
                  on_click=ui.Call("__panel__metricstream_controls")),
        ui.Button("Assessments", variant="ghost", size="sm", icon="ClipboardCheck",
                  on_click=ui.Call("__panel__metricstream_assessments")),
        ui.Divider(),
        _settings_button(),
    ])


@ext.panel("metricstream_connect_help", slot="center", title="How do I get this?", icon="HelpCircle", center_overlay=True)
async def metricstream_connect_help(ctx, **kwargs) -> ui.UINode:
    return ui.Stack(direction="v", gap=3, align="stretch", children=[
        ui.Header(text="Connecting MetricStream", level=2),
        ui.Text("In MetricStream, go to Admin settings and generate an API Key for integrations.", variant="body"),
        ui.Text("You'll also need your MetricStream instance URL, e.g. https://your-instance.metricstream.com.", variant="body"),
        ui.Text("Paste both into the connect form in the sidebar.", variant="body"),
    ])