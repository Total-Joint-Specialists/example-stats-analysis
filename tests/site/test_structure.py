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


def test_every_page_carries_the_tjs_logo_in_both_themes(site):
    for page in PAGES:
        logos = load(page).select("a.sidebar-logo-link img")
        assert [img["src"].rsplit("/", 1)[-1] for img in logos] == ["tjs-logo.png", "tjs-logo-dark.png"], page
        assert all(img.get("alt") == "Total Joint Specialists" for img in logos), page
    assert (site / "images" / "tjs-logo.png").exists() and (site / "images" / "tjs-logo-dark.png").exists()


def test_the_browser_tab_shows_the_tjs_mark(site):
    icon = load("index.html").select_one('link[rel="icon"]')
    assert icon is not None and icon["href"].endswith("images/tjs-icon.png")
    assert (site / "images" / "tjs-icon.png").exists()


def test_coming_soon_marking_is_consistent(site):
    for page in PAGES:
        soup = load(page)
        in_title = "(coming soon)" in soup.title.get_text()
        has_box = soup.select_one(".coming-soon") is not None
        assert in_title == has_box, f"{page}: title says {in_title}, box says {has_box}"
