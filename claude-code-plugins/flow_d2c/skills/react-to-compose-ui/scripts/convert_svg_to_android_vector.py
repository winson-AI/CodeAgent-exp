#!/usr/bin/env python3
"""Materialize parsed React resources into Android res/drawable assets."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path


DEFAULT_MANIFEST = "parsed_resources/resources.json"
DEFAULT_OUTPUT_DIR = "kmp/app/src/main/res/drawable"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read the parse_resources.py manifest, convert parsed SVG files into "
            "Android VectorDrawable XML files, and copy parsed bitmap assets into "
            "an Android res/drawable directory."
        )
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help=f"Path to the parse_resources.py manifest. Defaults to {DEFAULT_MANIFEST}.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Android drawable output directory. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=3,
        help="Float precision passed through to the SVG converter backend.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing drawable outputs when names collide.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Parsed resource manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Parsed resource manifest is not valid JSON: {path}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("resources"), list):
        raise SystemExit(f"Parsed resource manifest is missing the resources list: {path}")
    return payload


def resolve_existing_resources(
    manifest_path: Path,
    payload: dict,
) -> tuple[list[Path], list[tuple[Path, str]], list[dict[str, str]]]:
    manifest_root = manifest_path.parent
    svg_files: list[Path] = []
    bitmap_files: list[tuple[Path, str]] = []
    issues: list[dict[str, str]] = []

    for record in payload["resources"]:
        if not isinstance(record, dict):
            issues.append({"kind": "invalid_record", "detail": repr(record)})
            continue

        status = str(record.get("status", ""))
        source_url = str(record.get("url", ""))
        relative_path = record.get("relative_path")
        kind = str(record.get("kind", ""))
        filename = str(record.get("filename", ""))

        if status == "failed":
            issues.append({"kind": "source_failed", "detail": source_url})
            continue
        if not isinstance(relative_path, str) or not relative_path:
            issues.append({"kind": "missing_relative_path", "detail": source_url})
            continue

        file_path = (manifest_root / relative_path).resolve()
        if not file_path.exists():
            issues.append({"kind": "missing_file", "detail": str(file_path)})
            continue

        if kind == "svg":
            svg_files.append(file_path)
        else:
            bitmap_files.append((file_path, filename or file_path.name))

    return svg_files, bitmap_files, issues


def copy_bitmaps(bitmap_files: list[tuple[Path, str]], output_dir: Path, overwrite: bool) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for source_path, filename in bitmap_files:
        destination = output_dir / filename
        if destination.exists() and not overwrite:
            raise SystemExit(f"Refusing to overwrite existing bitmap without --overwrite: {destination}")
        shutil.copy2(source_path, destination)
        copied.append({"input": str(source_path), "output": str(destination)})

    return copied


def sanitize_resource_name(raw_name: str) -> str:
    normalized = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in raw_name.strip()).strip("_").lower()
    if not normalized:
        normalized = "vector_asset"
    if normalized[0].isdigit():
        normalized = f"asset_{normalized}"
    return normalized


def build_output_map(svg_files: list[Path], output_dir: Path, overwrite: bool) -> list[tuple[Path, Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    used_names: dict[str, int] = {}
    mappings: list[tuple[Path, Path]] = []

    for svg_file in svg_files:
        resource_name = sanitize_resource_name(svg_file.stem)
        suffix = used_names.get(resource_name, 0)
        used_names[resource_name] = suffix + 1
        if suffix:
            resource_name = f"{resource_name}_{suffix + 1}"

        output_path = output_dir / f"{resource_name}.xml"
        if output_path.exists() and not overwrite:
            raise SystemExit(f"Refusing to overwrite existing drawable without --overwrite: {output_path}")
        mappings.append((svg_file, output_path))

    return mappings


def detect_converter_command() -> list[str]:
    override = os.environ.get("SVG2VD_COMMAND", "").strip()
    if override:
        return shlex.split(override)

    for candidate in ("s2v", "svg2vectordrawable", "svg2avd", "svg2android", "svg2vector", "svg2drawable"):
        resolved = shutil.which(candidate)
        if resolved:
            return [resolved]

    npx = shutil.which("npx")
    if npx:
        return [npx, "--yes", "svg2vectordrawable"]

    raise SystemExit(
        "No SVG-to-VectorDrawable converter found. Install `svg2vectordrawable` "
        "(for example `npm install -g svg2vectordrawable`) or set SVG2VD_COMMAND."
    )


def run_conversion(base_command: list[str], svg_path: Path, output_path: Path, precision: int) -> dict[str, str]:
    command = [*base_command, "-p", str(precision), "-i", str(svg_path), "-o", str(output_path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(
            f"SVG conversion failed for {svg_path} -> {output_path}\n"
            f"command: {' '.join(shlex.quote(part) for part in command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    if not output_path.exists():
        raise SystemExit(f"Converter reported success but no XML file was written: {output_path}")
    return {"input": str(svg_path), "output": str(output_path)}


def convert_svgs(svg_files: list[Path], output_dir: Path, precision: int, overwrite: bool) -> dict | None:
    if not svg_files:
        return None

    mappings = build_output_map(svg_files, output_dir, overwrite)
    converter_command = detect_converter_command()
    generated = [
        run_conversion(converter_command, svg_path, output_path, precision)
        for svg_path, output_path in mappings
    ]
    return {
        "converter_command": converter_command,
        "generated": generated,
        "output_dir": str(output_dir),
    }


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    payload = load_manifest(manifest_path)
    svg_files, bitmap_files, issues = resolve_existing_resources(manifest_path, payload)
    copied = copy_bitmaps(bitmap_files, output_dir, args.overwrite)
    converted = convert_svgs(svg_files, output_dir, args.precision, args.overwrite)

    summary = {
        "manifest": str(manifest_path),
        "output_dir": str(output_dir),
        "bitmap_copied": copied,
        "svg_converted": converted,
        "issues": issues,
        "copied_count": len(copied),
        "svg_count": len(svg_files),
        "issue_count": len(issues),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
