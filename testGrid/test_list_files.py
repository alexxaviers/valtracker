#!/usr/bin/env python3
"""Simple script to list files for a GRID series and print raw JSON.

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

    url = f"https://api.grid.gg/file-download/list/{series_id}"
    headers = {"Accept": "application/json", "x-api-key": api_key}

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(url, headers=headers)
    except httpx.RequestError as exc:
        fail(f"Network request failed: {exc}")

    # Print HTTP status and headers first
    print("HTTP status:", resp.status_code)
    print("Response headers:")
    for k, v in resp.headers.items():
        print(f"{k}: {v}")

    # Try to parse JSON, but print raw body on parse error
    try:
        body: Any = resp.json()
    except Exception:
        print("Failed to parse JSON body. Raw response body:")
        print(resp.text)
        # Raise for status so caller sees non-2xx as failure
        try:
            resp.raise_for_status()
        except Exception as exc:
            fail(f"HTTP error: {exc}")
        fail("Invalid JSON response")

    # Pretty-print JSON
    print("\nJSON body:")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    # If non-success status, exit non-zero after printing
    if resp.status_code >= 400:
        fail(f"Request returned status {resp.status_code}")


if __name__ == "__main__":
    main()
