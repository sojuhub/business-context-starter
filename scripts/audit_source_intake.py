#!/usr/bin/env python3
"""Offline source-intake audit prototype; no live connector or account access."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

MAX_RECORDS = 200
MAX_TEXT_BYTES = 1_000_000
MAX_TOTAL_BYTES = 10_000_000
MAX_INPUT_BYTES = 12_000_000
TRUSTED_SYSTEM_SYMLINKS = {Path("/var"), Path("/tmp")}
REQUIRED = ("source_id", "record_id", "company_id", "locator", "text", "checked_at")


def _stable_key(record: dict[str, str]) -> str:
    raw = json.dumps([record[field] for field in ("company_id", "source_id", "record_id")], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"existing JSON is unreadable: {path}") from exc


def _reject_symlink_components(path: Path) -> Path:
    absolute = path.expanduser().absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        if current.is_symlink() and current not in TRUSTED_SYSTEM_SYMLINKS:
            raise ValueError(f"path contains a symlink component: {current}")
    return absolute


def _validate_destination(destination: Path) -> Path:
    destination = _reject_symlink_components(destination)
    resolved = destination.resolve(strict=False)
    repo = Path(__file__).resolve().parents[1]
    home = Path.home().resolve()
    plugin_cache = home / ".codex" / "plugins" / "cache"
    if resolved == repo or repo in resolved.parents:
        raise ValueError("destination must be outside the repository")
    if resolved == plugin_cache or plugin_cache in resolved.parents:
        raise ValueError("destination must be outside the plugin cache")
    if resolved == home:
        raise ValueError("destination must not be the home directory")
    return resolved


def _safe_child(path: Path, destination: Path) -> Path:
    path = _reject_symlink_components(path)
    resolved = path.resolve(strict=False)
    if resolved != destination and destination not in resolved.parents:
        raise ValueError(f"destination child escapes destination: {path}")
    return resolved


def _validate_records(records: list[dict[str, Any]], company_id: str, allowed: set[str]) -> list[dict[str, str]]:
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError(f"records must be a list of at most {MAX_RECORDS} items")
    try:
        serialized_bytes = len(json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    except (TypeError, ValueError) as exc:
        raise ValueError("records must be JSON-serializable") from exc
    if serialized_bytes > MAX_INPUT_BYTES:
        raise ValueError("serialized input exceeds the size limit")
    if not isinstance(company_id, str) or not company_id.strip():
        raise ValueError("company_id must be a non-empty string")
    if not isinstance(allowed, set) or not all(isinstance(item, str) for item in allowed):
        raise ValueError("allowed_source_ids must be a set of strings")
    clean: list[dict[str, str]] = []
    total = 0
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or any(field not in record for field in REQUIRED):
            raise ValueError(f"record {index} is missing a required field")
        if any(not isinstance(record[field], str) or not record[field].strip() for field in REQUIRED):
            raise ValueError(f"record {index} has an invalid required field")
        if record["company_id"] != company_id:
            raise ValueError(f"record {index} belongs to another company")
        if record["source_id"] not in allowed:
            raise ValueError(f"record {index} uses an unapproved source")
        text_bytes = len(record["text"].encode("utf-8"))
        if text_bytes > MAX_TEXT_BYTES:
            raise ValueError(f"record {index} exceeds the text size limit")
        total += text_bytes
        item = {field: record[field] for field in REQUIRED}
        identity = _stable_key(item)
        if identity in seen:
            raise ValueError(f"duplicate source identity in input: {identity}")
        seen.add(identity)
        clean.append(item)
    if total > MAX_TOTAL_BYTES:
        raise ValueError("input exceeds the total text size limit")
    return clean


def _write_json(path: Path, value: Any) -> None:
    _reject_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.tmp-", delete=False) as handle:
        temp = Path(handle.name)
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"existing evidence is unreadable: {path}") from exc
    rows = []
    seen = set()
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"existing evidence row {line_number} is invalid JSON") from exc
        required = ("id", "source_id", "locator", "claim", "status", "checked_at")
        if not isinstance(row, dict) or any(not isinstance(row.get(field), str) or not row[field].strip() for field in required):
            raise ValueError(f"existing evidence row {line_number} has invalid fields")
        if row["id"] in seen:
            raise ValueError(f"existing evidence has duplicate id: {row['id']}")
        seen.add(row["id"])
        rows.append(row)
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _reject_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.tmp-", delete=False) as handle:
        temp = Path(handle.name)
        handle.write("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def ingest(records: list[dict], destination: Path, company_id: str, allowed_source_ids: set[str]) -> dict:
    """Write approved records and return an audit summary."""
    clean = _validate_records(records, company_id, allowed_source_ids)
    destination = _validate_destination(Path(destination))
    sources = destination / "sources"
    snapshots = sources / "snapshots"
    _safe_child(sources, destination)
    _safe_child(snapshots, destination)
    _safe_child(sources / "manifest.json", destination)
    _safe_child(sources / "evidence.jsonl", destination)
    existing_manifest = _json(sources / "manifest.json", {"company_id": company_id, "sources": []})
    if not isinstance(existing_manifest, dict) or existing_manifest.get("company_id", company_id) != company_id:
        raise ValueError("existing manifest belongs to another company")
    manifest_sources = existing_manifest.get("sources", [])
    if not isinstance(manifest_sources, list):
        raise ValueError("existing manifest sources must be a list")
    for index, source in enumerate(manifest_sources):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source["id"].strip():
            raise ValueError(f"existing manifest source {index} has an invalid id")
        for field in ("record_ids", "locators"):
            if field in source and (not isinstance(source[field], list) or any(not isinstance(value, str) or not value.strip() for value in source[field])):
                raise ValueError(f"existing manifest source {index} has invalid {field}")
        inspected = source.get("inspected_scope")
        if inspected is not None and not isinstance(inspected, (str, list)):
            raise ValueError(f"existing manifest source {index} has invalid inspected_scope")
        if isinstance(inspected, list) and any(not isinstance(value, str) or not value.strip() for value in inspected):
            raise ValueError(f"existing manifest source {index} has invalid inspected_scope values")
    planned = [_stable_key(item) for item in clean]
    for identity in planned:
        _safe_child(snapshots / f"{identity}.json", destination)
    evidence_by_id = {item.get("id"): item for item in _jsonl(sources / "evidence.jsonl") if item.get("id")}
    source_by_id = {item["id"]: item for item in manifest_sources}
    for item in clean:
        identity = _stable_key(item)
        _write_json(snapshots / f"{identity}.json", {**item, "status": "source-stated/unreviewed", "identity": identity})
        prior = evidence_by_id.get(identity)
        evidence = {"id": identity, "source_id": item["source_id"], "locator": item["locator"], "claim": item["text"], "status": "source-stated/unreviewed", "checked_at": item["checked_at"]}
        if prior and prior.get("status") in {"owner-confirmed", "disputed"}:
            evidence = {**prior, "latest_source_claim": item["text"], "latest_checked_at": item["checked_at"]}
        evidence_by_id[identity] = evidence
        source = source_by_id.get(item["source_id"], {})
        record_ids = set(source.get("record_ids", []))
        if isinstance(source.get("inspected_scope"), str):
            record_ids.add(source["inspected_scope"])
        record_ids.add(item["record_id"])
        locators = set(source.get("locators", []))
        if isinstance(source.get("locator"), str):
            locators.add(source["locator"])
        locators.add(item["locator"])
        source_by_id[item["source_id"]] = {"id": item["source_id"], "kind": "approved-offline-record", "locator": item["locator"], "locators": sorted(locators), "scope": "caller-approved record", "auth_status": "not-tested-offline", "read_status": "synthetic-record-read", "inspected_scope": sorted(record_ids), "record_ids": sorted(record_ids), "checked_at": item["checked_at"], "update_mode": "repeat-safe-by-source-identity"}
    _write_json(sources / "manifest.json", {"company_id": company_id, "sources": sorted(source_by_id.values(), key=lambda x: x["id"])})
    _write_jsonl(sources / "evidence.jsonl", sorted(evidence_by_id.values(), key=lambda x: x["id"]))
    return {"company_id": company_id, "records": len(clean), "source_ids": sorted({item["source_id"] for item in clean}), "destination": str(destination), "status": "written"}


def _demo() -> None:
    record = {"source_id": "notion-demo", "record_id": "page-1", "company_id": "demo-co", "locator": "notion://page-1", "text": "A source-backed claim.", "checked_at": "2026-09-18"}
    with tempfile.TemporaryDirectory(prefix="source-intake-") as temp:
        first = ingest([record], Path(temp), "demo-co", {"notion-demo"})
        second = ingest([record], Path(temp), "demo-co", {"notion-demo"})
        assert first["records"] == second["records"] == 1
        assert len(_jsonl(Path(temp) / "sources" / "evidence.jsonl")) == 1
    print("offline source intake demo: ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        _demo()
    else:
        parser.error("this audit prototype only exposes ingest(); use --demo for the offline check")
