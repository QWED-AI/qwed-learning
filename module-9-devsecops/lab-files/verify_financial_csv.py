"""Sample deterministic verification gate for CI/CD course labs.

This script intentionally uses standard-library checks so learners can see the
policy boundary clearly:
- transaction AML threshold checks
- additive rate validation for the senior-citizen lab
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TESTED_QWED_VERSION = "5.2.0"


def verify_transactions(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        transaction_id = row.get("transaction_id", f"row-{index}")
        try:
            amount = float(row["amount"].strip())
            flagged_value = row["llm_flagged"].strip().lower()
            if flagged_value not in {"true", "false"}:
                raise ValueError("llm_flagged must be true or false")
            flagged = flagged_value == "true"
        except (KeyError, ValueError, AttributeError) as exc:
            findings.append(
                {
                    "rule": "MALFORMED_ROW",
                    "transaction_id": transaction_id,
                    "row": str(index),
                    "message": f"Malformed transaction row: {exc}",
                }
            )
            continue

        if amount >= 10_000 and not flagged:
            findings.append(
                {
                    "rule": "AML_THRESHOLD",
                    "transaction_id": transaction_id,
                    "row": str(index),
                    "message": "Transactions at or above $10,000 must be flagged.",
                }
            )
    return findings


def verify_rates(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        product_name = row.get("product") or row.get("product_name") or f"row-{index}"
        output_key = "claude_output" if "claude_output" in row else "claude_generated_final_rate"

        try:
            base_rate = float(row["base_rate"].strip())
            senior_margin = float(row["senior_margin"].strip())
            claude_output = float(row[output_key].strip())
        except (KeyError, ValueError, AttributeError) as exc:
            findings.append(
                {
                    "rule": "MALFORMED_ROW",
                    "product": product_name,
                    "row": str(index),
                    "message": f"Malformed rate row: {exc}",
                }
            )
            continue

        expected = round(base_rate + senior_margin, 3)
        if round(claude_output, 3) != expected:
            findings.append(
                {
                    "rule": "ADDITIVE_RATE_CHECK",
                    "product": product_name,
                    "row": str(index),
                    "message": (
                        f"Expected additive rate {expected:.3f}, found {claude_output:.3f}."
                    ),
                }
            )
    return findings


def find_policy_violations(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return [{"rule": "EMPTY_INPUT", "message": "No rows to verify."}]

    columns = set(rows[0].keys())
    if {"transaction_id", "amount", "llm_flagged"}.issubset(columns):
        return verify_transactions(rows)

    supports_rates = {"base_rate", "senior_margin"}.issubset(columns)
    supports_legacy_rate_shape = {"product", "claude_output"}.issubset(columns)
    supports_shipped_rate_shape = {"product_name", "claude_generated_final_rate"}.issubset(
        columns
    )
    if supports_rates and (supports_legacy_rate_shape or supports_shipped_rate_shape):
        return verify_rates(rows)

    return [
        {
            "rule": "UNSUPPORTED_SCHEMA",
            "message": "Input columns do not match the supported course lab formats.",
        }
    ]


def emit_findings(findings: list[dict[str, str]], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps({"findings": findings}, indent=2))
        return

    if output_format == "sarif":
        sarif = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {"driver": {"name": "qwed-learning-sample-gate"}},
                    "results": [
                        {"ruleId": finding["rule"], "message": {"text": finding["message"]}}
                        for finding in findings
                    ],
                }
            ],
        }
        print(json.dumps(sarif, indent=2))
        return

    if not findings:
        print("No deterministic policy violations found.")
        return

    for finding in findings:
        print(f"[{finding['rule']}] {finding['message']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    findings = find_policy_violations(rows)
    emit_findings(findings, args.format)

    return 1 if findings and args.fail_on_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
