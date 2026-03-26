# utils/api_client.py
from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from supabase import create_client, Client
from utils.config import get_config

load_dotenv()

# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_client() -> Client:
    url = get_config("SUPABASE_URL")
    key = get_config("SUPABASE_KEY")
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _unwrap(response) -> list[dict]:
    if hasattr(response, "error") and response.error:
        raise RuntimeError(response.error.message)
    return response.data or []


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def upload_images(files: list[dict]) -> list[str]:
    """
    files: list of {"name": str, "bytes": bytes, "mime": str}
    Returns list of public URLs.
    """
    client = get_client()
    supabase_url = get_config("SUPABASE_URL")
    urls = []

    for f in files:
        path = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{f['name']}"
        client.storage.from_("bug-attachments").upload(
            path=path,
            file=f["bytes"],
            file_options={"content-type": f["mime"]},
        )
        url = f"{supabase_url}/storage/v1/object/public/bug-attachments/{path}"
        urls.append(url)

    return urls

# ---------------------------------------------------------------------------
# Bugs
# ---------------------------------------------------------------------------

def create_bug(
    title: str,
    description: str,
    severity: str,
    bug_type: str,
    category: str,
    attachment_urls: list[str] | None = None,
) -> dict[str, Any]:
    payload = {
        "title": title,
        "description": description,
        "severity": severity,
        "type": bug_type,
        "category": category,
        "status": "open",
        "attachment_urls": attachment_urls or [],
    }
    result = _unwrap(get_client().table("bugs").insert(payload).execute())
    return result[0]


def get_all_bugs(
    status: str | None = None,
    severity: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    query = get_client().table("bugs").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    if severity:
        query = query.eq("severity", severity)
    if category:
        query = query.eq("category", category)
    return _unwrap(query.execute())


def get_bug_by_id(bug_id: str) -> dict[str, Any] | None:
    result = _unwrap(
        get_client().table("bugs").select("*").eq("id", bug_id).limit(1).execute()
    )
    return result[0] if result else None


def update_bug_status(bug_id: str, status: str) -> dict[str, Any]:
    result = _unwrap(
        get_client().table("bugs").update({"status": status}).eq("id", bug_id).execute()
    )
    return result[0]


def close_bug_with_resolution(bug_id: str, resolution: str) -> dict[str, Any]:
    result = _unwrap(
        get_client()
        .table("bugs")
        .update({
            "status": "closed",
            "resolution": resolution,
            "closed_at": _now_iso(),
        })
        .eq("id", bug_id)
        .execute()
    )
    return result[0]


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def add_comment(bug_id: str, comment: str) -> dict[str, Any]:
    result = _unwrap(
        get_client().table("comments").insert({"bug_id": bug_id, "comment": comment}).execute()
    )
    return result[0]


def get_comments_for_bug(bug_id: str) -> list[dict[str, Any]]:
    return _unwrap(
        get_client()
        .table("comments")
        .select("*")
        .eq("bug_id", bug_id)
        .order("created_at", desc=False)
        .execute()
    )