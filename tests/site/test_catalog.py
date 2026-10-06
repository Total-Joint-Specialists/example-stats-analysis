"""Part 2 · Test catalog: one page per row of the decision table, one section per cell."""

import pytest

from sitelib import CELL_ANCHORS, ROOT, load

# Catalog pages written so far. Later phases add pages 8-12 here.
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
]

# Spec section 6, steps 2-7, as h3 headings in this order. Page 4 describes a
# group rather than testing it: its estimate and CI are the result, so it has
# no separate effect-size step.
ANATOMY = ["When to use it", "Look at the data first", "Run it", "Read the output",
           "Effect size and 95% CI", "How to report it"]
DESCRIBE = [step for step in ANATOMY if step != "Effect size and 95% CI"]

SECTIONS = [(page, anchor) for page in WRITTEN for anchor in CELL_ANCHORS[page]]

# Survival cells give a short worked example and point to the full treatment.
SURVIVAL_LINKS = {cell: target for cell, target in {
    ("catalog/04-describe-one-group.html", "kaplan-meier"): "survival/13-kaplan-meier.html",
    ("catalog/06-two-unpaired-groups.html", "log-rank"): "survival/14-cox-regression.html",
    ("catalog/07-two-paired-groups.html", "stratified-cox"): "survival/14-cox-regression.html",
}.items() if cell[0] in WRITTEN}


def text_of(element):
    """Text with smart quotes straightened and runs of whitespace collapsed."""
    return " ".join(element.get_text(" ").replace("’", "'").split())


def section(page, anchor):
    found = load(page).select_one(f"section#{anchor}")
    assert found is not None, f"{page} has no section #{anchor}"
    return found


@pytest.mark.parametrize("page", WRITTEN)
def test_page_is_written_and_frozen(site, page):
    assert load(page).select_one(".coming-soon") is None, f"{page} is still a stub"
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page,anchor", SECTIONS)
def test_section_follows_the_page_anatomy(site, page, anchor):
    found = section(page, anchor)
    steps = [h.get_text(strip=True) for h in found.select("section.level3 > h3")]
    assert steps == (DESCRIBE if page.startswith("catalog/04-") else ANATOMY)
    text = text_of(found)
    assert "The question:" in text                                      # step 1
    report = " ".join(text_of(q) for q in found.select("blockquote"))
    assert "Methods:" in report and "Results:" in report                # step 7
    assert found.select("div.callout-warning"), "no ⚠️ Watch out box"   # step 8


@pytest.mark.parametrize("page,anchor", SECTIONS)
def test_section_shows_output_in_both_languages(site, page, anchor):
    ran = [tabset for tabset in section(page, anchor).select("div.panel-tabset")
           if all(pane.select(".cell-output, .cell-output-display")
                  for pane in tabset.select("div.tab-pane"))]
    assert ran, f"{page}#{anchor}: no tabset shows output in both R and Python"


@pytest.mark.parametrize("page", WRITTEN)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    exercises = load(page).select_one("section#exercises")
    headers = [h.get_text(strip=True) for h in exercises.select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", WRITTEN)
def test_page_shows_no_warnings_or_package_messages(site, page):
    assert [out.get_text()[:80] for out in load(page).select(".cell-output-stderr")] == []


@pytest.mark.parametrize("page", WRITTEN)
def test_outputs_are_short_and_never_dump_objects(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text and "<matplotlib." not in text, f"{page}: object dumped: {text[:80]}"
        assert len(text.splitlines()) <= 40, f"{page}: {len(text.splitlines())}-line output"


@pytest.mark.parametrize("cell,target", SURVIVAL_LINKS.items())
def test_survival_sections_point_to_the_full_treatment(site, cell, target):
    page, anchor = cell
    hrefs = [a["href"] for a in section(page, anchor).select("a[href]")]
    assert any(href.endswith(target) for href in hrefs)


def test_log_rank_section_names_the_mantel_haenszel_test(site):
    assert "Mantel-Haenszel" in text_of(section("catalog/06-two-unpaired-groups.html", "log-rank"))
