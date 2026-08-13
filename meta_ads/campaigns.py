"""Campaign-level operations."""
from __future__ import annotations

import json
from typing import Any, Optional

from .client import GraphClient

FIELDS = (
    "id,name,objective,status,effective_status,daily_budget,lifetime_budget,"
    "bid_strategy,special_ad_categories,start_time,stop_time,created_time,updated_time"
)


def list_campaigns(
    client: GraphClient,
    account_id: str,
    statuses: Optional[list[str]] = None,
    limit: Optional[int] = None,
) -> list[dict[str, Any]]:
    params = {"fields": FIELDS}
    if statuses:
        params["effective_status"] = json.dumps(statuses)
    return client.get_all(f"{account_id}/campaigns", params, limit=limit)


def get_campaign(client: GraphClient, campaign_id: str) -> dict[str, Any]:
    return client.get(campaign_id, {"fields": FIELDS})


def create_campaign(
    client: GraphClient,
    account_id: str,
    name: str,
    objective: str,
    status: str = "PAUSED",
    special_ad_categories: Optional[list[str]] = None,
    daily_budget: Optional[int] = None,
    lifetime_budget: Optional[int] = None,
    bid_strategy: Optional[str] = None,
) -> dict[str, Any]:
    """Create a campaign. Defaults to PAUSED so nothing spends until you
    explicitly activate it."""
    data: dict[str, Any] = {
        "name": name,
        "objective": objective,
        "status": status,
        "special_ad_categories": json.dumps(special_ad_categories or []),
    }
    if daily_budget is not None:
        data["daily_budget"] = daily_budget
    if lifetime_budget is not None:
        data["lifetime_budget"] = lifetime_budget
    if bid_strategy:
        data["bid_strategy"] = bid_strategy
    return client.post(f"{account_id}/campaigns", data)


def update_campaign(client: GraphClient, campaign_id: str, **fields: Any) -> dict[str, Any]:
    return client.post(campaign_id, fields)


def pause_campaign(client: GraphClient, campaign_id: str) -> dict[str, Any]:
    return update_campaign(client, campaign_id, status="PAUSED")


def activate_campaign(client: GraphClient, campaign_id: str) -> dict[str, Any]:
    return update_campaign(client, campaign_id, status="ACTIVE")


def delete_campaign(client: GraphClient, campaign_id: str) -> dict[str, Any]:
    return client.delete(campaign_id)
