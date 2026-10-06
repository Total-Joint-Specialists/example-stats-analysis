"""Shared constants and helpers for the built-site tests."""

import html
import re
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "_site"

PAGES = [
    "index.html",
    "choose-a-test.html",
    "tests-a-z.html",
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


# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
# Each phase adds its pages as they're written; tests/site/test_free_form.py checks them all.
FREE_FORM_SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
    "survival/14-cox-regression.html": [
        "hazard-ratio", "choosing-covariates", "univariable-multivariable", "linearity",
        "proportional-hazards", "remedies", "stratified-cox", "fine-gray", "reporting", "exercises"],
    "beyond/15-post-hoc.html": [
        "why-adjust", "adjusting-p-values", "after-anova", "after-kruskal-wallis", "after-chi-square",
        "after-repeated-measures-anova", "after-friedman", "after-cochran-q", "after-log-rank",
        "overall-test-first", "planned-comparisons", "exercises"],
    "beyond/16-mixed-models.html": [
        "why-mixed-models", "random-intercept", "estimated-marginal-means", "time", "group-by-time",
        "bilateral", "reporting", "exercises"],
    "beyond/17-agreement.html": [
        "reliability-vs-agreement", "icc", "inter-intra-rater", "bland-altman", "kappa", "reporting",
        "exercises"],
    "report/18-example-report.html": [
        "question", "tidy", "integrity", "table-1", "distributions", "primary-analysis", "survival",
        "manuscript", "aim", "methods", "results", "exercises"],
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


def code_of(found):
    """The code shown in a page element, as one string."""
    return " ".join(pre.get_text() for pre in found.select("pre"))


def docx_xml(path) -> str:
    """The body of a Word file. A .docx is a zip of XML files, so the site tests need no Word package."""
    with zipfile.ZipFile(path) as docx:
        return docx.read("word/document.xml").decode("utf-8")


def docx_text(path) -> str:
    """The text of a Word file, one paragraph per line (including the paragraphs in table cells),
    with smart quotes straightened and non-breaking spaces ("Table 1") made plain."""
    paragraphs = re.findall(r"<w:p[ >].*?</w:p>", docx_xml(path), re.DOTALL)
    text = "\n".join("".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p)) for p in paragraphs)
    return html.unescape(text).replace("’", "'").replace("\xa0", " ")


# ---- reporting conventions (spec section 4, page 0.2) ------------------------

# Results sentences report the numbers and stop: no comparison words, significance judgments, direction
# verbs or descriptive labels. Saying what the numbers mean is the Discussion's job (CLAUDE.md rule 8).
INTERPRETATION = re.compile(
    r"\b(?:similar(?:ly)?|comparable|differ(?:s|ed)?|higher|lower|greater|fewer|less|more|better|worse|longer"
    r"|shorter|older|younger|larger|smaller|than|significant(?:ly)?|non-?significant|evidence|imprecise"
    r"|associated|independently|rose|rise[sn]?|fell|falls?|increased?|decreased?|improved?|improvement"
    r"|declined?|excellent|good|moderate|substantial|almost perfect|poor|weak|strong(?:ly)?)\b", re.IGNORECASE)


def results_of(text):
    """The Results part of a Methods/Results blockquote's text, or "" if it has none."""
    return text.split("Results:", 1)[1] if "Results:" in text else ""


# In the teaching prose, a wide CI or a non-significant check is "no clear evidence of a difference",
# never "similar" or "held".
NO_EVIDENCE_AS_NO_DIFFERENCE = re.compile(
    r"\b(similar|no difference|held|not violated|(?:did not|does not|doesn't) improve)\b", re.IGNORECASE)
EFFECT_SIZE = re.compile(r"(ω²|ε²|η²( p)?|Kendall's W|Cramér's V|\br|ρ|φ|κ) = [\d.]+|(odds|hazard) ratio [\d.]+"
                         r"|\bICC(\([^)]*\))?( =)? [\d.]+")


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
