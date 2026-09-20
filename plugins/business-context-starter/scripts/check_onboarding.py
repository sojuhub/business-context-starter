#!/usr/bin/env python3
"""Read-only consistency check of recorded onboarding source receipts, not OAuth proof."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from compile_context import (_validate_destination, _safe_child, _read_json,
                             _read_evidence, _source_ids)


def check_onboarding(destination: Path) -> dict:
    destination = _validate_destination(destination)
    state = _read_json(_safe_child(destination, "state/onboarding.json"))
    manifest = _read_json(_safe_child(destination, "sources/manifest.json"))
    company, _, sources = _source_ids(manifest)
    if state.get("company_id") != company:
        raise ValueError("state and manifest company must match")
    ids = state.get("requested_source_ids", [])
    if not isinstance(ids, list) or any(not isinstance(x, str) or not x.strip() for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("requested_source_ids must be unique non-empty strings")
    scopes = state.get("approved_scopes", [])
    if not isinstance(scopes, list) or any(not isinstance(x, dict) for x in scopes):
        raise ValueError("approved_scopes must be a list of objects")
    evidence_path = _safe_child(destination, "sources/evidence.jsonl")
    evidence = _read_evidence(evidence_path) if evidence_path.exists() else {}
    blockers, deferred, fixtures, read = [], [], [], []
    if state.get("discovery_status") != "complete":
        blockers.append("connection-discovery-pending")
    if not ids:
        blockers.append("source-selection-pending")
    for source_id in ids:
        source = sources.get(source_id, {})
        disposition = source.get("disposition")
        if disposition in ("deferred", "not-used"):
            if not isinstance(source.get("decision_ref"), str) or not source["decision_ref"].strip():
                blockers.append(f"{source_id}:owner-decision-missing")
            elif disposition == "deferred":
                deferred.append(source_id)
            continue
        receipt = source.get("read_receipt", {})
        if not isinstance(receipt, dict):
            raise ValueError("read_receipt must be an object")
        matching_scope = any(
            x.get("source_id") == source_id
            and all(isinstance(x.get(k), str) and x[k].strip() for k in ("account_ref", "scope", "approval_ref"))
            and all(x[k] == receipt.get(k) for k in ("account_ref", "scope"))
            for x in scopes)
        if not matching_scope:
            blockers.append(f"{source_id}:scope-approval-missing-or-mismatched")
        count = source.get("record_count")
        valid = (disposition == "collect"
                 and source.get("auth_status") in ("authenticated", "not-required")
                 and source.get("read_status") == "read"
                 and source.get("gaps") == []
                 and type(count) is int and count >= 0
                 and receipt.get("coverage_complete") is True
                 and receipt.get("evidence_mode") in ("live", "fixture")
                 and all(isinstance(receipt.get(k), str) and receipt[k].strip()
                         for k in ("tool", "receipt_ref", "checked_at")))
        if not valid:
            blockers.append(f"{source_id}:read-or-coverage-pending")
            continue
        if count and not any(x["source_id"] == source_id for x in evidence.values()):
            blockers.append(f"{source_id}:content-evidence-missing")
            continue
        if matching_scope:
            read.append(source_id)
        if receipt["evidence_mode"] == "fixture":
            fixtures.append(source_id)
    status = ("source-blocked" if blockers else "source-partial" if deferred
              else "fixture-only" if fixtures else "source-complete" if read
              else "no-sources-read")
    return {"company_id": company, "source_status": status, "read_sources": read,
            "deferred_sources": deferred, "fixture_sources": fixtures, "blockers": blockers,
            "review_status": state.get("review_status", "not-reviewed"),
            "next_action": state.get("next_action"),
            "boundary": "Recorded receipt consistency only; not independent provider or fresh-session verification."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = check_onboarding(args.destination)
        print(json.dumps(result, indent=2))
        return 0 if result["source_status"] == "source-complete" else 1
    except (ValueError, OSError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
