#!/usr/bin/env python3
"""Compare two screenshots and emit a pixel mismatch summary plus diff image."""

from __future__ import annotations

import argparse
from pathlib import Path


try:
    from PIL import Image, ImageChops
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install it with: python3 -m pip install Pillow"
    ) from exc


def resize_to_match(reference: Image.Image, candidate: Image.Image) -> tuple[Image.Image, Image.Image]:
    if reference.size == candidate.size:
        return reference, candidate
    return reference, candidate.resize(reference.size)


def build_diff(reference: Image.Image, candidate: Image.Image, threshold: int) -> tuple[Image.Image, int]:
    diff = ImageChops.difference(reference.convert("RGBA"), candidate.convert("RGBA"))
    out = Image.new("RGBA", reference.size, (0, 0, 0, 0))
    mismatch_count = 0
    width, height = reference.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = diff.getpixel((x, y))
            if max(r, g, b, a) > threshold:
                mismatch_count += 1
                out.putpixel((x, y), (255, 0, 0, 180))
            else:
                out.putpixel((x, y), (0, 0, 0, 0))

    return out, mismatch_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two screenshots and emit a pixel mismatch summary plus diff image. "
            "Minimal usage: pixel_diff.py Preview.png current-preview.png."
        )
    )
    parser.add_argument("reference", type=Path, help="Reference screenshot, usually Preview.png")
    parser.add_argument("candidate", type=Path, help="Current captured screenshot")
    parser.add_argument(
        "--diff-out",
        type=Path,
        default=Path("pixel-diff.png"),
        help="Path to write the highlighted diff image",
    )
    parser.add_argument(
        "--channel-threshold",
        type=int,
        default=16,
        help="Per-channel difference threshold before a pixel is counted as mismatched",
    )
    args = parser.parse_args()

    reference = Image.open(args.reference)
    candidate = Image.open(args.candidate)
    reference, candidate = resize_to_match(reference, candidate)
    diff, mismatches = build_diff(reference, candidate, args.channel_threshold)

    total_pixels = reference.size[0] * reference.size[1]
    mismatch_ratio = mismatches / total_pixels if total_pixels else 0
    args.diff_out.parent.mkdir(parents=True, exist_ok=True)
    diff.save(args.diff_out)

    print(f"reference_size={reference.size[0]}x{reference.size[1]}")
    print(f"candidate_size={candidate.size[0]}x{candidate.size[1]}")
    print(f"mismatch_pixels={mismatches}")
    print(f"total_pixels={total_pixels}")
    print(f"mismatch_ratio={mismatch_ratio:.6f}")
    print(f"diff_image={args.diff_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
