"""Site-wide page conventions (spec section 6)."""

from sitelib import PAGES, ROOT, SITE, load


def test_language_tabs_are_grouped_and_ordered(site):
    for page in PAGES:
        for tabset in load(page).select("div.panel-tabset"):
            assert tabset.get("data-group") == "language", page
            labels = [a.get_text(strip=True)
                      for a in tabset.select(":scope > ul.nav-tabs a.nav-link")]
            assert labels == ["R", "Python"], f"{page}: tabs are {labels}"


def test_solutions_start_collapsed(site):
    for page in PAGES:
        for callout in load(page).select("div.callout"):
            header = callout.select_one(".callout-header")
            if header and header.get_text(strip=True).endswith("Solution"):
                body = callout.select_one(".callout-collapse")
                assert body is not None, f"{page}: a Solution box is not collapsible"
                assert "show" not in body.get("class", []), f"{page}: a Solution box starts open"


def test_hidden_checks_never_show(site):
    for page in PAGES:
        assert "check_agree" not in (SITE / page).read_text(encoding="utf-8"), page


def test_using_this_site_runs_both_languages(site):
    soup = load("getting-started/using-this-site.html")
    first = soup.select_one("div.panel-tabset")
    assert first is not None
    assert len(first.select(".cell-output")) >= 2, "R and Python should each print a result"
    assert (ROOT / "_freeze" / "getting-started" / "using-this-site").is_dir()


def test_callout_legend_shows_all_four_kinds(site):
    text = load("getting-started/using-this-site.html").get_text(" ")
    for title in ["In plain language", "Watch out", "R vs Python", "Under the hood"]:
        assert title in text, title


def test_every_python_print_shows_its_output(site):
    """reticulate can drop Python output silently (see test_sources.py); catch the symptom too."""
    for page in PAGES:
        for cell in load(page).select("div.cell"):
            code = cell.select_one("pre.sourceCode.python")
            if code is not None and "print(" in code.get_text():
                assert cell.select(".cell-output-stdout"), f"{page}: no output for {code.get_text()[:60]!r}"
