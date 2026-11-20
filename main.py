#!/usr/bin/env python3
"""Entry point: renders the front page for Friday 20 November 2026 and writes entry.png to the output directory."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontpage

ARTWORK_MAX_BYTES = 1048576


def resolve_output_dir() -> str:
    """Resolve output dir: env MAKEFUN_OUTPUT_DIR, else argv[1], else /output."""
    if "MAKEFUN_OUTPUT_DIR" in os.environ:
        return os.environ["MAKEFUN_OUTPUT_DIR"]
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "/output"


def main() -> int:
    outdir = resolve_output_dir()
    os.makedirs(outdir, exist_ok=True)

    dest = os.path.join(outdir, "entry.png")
    frontpage.save(dest)

    with open(dest, "rb") as fh:
        data = fh.read()

    # Read dimensions from PNG IHDR (bytes 16-24, big-endian width/height)
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    nbytes = len(data)

    print(f"saved {dest} bytes={nbytes} dimensions={width}x{height}")

    if width != 1024 or height != 1024:
        print(
            f"FAIL: expected 1024x1024, got {width}x{height}",
            file=sys.stderr,
        )
        return 1
    if nbytes >= ARTWORK_MAX_BYTES:
        print(
            f"FAIL: {nbytes} bytes exceeds limit {ARTWORK_MAX_BYTES}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())