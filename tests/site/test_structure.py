from sitelib import CELL_ANCHORS, PAGES, load, strip_dot


def test_every_page_is_built(site):
    missing = [p for p in PAGES if not (site / p).exists()]
    assert missing == []


def test_repo_files_are_not_published(site):
    for path in ["docs", "tests", "data-raw", "README.html", "CLAUDE.html", "scratch"]:
        assert not (site / path).exists(), f"{path} must not be in the site"


def test_sidebar_links_every_page(site):
    hrefs = {strip_dot(a["href"]) for a in load("index.html").select("#quarto-sidebar a[href]")}
    missing = [p for p in PAGES if p not in hrefs]
    assert missing == []


def test_catalog_pages_have_every_cell_anchor(site):
    for page, anchors in CELL_ANCHORS.items():
        ids = {el["id"] for el in load(page).select("[id]")}
        missing = [a for a in anchors if a not in ids]
        assert missing == [], f"{page} is missing anchors {missing}"


def test_coming_soon_marking_is_consistent(site):
    for page in PAGES:
        soup = load(page)
        in_title = "(coming soon)" in soup.title.get_text()
        has_box = soup.select_one(".coming-soon") is not None
        assert in_title == has_box, f"{page}: title says {in_title}, box says {has_box}"
