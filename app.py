"""MetricStream Connector extension declaration.

MetricStream is an enterprise Integrated Risk Management (IRM) / GRC platform
for Risk Management, Issues, Controls testing and Assessments, exposed
through a REST API via a static Bearer API Key.
"""
from __future__ import annotations

from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "metricstream-connector",
    version="0.1.0",
    display_name="MetricStream",
    description=(
        "Connect your own MetricStream tenant (static API Key) to browse "
        "the Risk register, review and manage Issues, check Controls "
        "testing status and Assessments, and get an aggregated risk-"
        "posture report."
    ),
    icon="icon.svg",
    capabilities=["metricstream:read", "metricstream:write"],
    actions_explicit=True,
    system=False,
)

chat = ChatExtension(
    ext,
    tool_name="metricstream",
    description=(
        "MetricStream Connector — manage Risks, Issues, Controls and "
        "Assessments on a MetricStream tenant."
    ),
)

ext.secret(
    "metricstream_connections",
    "JSON list of connected MetricStream tenants and encrypted API Keys. Managed only through connect_metricstream and disconnect_metricstream.",
    required=True,
    write_mode="both",
    max_bytes=65536,
    rotation_hint_days=90,
)(lambda: None)


@ext.health_check
async def health_check(ctx) -> dict:
    """Report whether at least one MetricStream tenant connection is saved."""
    import json

    raw = await ctx.secrets.get("metricstream_connections")
    connections = []
    if raw:
        try:
            connections = json.loads(raw)
        except (TypeError, ValueError):
            connections = []
    return {
        "healthy": True,
        "connections": len(connections),
    }
