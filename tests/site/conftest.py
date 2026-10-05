import pytest

from sitelib import SITE


@pytest.fixture(scope="session")
def site():
    if not (SITE / "index.html").exists():
        pytest.fail("No built site in _site/. Run `quarto render` first.")
    return SITE
