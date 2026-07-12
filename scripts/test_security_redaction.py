#!/usr/bin/env python3
"""Offline regression tests for outbound evaluation-data sanitization."""
from __future__ import annotations

import io
import json
import sys
import unittest
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import run_behavioral_evals as behavioral
from evaluation_context import build_evaluation_request
from security.redaction import (
    UnsafeExternalTransmissionError,
    assert_safe_for_external_transmission,
    find_unredacted_secrets,
    redact_sensitive_data,
)


class _Response:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class RedactionTests(unittest.TestCase):
    def assert_absent(self, raw: str, sanitized: object) -> None:
        self.assertFalse(raw in json.dumps(sanitized, ensure_ascii=False), "raw credential survived sanitization")

    def test_environment_and_authorization_examples_are_redacted(self) -> None:
        examples = [
            "OPENAI_API_KEY=sk-proj-EXAMPLEVALUE1234567890",
            "Authorization: Bearer ghp_EXAMPLEVALUE1234567890",
            "GITHUB_TOKEN=github_pat_EXAMPLEVALUE1234567890",
            "DATABASE_PASSWORD=super-secret-example",
            "STRIPE_SECRET_KEY=sk_live_EXAMPLEVALUE1234567890",
            "AWS_SECRET_ACCESS_KEY=example-secret-value",
        ]
        for raw in examples:
            sanitized = redact_sensitive_data(raw)
            self.assert_absent(raw.split("=", 1)[-1].split()[-1], sanitized)
            self.assertEqual(set(), find_unredacted_secrets(sanitized))

    def test_nested_headers_files_and_mixed_case_sensitive_fields_are_redacted(self) -> None:
        raw_values = ["sk-proj-EXAMPLEVALUE1234567890", "ghp_EXAMPLEVALUE1234567890", "very-secret", "basic-value"]
        source = {
            "payload": [{"api_key": raw_values[0]}, {"Headers": {"Authorization": "Bearer " + raw_values[1]}}],
            "files": [{"content": "DATABASE_PASSWORD=" + raw_values[2]}],
            "clientSecret": raw_values[3],
            "tuple": ({"PassWd": raw_values[2]},),
        }
        sanitized = redact_sensitive_data(source)
        for raw in raw_values:
            self.assert_absent(raw, sanitized)
        self.assertEqual(set(), find_unredacted_secrets(sanitized))
        self.assertEqual("[REDACTED_AUTHORIZATION]", sanitized["payload"][1]["Headers"]["Authorization"])

    def test_case_insensitive_sensitive_field_matrix_is_redacted_recursively(self) -> None:
        field_names = ["api_key", "Api_Key", "API_KEY", "clientSecret", "CLIENT_SECRET", "password", "PassWd"]
        source = {"outer": [{name: "opaque-example-value-" + str(index)} for index, name in enumerate(field_names)]}
        sanitized = redact_sensitive_data(source)
        for index in range(len(field_names)):
            self.assert_absent("opaque-example-value-" + str(index), sanitized)
        self.assertEqual(set(), find_unredacted_secrets(sanitized))

    def test_authorization_proxy_authorization_and_session_cookie_values_are_redacted(self) -> None:
        values = [
            "Authorization: Basic YWxpY2U6c2VjcmV0LWV4YW1wbGU=",
            "Proxy-Authorization: Bearer ghp_EXAMPLEVALUE1234567890",
            "Cookie: sessionid=session-example-value-123456",
        ]
        sanitized = redact_sensitive_data("\n".join(values))
        for raw in values:
            self.assert_absent(raw.split(": ", 1)[1], sanitized)
        self.assertEqual(set(), find_unredacted_secrets(sanitized))

    def test_provider_patterns_database_urls_jwts_and_pem_blocks_are_redacted(self) -> None:
        values = [
            "xoxb-EXAMPLEVALUE1234567890",
            "AKIA1234567890ABCDEF",
            "AIza" + "A" * 35,
            "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJleGFtcGxlIn0.signature-example-value",
            "postgresql://user:database-password@db.example.test/app",
            "-----BEGIN PRIVATE KEY-----\nexample-private-material\n-----END PRIVATE KEY-----",
        ]
        sanitized = redact_sensitive_data("\n".join(values))
        for raw in values:
            self.assert_absent(raw, sanitized)
        self.assertEqual(set(), find_unredacted_secrets(sanitized))

    def test_normal_technical_prose_is_not_over_redacted(self) -> None:
        prose = "The token budget covers primary key design, keyboard key handling, password policy, and API key rotation documentation."
        self.assertEqual(prose, redact_sensitive_data(prose))
        self.assertEqual(set(), find_unredacted_secrets(prose))

    def test_cycles_depth_and_hostile_objects_fail_safe_without_stringifying(self) -> None:
        class Hostile:
            def __str__(self) -> str:
                raise AssertionError("must not stringify untrusted object")

        cycle: list[object] = []
        cycle.append(cycle)
        sanitized = redact_sensitive_data({"cycle": cycle, "unknown": Hostile()}, max_depth=2)
        self.assertEqual("[REDACTED_CYCLE]", sanitized["cycle"][0])
        self.assertEqual("[REDACTED_UNSUPPORTED]", sanitized["unknown"])

    def test_preflight_blocks_raw_suspicious_data_without_echoing_it(self) -> None:
        raw = "Authorization: Bearer ghp_EXAMPLEVALUE1234567890"
        with self.assertRaises(UnsafeExternalTransmissionError) as raised:
            assert_safe_for_external_transmission(raw)
        self.assertNotIn("ghp_", str(raised.exception))


class ExternalBoundaryTests(unittest.TestCase):
    ENV = {
        "EVAL_OPENAI_BASE_URL": "https://model.example.test/v1",
        "EVAL_OPENAI_API_KEY": "provider-test-key",
        "EVAL_OPENAI_MODEL": "test-model",
    }

    def evaluation_request(self, user_request: str, files: list[str] | None = None):
        case = next(case for case in behavioral.load_cases() if case["id"] == "security-audit-happy-path-001")
        case = deepcopy(case)
        case["input"]["request"] = user_request
        case["input"]["files"] = files or []
        return build_evaluation_request(case, "security-audit")

    def test_only_sanitized_payload_reaches_mocked_transport_and_no_logs_leak(self) -> None:
        request_secret = "sk-proj-EXAMPLEVALUE1234567890"
        header_secret = "ghp_EXAMPLEVALUE1234567890"
        fixture_secret = "sk_live_SYNTHETIC_NOT_A_REAL_SECRET_123456"
        calls: list[object] = []

        def transport(request: object, timeout: int) -> _Response:
            calls.append(request)
            body = request.data.decode("utf-8")  # type: ignore[attr-defined]
            headers = dict(request.header_items())  # type: ignore[attr-defined]
            for raw in (request_secret, header_secret, fixture_secret):
                self.assertFalse(raw in body, "raw credential reached mocked body")
                self.assertFalse(any(raw in value for value in headers.values()), "raw credential reached mocked headers")
            return _Response({"choices": [{"message": {"content": "Scope\nEvidence\nAssumptions\nFindings\nNext steps"}}]})

        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = behavioral.openai_compatible(
                self.evaluation_request(f"OPENAI_API_KEY={request_secret}\nAuthorization: Bearer {header_secret}", ["fixtures/synthetic-secret.txt"]),
                environment=self.ENV,
                transport=transport,
            )
        self.assertEqual(1, len(calls))
        self.assertIn("Scope", result["text"])
        combined_logs = stdout.getvalue() + stderr.getvalue()
        for raw in (request_secret, header_secret, fixture_secret):
            self.assertFalse(raw in combined_logs, "raw credential reached logs")

    def test_preflight_failure_blocks_transport(self) -> None:
        calls: list[object] = []

        def transport(*_: object, **__: object) -> _Response:
            calls.append(object())
            return _Response({})

        raw = "OPENAI_API_KEY=sk-proj-EXAMPLEVALUE1234567890"
        # Simulate a future sanitizer regression: the final boundary scan must
        # still stop the request and must not disclose the raw value.
        with patch.object(behavioral, "redact_sensitive_data", side_effect=lambda value: value):
            with self.assertRaises(UnsafeExternalTransmissionError) as raised:
                behavioral.openai_compatible(self.evaluation_request(raw), environment=self.ENV, transport=transport)
        self.assertEqual([], calls)
        self.assertNotIn("sk-proj", str(raised.exception))

    def test_transport_exceptions_are_converted_without_payload_details(self) -> None:
        raw = "sk-proj-EXAMPLEVALUE1234567890"

        def transport(*_: object, **__: object) -> _Response:
            raise RuntimeError("request failed: " + raw)

        with self.assertRaises(behavioral.ExternalModelEvaluationError) as raised:
            behavioral.openai_compatible(self.evaluation_request("request"), environment=self.ENV, transport=transport)
        self.assertNotIn(raw, str(raised.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
