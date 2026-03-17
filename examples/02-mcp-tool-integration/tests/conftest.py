"""Pytest configuration for example 02 tests."""

from __future__ import annotations

import sys
from pathlib import Path

EXAMPLE_ROOT = Path(__file__).resolve().parents[1]

for key in list(sys.modules.keys()):
    if key == "src" or key.startswith("src."):
        mod = sys.modules[key]
        mod_file = getattr(mod, "__file__", None) or ""
        if mod_file and str(EXAMPLE_ROOT) not in mod_file:
            del sys.modules[key]

if str(EXAMPLE_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_ROOT))
