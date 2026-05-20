#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import subprocess
import shutil
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_SOURCE = "react/src/ValidatedComponent.jsx"
DEFAULT_OUTPUT_ROOT = "parsed_resources"
DEFAULT_MANIFEST = "parsed_resources/resources.json"
URL_RE = re.compile(
    r"""https://cdn-tos-cn\.bytedance\.net/obj/ies-semi/images/[^\s"'`)]+?\.(?:svg|png|jpg|jpeg|webp)(?:\?[^\s"'`)]+)?""",
    re.IGNORECASE,
)


@dataclass
class ResourceRecord:
    url: str
    kind: str
    extension: str
    filename: str
    relative_path: str
    status: str
    error: str | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Parse CDN resource URLs from a React JSX file, download them into a local "
            "resource workspace, and write a manifest for later React or Compose stages."
        )
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE, help=f"JSX source file. Defaults to {DEFAULT_SOURCE}.")
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Directory for downloaded resources. Defaults to {DEFAULT_OUTPUT_ROOT}.",
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help=f"Manifest JSON path. Defaults to {DEFAULT_MANIFEST}.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=60,
        help="Download timeout in seconds. Defaults to 60.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Do not redownload files that already exist on disk.",
    )
    return parser


def ordered_unique_urls(text: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for match in URL_RE.finditer(text):
        url = match.group(0)
        if url in seen:
            continue
        seen.add(url)
        ordered.append(url)
    return ordered


def sanitize_stem(raw_stem: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_]+", "_", raw_stem).strip("_").lower()
    return sanitized or "resource"


def build_filename(url: str, ext: str) -> str:
    parsed = urllib.parse.urlparse(url)
    stem = sanitize_stem(Path(parsed.path).stem)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    return f"img_{stem}_{digest}{ext}"


def classify_kind(ext: str) -> str:
    return "svg" if ext.lower() == ".svg" else "bitmap"


def destination_for(url: str, output_root: Path) -> tuple[str, str, Path]:
    parsed = urllib.parse.urlparse(url)
    ext = Path(parsed.path).suffix.lower()
    kind = classify_kind(ext)
    folder = "svgs" if kind == "svg" else "bitmaps"
    filename = build_filename(url, ext)
    return kind, filename, output_root / folder / filename


def download(url: str, destination: Path, timeout_seconds: int, skip_existing: bool) -> tuple[str, str | None]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if skip_existing and destination.exists():
        return "skipped_existing", None

    request = urllib.request.Request(url, headers={"User-Agent": "mobile-react-refactor/parse_resources"})
    temp_path = destination.with_suffix(destination.suffix + ".tmp")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            temp_path.write_bytes(response.read())
        temp_path.replace(destination)
        
        # Add SVGO post-processing for SVG files
        if destination.suffix.lower() == ".svg":
            npx_path = shutil.which("npx")
            if npx_path:
                try:
                    # Run svgo to clean up the SVG, preserving fill colors and inline styles
                    subprocess.run(
                        [npx_path, "svgo", str(destination), "-o", str(destination)],
                        capture_output=True,
                        check=True,
                        timeout=30
                    )
                except (subprocess.SubprocessError, OSError) as svgo_exc:
                    # Non-fatal if SVGO fails, we still have the original SVG
                    pass
        
        return "downloaded", None
    except (urllib.error.URLError, OSError) as exc:
        temp_path.unlink(missing_ok=True)
        return "failed", str(exc)


def main() -> int:
    args = build_parser().parse_args()
    source_path = Path(args.source).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()

    if not source_path.exists():
        print(f"Source file does not exist: {source_path}", file=sys.stderr)
        return 1

    urls = ordered_unique_urls(source_path.read_text(encoding="utf-8"))
    records: list[ResourceRecord] = []

    for url in urls:
        kind, filename, destination = destination_for(url, output_root)
        status, error = download(url, destination, args.timeout_seconds, args.skip_existing)
        records.append(
            ResourceRecord(
                url=url,
                kind=kind,
                extension=destination.suffix.lower(),
                filename=filename,
                relative_path=os.path.relpath(destination, manifest_path.parent),
                status=status,
                error=error,
            )
        )

    manifest = {
        "source": str(source_path),
        "output_root": str(output_root),
        "resource_count": len(records),
        "downloaded_count": sum(1 for record in records if record.status == "downloaded"),
        "skipped_existing_count": sum(1 for record in records if record.status == "skipped_existing"),
        "failed_count": sum(1 for record in records if record.status == "failed"),
        "resources": [asdict(record) for record in records],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
