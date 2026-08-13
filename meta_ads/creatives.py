"""Ad creative operations."""
from __future__ import annotations

import json
from typing import Any, Optional

from .client import GraphClient

FIELDS = "id,name,object_story_spec,status,thumbnail_url,effective_object_story_id"


def list_creatives(client: GraphClient, account_id: str, limit: Optional[int] = None) -> list[dict[str, Any]]:
    return client.get_all(f"{account_id}/adcreatives", {"fields": FIELDS}, limit=limit)


def get_creative(client: GraphClient, creative_id: str) -> dict[str, Any]:
    return client.get(creative_id, {"fields": FIELDS})


def create_link_creative(
    client: GraphClient,
    account_id: str,
    name: str,
    page_id: str,
    link: str,
    message: str,
    headline: Optional[str] = None,
    description: Optional[str] = None,
    image_hash: Optional[str] = None,
    call_to_action_type: Optional[str] = None,
) -> dict[str, Any]:
    """Create a straightforward link-ad creative (page post with a link)."""
    link_data: dict[str, Any] = {"link": link, "message": message}
    if headline:
        link_data["name"] = headline
    if description:
        link_data["description"] = description
    if image_hash:
        link_data["image_hash"] = image_hash
    if call_to_action_type:
        link_data["call_to_action"] = {"type": call_to_action_type, "value": {"link": link}}

    object_story_spec = {"page_id": page_id, "link_data": link_data}
    data = {"name": name, "object_story_spec": json.dumps(object_story_spec)}
    return client.post(f"{account_id}/adcreatives", data)


def create_creative_from_spec(
    client: GraphClient, account_id: str, name: str, object_story_spec: dict[str, Any]
) -> dict[str, Any]:
    """Create a creative from a full object_story_spec dict (for anything the
    convenience helpers above don't cover -- carousels, video, DPA, etc.)."""
    data = {"name": name, "object_story_spec": json.dumps(object_story_spec)}
    return client.post(f"{account_id}/adcreatives", data)


def upload_image(client: GraphClient, account_id: str, image_path: str) -> dict[str, Any]:
    """Upload an image file and return the response containing its image
    hash, for use in create_link_creative(image_hash=...)."""
    import requests

    url = client._url(f"{account_id}/adimages")
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {"access_token": client.access_token}
        resp = requests.post(url, files=files, data=data, timeout=client.timeout)
    return client._handle(resp)
