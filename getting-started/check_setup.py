"""Checks that Python is ready for the tutorials.

Run from the repository folder:  uv run python getting-started/check_setup.py
"""

import importlib.util
import sys

ok = True


def report(label: str, passed: bool, fix: str) -> None:
    global ok
    print(f"{label:<40} {'OK' if passed else 'PROBLEM - ' + fix}")
    ok = ok and passed


version = ".".join(map(str, sys.version_info[:3]))
report(f"Python version {version}", sys.version_info >= (3, 12),
       "run `uv python install 3.13`, then `uv sync`")
report("using the project's .venv", ".venv" in sys.prefix,
       "run this with `uv run python ...` from the repository folder")
for name in ["pandas", "numpy", "matplotlib"]:
    report(f"Python package {name}", importlib.util.find_spec(name) is not None, "run `uv sync`")

print("\nAll good - you are ready." if ok else "\nFix the problems above, then run this again.")
sys.exit(0 if ok else 1)
