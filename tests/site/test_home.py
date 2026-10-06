"""The ways into the site (spec section 3): the welcome page, the test chooser (the decision table)
and the A–Z index of tests and methods."""

from sitelib import CELL_ANCHORS, load, strip_dot, text_of

HOME = "index.html"
CHOOSE = "choose-a-test.html"
A_TO_Z = "tests-a-z.html"

BEYOND_LINKS = [
    "survival/13-kaplan-meier.html",
    "survival/14-cox-regression.html",
    "beyond/15-post-hoc.html",
    "beyond/16-mixed-models.html",
    "beyond/17-agreement.html",
    "foundations/03-distributions.html",
]


def hrefs(page):
    return {strip_dot(a["href"]) for a in load(page).select("main a[href]")}


def main_text(page):
    return text_of(load(page).select_one("main"))


# ---- the welcome page ----------------------------------------------------------------------

def test_home_page_offers_three_ways_in(site):
    links = hrefs(HOME)
    assert "getting-started/setup.html" in links                                 # 1. getting started
    for first_page in ["foundations/01-tidy-data.html", "catalog/04-describe-one-group.html",
                       "survival/13-kaplan-meier.html", "beyond/15-post-hoc.html", "report/18-example-report.html"]:
        assert first_page in links, first_page                                    # 2. the five parts
    assert CHOOSE in links and A_TO_Z in links                                    # 3. which test?
    assert load(HOME).select_one("div.decision-table") is None                   # the table has its own page


def test_synthetic_data_warning(site):
    assert "SYNTHETIC DATA" in main_text(HOME)


# ---- which test should I use? -------------------------------------------------------------------

def test_the_test_chooser_is_titled_by_the_readers_question(site):
    assert text_of(load(CHOOSE).select_one("h1.title")) == "Which statistical test should I use?"
    assert A_TO_Z in hrefs(CHOOSE)


def test_every_table_cell_links_to_its_section(site):
    expected = {f"{page}#{a}" for page, anchors in CELL_ANCHORS.items() for a in anchors}
    assert expected - hrefs(CHOOSE) == set()


def test_beyond_the_table_links(site):
    assert set(BEYOND_LINKS) - hrefs(CHOOSE) == set()


def test_table_is_credited_and_spelled_right(site):
    text = main_text(CHOOSE)
    assert "Motulsky" in text and "Intuitive Biostatistics" in text
    assert "Cochran's Q" in text
    assert "Cochrane" not in text
    assert "orthoteers" not in str(load(CHOOSE))


def test_decision_table_scrolls_on_small_screens(site):
    assert load(CHOOSE).select_one("div.decision-table.table-responsive table") is not None


# ---- tests A–Z ------------------------------------------------------------------------------

# Every method the site teaches beyond the decision table's cells: pages 2-3 and 13-17.
METHOD_SECTIONS = [
    "foundations/02-demographics.html#smd", "foundations/03-distributions.html#shapiro",
    "survival/13-kaplan-meier.html#kaplan-meier", "survival/13-kaplan-meier.html#follow-up",
    "survival/13-kaplan-meier.html#log-rank", "survival/13-kaplan-meier.html#competing-risks",
    "survival/14-cox-regression.html#hazard-ratio", "survival/14-cox-regression.html#proportional-hazards",
    "survival/14-cox-regression.html#stratified-cox", "survival/14-cox-regression.html#fine-gray",
    "beyond/15-post-hoc.html#adjusting-p-values", "beyond/15-post-hoc.html#after-anova",
    "beyond/15-post-hoc.html#after-kruskal-wallis", "beyond/15-post-hoc.html#after-chi-square",
    "beyond/15-post-hoc.html#after-repeated-measures-anova", "beyond/15-post-hoc.html#after-friedman",
    "beyond/15-post-hoc.html#after-cochran-q", "beyond/15-post-hoc.html#after-log-rank",
    "beyond/16-mixed-models.html#random-intercept", "beyond/16-mixed-models.html#estimated-marginal-means",
    "beyond/17-agreement.html#icc", "beyond/17-agreement.html#bland-altman", "beyond/17-agreement.html#kappa",
]


def index_rows():
    """(name, row text, links) for each row of the A–Z table."""
    rows = []
    for tr in load(A_TO_Z).select("main table tbody tr"):
        rows.append((text_of(tr.select_one("td")), text_of(tr), {strip_dot(a["href"]) for a in tr.select("a[href]")}))
    return rows


def test_index_lists_every_test_and_method(site):
    linked = set().union(*(links for _, _, links in index_rows()))
    cells = {f"{page}#{a}" for page, anchors in CELL_ANCHORS.items() for a in anchors}
    assert (cells | set(METHOD_SECTIONS)) - linked == set()


def test_index_is_alphabetical(site):
    names = [name.lower() for name, _, _ in index_rows()]
    assert names == sorted(names)


def test_index_finds_tests_under_their_other_names(site):
    rows = {name: links for name, _, links in index_rows()}
    for alias, target in [("Wilcoxon rank-sum test", "catalog/06-two-unpaired-groups.html#mann-whitney"),
                          ("Mantel-Cox test", "catalog/06-two-unpaired-groups.html#log-rank"),
                          ("Welch's t test", "catalog/06-two-unpaired-groups.html#unpaired-t"),
                          ("Conditional proportional hazards regression", "survival/14-cox-regression.html#stratified-cox")]:
        assert alias in rows and target in rows[alias], alias
