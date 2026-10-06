"""Free-form pages (spec section 6): the survival, "beyond the table" and example-report pages, which
have no fixed section anatomy. Every page in FREE_FORM_SECTIONS gets these checks."""

import pytest

from sitelib import FREE_FORM_SECTIONS, NO_EVIDENCE_AS_NO_DIFFERENCE, ROOT, load, section, text_of, unreported


@pytest.mark.parametrize("page,sections", FREE_FORM_SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("section[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_page_runs_both_languages_and_is_frozen(site, page):
    ran = [tabset for tabset in load(page).select("div.panel-tabset")
           if all(pane.select(".cell-output, .cell-output-display") for pane in tabset.select("div.tab-pane"))]
    assert len(ran) >= 5, f"{page}: only {len(ran)} tabsets show output in both R and Python"
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in section(page, "exercises").select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    assert [out.get_text()[:80] for out in load(page).select(".cell-output-stderr")] == []


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_outputs_are_short_and_never_dump_objects(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text and "<matplotlib." not in text and "<lifelines." not in text, \
            f"{page}: object dumped: {text[:80]}"
        assert len(text.splitlines()) <= 40, f"{page}: {len(text.splitlines())}-line output"


def test_conventions_rule_catches_kappa_and_icc_without_a_ci():
    for sentence in ["Agreement was moderate (κ = 0.58).", "Agreement was moderate (weighted κ = 0.73).",
                     "Reliability was good (ICC 0.89).", "Reliability was good (ICC(A,1) = 0.889)."]:
        assert unreported(sentence) == ["effect size without a CI"], sentence
    assert unreported("Reliability was good (ICC 0.89, 95% CI 0.82 to 0.93).") == []


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_reports_follow_the_reporting_conventions(site, page):
    """Methods and Results (blockquotes, or page 18's manuscript sections) and exercise answers: CIs
    with effect sizes, and no "similar" or "held" where the data only fail to show a difference."""
    soup = load(page)
    quotes = [text_of(q) for q in soup.select("blockquote")]
    manuscript = [text_of(p) for anchor in ["methods", "results"] for p in soup.select(f"section#{anchor} p")]
    assert any("Methods:" in q and "Results:" in q for q in quotes) or manuscript, f"{page}: no Methods and Results"
    answers = [text_of(p) for p in section(page, "exercises").select("p")]
    for text in quotes + manuscript + answers:
        assert unreported(text) == [], text
        assert not NO_EVIDENCE_AS_NO_DIFFERENCE.findall(text), text


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_printed_tables_show_every_column(site, page):
    """pandas swaps columns that don't fit for "..."; print wide tables with .to_string()."""
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert " ... " not in text and "rows x" not in text, f"{page}: {text[:120]}"
