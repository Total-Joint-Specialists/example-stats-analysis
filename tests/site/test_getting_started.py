from sitelib import load

SETUP_COMMANDS = [
    "uv python install 3.13",
    "git clone https://github.com/Total-Joint-Specialists/example-stats-analysis.git",
    "renv::restore()",
    "uv sync",
    "Rscript getting-started/check_setup.R",
    "uv run python getting-started/check_setup.py",
    'source("getting-started/check_setup.R")',
    "sudo xcodebuild -license accept",
]


def test_setup_page_shows_every_command_an_ra_types(site):
    text = load("getting-started/setup.html").get_text()
    missing = [c for c in SETUP_COMMANDS if c not in text]
    assert missing == []


def test_setup_page_is_no_longer_a_stub(site):
    assert load("getting-started/setup.html").select_one(".coming-soon") is None


def test_real_data_page_lists_all_18_safe_harbor_identifiers(site):
    items = load("getting-started/real-data.html").select(".phi-identifiers ol > li")
    assert len(items) == 18


def test_real_data_page_covers_tjs_traps(site):
    text = load("getting-started/real-data.html").get_text(" ")
    for phrase in ["MRN", "older than 89", "implant", "DICOM", "AI", "git status",
                   "git diff --staged"]:
        assert phrase in text, phrase


def test_real_data_page_is_no_longer_a_stub(site):
    assert load("getting-started/real-data.html").select_one(".coming-soon") is None
