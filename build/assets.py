"""Копирование статики в dist/."""

import shutil
from pathlib import Path

STATIC_DIRS = ("css", "js", "fonts", "img", "vendor")


def copy_static(dist, src=None):
    src = Path(src or Path(__file__).resolve().parent.parent / "src")
    dist = Path(dist)
    copied = []
    for name in STATIC_DIRS:
        source = src / name
        if not source.is_dir():
            continue
        shutil.copytree(source, dist / name, dirs_exist_ok=True)
        copied.append(name)
    return copied
