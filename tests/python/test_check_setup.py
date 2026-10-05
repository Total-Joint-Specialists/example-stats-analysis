import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "getting-started" / "check_setup.py"


def run(python: str) -> subprocess.CompletedProcess:
    return subprocess.run([python, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True)


def test_passes_inside_the_project_environment():
    result = run(sys.executable)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All good - you are ready." in result.stdout


def test_flags_a_python_outside_the_project_environment():
    base_python = Path(sys.base_prefix) / "bin" / "python3"
    result = run(str(base_python))
    assert result.returncode == 1
    assert "PROBLEM" in result.stdout
