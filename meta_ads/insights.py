"""Performance insights / reporting."""
from __future__ import annotations

import json
from typing import Any, Optional

from .client import GraphClient

DEFAULT_FIELDS = [
    "date_start",
    "date_stop",
    "campaign_name",
    "adset_name",
    "ad_name",
    "spend",
    "impressions",
    "reach",
    "frequency",
    "clicks",
    "ctr",
    "cpc",
    "cpm",
    "actions",
    "cost_per_action_type",
]

VALID_DATE_PRESETS = {
    "today",
    "yesterday",
    "this_month",
    "last_month",
    "this_quarter",
    "last_3d",
    "last_7d",
    "last_14d",
    "last_28d",
    "last_30d",
    "last_90d",
    "last_week_mon_sun",
    "last_week_sun_sat",
    "last_quarter",
    "last_year",
    "this_week_mon_sun",
    "this_week_sun_sat",
    "this_year",
    "maximum",
}


def get_insights(
    client: GraphClient,
    object_id: str,
    date_preset: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    fields: Optional[list[str]] = None,
    level: Optional[str] = None,
    breakdowns: Optional[list[str]] = None,
    time_increment: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Pull insights for an account, campaign, ad set, or ad.

    Exactly one of `date_preset` or (`since` + `until`) should be given.
    """
    params: dict[str, Any] = {"fields": ",".join(fields or DEFAULT_FIELDS)}
    if since and until:
        params["time_range"] = json.dumps({"since": since, "until": until})
    elif date_preset:
        params["date_preset"] = date_preset
    else:
        params["date_preset"] = "last_7d"
    if level:
        params["level"] = level
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    if time_increment:
        params["time_increment"] = time_increment
    return client.get_all(f"{object_id}/insights", params, limit=limit)
