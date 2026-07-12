"""Fail-closed sanitization for data that may cross an external boundary.

This module intentionally treats unknown objects conservatively.  It returns a
sanitized copy and never calls ``repr`` on caller-controlled objects, because a
custom representation can both fail and disclose data.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


class UnsafeExternalTransmissionError(RuntimeError):
    """Raised when an outbound payload still appears to contain a credential."""

    def __init__(self) -> None:
        super().__init__("Outbound evaluation request blocked by secret-safety preflight.")


REDACTED = "[REDACTED]"
_PLACEHOLDER = re.compile(r"^\[REDACTED(?:_[A-Z]+)*\]$")
_SENSITIVE_PARTS = frozenset({
    "key", "token", "secret", "password", "passwd", "pwd", "credential",
    "auth", "authorization", "private", "access", "session", "cookie",
})
_AUTH_HEADER_NAMES = frozenset({"authorization", "proxyauthorization"})
_COOKIE_HEADER_NAMES = frozenset({"cookie", "setcookie"})

# These patterns identify values, not ordinary prose.  Environment-style and
# header-style credentials are handled structurally before these patterns run.
_PEM = re.compile(r"-----BEGIN(?: [A-Z0-9]+)? PRIVATE KEY-----.*?-----END(?: [A-Z0-9]+)? PRIVATE KEY-----", re.I | re.S)
_DATABASE_URL = re.compile(r"\b(?:postgres(?:ql)?|mysql(?:\+[\w-]+)?|mariadb|mongodb(?:\+srv)?|redis|amqps?)://[^\s/@:]+:[^\s/@]+@[^\s]+", re.I)
_AUTH_HEADER = re.compile(r"(?im)\b(?:proxy-)?authorization\s*:\s*(?:bearer|basic)\s+[^\s,;]+")
_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{8,}")
_COOKIE = re.compile(r"(?i)\b(?:session(?:id)?|auth(?:entication)?|access[_-]?token|refresh[_-]?token|jwt)\s*=\s*[^;\s,]+")
_OPENAI = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{8,}\b")
_GITHUB = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]{8,})\b", re.I)
_STRIPE = re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9_]{8,}\b", re.I)
_SLACK = re.compile(r"\bxox(?:b|p|a|r|s)-[A-Za-z0-9-]{8,}\b|\bxapp-[A-Za-z0-9-]{8,}\b", re.I)
_AWS_ACCESS_KEY = re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")
_GOOGLE = re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_ENV_ASSIGNMENT = re.compile(r"(?im)\b([A-Za-z][A-Za-z0-9_.-]{1,127})\s*=\s*([^\s,;]+)")


def _key_parts(value: str) -> set[str]:
    # Split snake/kebab/camel case without treating prose such as "keyboard"
    # or "token budget" as a sensitive field name.
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return {part.lower() for part in re.findall(r"[A-Za-z0-9]+", normalized)}


def is_sensitive_field_name(value: object) -> bool:
    """Return whether a structured field name conventionally carries a secret."""
    if not isinstance(value, str):
        return False
    parts = _key_parts(value)
    if not parts:
        return False
    compact = re.sub(r"[^a-z0-9]", "", value.lower())
    if compact in _AUTH_HEADER_NAMES or compact in _COOKIE_HEADER_NAMES:
        return True
    if compact in {"apikey", "accesstoken", "clientsecret", "privatekey", "password", "passwd", "pwd"}:
        return True
    return bool(parts & _SENSITIVE_PARTS)


def _placeholder_for_field(name: object) -> str:
    parts = _key_parts(name) if isinstance(name, str) else set()
    if "private" in parts and "key" in parts:
        return "[REDACTED_PRIVATE_KEY]"
    if "password" in parts or "passwd" in parts or "pwd" in parts:
        return "[REDACTED_PASSWORD]"
    if "authorization" in parts or "auth" in parts:
        return "[REDACTED_AUTHORIZATION]"
    if "cookie" in parts or "session" in parts:
        return "[REDACTED_SESSION]"
    if "token" in parts or "access" in parts:
        return "[REDACTED_TOKEN]"
    return REDACTED


def _redact_string(value: str) -> str:
    """Remove credential-shaped values while leaving normal technical prose intact."""
    def assignment(match: re.Match[str]) -> str:
        name, secret = match.group(1), match.group(2)
        return f"{name}={_placeholder_for_field(name)}" if is_sensitive_field_name(name) else match.group(0)

    result = _ENV_ASSIGNMENT.sub(assignment, value)
    replacements: tuple[tuple[re.Pattern[str], str], ...] = (
        (_PEM, "[REDACTED_PRIVATE_KEY]"),
        (_DATABASE_URL, "[REDACTED_DATABASE_URL]"),
        (_AUTH_HEADER, "Authorization: [REDACTED_AUTHORIZATION]"),
        (_BEARER, "Bearer [REDACTED_TOKEN]"),
        (_COOKIE, "[REDACTED_SESSION]"),
        (_OPENAI, "[REDACTED_TOKEN]"),
        (_GITHUB, "[REDACTED_TOKEN]"),
        (_STRIPE, "[REDACTED_TOKEN]"),
        (_SLACK, "[REDACTED_TOKEN]"),
        (_AWS_ACCESS_KEY, "[REDACTED_ACCESS_KEY]"),
        (_GOOGLE, "[REDACTED_TOKEN]"),
        (_JWT, "[REDACTED_TOKEN]"),
    )
    for pattern, replacement in replacements:
        result = pattern.sub(replacement, result)
    return result


def redact_sensitive_data(value: Any, *, max_depth: int = 32) -> Any:
    """Return a sanitized copy of strings and nested JSON-like input.

    Cycles, overly deep structures, unsupported objects, and exceptions are
    replaced by a safe placeholder rather than being stringified.
    """
    def visit(item: Any, depth: int, seen: set[int]) -> Any:
        if depth > max_depth:
            return "[REDACTED_DEPTH_LIMIT]"
        if item is None or isinstance(item, (bool, int, float)):
            return item
        if isinstance(item, str):
            return _redact_string(item)
        if isinstance(item, BaseException):
            return "[REDACTED_EXCEPTION]"
        if isinstance(item, Mapping):
            identifier = id(item)
            if identifier in seen:
                return "[REDACTED_CYCLE]"
            seen.add(identifier)
            try:
                sanitized: dict[str, Any] = {}
                for key, child in item.items():
                    safe_key = key if isinstance(key, str) else "[REDACTED_KEY]"
                    sanitized[safe_key] = _placeholder_for_field(safe_key) if is_sensitive_field_name(safe_key) else visit(child, depth + 1, seen)
                return sanitized
            except Exception:
                return "[REDACTED_UNSUPPORTED]"
            finally:
                seen.discard(identifier)
        if isinstance(item, (list, tuple)):
            identifier = id(item)
            if identifier in seen:
                return "[REDACTED_CYCLE]"
            seen.add(identifier)
            try:
                values = [visit(child, depth + 1, seen) for child in item]
                return tuple(values) if isinstance(item, tuple) else values
            except Exception:
                return "[REDACTED_UNSUPPORTED]"
            finally:
                seen.discard(identifier)
        return "[REDACTED_UNSUPPORTED]"

    return visit(value, 0, set())


def find_unredacted_secrets(value: Any, *, max_depth: int = 32) -> set[str]:
    """Return secret categories found in a value without returning their values."""
    findings: set[str] = set()

    def inspect_string(item: str) -> None:
        if _PLACEHOLDER.fullmatch(item):
            return
        patterns = (
            ("private_key", _PEM), ("database_url", _DATABASE_URL), ("authorization", _AUTH_HEADER),
            ("bearer", _BEARER), ("session_cookie", _COOKIE), ("openai", _OPENAI),
            ("github", _GITHUB), ("stripe", _STRIPE), ("slack", _SLACK),
            ("aws_access_key", _AWS_ACCESS_KEY), ("google_api_key", _GOOGLE), ("jwt", _JWT),
        )
        for category, pattern in patterns:
            if pattern.search(item):
                findings.add(category)
        for match in _ENV_ASSIGNMENT.finditer(item):
            if is_sensitive_field_name(match.group(1)) and not _PLACEHOLDER.fullmatch(match.group(2)):
                findings.add("sensitive_assignment")

    def visit(item: Any, depth: int, seen: set[int]) -> None:
        if depth > max_depth:
            findings.add("depth_limit")
            return
        if isinstance(item, str):
            inspect_string(item)
            return
        if isinstance(item, BaseException):
            findings.add("unsupported_exception")
            return
        if isinstance(item, Mapping):
            identifier = id(item)
            if identifier in seen:
                findings.add("cycle")
                return
            seen.add(identifier)
            try:
                for key, child in item.items():
                    if is_sensitive_field_name(key) and child != _placeholder_for_field(key) and child != REDACTED:
                        findings.add("sensitive_field")
                    else:
                        visit(child, depth + 1, seen)
            except Exception:
                findings.add("unsupported_mapping")
            finally:
                seen.discard(identifier)
            return
        if isinstance(item, (list, tuple)):
            identifier = id(item)
            if identifier in seen:
                findings.add("cycle")
                return
            seen.add(identifier)
            try:
                for child in item:
                    visit(child, depth + 1, seen)
            except Exception:
                findings.add("unsupported_sequence")
            finally:
                seen.discard(identifier)
            return
        if item is not None and not isinstance(item, (bool, int, float)):
            findings.add("unsupported_object")

    visit(value, 0, set())
    return findings


def assert_safe_for_external_transmission(value: Any) -> None:
    """Fail closed without including payload data in the resulting exception."""
    if find_unredacted_secrets(value):
        raise UnsafeExternalTransmissionError()
