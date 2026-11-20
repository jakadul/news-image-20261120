"""Install the committed front page for Friday 20 November 2026 into the output directory.

The artwork is committed as entry.png rather than drawn at run time because a
make.fun entry may be an image plus a copy step; this program only verifies it
and copies it where the platform expects it.
"""

import os
import shutil
import struct
import sys

# The cap comes from the competition rules.
ARTWORK_MAX_BYTES = 1048576

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def resolve_output_dir(argv):
    """MAKEFUN_OUTPUT_DIR wins, then argv[1], then /output."""
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return env
    if len(argv) > 1:
        return argv[1]
    return "/output"


def read_png_dimensions(path):
    """Return (width, height) from the IHDR chunk, or raise ValueError."""
    with open(path, "rb") as fh:
        header = fh.read(8)
        if header != PNG_MAGIC:
            raise ValueError("not a PNG file (bad magic)")
        length_bytes = fh.read(4)
        chunk_type = fh.read(4)
        if chunk_type != b"IHDR":
            raise ValueError("missing IHDR chunk")
        length = struct.unpack(">I", length_bytes)[0]
        if length < 8:
            raise ValueError("IHDR too short")
        data = fh.read(8)
        if len(data) < 8:
            raise ValueError("truncated IHDR")
        width, height = struct.unpack(">II", data)
        return width, height


def main(argv):
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    if not os.path.isfile(source):
        print("error: entry.png not found beside main.py at %s" % source, file=sys.stderr)
        return 1

    size = os.path.getsize(source)
    if size > ARTWORK_MAX_BYTES:
        print(
            "error: artwork is %d bytes, over the %d byte cap" % (size, ARTWORK_MAX_BYTES),
            file=sys.stderr,
        )
        return 1

    try:
        width, height = read_png_dimensions(source)
    except (OSError, ValueError) as exc:
        print("error: cannot read IHDR from %s: %s" % (source, exc), file=sys.stderr)
        return 1

    if width != 1024 or height != 1024:
        print(
            "error: artwork is %dx%d, expected 1024x1024" % (width, height),
            file=sys.stderr,
        )
        return 1

    out_dir = resolve_output_dir(argv)
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print("error: cannot create output directory %s: %s" % (out_dir, exc), file=sys.stderr)
        return 1

    destination = os.path.join(out_dir, "entry.png")
    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        print("error: copy failed to %s: %s" % (destination, exc), file=sys.stderr)
        return 1

    print("path: %s" % destination)
    print("bytes: %d" % size)
    print("dimensions: %dx%d" % (width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))