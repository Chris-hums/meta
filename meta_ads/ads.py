"""Ad-level operations."""
from __future__ import annotations

from typing import Any, Optional

from .client import GraphClient

FIELDS = (
    "id,name,adset_id,campaign_id,creative,status,effective_status,"
    "created_time,updated_time"
)


def list_ads(
    client: GraphClient,
    account_id: str,
    adset_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict[str, Any]]:
    if adset_id:
        scope = f"{adset_id}/ads"
    elif campaign_id:
        scope = f"{campaign_id}/ads"
    else:
        scope = f"{account_id}/ads"
    return client.get_all(scope, {"fields": FIELDS}, limit=limit)


def get_ad(client: GraphClient, ad_id: str) -> dict[str, Any]:
    return client.get(ad_id, {"fields": FIELDS})


def create_ad(
    client: GraphClient,
    account_id: str,
    name: str,
    adset_id: str,
    creative_id: str,
    status: str = "PAUSED",
) -> dict[str, Any]:
    """Create an ad. Defaults to PAUSED."""
    data = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status,
    }
    import json

    data["creative"] = json.dumps(data["creative"])
    return client.post(f"{account_id}/ads", data)


def update_ad(client: GraphClient, ad_id: str, **fields: Any) -> dict[str, Any]:
    return client.post(ad_id, fields)


def pause_ad(client: GraphClient, ad_id: str) -> dict[str, Any]:
    return update_ad(client, ad_id, status="PAUSED")


def activate_ad(client: GraphClient, ad_id: str) -> dict[str, Any]:
    return update_ad(client, ad_id, status="ACTIVE")


def delete_ad(client: GraphClient, ad_id: str) -> dict[str, Any]:
    return client.delete(ad_id)
