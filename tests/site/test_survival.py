"""Part 3 · Survival analysis: Kaplan-Meier and Cox regression in full (spec section 4, pages 13-14)."""

import pytest

from sitelib import NO_EVIDENCE_AS_NO_DIFFERENCE, ROOT, load, section, text_of, unreported

# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
}
KM = "survival/13-kaplan-meier.html"


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
