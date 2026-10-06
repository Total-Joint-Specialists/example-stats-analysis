"""Part 3 · Survival analysis: Kaplan-Meier and Cox regression in full (spec section 4, pages 13-14)."""

import pytest

from sitelib import NO_EVIDENCE_AS_NO_DIFFERENCE, ROOT, load, section, text_of, unreported

# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
    "survival/14-cox-regression.html": [
        "hazard-ratio", "choosing-covariates", "univariable-multivariable", "linearity",
        "proportional-hazards", "remedies", "stratified-cox", "fine-gray", "reporting", "exercises"],
}
KM = "survival/13-kaplan-meier.html"
COX = "survival/14-cox-regression.html"


def code_of(found):
    return " ".join(pre.get_text() for pre in found.select("pre"))


@pytest.mark.parametrize("page,sections", SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("section[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_page_runs_both_languages_and_is_frozen(site, page):
    ran = [tabset for tabset in load(page).select("div.panel-tabset")
           if all(pane.select(".cell-output, .cell-output-display") for pane in tabset.select("div.tab-pane"))]
    assert len(ran) >= 5, f"{page}: only {len(ran)} tabsets show output in both R and Python"
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in section(page, "exercises").select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    assert [out.get_text()[:80] for out in load(page).select(".cell-output-stderr")] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_outputs_are_short_and_never_dump_objects(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text and "<matplotlib." not in text and "<lifelines." not in text, \
            f"{page}: object dumped: {text[:80]}"
        assert len(text.splitlines()) <= 40, f"{page}: {len(text.splitlines())}-line output"


@pytest.mark.parametrize("page", SECTIONS)
def test_reports_follow_the_reporting_conventions(site, page):
    """Methods and Results blockquotes and exercise answers: CIs with effect sizes, and no
    "similar" or "held" where the data only fail to show a difference."""
    quotes = [text_of(q) for q in load(page).select("blockquote")]
    assert any("Methods:" in q and "Results:" in q for q in quotes), f"{page}: no Methods and Results"
    answers = [text_of(p) for p in section(page, "exercises").select("p")]
    for text in quotes + answers:
        assert unreported(text) == [], text
        assert not NO_EVIDENCE_AS_NO_DIFFERENCE.findall(text), text


# ---- page 13: Kaplan-Meier and the log-rank test -----------------------------

def test_kaplan_meier_curves_show_numbers_at_risk_and_a_ci_band(site):
    found = section(KM, "kaplan-meier")
    code = code_of(found)
    assert "add_risktable(" in code and "add_confidence_interval()" in code and "add_at_risk_counts(" in code
    panes = found.select("div.panel-tabset div.tab-pane")
    assert len(panes) == 2 and all(pane.select("img") for pane in panes), "the curve is drawn in both languages"


def test_survivorship_is_reported_at_2_5_and_10_years_with_cis_and_numbers_at_risk(site):
    results = " ".join(text_of(q) for q in section(KM, "survivorship").select("blockquote"))
    for years in ["at 2 years", "at 5 years", "at 10 years"]:
        assert years in results, years
    assert results.count("95% CI") >= 3 and "remained at risk" in results


def test_median_follow_up_uses_reverse_kaplan_meier(site):
    found = section(KM, "follow-up")
    assert "reverse Kaplan-Meier" in " ".join(text_of(q) for q in found.select("blockquote"))
    assert "5.62 years" in text_of(found)


def test_log_rank_covers_two_groups_and_three_or_more(site):
    found = section(KM, "log-rank")
    outputs = " ".join(out.get_text() for out in found.select(".cell-output"))
    assert "on 1 degrees of freedom" in outputs and "on 2 degrees of freedom" in outputs
    assert "Mantel-Haenszel" in text_of(found)


def test_competing_risks_compare_the_cumulative_incidence_with_one_minus_km(site):
    text = text_of(section(KM, "competing-risks"))
    for phrase in ["Aalen-Johansen", "1 − Kaplan-Meier", "Gray's test", "Python has no mature implementation of Gray's test"]:
        assert phrase in text, phrase


# ---- page 14: Cox regression ---------------------------------------------------

def test_covariates_are_chosen_in_advance_with_enough_events(site):
    text = text_of(section(COX, "choosing-covariates"))
    assert "chosen before you look" in text and "10 events per term" in text


def test_proportional_hazards_are_checked_on_the_built_in_violation(site):
    found = section(COX, "proportional-hazards")
    assert "Schoenfeld" in text_of(found) and "cox.zph(" in code_of(found)
    plotted = [tabset for tabset in found.select("div.panel-tabset")
               if all(pane.select("img") for pane in tabset.select("div.tab-pane"))]
    assert plotted, "the residual plot is drawn in both languages"
    assert "approach" in code_of(plotted[0])


def test_remedies_cover_stratification_and_a_time_split(site):
    code = code_of(section(COX, "remedies"))
    for call in ["strata(approach)", 'strata=["approach"]', "survSplit(", "CoxTimeVaryingFitter("]:
        assert call in code, call


def test_stratified_cox_covers_matched_sets_and_bilateral_patients(site):
    found = section(COX, "stratified-cox")
    hrefs = [a["href"] for a in found.select("a[href]")]
    for target in ["07-two-paired-groups.html#stratified-cox", "09-three-plus-matched.html#stratified-cox"]:
        assert any(href.endswith(target) for href in hrefs), target
    code = code_of(found)
    assert "cluster = patient_id" in code and 'cluster_col="patient_id"' in code


def test_fine_gray_is_labeled_r_only(site):
    found = section(COX, "fine-gray")
    assert "(R only)" in found.select_one("h2").get_text()
    assert found.select("pre.r") and not found.select("pre.python")
    assert "subdistribution hazard ratio" in text_of(found)


def test_reporting_gives_univariable_and_multivariable_hazard_ratios(site):
    found = section(COX, "reporting")
    table = found.select_one("table")
    assert table is not None and "Univariable" in text_of(table) and "Multivariable" in text_of(table)
    assert "Univariable HR (95% CI)" in " ".join(out.get_text() for out in found.select(".cell-output"))
