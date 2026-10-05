"""Python-side checks on the tidy CSVs: every file opens in pandas, matches its
codebook, and stores missing values as blank cells (never the text "NA")."""

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CODEBOOKS = sorted((DATA / "codebooks").glob("*.csv"))


def dataset_for(codebook: Path) -> Path:
    direct = DATA / codebook.name
    return direct if direct.exists() else DATA / "answer-keys" / codebook.name


@pytest.mark.parametrize("codebook", CODEBOOKS, ids=lambda p: p.name)
def test_columns_match_codebook(codebook):
    df = pd.read_csv(dataset_for(codebook))
    assert list(df.columns) == list(pd.read_csv(codebook)["variable"])


@pytest.mark.parametrize("codebook", CODEBOOKS, ids=lambda p: p.name)
def test_missing_values_are_blank_cells(codebook):
    df = pd.read_csv(dataset_for(codebook), keep_default_na=False, na_values=[""])
    text = df.select_dtypes(include=["object", "string"])
    for token in ["NA", "N/A", "NaN", "null", "None"]:
        assert not (text == token).any().any(), f"{codebook.name} contains the text {token!r}"


def test_cohort_dates_parse():
    cohort = pd.read_csv(DATA / "cohort.csv", parse_dates=["surgery_date"])
    assert len(cohort) > 0
    assert cohort["surgery_date"].dt.year.between(2015, 2025).all()
