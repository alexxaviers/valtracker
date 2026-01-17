#!/usr/bin/env python3
"""Fetch end-state for a GRID series and print top-level keys and a preview.

Requirements: httpx, Python 3.11+
Reads GRID_API_KEY and GRID_TEST_SERIES_ID from environment.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

import httpx


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> None:
    api_key = os.getenv("GRID_API_KEY")
    series_id = os.getenv("GRID_TEST_SERIES_ID")

    if not api_key:
        fail("GRID_API_KEY environment variable is not set", 2)
    if not series_id:
        fail("GRID_TEST_SERIES_ID environment variable is not set", 2)

    url = f"https://api.grid.gg/file-download/end-state/grid/series/{series_id}"
    headers = {"Accept": "application/json", "x-api-key": api_key}

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(url, headers=headers)
    except httpx.RequestError as exc:
        fail(f"Network request failed: {exc}")

    print("HTTP status:", resp.status_code)

    # Try parse JSON
    try:
        body: Any = resp.json()
    except Exception:
        print("Failed to parse JSON body. Raw response body:")
        print(resp.text)
        try:
            resp.raise_for_status()
        except Exception as exc:
            fail(f"HTTP error: {exc}")
        fail("Invalid JSON response")

    # Print top-level keys if object, otherwise print type
    if isinstance(body, dict):
        print("Top-level keys:", list(body.keys()))
    else:
        print("Response JSON is not an object; type:", type(body))

    pretty = json.dumps(body, indent=2, ensure_ascii=False)
    preview = pretty[:2000]
    print("\nJSON preview (first ~2000 chars):")
    print(preview)

    if resp.status_code >= 400:
        fail(f"Request returned status {resp.status_code}")


if __name__ == "__main__":
    main()
