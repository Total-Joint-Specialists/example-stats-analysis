from sitelib import CELL_ANCHORS, load, strip_dot

BEYOND_LINKS = [
    "survival/13-kaplan-meier.html",
    "survival/14-cox-regression.html",
    "beyond/15-post-hoc.html",
    "beyond/16-mixed-models.html",
    "beyond/17-agreement.html",
    "foundations/03-distributions.html",
]


def main_hrefs():
    return {strip_dot(a["href"]) for a in load("index.html").select("main a[href]")}


def main_text():
    return load("index.html").select_one("main").get_text(" ").replace("’", "'")


def test_every_table_cell_links_to_its_section(site):
    expected = {f"{page}#{a}" for page, anchors in CELL_ANCHORS.items() for a in anchors}
    assert expected - main_hrefs() == set()


def test_beyond_the_table_links(site):
    assert set(BEYOND_LINKS) - main_hrefs() == set()


def test_table_is_credited_and_spelled_right(site):
    text = main_text()
    assert "Motulsky" in text and "Intuitive Biostatistics" in text
    assert "Cochran's Q" in text
    assert "Cochrane" not in text
    assert "orthoteers" not in str(load("index.html"))


def test_synthetic_data_warning(site):
    assert "SYNTHETIC DATA" in main_text()


def test_decision_table_scrolls_on_small_screens(site):
    assert load("index.html").select_one("div.decision-table.table-responsive table") is not None
