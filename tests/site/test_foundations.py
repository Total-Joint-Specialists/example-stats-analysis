"""Part 1 · Foundations: the tidy-data, Table 1 and distributions pages."""

import pytest

from sitelib import ROOT, load

SECTIONS = {
    "foundations/01-tidy-data.html": [
        "what-tidy-means", "collecting", "tidying", "reshaping", "integrity", "exercises"],
    "foundations/02-demographics.html": [
        "setup", "one-group", "which-summary", "by-group", "smd", "missing", "export", "exercises"],
    "foundations/03-distributions.html": [
        "why", "look", "shapiro", "within-groups", "robustness", "transform", "ordinal",
        "paired", "flowchart", "effect-sizes", "exercises"],
}


@pytest.mark.parametrize("page,sections", SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in load(page).select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", SECTIONS)
def test_page_runs_code_in_both_languages_and_is_frozen(site, page):
    tabsets = load(page).select("div.panel-tabset")
    executed = [t for t in tabsets if t.select(".cell-output, .cell-output-display")]
    assert len(executed) >= 3
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    noise = [o.get_text()[:80] for o in load(page).select(".cell-output-stderr")]
    assert noise == []


def test_distributions_page_has_the_flowchart(site):
    assert load("foundations/03-distributions.html").select_one(".mermaid, pre.mermaid-js") is not None


def test_tidy_page_says_to_run_the_steps_in_order(site):
    assert "Run the steps in order" in load("foundations/01-tidy-data.html").get_text(" ")


# ---- review fixes ---------------------------------------------------------

def text_of(page):
    """Page text with smart quotes straightened and runs of whitespace collapsed."""
    return " ".join(load(page).get_text(" ").replace("’", "'").split())


@pytest.mark.parametrize("page", SECTIONS)
def test_outputs_never_dump_raw_arrays_or_run_long(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text, f"{page}: raw array printed"
        assert len(text.splitlines()) <= 60, f"{page}: {len(text.splitlines())}-line output"


def test_tidy_page_explains_the_day_first_bug_correctly(site):
    text = text_of("foundations/01-tidy-data.html")
    assert "2015-11-02" in text and "Never use dayfirst=True" in text.replace("`", "")
    assert "would quietly change results" not in text


def test_demographics_page_states_smds_and_formats_consistently(site):
    page = "foundations/02-demographics.html"
    text = text_of(page)
    assert "just over 0.1" in text
    assert "Smoking status (0.23)" in text
    assert "always returns an observed value" not in text
    assert "tableone shows both" in text
    assert "not independent" in text
    html = str(load(page))
    assert ">65.5 (9.4)<" in html and ">0.203<" in html     # R table: 1 decimal, 3-decimal p


def test_distributions_page_states_statistics_correctly(site):
    text = text_of("foundations/03-distributions.html")
    assert "unlikely to be pure chance" not in text
    assert "would be unusual if there were really no difference" in text
    assert "bouncing around 0.05" in text
    assert "make no assumption about the shape" not in text
    assert "typical BMI of 30" not in text
    assert "within-patient" in text                       # MCID caveat
    assert "p = 0.173" in text                            # three-decimal p-values
    assert "bilateral" in text and "independent" in text


def test_flowchart_covers_hypothetical_values_and_matches_the_guidance(site):
    soup = load("foundations/03-distributions.html")
    chart = soup.select_one(".mermaid, pre.mermaid-js").get_text()
    assert "hypothetical value" in chart
    assert "small groups" not in chart
