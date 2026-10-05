"""Python-side checks on the tidy CSVs: every file opens in pandas, matches its
codebook, and stores missing values as blank cells (never the text "NA")."""

import hashlib
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


def test_csvs_match_the_generators_checksums():
    """CI runs no R, so this is what catches a CSV edited by hand (or re-saved by
    Excel): data-raw/generate.R records an MD5 for every CSV it writes."""
    listed = {}
    for line in (DATA / "CHECKSUMS.md5").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        listed[name] = digest
    on_disk = sorted(str(p.relative_to(DATA)) for p in DATA.rglob("*.csv"))
    assert sorted(listed) == on_disk
    for name, digest in listed.items():
        actual = hashlib.md5((DATA / name).read_bytes()).hexdigest()
        assert actual == digest, f"data/{name} differs from what data-raw/generate.R wrote"
