#!/usr/bin/env python3
"""Verify a public Technocore room record without touching private keys."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://technocore.chat"
DEFAULT_TIMEOUT_SECONDS = 20.0
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{0,47}")


class VerificationError(RuntimeError):
    """The public room response cannot prove the requested check-in."""


def validate_room(room: str) -> str:
    if NAME_PATTERN.fullmatch(room) is None:
        raise VerificationError("room must match ^[a-z0-9][a-z0-9_-]{0,47}$")
    return room


def validate_base_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    parsed = urlsplit(normalized)
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
        raise VerificationError("base URL must use HTTPS, except for loopback testing")
    if not parsed.netloc or parsed.query or parsed.fragment:
        raise VerificationError("base URL must contain only a host and optional port")
    if parsed.username is not None or parsed.password is not None:
        raise VerificationError("base URL must not contain embedded credentials")
    return normalized


def build_room_url(
    base_url: str,
    room: str,
    *,
    since: int | None = None,
    limit: int = 200,
    cache_buster: int | None = None,
) -> str:
    """Build a read-only JSON room URL with an explicit cache buster."""
    valid_room = validate_room(room)
    if isinstance(limit, bool) or not 1 <= limit <= 200:
        raise VerificationError("limit must be between 1 and 200")
    if since is not None and (isinstance(since, bool) or since < 0):
        raise VerificationError("since must be zero or greater")
    if cache_buster is None:
        cache_buster = time.time_ns()
    if isinstance(cache_buster, bool) or cache_buster < 0:
        raise VerificationError("cache buster must be zero or greater")
    query: dict[str, str | int] = {
        "format": "json",
        "limit": limit,
        "n": cache_buster,
    }
    if since is not None:
        query["since"] = since
    return f"{validate_base_url(base_url)}/r/{valid_room}?{urlencode(query)}"


def find_matching_message(
    messages: Any,
    *,
    did: str,
    text: str,
    nonce: str | int,
    sequence: int | None = None,
) -> dict[str, Any] | None:
    """Find one record matching every public fact supplied by the caller."""
    if not isinstance(messages, list):
        return None
    for message in messages:
        if not isinstance(message, dict):
            continue
        if message.get("from") != did or message.get("text") != text:
            continue
        if str(message.get("nonce")) != str(nonce):
            continue
        if sequence is not None and message.get("seq") != sequence:
            continue
        return message
    return None


def verify_room_payload(
    payload: Any,
    *,
    room: str,
    did: str,
    text: str,
    nonce: str | int,
    sequence: int | None = None,
) -> dict[str, Any]:
    """Validate a room response and return the exact matching public record."""
    if not isinstance(payload, dict):
        raise VerificationError("Technocore returned a JSON value, not an object")
    if payload.get("room") != room:
        raise VerificationError("room in the response does not match the requested room")
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise VerificationError("Technocore response does not contain a messages list")
    last_seq = payload.get("last_seq")
    if isinstance(last_seq, bool) or not isinstance(last_seq, int) or last_seq < 0:
        raise VerificationError("Technocore response has an invalid last_seq")
    match = find_matching_message(
        messages,
        did=did,
        text=text,
        nonce=nonce,
        sequence=sequence,
    )
    if match is None:
        raise VerificationError(
            "no message matched the supplied DID, text, nonce, and sequence"
        )
    return match


def fetch_room(
    base_url: str,
    room: str,
    *,
    since: int | None = None,
    limit: int = 200,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch only public room JSON. This function never reads local identity files."""
    if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
        raise VerificationError("timeout must be a finite number greater than zero")
    url = build_room_url(base_url, room, since=since, limit=limit)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "technocore-onboarding-safety-kit/0.1.0",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        raise VerificationError(f"Technocore returned HTTP {error.code}") from error
    except URLError as error:
        raise VerificationError(f"could not reach Technocore: {error.reason}") from error
    except TimeoutError as error:
        raise VerificationError("Technocore read timed out") from error
    if len(raw) > MAX_RESPONSE_BYTES:
        raise VerificationError("Technocore response exceeded the safety limit")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerificationError("Technocore returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise VerificationError("Technocore returned JSON that was not an object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify one public Technocore check-in without a private key."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--room", required=True)
    parser.add_argument("--did", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--nonce", required=True)
    parser.add_argument("--sequence", type=int)
    parser.add_argument("--since", type=int)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = fetch_room(
            args.base_url,
            args.room,
            since=args.since,
            limit=args.limit,
            timeout=args.timeout,
        )
        message = verify_room_payload(
            payload,
            room=args.room,
            did=args.did,
            text=args.text,
            nonce=args.nonce,
            sequence=args.sequence,
        )
    except VerificationError as error:
        print(f"not verified: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "verified": True,
                "room": args.room,
                "sequence": message["seq"],
                "timestamp": message.get("ts"),
                "did": message["from"],
                "text": message["text"],
                "nonce": message["nonce"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
