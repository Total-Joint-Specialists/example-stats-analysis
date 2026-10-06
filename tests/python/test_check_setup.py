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


def test_r_check_covers_the_packages_the_pages_call():
    script = (ROOT / "getting-started" / "check_setup.R").read_text(encoding="utf-8")
    for pkg in ["tidyverse", "readxl", "tidyxl", "janitor", "gtsummary", "flextable", "smd",
                "effectsize", "DescTools", "survival", "ggsurvfit", "rstatix", "tidycmprsk",
                "broom.helpers", "lme4", "lmerTest", "emmeans", "PMCMRplus"]:
        assert f'"{pkg}"' in script, pkg


def test_python_check_covers_the_packages_the_pages_import():
    script = SCRIPT.read_text(encoding="utf-8")
    for name in ["pandas", "numpy", "matplotlib", "scipy", "statsmodels", "pingouin", "lifelines", "scikit_posthocs"]:
        assert f'"{name}"' in script, name


def test_project_python_uses_pandas_3():
    """The pages are written for pandas 3. lifelines declares pandas<3, so pyproject.toml overrides it."""
    import pandas

    assert int(pandas.__version__.split(".")[0]) >= 3, pandas.__version__
