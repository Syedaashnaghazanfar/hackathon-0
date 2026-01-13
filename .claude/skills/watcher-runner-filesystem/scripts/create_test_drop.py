#!/usr/bin/env python3

"""Create a small test file in a watched drop folder.

Usage:
  python create_test_drop.py /absolute/path/to/WATCH_FOLDER

This is used only to verify the filesystem watcher triggers.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python create_test_drop.py /path/to/WATCH_FOLDER")
        return 2

    watch_folder = Path(sys.argv[1]).expanduser().resolve()
    watch_folder.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    p = watch_folder / f"watcher-smoke-test-{ts}.txt"
    p.write_text("watcher smoke test\n", encoding="utf-8")
    print(str(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
