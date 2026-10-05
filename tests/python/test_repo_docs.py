from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE_URL = "https://total-joint-specialists.github.io/example-stats-analysis/"


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_readme_links_the_site_and_says_synthetic():
    text = read("README.md")
    assert SITE_URL in text
    assert "synthetic" in text.lower()


def test_licenses():
    assert read("LICENSE").startswith("MIT License")
    assert "Total Joint Specialists" in read("LICENSE")
    content = read("LICENSE-CONTENT")
    assert "CC BY 4.0" in content
    assert "https://creativecommons.org/licenses/by/4.0/legalcode" in content


def test_claude_md_states_the_golden_rules():
    text = read("CLAUDE.md")
    for rule in ["engine: knitr", "group=\"language\"", "check_agree", "_freeze", "Synthetic data only"]:
        assert rule in text, rule
