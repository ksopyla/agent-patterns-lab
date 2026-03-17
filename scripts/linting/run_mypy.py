"""Run mypy per-directory to avoid duplicate module names in monorepo.

Each example has its own `src/` package, so mypy must check them separately
to prevent 'Duplicate module named src' errors.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "examples"
LIBS_DIR = ROOT / "libs"

MYPY_BASE_ARGS: list[str] = [
    sys.executable,
    "-m",
    "mypy",
    "--ignore-missing-imports",
    "--exclude",
    "(^|/)tests/",
    "--disable-error-code=misc",
    "--disable-error-code=unused-ignore",
]


def discover_check_dirs() -> list[Path]:
    """Return directories that should be type-checked individually."""
    dirs: list[Path] = []
    if LIBS_DIR.exists():
        dirs.append(LIBS_DIR)
    if EXAMPLES_DIR.exists():
        for example in sorted(EXAMPLES_DIR.iterdir()):
            if example.is_dir() and (example / "src").is_dir():
                dirs.append(example)
    return dirs


def main() -> int:
    dirs = discover_check_dirs()
    if not dirs:
        print("No directories to type-check.")
        return 0

    worst_rc = 0
    for d in dirs:
        rel = d.relative_to(ROOT)
        print(f"mypy {rel}/")
        result = subprocess.run(
            [*MYPY_BASE_ARGS, str(d)],
            cwd=ROOT,
            check=False,
        )
        worst_rc = max(worst_rc, result.returncode)

    return worst_rc


if __name__ == "__main__":
    raise SystemExit(main())
