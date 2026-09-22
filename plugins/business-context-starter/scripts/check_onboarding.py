#!/usr/bin/env python3
"""Read-only consistency check of recorded onboarding source receipts, not OAuth proof."""
from __future__ import annotations

import argparse
import hashlib
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
    result = {"company_id": company, "source_status": status, "read_sources": read,
            "deferred_sources": deferred, "fixture_sources": fixtures, "blockers": blockers,
            "review_status": state.get("review_status", "not-reviewed"),
            "next_action": state.get("next_action"),
            "boundary": "Recorded receipt and file consistency only; not independent provider, semantic quality or session authenticity verification."}
    pending = _completion_gaps(destination, state, sources, evidence, result)
    result.update(onboarding_status="onboarding-incomplete" if pending else "onboarding-complete",
                  completion_blockers=pending)
    return result


COVERAGE = ("customers", "products", "pricing", "workflows", "policies", "tone", "services")


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _strings(value):
    return isinstance(value, list) and all(_text(x) for x in value) and len(set(value)) == len(value)


def _artifact_matches(destination, relative, digest):
    if not _text(relative) or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("saved artifact must be a relative path inside the private workspace")
    if not isinstance(digest, str) or len(digest) != 64:
        return False
    path = _safe_child(destination, relative)
    if not path.is_file():
        return False
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest() == digest


def _completion_gaps(destination, state, sources, evidence, source_result):
    """Require recorded discovery, reviewed knowledge and fresh-session file evidence."""
    completion = _object(state.get("completion", {}), "completion")
    gaps = []
    if state.get("run_status", "active") != "active":
        gaps.append("owner-stop-or-defer")
    if source_result["source_status"] != "source-complete":
        gaps.append("source-collection-incomplete")
    interview = _object(completion.get("service_interview", {}), "service_interview")
    if not all(_text(interview.get(k)) for k in ("most_used", "purpose", "other_services", "confirmation_ref")):
        gaps.append("service-interview-pending")
    services = completion.get("services", [])
    if not isinstance(services, list):
        raise ValueError("services must be a list")
    service_ids, mapped_sources = set(), set()
    for service in services:
        service = _object(service, "service")
        if not all(_text(service.get(k)) for k in ("id", "name", "purpose", "owner_ref")):
            gaps.append("service-inventory-unconfirmed")
            continue
        if service["id"] in service_ids:
            raise ValueError("duplicate service id")
        service_ids.add(service["id"])
        source_ids = service.get("source_ids", [])
        if not _strings(source_ids) or not source_ids or not set(source_ids) <= set(sources):
            gaps.append("service-source-mapping-missing")
        else:
            mapped_sources.update(source_ids)
    if not services or mapped_sources != set(state.get("requested_source_ids", [])):
        gaps.append("service-inventory-incomplete")
    browser = _object(completion.get("browser_discovery", {}), "browser_discovery")
    if not _text(browser.get("owner_confirmation_ref")):
        gaps.append("browser-candidates-unconfirmed")
    if browser.get("status") == "confirmed":
        candidates = browser.get("candidate_service_ids")
        if (not all(_text(browser.get(k)) for k in ("profile_ref", "history_scope", "discovery_approval_ref", "receipt_ref"))
                or not _strings(candidates) or not set(candidates) <= service_ids):
            gaps.append("browser-discovery-incomplete")
    elif browser.get("status") in ("manual-fallback", "not-used"):
        if not _text(browser.get("reason")):
            gaps.append("browser-fallback-reason-missing")
    else:
        gaps.append("browser-discovery-pending")
    coverage = _object(completion.get("business_coverage", {}), "business_coverage")
    coverage_paths, accepted_evidence, evidence_paths = set(), set(), {}
    for category in COVERAGE:
        row = _object(coverage.get(category, {}), category)
        valid = all(_text(row.get(k)) for k in ("summary", "owner_ref"))
        paths = row.get("saved_paths", [])
        valid = valid and _strings(paths) and bool(paths)
        if _strings(paths):
            coverage_paths.update(paths)
        if row.get("status") == "confirmed":
            ids = row.get("evidence_ids", [])
            supported = (_strings(ids) and bool(ids) and all(
                x in evidence and evidence[x]["source_id"] in source_result["read_sources"]
                and evidence[x]["status"] in ("source-stated", "owner-confirmed") for x in ids))
            valid = valid and supported
            if supported:
                accepted_evidence.update(ids)
                if _strings(paths):
                    for evidence_id in ids:
                        evidence_paths.setdefault(evidence_id, set()).update(paths)
        elif row.get("status") == "not-applicable":
            valid = valid and _text(row.get("reason"))
        else:
            valid = False
        if not valid:
            gaps.append(f"business-coverage-pending:{category}")
    if completion.get("material_gaps") != []:
        gaps.append("material-gaps-unresolved")
    storage = _object(completion.get("storage", {}), "storage")
    files = _object(storage.get("files", {}), "storage.files")
    required = {"INDEX.md", "outputs/business-brief.md", "sources/manifest.json", "sources/evidence.jsonl"}
    if not required.union(coverage_paths) <= set(files):
        gaps.append("saved-knowledge-incomplete")
    for path, digest in files.items():
        if not _artifact_matches(destination, path, digest):
            gaps.append(f"saved-artifact-missing-or-changed:{path}")
    retention = _object(completion.get("retention", {}), "retention")
    originals = retention.get("originals")
    if retention.get("mode") != "selective-originals" or not isinstance(originals, list):
        gaps.append("retention-review-pending")
    else:
        for original in originals:
            original = _object(original, "retained original")
            if (not _text(original.get("reason")) or not _text(original.get("path"))
                    or original["path"] not in files or not _text(original.get("source_id"))
                    or original["source_id"] not in source_result["read_sources"]):
                gaps.append("retained-original-unverified")
    review = _object(completion.get("owner_review", {}), "owner_review")
    if (state.get("review_status") != "owner-approved" or review.get("status") != "approved"
            or not _text(review.get("receipt_ref")) or not files or review.get("files") != files):
        gaps.append("owner-review-missing-or-stale")
    fresh = _object(completion.get("fresh_session", {}), "fresh_session")
    read_files = _object(fresh.get("files_read", {}), "fresh_session.files_read")
    applied = fresh.get("applied_evidence_ids", [])
    valid_fresh = (fresh.get("status") == "passed"
                   and all(_text(fresh.get(k)) for k in ("session_id", "onboarding_session_id", "receipt_ref", "checked_at"))
                   and fresh.get("session_id") != fresh.get("onboarding_session_id")
                   and "INDEX.md" in read_files and bool((coverage_paths - {"INDEX.md"}).intersection(read_files))
                   and all(path in files and files[path] == digest for path, digest in read_files.items())
                   and _strings(applied) and bool(applied) and set(applied) <= accepted_evidence
                   and all(evidence_paths.get(x, set()).intersection(read_files) for x in applied))
    if not valid_fresh:
        gaps.append("fresh-session-verification-pending")
    if not _text(fresh.get("draft_path")) or not _artifact_matches(destination, fresh["draft_path"], fresh.get("draft_sha256")):
        gaps.append("fresh-session-draft-missing-or-changed")
    return gaps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--sources-only", action="store_true", help="Diagnostic only; does not establish onboarding completion")
    args = parser.parse_args()
    try:
        result = check_onboarding(args.destination)
        print(json.dumps(result, indent=2))
        complete = result["source_status"] == "source-complete" if args.sources_only else result["onboarding_status"] == "onboarding-complete"
        return 0 if complete else 1
    except (ValueError, OSError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
