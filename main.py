#!/usr/bin/env python3
"""make.fun entry: news-image-20261120 — "Sum up 20 November's world news in one image".

The artwork (entry.png) is checked into this repository. It was rendered by
render.py (Pillow, build-time only) from original vector-style drawing code.
This runtime uses only the Python standard library: it copies the committed
image to the output directory, byte for byte, so every run is deterministic.

Sandbox: python3 main.py  -> writes /output/entry.png
Local:   MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

IMAGE_NAME = "entry.png"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    here = Path(__file__).resolve().parent
    src = here / IMAGE_NAME
    if not src.is_file():
        print(f"error: missing artwork {src}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / IMAGE_NAME
    shutil.copyfile(src, dst)

    src_hash, dst_hash = sha256(src), sha256(dst)
    if src_hash != dst_hash:
        print("error: copied image differs from committed artwork", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({dst.stat().st_size} bytes, sha256 {dst_hash})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
