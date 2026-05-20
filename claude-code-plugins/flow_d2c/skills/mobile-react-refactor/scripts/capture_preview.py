#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional


def _load_skill_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config.json"
    return json.loads(config_path.read_text(encoding="utf-8"))


def _pixel_validation_config() -> dict:
    payload = _load_skill_config().get("pixelValidation")
    return payload if isinstance(payload, dict) else {}


def _read_png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Reference file is not a valid PNG: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def _decode(data: Optional[bytes]) -> str:
    if not data:
        return ""
    return data.decode("utf-8", errors="replace")


def _start_preview_server(dist_dir: Path) -> tuple[ThreadingHTTPServer, threading.Thread]:
    class QuietStaticHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            return

    handler = partial(QuietStaticHandler, directory=str(dist_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main() -> int:
    defaults = _pixel_validation_config()
    parser = argparse.ArgumentParser(
        description=(
            "Capture a screenshot from the built React preview using skill defaults. "
            "Minimal usage: --react-root react. "
            "The script reads the reference image size, starts a temporary local server from react/dist, "
            "and writes ./current-preview.png by default."
        )
    )
    parser.add_argument(
        "--react-root",
        default="react",
        help="React project root containing dist/. Defaults to ./react.",
    )
    parser.add_argument(
        "--reference",
        default=defaults.get("referenceScreenshot", "Preview.png"),
        help="Reference PNG used to match the capture viewport size. Defaults to ./Preview.png.",
    )
    parser.add_argument(
        "--output",
        default=defaults.get("screenshotPath", "current-preview.png"),
        help="Path to write the captured screenshot. Defaults to ./current-preview.png.",
    )
    parser.add_argument(
        "--browser",
        default=defaults.get("browser", "chromium"),
        help="Playwright browser name to use for the capture. Defaults to chromium.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=int(defaults.get("waitMs", 10000)),
        help="Milliseconds to wait before capture so remote assets can load.",
    )
    args = parser.parse_args()

    react_root = Path(args.react_root).expanduser().resolve()
    reference = Path(args.reference).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    dist_dir = react_root / "dist"
    if not dist_dir.exists():
        raise RuntimeError(f"React build did not produce dist/: {dist_dir}")
    if not reference.exists():
        raise RuntimeError(f"Reference screenshot does not exist: {reference}")

    width, height = _read_png_size(reference)
    server, thread = _start_preview_server(dist_dir)
    port = int(server.server_address[1])
    try:
        completed = subprocess.run(
            [
                "npx",
                "playwright",
                "screenshot",
                f"--browser={args.browser}",
                f"--viewport-size={width},{height}",
                f"--wait-for-timeout={args.wait_ms}",
                f"http://127.0.0.1:{port}",
                str(output),
            ],
            cwd=str(react_root),
            capture_output=True,
            text=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    stdout = _decode(completed.stdout)
    stderr = _decode(completed.stderr)
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)
    sys.stdout.write(
        "\n".join(
            [
                f"reference_size={width}x{height}",
                f"browser={args.browser}",
                f"wait_ms={args.wait_ms}",
                f"port={port}",
                f"output={output}",
            ]
        )
        + "\n"
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
