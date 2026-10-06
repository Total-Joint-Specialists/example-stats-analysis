"""Source-level rules for .qmd files (no built site needed)."""

import re

from sitelib import ROOT

CONTENT_DIRS = ["getting-started", "foundations", "catalog", "survival", "beyond", "report"]
EXECUTABLE_CHUNK = re.compile(r"^```\{(r|python)[ ,}]", re.MULTILINE)
KNITR = re.compile(r"^engine:\s*knitr\s*$", re.MULTILINE)


def qmd_files():
    files = [ROOT / "index.qmd"]
    for d in CONTENT_DIRS:
        files += sorted((ROOT / d).glob("*.qmd"))
    return files


def front_matter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return match.group(1) if match else ""


def missing_knitr(text: str) -> bool:
    return bool(EXECUTABLE_CHUNK.search(text)) and not KNITR.search(front_matter(text))


def test_rule_catches_python_page_without_knitr():
    assert missing_knitr("---\ntitle: x\n---\n\n```{python}\nprint(1)\n```\n")


def test_rule_accepts_page_that_declares_knitr():
    assert not missing_knitr("---\ntitle: x\nengine: knitr\n---\n\n```{python}\nprint(1)\n```\n")


def test_rule_ignores_display_only_code():
    assert not missing_knitr("---\ntitle: x\n---\n\n```python\nprint(1)\n```\n")


def test_every_page_with_code_declares_knitr():
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files()
                 if missing_knitr(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Add `engine: knitr` to the front matter of: " + ", ".join(offenders)


HIDDEN_CHUNK = re.compile(r"```\{(r|python)\}\n#\| include: false\n(.*?)\n```", re.DOTALL)


def test_tidy_page_checks_both_answer_keys_in_both_languages():
    """Spec 8.4: page 1's reference solutions must reproduce the answer keys exactly."""
    chunks = HIDDEN_CHUNK.findall((ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8"))
    for key in ["abstraction_workbook_tidy.csv", "survey_items_long.csv"]:
        assert any(lang == "r" and key in code and "stopifnot(isTRUE(all.equal(" in code
                   for lang, code in chunks), f"no hidden R check against {key}"
        assert any(lang == "python" and key in code and "assert_frame_equal" in code
                   for lang, code in chunks), f"no hidden Python check against {key}"


def written_pages(*dirs):
    """Pages in these folders that are no longer "(coming soon)" stubs."""
    for d in dirs:
        for path in sorted((ROOT / d).glob("*.qmd")):
            text = path.read_text(encoding="utf-8")
            if "(coming soon)" not in front_matter(text):
                yield f"{d}/{path.name}", text


def test_exercise_solutions_are_executed():
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog"):
        exercises = text[text.index("## Exercises {#exercises}"):]
        assert "```r\n" not in exercises and "```python\n" not in exercises, name


def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog"):
        chunks = HIDDEN_CHUNK.findall(text)
        assert any(lang == "r" and "Prose guard" in code and "stopifnot(" in code
                   for lang, code in chunks), name


def section(text, start, end):
    """The source between two markers (tabset "## R" headers make heading-based cuts unreliable)."""
    i = text.index(start)
    return text[i:text.index(end, i)]


def test_recode_cross_tabs_compare_raw_values_with_the_result():
    text = (ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8")
    check = section(text, "**3. Cross-tab every recode.**", "**4. Range and logic checks.**")
    assert "left_join(" in check and "merge(" in check


def test_tidy_recodes_send_unexpected_codes_to_missing():
    text = (ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8")
    step5 = section(text, "### Step 5: give every column its real type", "## Reshaping a survey export")
    assert step5.count("case_when(") >= 3      # sex, procedure, side
    assert step5.count("np.select(") >= 2      # procedure, side


def test_quartile_guard_reads_what_the_libraries_display():
    text = (ROOT / "foundations" / "02-demographics.qmd").read_text(encoding="utf-8")
    chunks = HIDDEN_CHUNK.findall(text)
    assert any(lang == "r" and "table_body" in code and "1 (0–2)" in code for lang, code in chunks)
    assert any(lang == "python" and "1.0 [0.0,1.8]" in code for lang, code in chunks)


# ---- reticulate: never assign to _ ---------------------------------------
# reticulate decides whether to print a statement's value by looking at Python's
# last value, `_`. Code that assigns `_` itself (`_ = ax.hist(...)`) hides
# reticulate's placeholder, and once `_` holds a plot object every later Python
# output on the page is silently dropped. Name the result instead.

PYTHON_CHUNK = re.compile(r"```\{python[^}]*\}\n(.*?)\n```", re.DOTALL)
ASSIGNMENT_TARGET = re.compile(r"^([^=#\n]*?)(?<![=!<>])=(?!=)", re.MULTILINE)
UNDERSCORE_NAME = re.compile(r"(?<![\w.])_(?!\w)")


def assigns_underscore(text):
    return any(UNDERSCORE_NAME.search(target)
               for code in PYTHON_CHUNK.findall(text)
               for target in ASSIGNMENT_TARGET.findall(code))


def test_rule_catches_underscore_assignments():
    assert assigns_underscore("```{python}\n_ = ax.hist(x)\nplt.show()\n```")
    assert assigns_underscore("```{python}\nstat, _ = f(x)\n```")


def test_rule_allows_named_results_and_keyword_arguments():
    assert not assigns_underscore("```{python}\nqq = stats.probplot(x, plot=ax)\nmax_iter = 5\n```")
    assert not assigns_underscore("```{python}\nax.hist(x, bins=30)\n```")


def test_no_python_chunk_assigns_to_underscore():
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files() if assigns_underscore(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Name the result instead of assigning to _ in: " + ", ".join(offenders)


# ---- catalog sections ------------------------------------------------------

CELL_HEADING = re.compile(r"^## .*\{#([a-z0-9-]+)\}\s*$", re.MULTILINE)
VISIBLE_CHUNK = re.compile(r"```\{(r|python)\}\n(?!#\| include: false)(.*?)\n```", re.DOTALL)


def catalog_sections():
    """(page, anchor, source) for every decision-table section of the written catalog pages."""
    for name, text in written_pages("catalog"):
        marks = list(CELL_HEADING.finditer(text))
        for mark, following in zip(marks, marks[1:] + [None]):
            if mark.group(1) != "exercises":
                yield name, mark.group(1), text[mark.end():following.start() if following else len(text)]


def test_each_catalog_section_loads_its_own_packages_and_data():
    """Readers arrive from the decision table straight at a section and copy its code."""
    for name, anchor, body in catalog_sections():
        first = {}
        for lang, code in VISIBLE_CHUNK.findall(body):
            first.setdefault(lang, code)
        assert "library(" in first["r"] and 'read_csv("data/' in first["r"], f"{name}#{anchor}: first R block"
        assert "import " in first["python"] and 'read_csv("data/' in first["python"], f"{name}#{anchor}: first Python block"


def test_every_catalog_section_checks_r_against_python():
    for name, anchor, body in catalog_sections():
        hidden = HIDDEN_CHUNK.findall(body)
        r_checks = sum(lang == "r" and "check_agree(" in code for lang, code in hidden)
        py_values = sum(lang == "python" and "chk = " in code for lang, code in hidden)
        assert r_checks >= 1 and r_checks == py_values, f"{name}#{anchor}: {r_checks} R checks, {py_values} Python chk"
