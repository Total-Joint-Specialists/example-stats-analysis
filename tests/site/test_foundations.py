"""Part 1 · Foundations: the tidy-data, Table 1 and distributions pages."""

import pytest

from sitelib import ROOT, load

SECTIONS = {
    "foundations/01-tidy-data.html": [
        "what-tidy-means", "collecting", "tidying", "reshaping", "integrity", "exercises"],
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


def test_tidy_page_says_to_run_the_steps_in_order(site):
    assert "Run the steps in order" in load("foundations/01-tidy-data.html").get_text(" ")
