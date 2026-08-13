"""Ad set-level operations."""
from __future__ import annotations

import json
from typing import Any, Optional

from .client import GraphClient

FIELDS = (
    "id,name,campaign_id,status,effective_status,daily_budget,lifetime_budget,"
    "optimization_goal,billing_event,bid_amount,bid_strategy,targeting,"
    "start_time,end_time,created_time,updated_time"
)


def list_adsets(
    client: GraphClient,
    account_id: str,
    campaign_id: Optional[str] = None,
    statuses: Optional[list[str]] = None,
    limit: Optional[int] = None,
) -> list[dict[str, Any]]:
    params = {"fields": FIELDS}
    if statuses:
        params["effective_status"] = json.dumps(statuses)
    scope = f"{campaign_id}/adsets" if campaign_id else f"{account_id}/adsets"
    return client.get_all(scope, params, limit=limit)


def get_adset(client: GraphClient, adset_id: str) -> dict[str, Any]:
    return client.get(adset_id, {"fields": FIELDS})


def create_adset(
    client: GraphClient,
    account_id: str,
    name: str,
    campaign_id: str,
    optimization_goal: str,
    billing_event: str,
    targeting: dict[str, Any],
    status: str = "PAUSED",
    daily_budget: Optional[int] = None,
    lifetime_budget: Optional[int] = None,
    bid_amount: Optional[int] = None,
    bid_strategy: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    promoted_object: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Create an ad set. Defaults to PAUSED."""
    data: dict[str, Any] = {
        "name": name,
        "campaign_id": campaign_id,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "targeting": json.dumps(targeting),
        "status": status,
    }
    if daily_budget is not None:
        data["daily_budget"] = daily_budget
    if lifetime_budget is not None:
        data["lifetime_budget"] = lifetime_budget
    if bid_amount is not None:
        data["bid_amount"] = bid_amount
    if bid_strategy:
        data["bid_strategy"] = bid_strategy
    if start_time:
        data["start_time"] = start_time
    if end_time:
        data["end_time"] = end_time
    if promoted_object:
        data["promoted_object"] = json.dumps(promoted_object)
    return client.post(f"{account_id}/adsets", data)


def update_adset(client: GraphClient, adset_id: str, **fields: Any) -> dict[str, Any]:
    if "targeting" in fields and isinstance(fields["targeting"], dict):
        fields["targeting"] = json.dumps(fields["targeting"])
    return client.post(adset_id, fields)


def pause_adset(client: GraphClient, adset_id: str) -> dict[str, Any]:
    return update_adset(client, adset_id, status="PAUSED")


def activate_adset(client: GraphClient, adset_id: str) -> dict[str, Any]:
    return update_adset(client, adset_id, status="ACTIVE")


def delete_adset(client: GraphClient, adset_id: str) -> dict[str, Any]:
    return client.delete(adset_id)
