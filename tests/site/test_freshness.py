"""Pages that read data/ must have been rendered from the current data.

Quarto's freeze only notices changes to a page's .qmd, not to the data it
reads. Each such page stamps the MD5 of data/CHECKSUMS.md5 into its HTML; if
the data change and nobody re-renders, this test fails (locally and in CI).
"""

import hashlib
import re

from sitelib import ROOT, SITE

CONTENT_DIRS = ["getting-started", "foundations", "catalog", "survival", "beyond", "report"]
READS_DATA = re.compile(r"""["']data/""")


def data_pages():
    for d in CONTENT_DIRS:
        for qmd in sorted((ROOT / d).glob("*.qmd")):
            text = qmd.read_text(encoding="utf-8")
            if "```{r" in text and READS_DATA.search(text):
                yield qmd.relative_to(ROOT).with_suffix(".html")


def test_pages_that_read_data_were_rendered_from_the_current_data(site):
    current = hashlib.md5((ROOT / "data" / "CHECKSUMS.md5").read_bytes()).hexdigest()
    pages = list(data_pages())
    assert pages, "expected at least one page that reads data/"
    for page in pages:
        html = (SITE / page).read_text(encoding="utf-8")
        assert f"<!-- data-checksum: {current} -->" in html, f"{page} was rendered from other data; re-render it"


def test_just_data_re_renders_the_pages_that_read_data():
    justfile = (ROOT / "Justfile").read_text(encoding="utf-8")
    recipe = justfile[justfile.index("\ndata:"):]
    assert "quarto render foundations" in recipe
