#!/usr/bin/env python3
"""Render a reviewed, source-linked candidate brief into a private workspace."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


MAX_PLAN_BYTES = 1_000_000
MAX_EVIDENCE_BYTES = 12_000_000
MAX_TEXT_BYTES = 500_000
MAX_CLAIMS = 500
MAX_UNKNOWNS = 100
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
CATEGORIES = ("company", "tone", "policies", "products", "workflows")
ROUTES = {category: f"context/{category}.md" for category in CATEGORIES}
TRUSTED_SYMLINKS = {Path("/tmp"), Path("/var")}


class CompileError(ValueError):
    """The plan or private workspace is unsafe or inconsistent."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _checked_path(value: str | Path) -> Path:
    path = Path(os.path.abspath(os.path.expanduser(str(value))))
    if any(char in str(path) for char in ("\x00", "\n", "\r", "`")):
        raise CompileError("path contains unsupported control characters")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        if current.is_symlink() and current not in TRUSTED_SYMLINKS:
            raise CompileError(f"symlink path requires manual review: {current}")
    return path


def _repo_path(path: Path) -> bool:
    current = path if path.is_dir() else path.parent
    while True:
        if (current / ".git").exists():
            return True
        if current == current.parent:
            return False
        current = current.parent


def _validate_destination(value: str | Path) -> Path:
    destination = _checked_path(value)
    if destination in {Path.home(), Path("/"), Path("/tmp"), Path("/var")}:
        raise CompileError("choose a dedicated private workspace directory")
    plugin_cache = Path.home() / ".codex" / "plugins" / "cache"
    if destination == plugin_cache or plugin_cache in destination.parents:
        raise CompileError("private workspace must be outside the plugin cache")
    if _repo_path(destination):
        raise CompileError("private workspace must be outside a git repository")
    if destination.exists() and not destination.is_dir():
        raise CompileError("destination must be a directory")
    return destination


def _safe_child(destination: Path, relative: str) -> Path:
    child = _checked_path(destination / relative)
    if child != destination and destination not in child.parents:
        raise CompileError(f"output escapes destination: {relative}")
    if child.exists() and child.is_symlink():
        raise CompileError(f"output is a symlink: {child}")
    if child.exists() and not child.is_file():
        raise CompileError(f"output is not a regular file: {child}")
    return child


def _read_json(path: Path, *, limit: int = MAX_PLAN_BYTES) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise CompileError(f"expected a regular JSON file: {path}")
    if path.stat().st_size > limit:
        raise CompileError(f"JSON file exceeds the size limit: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CompileError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CompileError(f"expected a JSON object: {path}")
    return value


def _read_evidence(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file() or path.is_symlink():
        raise CompileError(f"expected evidence JSONL: {path}")
    if path.stat().st_size > MAX_EVIDENCE_BYTES:
        raise CompileError("evidence file exceeds the size limit")
    rows: dict[str, dict[str, str]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise CompileError(f"evidence is unreadable: {path}") from exc
    required = ("id", "source_id", "locator", "claim", "status", "checked_at")
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CompileError(f"invalid evidence row {number}") from exc
        if not isinstance(row, dict) or any(not isinstance(row.get(field), str) or not row[field].strip() for field in required):
            raise CompileError(f"evidence row {number} has invalid fields")
        if row["id"] in rows:
            raise CompileError(f"duplicate evidence id: {row['id']}")
        rows[row["id"]] = {field: row[field] for field in required}
    return rows


def _validate_plan(plan: dict[str, Any], evidence: dict[str, dict[str, str]], company_id: str, source_ids: set[str]) -> dict[str, Any]:
    if set(plan) != {"company_id", "overview", "claims", "unknowns"}:
        raise CompileError("plan must contain exactly company_id, overview, claims and unknowns")
    if plan["company_id"] != company_id or not isinstance(company_id, str) or not SLUG.fullmatch(company_id):
        raise CompileError("plan and manifest company_id must be the same lowercase slug")
    if not isinstance(plan["overview"], str) or not plan["overview"].strip():
        raise CompileError("overview must be non-empty text")
    if len(plan["overview"].encode("utf-8")) > MAX_TEXT_BYTES:
        raise CompileError("overview exceeds the size limit")
    try:
        plan_size = len(_json_bytes(plan))
    except (TypeError, ValueError) as exc:
        raise CompileError("plan must be JSON-serializable") from exc
    if plan_size > MAX_PLAN_BYTES:
        raise CompileError("plan exceeds the size limit")
    claims = plan["claims"]
    if not isinstance(claims, list) or len(claims) > MAX_CLAIMS:
        raise CompileError(f"claims must be a list of at most {MAX_CLAIMS} items")
    clean_claims = []
    seen: set[tuple[str, str, str, str]] = set()
    for index, item in enumerate(claims):
        if not isinstance(item, dict) or set(item) != {"evidence_id", "category", "quote", "summary"}:
            raise CompileError(f"claim {index} has an invalid shape")
        if any(not isinstance(item[key], str) or not item[key].strip() for key in item):
            raise CompileError(f"claim {index} has an empty field")
        if item["category"] not in CATEGORIES:
            raise CompileError(f"claim {index} has an unsupported category")
        evidence_item = evidence.get(item["evidence_id"])
        if evidence_item is None:
            raise CompileError(f"claim {index} references unknown evidence: {item['evidence_id']}")
        claim_key = (item["evidence_id"], item["category"], item["quote"], item["summary"])
        if claim_key in seen:
            raise CompileError(f"duplicate claim tuple: {item['evidence_id']}")
        if item["quote"] not in evidence_item["claim"]:
            raise CompileError(f"claim {index} quote is not an exact evidence substring")
        if evidence_item["source_id"] not in source_ids:
            raise CompileError(f"evidence source is absent from the manifest: {evidence_item['source_id']}")
        seen.add(claim_key)
        clean_claims.append(dict(item))
    unknowns = plan["unknowns"]
    if not isinstance(unknowns, list) or len(unknowns) > MAX_UNKNOWNS or any(not isinstance(item, str) or not item.strip() for item in unknowns):
        raise CompileError(f"unknowns must contain at most {MAX_UNKNOWNS} non-empty strings")
    return {"company_id": company_id, "overview": plan["overview"].strip(), "claims": clean_claims, "unknowns": list(unknowns)}


def _source_ids(manifest: dict[str, Any]) -> tuple[str, set[str], dict[str, dict[str, Any]]]:
    records = manifest.get("records", manifest.get("sources", []))
    if not isinstance(records, list):
        raise CompileError("manifest records/sources must be a list")
    if not records:
        raise CompileError("manifest must contain at least one source")
    ids: set[str] = set()
    metadata: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise CompileError(f"manifest record {index} is invalid")
        source_id = item.get("id", item.get("source_id"))
        if not isinstance(source_id, str) or not source_id.strip():
            raise CompileError(f"manifest record {index} has no source id")
        if source_id in ids:
            raise CompileError(f"duplicate manifest source id: {source_id}")
        ids.add(source_id)
        metadata[source_id] = item
    company_id = manifest.get("company_id")
    if not isinstance(company_id, str) or not SLUG.fullmatch(company_id):
        raise CompileError("manifest company_id is invalid")
    return company_id, ids, metadata


def _quote(text: str) -> str:
    return "\n".join(f"> {line}" for line in text.splitlines())


def _render_claim(item: dict[str, str], evidence: dict[str, str], source: dict[str, Any]) -> str:
    status = evidence["status"]
    kind = str(source.get("kind", ""))
    read_status = str(source.get("read_status", ""))
    snapshot = ""
    if read_status.lower() == "partial" or "snapshot" in str(source.get("update_mode", "")).lower() or any(word in kind.lower() for word in ("transaction", "order")):
        snapshot = "\n- Boundary: snapshot only; do not treat this partial/current transaction as durable policy."
    return f"""### {item['summary']}\n- Evidence ID: `{item['evidence_id']}`\n- Locator: `{evidence['locator']}`\n- Evidence status: `{status}`\n- Unreviewed candidate summary: {item['summary']}\n- Source quote:\n{_quote(item['quote'])}{snapshot}\n"""


def _render_page(category: str, plan: dict[str, Any], evidence: dict[str, dict[str, str]], sources: dict[str, dict[str, Any]]) -> str:
    title = category.title()
    claims = [claim for claim in plan["claims"] if claim["category"] == category]
    body = "\n".join(_render_claim(claim, evidence[claim["evidence_id"]], sources.get(evidence[claim["evidence_id"]]["source_id"], {})) for claim in claims)
    if not body:
        body = "No source-grounded candidate is available for this page yet.\n"
    note = "\n> All summaries below are model-produced, unreviewed candidates. Owner review is required before durable policy or memory use.\n"
    if category == "policies":
        note += "> Policy candidates remain snapshots until the owner confirms scope and effective date.\n"
        note += "> Apply only the stated scope. Do not infer broader bans, fees, guarantees or exceptions. Separately quoted work does not establish that free service is never available; missing terms remain unknown.\n"
    return f"# {title}\n\n<!-- company-onboarding:generated category={category} -->\n{note}\n{body}"


def _render_index(plan: dict[str, Any]) -> str:
    unknowns = "\n".join(f"- {item}" for item in plan["unknowns"]) or "- None recorded."
    active = {claim["category"] for claim in plan["claims"]}
    routes = "\n".join(
        f"- `{ROUTES[category]}` — {category}"
        for category in CATEGORIES
        if category not in {"products", "workflows"} or category in active
    )
    return f"""# {plan['company_id']}\n\n<!-- company-onboarding:generated index -->\n## Overview\n{plan['overview']}\n\n## Review status\nCandidate brief generated from source evidence. Owner review is required before durable business knowledge is accepted.\n\n## Reading map\n{routes}\n- `outputs/business-brief.md` — compact review copy\n\n## Unknowns\n{unknowns}\n"""


def _render_brief(plan: dict[str, Any], evidence: dict[str, dict[str, str]], sources: dict[str, dict[str, Any]]) -> str:
    sections = []
    for category in CATEGORIES:
        claims = [claim for claim in plan["claims"] if claim["category"] == category]
        if claims:
            sections.append(f"## {category.title()}\n\n" + "\n".join(_render_claim(claim, evidence[claim["evidence_id"]], sources.get(evidence[claim["evidence_id"]]["source_id"], {})) for claim in claims))
    section_text = "\n".join(sections) or "No claims were selected."
    unknown_text = "\n".join(f"- {item}" for item in plan["unknowns"]) or "- None recorded."
    return f"""# Business brief — {plan['company_id']}\n\n<!-- company-onboarding:generated brief -->\n## Overview\n{plan['overview']}\n\n> This is a reviewable candidate brief. Summaries are unreviewed model candidates and retain source provenance.\n\n{section_text}\n\n## Unknowns\n{unknown_text}\n"""


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.tmp-", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def compile_context(destination: Path, plan: dict[str, Any]) -> dict[str, Any]:
    """Validate and materialize one exact plan into a private workspace."""
    destination = _validate_destination(destination)
    if not isinstance(plan, dict):
        raise CompileError("plan must be a JSON object")
    try:
        plan_size = len(_json_bytes(plan))
    except (TypeError, ValueError) as exc:
        raise CompileError("plan must be JSON-serializable") from exc
    if plan_size > MAX_PLAN_BYTES:
        raise CompileError("plan exceeds the size limit")
    # Read all inputs and compute every output before creating a directory or file.
    manifest_path = _safe_child(destination, "sources/manifest.json")
    evidence_path = _safe_child(destination, "sources/evidence.jsonl")
    manifest = _read_json(manifest_path)
    company_id, source_ids, sources = _source_ids(manifest)
    evidence = _read_evidence(evidence_path)
    clean = _validate_plan(plan, evidence, company_id, source_ids)
    plan_hash = _digest(_json_bytes(clean))
    rendered: dict[str, bytes] = {"INDEX.md": _render_index(clean).encode("utf-8")}
    for category, relative in ROUTES.items():
        if category in {"products", "workflows"} and not any(claim["category"] == category for claim in clean["claims"]):
            continue
        rendered[relative] = _render_page(category, clean, evidence, sources).encode("utf-8")
    rendered["outputs/business-brief.md"] = _render_brief(clean, evidence, sources).encode("utf-8")
    state_path = _safe_child(destination, "state/onboarding.json")
    state = _read_json(state_path, limit=MAX_PLAN_BYTES) if state_path.exists() else {}
    if state.get("company_id") not in (None, company_id):
        raise CompileError("existing onboarding state belongs to another company")
    generation = state.get("_compile_context", {})
    if generation and not isinstance(generation, dict):
        raise CompileError("existing compile state is invalid")
    old_hashes = generation.get("generated_files", {}) if generation else {}
    if old_hashes and (not isinstance(old_hashes, dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in old_hashes.items())):
        raise CompileError("existing generated file hashes are invalid")
    paths = {relative: _safe_child(destination, relative) for relative in rendered}
    conflicts = []
    for relative, data in rendered.items():
        path = paths[relative]
        if not path.exists():
            continue
        current_hash = _digest(path.read_bytes())
        expected_hash = _digest(data)
        if current_hash == expected_hash:
            continue
        if old_hashes.get(relative) == current_hash:
            continue
        conflicts.append(relative)
    if conflicts:
        raise CompileError("external edits detected; refusing to overwrite: " + ", ".join(sorted(conflicts)))
    next_hashes = {relative: _digest(data) for relative, data in rendered.items()}
    next_state = dict(state)
    next_state.setdefault("company_id", company_id)
    next_state.setdefault("phase", "candidate-brief")
    next_state.setdefault("review_status", "needs-owner-review")
    next_state.setdefault("private_destination", str(destination))
    next_state.setdefault("approved_scopes", [])
    next_state.setdefault("blockers", list(clean["unknowns"]))
    same_generation = generation.get("plan_sha256") == plan_hash and generation.get("generated_files") == next_hashes
    if same_generation:
        next_state["_compile_context"] = generation
    else:
        next_state["_compile_context"] = {"schema_version": 1, "company_id": company_id, "plan_sha256": plan_hash, "generated_files": next_hashes, "last_updated": _now()}
    if next_state.get("schema_version") not in (None, 1):
        raise CompileError("unsupported onboarding state schema_version")
    next_state["schema_version"] = 1
    if not same_generation:
        next_state["review_status"] = "needs-owner-review"
        next_state["last_updated"] = _now()
    else:
        next_state.setdefault("last_updated", next_state["_compile_context"].get("last_updated", _now()))
    state_data = (json.dumps(next_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(state_data) > MAX_PLAN_BYTES:
        raise CompileError("onboarding state exceeds the size limit")
    same_state = state_path.exists() and state_path.read_bytes() == state_data
    unchanged = all(paths[relative].exists() and paths[relative].read_bytes() == data for relative, data in rendered.items()) and same_state
    if unchanged:
        return {"status": "unchanged", "company_id": company_id, "plan_sha256": plan_hash, "files": sorted(rendered)}
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    for relative, data in rendered.items():
        _atomic_write(paths[relative], data)
    _atomic_write(state_path, state_data)
    return {"status": "written", "company_id": company_id, "plan_sha256": plan_hash, "files": sorted(rendered)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()
    try:
        plan = _read_json(_checked_path(args.plan))
        print(json.dumps(compile_context(Path(args.destination), plan), ensure_ascii=False, indent=2))
        return 0
    except (CompileError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"STOP: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
