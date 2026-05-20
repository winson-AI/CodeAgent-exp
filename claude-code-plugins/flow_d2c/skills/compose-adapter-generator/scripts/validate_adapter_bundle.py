#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


REQUIRED_REGISTRY_FIELDS = ("id", "path", "displayName")
REQUIRED_MANIFEST_FIELDS = ("id", "displayName", "framework", "selectionHints")
REQUIRED_BUNDLE_FILES = (
    "manifest.json",
    "aliases.json",
    "component_knowledge.json",
    "prompt.md",
)
OPTIONAL_BUNDLE_FILES = ("component_knowledge.jsonl",)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON ({exc})")


def load_jsonl(path: Path) -> None:
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{path}:{lineno}: invalid JSONL entry ({exc})")


def validate_manifest(manifest: Dict[str, Any], bundle_dir: Path, expected_id: Optional[str]) -> None:
    if not isinstance(manifest, dict):
        fail(f"{bundle_dir / 'manifest.json'}: manifest must be a JSON object")
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            fail(f"{bundle_dir / 'manifest.json'}: missing required field '{field}'")
    if manifest["framework"] != "android-compose":
        fail(
            f"{bundle_dir / 'manifest.json'}: framework must be 'android-compose', got {manifest['framework']!r}"
        )
    dir_id = bundle_dir.name
    if manifest["id"] != dir_id:
        fail(
            f"{bundle_dir / 'manifest.json'}: manifest id {manifest['id']!r} does not match directory {dir_id!r}"
        )
    if expected_id is not None and manifest["id"] != expected_id:
        fail(
            f"{bundle_dir / 'manifest.json'}: manifest id {manifest['id']!r} does not match expected adapter id {expected_id!r}"
        )
    if not isinstance(manifest["selectionHints"], dict):
        fail(f"{bundle_dir / 'manifest.json'}: selectionHints must be a JSON object")


def validate_bundle_dir(bundle_dir: Path, expected_id: Optional[str] = None) -> None:
    if not bundle_dir.exists():
        fail(f"{bundle_dir}: bundle directory does not exist")
    if not bundle_dir.is_dir():
        fail(f"{bundle_dir}: bundle path must be a directory")

    for filename in REQUIRED_BUNDLE_FILES:
        path = bundle_dir / filename
        if not path.exists():
            fail(f"{bundle_dir}: missing required file {filename}")

    manifest = load_json(bundle_dir / "manifest.json")
    validate_manifest(manifest, bundle_dir, expected_id)

    aliases = load_json(bundle_dir / "aliases.json")
    if not isinstance(aliases, dict):
        fail(f"{bundle_dir / 'aliases.json'}: aliases must be a JSON object")

    knowledge = load_json(bundle_dir / "component_knowledge.json")
    if not isinstance(knowledge, dict):
        fail(f"{bundle_dir / 'component_knowledge.json'}: component knowledge must be a JSON object keyed by component name")

    prompt_path = bundle_dir / "prompt.md"
    if not prompt_path.read_text().strip():
        fail(f"{prompt_path}: prompt file must not be empty")

    jsonl_path = bundle_dir / "component_knowledge.jsonl"
    if jsonl_path.exists():
        load_jsonl(jsonl_path)


def resolve_registry_entries(registry_path: Path) -> List[Dict[str, Any]]:
    if not registry_path.exists():
        fail(f"{registry_path}: registry file does not exist")
    registry = load_json(registry_path)
    if not isinstance(registry, dict):
        fail(f"{registry_path}: registry must be a JSON object")
    adapters = registry.get("adapters")
    if not isinstance(adapters, list):
        fail(f"{registry_path}: adapters must be a JSON array")
    for idx, entry in enumerate(adapters):
        if not isinstance(entry, dict):
            fail(f"{registry_path}: adapters[{idx}] must be a JSON object")
        for field in REQUIRED_REGISTRY_FIELDS:
            if field not in entry:
                fail(f"{registry_path}: adapters[{idx}] missing required field '{field}'")
    return adapters


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate react-to-compose-ui adapter bundles.")
    parser.add_argument("--adapter-id", help="Validate a single adapter from the built-in registry.")
    parser.add_argument(
        "--adapter-dir",
        help="Validate a specific bundle directory directly. Useful for templates or work-in-progress bundles.",
    )
    parser.add_argument(
        "--registry",
        default=None,
        help="Override registry path. Defaults to the built-in registry inside this skill.",
    )
    args = parser.parse_args()

    generator_skill_root = Path(__file__).resolve().parent.parent
    runtime_skill_root = generator_skill_root.parent / "react-to-compose-ui"
    registry_path = (
        Path(args.registry).resolve()
        if args.registry
        else runtime_skill_root / "adapters" / "registry.json"
    )

    if args.adapter_dir:
        validate_bundle_dir(Path(args.adapter_dir).resolve(), expected_id=None)
        print(f"OK: validated bundle directory {Path(args.adapter_dir).resolve()}")
        return

    entries = resolve_registry_entries(registry_path)
    if args.adapter_id:
        matches = [entry for entry in entries if entry["id"] == args.adapter_id]
        if not matches:
            fail(f"{registry_path}: adapter id {args.adapter_id!r} not found")
        entry = matches[0]
        bundle_dir = (runtime_skill_root / entry["path"]).resolve()
        validate_bundle_dir(bundle_dir, expected_id=entry["id"])
        print(f"OK: validated adapter {entry['id']} at {bundle_dir}")
        return

    validated = 0
    for entry in entries:
        bundle_dir = (runtime_skill_root / entry["path"]).resolve()
        validate_bundle_dir(bundle_dir, expected_id=entry["id"])
        print(f"OK: validated adapter {entry['id']} at {bundle_dir}")
        validated += 1

    print(f"Validated {validated} adapter bundle(s).")


if __name__ == "__main__":
    main()
