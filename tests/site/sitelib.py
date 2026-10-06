"""Shared constants and helpers for the built-site tests."""

import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "_site"

PAGES = [
    "index.html",
    "getting-started/setup.html",
    "getting-started/using-this-site.html",
    "getting-started/real-data.html",
    "foundations/01-tidy-data.html",
    "foundations/02-demographics.html",
    "foundations/03-distributions.html",
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
    "catalog/11-predict-from-one.html",
    "catalog/12-predict-from-several.html",
    "survival/13-kaplan-meier.html",
    "survival/14-cox-regression.html",
    "beyond/15-post-hoc.html",
    "beyond/16-mixed-models.html",
    "beyond/17-agreement.html",
    "report/18-example-report.html",
]

# Spec section 3.2: every non-empty cell of the decision table, by row page.
CELL_ANCHORS = {
    "catalog/04-describe-one-group.html": ["mean-sd", "median-iqr", "proportion", "kaplan-meier"],
    "catalog/05-one-group-vs-hypothetical.html": [
        "one-sample-t", "wilcoxon-signed-rank", "chi-square-gof", "binomial-test"],
    "catalog/06-two-unpaired-groups.html": [
        "unpaired-t", "mann-whitney", "fisher-chi-square", "log-rank"],
    "catalog/07-two-paired-groups.html": [
        "paired-t", "wilcoxon-signed-rank", "mcnemar", "stratified-cox"],
    "catalog/08-three-plus-unmatched.html": [
        "one-way-anova", "kruskal-wallis", "chi-square", "cox"],
    "catalog/09-three-plus-matched.html": [
        "repeated-measures-anova", "friedman", "cochran-q", "stratified-cox"],
    "catalog/10-association.html": ["pearson", "spearman", "contingency-coefficients"],
    "catalog/11-predict-from-one.html": [
        "linear-regression", "nonlinear-regression", "nonparametric-regression",
        "logistic-regression", "cox"],
    "catalog/12-predict-from-several.html": [
        "multiple-linear-regression", "multiple-nonlinear-regression",
        "multiple-logistic-regression", "cox"],
}


def load(page: str) -> BeautifulSoup:
    return BeautifulSoup((SITE / page).read_text(encoding="utf-8"), "html.parser")


def strip_dot(href: str) -> str:
    return href.removeprefix("./")


def text_of(element):
    """Text with smart quotes straightened and runs of whitespace collapsed."""
    return " ".join(element.get_text(" ").replace("’", "'").split())


def section(page, anchor):
    found = load(page).select_one(f"section#{anchor}")
    assert found is not None, f"{page} has no section #{anchor}"
    return found


# ---- reporting conventions (spec section 4, page 0.2) ------------------------

# A wide CI or a non-significant check is "no clear evidence of a difference", never "similar" or "held".
NO_EVIDENCE_AS_NO_DIFFERENCE = re.compile(
    r"\b(similar|no difference|held|not violated|(?:did not|does not|doesn't) improve)\b", re.IGNORECASE)
EFFECT_SIZE = re.compile(r"(ω²|ε²|η²( p)?|Kendall's W|Cramér's V|\br|ρ|φ) = [\d.]+|(odds|hazard) ratio [\d.]+")


def unreported(text):
    """The conventions a model Results sentence breaks: an effect size needs its CI,
    a mean its SD and a median its IQR."""
    problems = []
    if EFFECT_SIZE.search(text) and "CI" not in text:
        problems.append("effect size without a CI")
    if re.search(r"\bmeans? of [\d.]+", text) and "SD" not in text:
        problems.append("mean without an SD")
    if re.search(r"\bmedian\b[^.]*\d", text) and "IQR" not in text:
        problems.append("median without an IQR")
    return problems
