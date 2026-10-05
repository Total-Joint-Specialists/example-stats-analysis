"""This repo is public. Data files must never be committable outside data/
and templates/, and local environments and build output stay out of git."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def ignored(path: str) -> bool:
    result = subprocess.run(["git", "check-ignore", "--no-index", "-q", path], cwd=ROOT)
    return result.returncode == 0


@pytest.mark.parametrize(
    "path",
    [
        "patients.xlsx",
        "export.csv",
        "analysis/real_data.csv",
        "chart_pull.xls",
        "dataset.sav",
        "dataset.dta",
        "dataset.sas7bdat",
        "cohort.rds",
        "cohort.parquet",
        "IMG0001.dcm",
        "scratch/my_analysis.R",
        ".venv/bin/python",
        "_site/index.html",
        ".Renviron",
    ],
)
def test_risky_or_generated_files_are_ignored(path):
    assert ignored(path), f"{path} could be committed"


@pytest.mark.parametrize(
    "path",
    [
        "data/cohort.csv",
        "data/codebooks/cohort.csv",
        "data/answer-keys/survey_items_long.csv",
        "data/messy_abstraction_workbook.xlsx",
        "templates/data-collection-template.xlsx",
        "scratch/README.md",
        "_freeze/getting-started/using-this-site/execute-results/html.json",
        "renv.lock",
    ],
)
def test_project_files_are_not_ignored(path):
    assert not ignored(path), f"{path} is wrongly ignored"
