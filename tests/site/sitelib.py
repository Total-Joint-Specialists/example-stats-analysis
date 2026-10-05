"""Shared constants and helpers for the built-site tests."""

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
