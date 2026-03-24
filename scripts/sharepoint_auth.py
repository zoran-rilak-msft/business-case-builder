"""MSAL device-code flow authentication for Microsoft Graph API.

Provides token acquisition and caching for SharePoint document access.
Requires BCB_GRAPH_CLIENT_ID environment variable (Azure AD app registration).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import msal

# Default scopes for SharePoint read access
DEFAULT_SCOPES = ["Sites.Read.All", "Files.Read.All"]

# Token cache location
_CACHE_DIR = Path.home() / ".bcb"
_CACHE_FILE = _CACHE_DIR / "graph_token_cache.bin"

# Microsoft common authority (multi-tenant)
_AUTHORITY = "https://login.microsoftonline.com/common"


def _get_client_id() -> str:
    client_id = os.environ.get("BCB_GRAPH_CLIENT_ID")
    if not client_id:
        print(
            "Error: BCB_GRAPH_CLIENT_ID environment variable is not set.\n"
            "Set it to the Application (client) ID of your Azure AD app registration.\n"
            "See README.md for setup instructions.",
            file=sys.stderr,
        )
        sys.exit(1)
    return client_id


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if _CACHE_FILE.exists():
        cache.deserialize(_CACHE_FILE.read_text())
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(cache.serialize())


def get_graph_token(scopes: list[str] | None = None) -> str:
    """Acquire a Microsoft Graph access token using device-code flow with caching.

    Returns the access token string. Exits with error if authentication fails.
    """
    scopes = scopes or DEFAULT_SCOPES
    client_id = _get_client_id()
    cache = _load_cache()

    app = msal.PublicClientApplication(
        client_id,
        authority=_AUTHORITY,
        token_cache=cache,
    )

    # Try silent acquisition from cache first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _save_cache(cache)
            return result["access_token"]

    # Fall back to device-code flow
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        print(
            "Error: Could not initiate device-code flow: "
            f"{flow.get('error_description', 'unknown error')}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(flow["message"], file=sys.stderr)

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        print(
            f"Error: Authentication failed: {result.get('error_description', 'unknown error')}",
            file=sys.stderr,
        )
        sys.exit(1)

    _save_cache(cache)
    return result["access_token"]


def clear_cache() -> None:
    """Remove the cached token file."""
    if _CACHE_FILE.exists():
        _CACHE_FILE.unlink()
        print("Token cache cleared.", file=sys.stderr)
    else:
        print("No token cache found.", file=sys.stderr)
