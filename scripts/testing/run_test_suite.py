"""Run unit, API, and end-to-end tests across all examples."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "examples"
LIBS_DIR = ROOT / "libs"


def _resolve_uv_binary() -> str:
    """Resolve uv binary in a cross-platform friendly way."""
    uv_from_env = os.environ.get("UV_BIN")
    if uv_from_env:
        return uv_from_env

    uv_on_path = shutil.which("uv")
    if uv_on_path:
        return uv_on_path

    default_windows_uv = Path.home() / ".local" / "bin" / "uv.exe"
    if default_windows_uv.exists():
        return str(default_windows_uv)

    msg = (
        "Could not find uv executable. Set UV_BIN or add uv to PATH. "
        "See https://docs.astral.sh/uv/getting-started/installation/."
    )
    raise FileNotFoundError(msg)


def discover_example_test_paths() -> list[Path]:
    """Return test directories for all examples that contain tests."""
    if not EXAMPLES_DIR.exists():
        return []

    paths: list[Path] = []
    for example_dir in sorted(EXAMPLES_DIR.iterdir()):
        tests_dir = example_dir / "tests"
        if example_dir.is_dir() and tests_dir.is_dir():
            paths.append(tests_dir)
    return paths


def build_pytest_command(test_path: Path, *, include_coverage: bool) -> list[str]:
    """Build pytest command for a single test directory."""
    uv_bin = _resolve_uv_binary()
    command = [uv_bin, "run", "pytest", "--tb=short", "-q"]

    if not include_coverage:
        command.append("--no-cov")

    command.append(str(test_path.relative_to(ROOT)))
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run complete repository tests.")
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    test_paths = discover_example_test_paths()
    libs_tests = LIBS_DIR / "common" / "tests"
    if libs_tests.is_dir():
        test_paths.append(libs_tests)

    if not test_paths:
        msg = "No tests found in examples/*/tests or libs/common/tests."
        raise RuntimeError(msg)

    worst_rc = 0
    for test_path in test_paths:
        rel = test_path.relative_to(ROOT)
        command = build_pytest_command(test_path, include_coverage=not args.no_coverage)
        print(f"\npytest {rel}/")
        result = subprocess.run(command, cwd=ROOT, check=False)
        rc = result.returncode
        if rc == 5:
            print(f"  (no tests collected in {rel}, skipping)")
            continue
        worst_rc = max(worst_rc, rc)

    return worst_rc


if __name__ == "__main__":
    raise SystemExit(main())
