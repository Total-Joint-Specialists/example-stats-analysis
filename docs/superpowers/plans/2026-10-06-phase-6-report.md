# Phase 6: Example Study Report (Page 18) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the last stub, `report/18-example-report.qmd`, with a complete mini-study that runs from the raw abstraction workbook to a manuscript's Methods and Results, on the site and as a downloadable Word document.

**Architecture:**
- One page, two output formats. The front matter lists `html` and `docx`; Quarto renders both and links the Word file from the page under "Other Formats".
- The page follows spec §4's eight steps: the research question, tidying the workbook, integrity checks, Table 1, distribution checks, the primary analysis, a survival analysis, then the manuscript.
- Steps 1 to 7, the 🔀 and 💡 boxes and the exercises sit inside `::: {.content-visible when-format="html"}`. The manuscript (Aim, Methods, Results, Table 1, Figure 1) is in both formats, so the `.docx` holds only the manuscript.
- The same building blocks as Phases 2–5:
  - knitr-engine page with R ⟷ Python tabsets
  - hidden `check_agree()` R ⟷ Python checks that read the objects the visible code printed
  - a `# Prose guard` that pins every number in the text, including the manuscript's
  - a data-checksum stamp, and exercise solutions that are executed chunks
- Freeze stores each format separately (`execute-results/html.json` and `docx.json`, `figure-html/` and `figure-docx/`), so CI rebuilds both from `_freeze/` without R.
- Page 18 joins `FREE_FORM_SECTIONS`, so it gets the shared free-form tests. Their reporting-conventions test learns to read a manuscript's `#methods` and `#results` sections as well as Methods/Results blockquotes.
- `tests/site/test_report.py` holds the page-specific tests. It reads the `.docx` with Python's `zipfile`, because CI runs the site tests with only the dev packages.
- `just data` re-renders `report/`.

**Tech Stack:**
- R: readxl, tidyxl and janitor (tidying), gtsummary with `add_difference()` and `as_flex_table()` (Table 1), effectsize (Hedges' g), survival and ggsurvfit (cumulative incidence)
- Python: pandas and openpyxl (tidying), tableone (Table 1), scipy and pingouin (Welch's t test, Hedges' g), lifelines (reverse Kaplan-Meier), statsmodels (`CumIncidenceRight`, `ols`)
- No new packages
- Quarto 1.9.37: the `docx` format, `content-visible`, `code-fold`, cross-references (`@tbl-`, `@fig-`)

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`, especially:
- §4, page 18: the eight steps, and "Rendered to HTML (on the site) and to `.docx` (downloadable)"
- §4, pages 0.2 and 1–3: the reporting conventions, tidying, integrity checks, Table 1 and distribution checks this page reuses
- §5.3 and §5.3a: the messy workbook and its answer key
- §7.2 and §7.4: freeze, and publishing without R
- §8: quality checks

## Global Constraints

- **`engine: knitr` per page.** Every page with code declares `engine: knitr` in its own front matter. Don't add `execute: message: false`; `_quarto.yml` already hides messages.
- **Tabsets:** `::: {.panel-tabset group="language"}`, with `## R` first and `## Python` second.
- **Hidden agreement checks:**
  - A hidden Python chunk sets `chk = {name: float(...)}`.
  - A hidden R chunk then calls `check_agree(list(name = <R value>), reticulate::py$chk)`.
  - Both sides read the objects the visible code made, never a fresh call.
  - Never pass DataFrames, sets or `pd.NA` through `reticulate::py`.
  - A looser `tol` gets its own `check_agree()` call, with a comment saying why.
- **Quiet output:**
  - Chunks that call `library()` add `#| warning: false`. No page may show stderr output.
  - Call janitor and effectsize as `pkg::fun()`.
  - Never assign to `_` in a Python chunk.
  - Print numbers, not objects: no `np.float64(...)` wrappers, and `.to_string()` for Series and tables.
- **Prose guard:** one hidden R chunk headed `# Prose guard`, immediately before the exercises, that `stopifnot()`s every quoted number, including the manuscript's and the exercise answers.
- **Data stamp:** the page has the `<!-- data-checksum: … -->` chunk.
- **Solutions:** exercise solutions are executed `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`.
- **Freeze:** render every changed page and commit its `_freeze/` directory, including `docx.json` and `figure-docx/`, and any new folder under `_freeze/site_libs/`. After a deliberately failed render, delete the leftover `<page>_files/` folder.
- **Reporting conventions:**
  - mean (SD) or median (IQR); n (%); a 95% CI with every estimate
  - p to 3 decimals, with a floor of "p < 0.001"
  - "no clear evidence" or "imprecise", never "similar", "held" or "the same"
- **Synthetic data:** the Word file says on its first page that every patient in it is invented.
- **Branching:** work on branch `phase-6-report`, in a worktree under `.worktrees/phase-6`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **The Word file carries tutorial content.**
   - A forgotten `content-visible` wrapper would put code, steps or exercises in the manuscript.
   - `test_report.py::test_the_word_version_is_the_manuscript_only` checks for them. The Task 1 mutation removes the exercises' wrapper and the test catches it.
   - Word draws each callout's icon as an image, so `test_the_word_version_has_table_1_and_the_revision_figure`, which expects exactly one drawing, catches leaked callouts too.
2. **CI can't rebuild the Word file.**
   - CI has no R. A full render must find `docx.json`, `figure-docx/` and flextable's `_freeze/site_libs/tabwid-1.1.3/`.
   - `test_the_word_version_is_frozen_so_ci_can_rebuild_it_without_r` checks the first two.
   - Task 2 renders the whole site with R out of reach and runs the site tests with only the dev packages, as CI does.
3. **The manuscript's numbers drift from the analysis.**
   - The Methods and Results are static text.
   - The prose guard pins every number, including the R and Python versions in the Methods.
   - `just data` re-renders `report/`, and the freshness test fails if the data change without a re-render.
4. **Two questionnaires compared as if they were one.**
   - THA patients answer HOOS JR, TKA patients KOOS JR.
   - Step 1's ⚠️ box and the Methods say the comparison is of points on each joint's own scale. `test_the_question_is_written_down_before_the_analysis` and `test_the_manuscript_states_the_caveats_and_the_missing_data` pin both.
5. **Missing data handled silently.**
   - The primary analysis is complete-case (93 of 120).
   - Step 3 counts every missing value, the Results give the available numbers per procedure, and exercise 3 shows the 1-year score is missing more often after TKA (p = 0.046).
   - `test_the_manuscript_states_the_caveats_and_the_missing_data` pins the Results sentence.

## Plan rulings (made while prototyping)

- **The study:** "do patients improve as much in the first year after TKA as after THA?"
  - The generator builds in a larger improvement after THA: 42.9 against 34.2 points in the full cohort, and 42.4 against 33.4 in the workbook.
  - The workbook's other variables have no built-in effect worth a primary question; diabetes, for one, has 8 patients.
  - The cost is comparing two questionnaires. The page says so in a ⚠️ box and in the Methods, and names the stronger design (a score every patient completes).
- **The data:**
  - The study is the 120 cases in `data/messy_abstraction_workbook.xlsx`, tidied with page 1's code, condensed into one folded block per language. Hidden chunks check the result against the answer key in both languages (spec §8.4).
  - The workbook has no follow-up, so follow-up comes from `data/cohort.csv`, presented as the joint registry and linked by study ID.
  - Integrity checks confirm that every case is found and that the workbook's red fills agree with the registry's revisions (120 of 120).
- **Table 1** shows SMDs instead of p-values, as page 2 advises for observational cohorts, with Missing rows. The manuscript's copy hides the SMDs' CIs and prints through `as_flex_table()`, which works in both formats.
- **Primary analysis:** Welch's t test on the change, as pre-specified, because the changes are roughly symmetric (skewness −0.19 and 0.23) with 46 and 47 per group.
  - Hedges' g: effectsize's exact small-sample correction and pingouin's approximation differ by 4e-6 with 93 patients. So g gets its own check at `tol = 1e-5`, with a comment and a 🔀 box.
- **Revision:** a cumulative incidence with death as a competing risk, since 18 patients were revised and 18 died first. It is descriptive only: 18 events can't support a comparison, and the page says so.
- **The Word version:**
  - The title and a synthetic-data subtitle go under `format: docx:`.
  - Aim, Methods and Results are level-2 headings. Table 1 and Figure 1 are cross-referenced (`@tbl-baseline`, `@fig-revision`).
  - There's no Discussion: the spec asks for Methods and Results.
  - The site links the file automatically ("Other Formats → MS Word").
- **Tests:**
  - The `.docx` is read with `zipfile` (`docx_xml()`, `docx_text()` in `sitelib.py`), because CI runs the site tests with `uv run --only-group dev`, and python-docx isn't in the dev group.
  - The shared reporting-conventions test also reads `#methods` and `#results` sections, so the manuscript is held to the same conventions as every Methods/Results blockquote.
- **The Methods name R 4.6 and Python 3.13.** The prose guard pins them, so upgrading either stops page 18's render until the sentence is updated. That is intended: a manuscript must state the versions it used.
- **Exercises:**
  1. a rank-based check of the primary result, because 15 THA patients sit at the ceiling
  2. a reviewer's request to adjust for the pre-op score, answered with a regression (page 12)
  3. whether the 1-year score went missing more often after one procedure (Fisher's exact test)

## Reference results (prototype, 2026-10-06, R 4.6.0 / Python 3.13.5 / pandas 3.0.6 / statsmodels 0.15.0 / pingouin 0.7.0 / tableone 0.9.6 / gtsummary 2.6.1)

Page 18 rendered in both formats with every hidden check passing. Full suite:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- pytest `tests/python`: 81 passed
- pytest `tests/site`: 352 passed
- lychee: 0 errors
- a full `quarto render` re-executes nothing
- a full render with R out of reach succeeds, and the site tests then pass with only the dev packages

Mutation checks (each failed as it should):
- Python's t test switched to Student's: `disagree on 't': R = 3.23509648, Python = 3.232682451`
- the R tidying without `"999"` as a missing code: the answer-key check stops the render
- the exercises' `content-visible` wrapper removed: 2 failures in `test_report.py`, on `Exercises` in the Word text and on 4 drawings instead of 1
- `report` dropped from `just data`: `` `just data` must re-render: ['report'] ``

| Step | Numbers |
|---|---|
| Tidy and link | 120 cases × 18 columns; 53 THA, 67 TKA; 18 revised, agreeing with the registry for all 120 |
| Missing | BMI 8, ASA 3, length of stay 3, pre-op score 5, 1-year score 22 |
| Table 1 | women 72% (THA) vs 49% (TKA), SMD 0.47; sleep apnea 0.31; ASA 0.29; pre-op score 48.1 vs 51.0, 0.26 |
| Primary | 93 with both scores (46 THA, 47 TKA); change 42.4 (SD 13.0) vs 33.4 (SD 13.9); difference 9.0 (95% CI 3.5 to 14.6), t = 3.24, df = 90.8, p = 0.002; Hedges' g 0.66 (0.25 to 1.08); at the ceiling 15 (32.6%) vs 7 (14.9%) |
| Revision | median follow-up 6.05 years (IQR 4.16 to 8.27); 18 revisions, 18 deaths; cumulative incidence 3.4% (1.1% to 7.8%) at 2 years, 12.6% (7.0% to 19.8%) at 5 years |
| Exercises | Hodges-Lehmann 9.5 (3.6 to 15.2), p = 0.003; adjusted for pre-op score, TKA −7.4 (−11.9 to −2.9), p = 0.002; change score missing in 7 of 53 THA (13.2%) vs 20 of 67 TKA (29.9%), p = 0.046 |

---

### Task 1: Page 18, the example study report on the site and in Word

**Files:**
- Modify: `report/18-example-report.qmd` (replace the stub)
- Create: `_freeze/report/18-example-report/` and `_freeze/site_libs/tabwid-1.1.3/` (render output; commit both)
- Create: `tests/site/test_report.py`
- Modify: `tests/site/sitelib.py`, `tests/site/test_free_form.py`, `tests/site/test_sources.py`, `Justfile`

**Interfaces:**
- Consumes:
  - `sitelib.py`: `FREE_FORM_SECTIONS`, `load`, `section`, `text_of`, `code_of`, `unreported`, `NO_EVIDENCE_AS_NO_DIFFERENCE`
  - `test_sources.py`: `written_pages`, `hidden_chunks`
  - `data/messy_abstraction_workbook.xlsx`, `data/answer-keys/abstraction_workbook_tidy.csv`, `data/cohort.csv`
  - the anchors it links to: page 1 `#tidying` and `#integrity`, page 2 `#by-group` and `#smd`, page 6 `#unpaired-t` and `#mann-whitney`, page 12 `#multiple-linear-regression`, page 13 `#competing-risks`, page 15 `#planned-comparisons`
- Produces:
  - page 18 anchors `#question`, `#tidy`, `#integrity`, `#table-1`, `#distributions`, `#primary-analysis`, `#survival`, `#manuscript`, `#aim`, `#methods`, `#results` and `#exercises`
  - `_site/report/18-example-report.docx`
  - in `sitelib.py`: `docx_xml(path) -> str` (the body XML) and `docx_text(path) -> str` (one paragraph per line, quotes straightened, non-breaking spaces made plain)
  - `tests/site/test_report.py` with `REPORT` and `WORD`

- [ ] **Step 1: Create the worktree and build the current site**

```bash
git checkout main
git worktree add .worktrees/phase-6 -b phase-6-report main
cd .worktrees/phase-6
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `328 passed`.

- [ ] **Step 2: Write the tests**

In `tests/site/sitelib.py`, replace

```python
import re
from pathlib import Path
```

with

```python
import html
import re
import zipfile
from pathlib import Path
```

replace

```python
    "beyond/17-agreement.html": [
        "reliability-vs-agreement", "icc", "inter-intra-rater", "bland-altman", "kappa", "reporting",
        "exercises"],
}
```

with

```python
    "beyond/17-agreement.html": [
        "reliability-vs-agreement", "icc", "inter-intra-rater", "bland-altman", "kappa", "reporting",
        "exercises"],
    "report/18-example-report.html": [
        "question", "tidy", "integrity", "table-1", "distributions", "primary-analysis", "survival",
        "manuscript", "aim", "methods", "results", "exercises"],
}
```

and replace

```python
def code_of(found):
    """The code shown in a page element, as one string."""
    return " ".join(pre.get_text() for pre in found.select("pre"))
```

with

```python
def code_of(found):
    """The code shown in a page element, as one string."""
    return " ".join(pre.get_text() for pre in found.select("pre"))


def docx_xml(path) -> str:
    """The body of a Word file. A .docx is a zip of XML files, so the site tests need no Word package."""
    with zipfile.ZipFile(path) as docx:
        return docx.read("word/document.xml").decode("utf-8")


def docx_text(path) -> str:
    """The text of a Word file, one paragraph per line (including the paragraphs in table cells),
    with smart quotes straightened and non-breaking spaces ("Table 1") made plain."""
    paragraphs = re.findall(r"<w:p[ >].*?</w:p>", docx_xml(path), re.DOTALL)
    text = "\n".join("".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p)) for p in paragraphs)
    return html.unescape(text).replace("’", "'").replace("\xa0", " ")
```

In `tests/site/test_free_form.py`, replace

```python
"""Free-form pages (spec section 6): the survival and "beyond the table" pages, which have no fixed
section anatomy. Every page in FREE_FORM_SECTIONS gets these checks."""
```

with

```python
"""Free-form pages (spec section 6): the survival, "beyond the table" and example-report pages, which
have no fixed section anatomy. Every page in FREE_FORM_SECTIONS gets these checks."""
```

and replace

```python
    """Methods and Results blockquotes and exercise answers: CIs with effect sizes, and no
    "similar" or "held" where the data only fail to show a difference."""
    quotes = [text_of(q) for q in load(page).select("blockquote")]
    assert any("Methods:" in q and "Results:" in q for q in quotes), f"{page}: no Methods and Results"
    answers = [text_of(p) for p in section(page, "exercises").select("p")]
    for text in quotes + answers:
```

with

```python
    """Methods and Results (blockquotes, or page 18's manuscript sections) and exercise answers: CIs
    with effect sizes, and no "similar" or "held" where the data only fail to show a difference."""
    soup = load(page)
    quotes = [text_of(q) for q in soup.select("blockquote")]
    manuscript = [text_of(p) for anchor in ["methods", "results"] for p in soup.select(f"section#{anchor} p")]
    assert any("Methods:" in q and "Results:" in q for q in quotes) or manuscript, f"{page}: no Methods and Results"
    answers = [text_of(p) for p in section(page, "exercises").select("p")]
    for text in quotes + manuscript + answers:
```

Create `tests/site/test_report.py`:

```python
"""Part 5 · Putting it together: the example study report (spec section 4, page 18), on the site and
as a Word manuscript. tests/site/test_free_form.py checks what every free-form page shares."""

import re

import pytest

from sitelib import ROOT, SITE, code_of, docx_text, docx_xml, load, section, text_of

REPORT = "report/18-example-report.html"
WORD = SITE / "report" / "18-example-report.docx"


# ---- the Word version ------------------------------------------------------------------

def test_the_page_offers_the_word_version(site):
    links = [a["href"] for a in load(REPORT).select(".quarto-alternate-formats a[href]")]
    assert links == ["18-example-report.docx"] and WORD.exists()


def test_the_word_version_is_frozen_so_ci_can_rebuild_it_without_r():
    frozen = ROOT / "_freeze" / "report" / "18-example-report"
    assert (frozen / "execute-results" / "docx.json").exists() and (frozen / "figure-docx").is_dir()


def test_the_word_version_is_the_manuscript_only(site):
    text = docx_text(WORD)
    assert text.startswith("Improvement in joint-specific scores") and "Every patient in this report is invented" in text
    assert re.findall(r"^(Aim|Methods|Results)$", text, re.MULTILINE) == ["Aim", "Methods", "Results"]
    for tutorial in ["library(", "import ", "check_agree", "data-checksum", "Exercises", "Tidy the raw workbook"]:
        assert tutorial not in text, tutorial


def test_the_word_version_has_table_1_and_the_revision_figure(site):
    text = docx_text(WORD)
    assert "(Table 1)" in text and "(Figure 1)" in text
    assert "Age, years" in text and "SMD" in text and "Pre-op score, points" in text
    assert docx_xml(WORD).count("<w:drawing>") == 1


# ---- the steps ---------------------------------------------------------------------------

def test_the_question_is_written_down_before_the_analysis(site):
    text = text_of(section(REPORT, "question"))
    for part in ["Question:", "Primary outcome:", "Primary analysis:", "Secondary outcome:"]:
        assert part in text, part
    assert "Watch out: two questionnaires" in text


STEP_LINKS = {
    "tidy": "foundations/01-tidy-data.html#tidying",
    "integrity": "foundations/01-tidy-data.html#integrity",
    "table-1": "foundations/02-demographics.html#smd",
    "distributions": "foundations/03-distributions.html",
    "primary-analysis": "catalog/06-two-unpaired-groups.html#unpaired-t",
    "survival": "survival/13-kaplan-meier.html#competing-risks",
}


@pytest.mark.parametrize("anchor,target", STEP_LINKS.items())
def test_each_step_links_to_the_page_that_explains_it(site, anchor, target):
    hrefs = [a["href"].removeprefix("../") for a in section(REPORT, anchor).select("a[href]")]
    assert target in hrefs, hrefs


def test_failed_integrity_checks_stop_the_script(site):
    code = code_of(section(REPORT, "integrity"))
    assert code.count("stopifnot(") >= 4 and code.count("assert ") >= 4
    assert "revised_registry" in code   # the workbook's red fills, checked against the registry


def test_table_1_uses_smds_and_shows_missing_values(site):
    code = code_of(section(REPORT, "table-1"))
    assert 'add_difference(test = everything() ~ "smd")' in code and "smd=True" in code
    assert 'missing_text = "Missing"' in code and "missing=True" in code


def test_the_primary_analysis_is_the_one_planned(site):
    code = code_of(section(REPORT, "primary-analysis"))
    assert "t.test(change ~ procedure" in code and "equal_var=False" in code
    assert "hedges_g(" in code and 'eftype="hedges"' in code


def test_revision_is_a_cumulative_incidence_with_death_competing(site):
    code = code_of(section(REPORT, "survival"))
    assert 'labels = c("censored", "revision", "death")' in code and "CumIncidenceRight(" in code
    assert "event_status == 0" in code   # the reverse Kaplan-Meier follow-up


# ---- the manuscript ----------------------------------------------------------------------

def test_the_manuscript_states_the_caveats_and_the_missing_data(site):
    methods = text_of(section(REPORT, "methods"))
    results = text_of(section(REPORT, "results"))
    assert "points on each joint's own scale" in methods and "treating death as a competing risk" in methods
    assert "Both scores were available for 93 patients (77.5%)" in results
```

In `tests/site/test_sources.py`, replace

```python
def test_exercise_solutions_are_executed():
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog", "survival", "beyond"):
        exercises = text[text.index("## Exercises {#exercises}"):]
        assert "```r\n" not in exercises and "```python\n" not in exercises, name
```

with

```python
def test_exercise_solutions_are_executed():
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog", "survival", "beyond", "report"):
        exercises = text[text.index("## Exercises {#exercises}"):]
        assert "```r\n" not in exercises and "```python\n" not in exercises, name
```

replace

```python
def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog", "survival", "beyond"):
        chunks = hidden_chunks(text)
        assert any(lang == "r" and "Prose guard" in code and "stopifnot(" in code
                   for lang, code in chunks), name
```

with

```python
def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog", "survival", "beyond", "report"):
        chunks = hidden_chunks(text)
        assert any(lang == "r" and "Prose guard" in code and "stopifnot(" in code
                   for lang, code in chunks), name
```

replace

```python
def test_free_form_pages_check_r_against_python():
    """Free-form pages have no cell sections, so count the whole page's checks."""
    for name, text in written_pages("survival", "beyond"):
        hidden = hidden_chunks(text)
        r_checks = sum(lang == "r" and "check_agree(" in code for lang, code in hidden)
        py_values = sum(lang == "python" and "chk = " in code for lang, code in hidden)
        assert r_checks >= 5 and r_checks == py_values, f"{name}: {r_checks} R checks, {py_values} Python chk"
```

with

```python
def test_free_form_pages_check_r_against_python():
    """Free-form pages have no cell sections, so count the whole page's checks."""
    for name, text in written_pages("survival", "beyond", "report"):
        hidden = hidden_chunks(text)
        r_checks = sum(lang == "r" and "check_agree(" in code for lang, code in hidden)
        py_values = sum(lang == "python" and "chk = " in code for lang, code in hidden)
        assert r_checks >= 5 and r_checks == py_values, f"{name}: {r_checks} R checks, {py_values} Python chk"
```

and replace

```python
def test_beyond_hidden_checks_reuse_the_printed_results():
    """A hidden check that recomputes its own value can't notice a change in the visible code (Phase 5 review)."""
    for name, text in written_pages("beyond"):
        hidden = "\n".join(code for lang, code in hidden_chunks(text) if "Prose guard" not in code)
        for fresh_call in ["t.test(", "marginal_means(", "1 - 0.95"]:
            assert fresh_call not in hidden, f"{name}: hidden check calls {fresh_call}"
```

with

```python
def test_beyond_hidden_checks_reuse_the_printed_results():
    """A hidden check that recomputes its own value can't notice a change in the visible code (Phase 5 review)."""
    for name, text in written_pages("beyond"):
        hidden = "\n".join(code for lang, code in hidden_chunks(text) if "Prose guard" not in code)
        for fresh_call in ["t.test(", "marginal_means(", "1 - 0.95"]:
            assert fresh_call not in hidden, f"{name}: hidden check calls {fresh_call}"


def test_report_hidden_checks_reuse_the_printed_results():
    text = dict(written_pages("report"))["report/18-example-report.qmd"]
    hidden = "\n".join(code for lang, code in hidden_chunks(text) if "Prose guard" not in code)
    for fresh_call in ["t.test(", "hedges_g(", "quantile(", "tidy_survfit(", "qth_survival_times(", "summarise("]:
        assert fresh_call not in hidden, f"hidden check calls {fresh_call}"
```

- [ ] **Step 3: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `21 failed, 331 passed`:
- 4 in `test_free_form.py`, page 18's written, runs-both-languages, exercises and reporting tests. Its no-warnings, short-outputs and printed-tables tests pass trivially on a stub.
- all 16 tests in `test_report.py`
- `test_sources.py::test_report_hidden_checks_reuse_the_printed_results`, with a `KeyError`: `written_pages()` skips the stub

- [ ] **Step 4: Write the page**

Replace `report/18-example-report.qmd`, which is now the stub

````markdown
---
title: "18 · Example study report (coming soon)"
description: "A complete mini-study from raw workbook to manuscript-style Results."
---

::: {.callout-note .coming-soon}
## Coming soon
This page is being written. Links from the decision table already point at its sections, so they will keep working when the content arrives.
:::
````

with:

````markdown
---
title: "18 · Example study report"
description: "A complete mini-study, from the raw abstraction workbook to a manuscript's Methods and Results, with a Word version to download."
engine: knitr
format:
  html: default
  docx:
    title: "Improvement in joint-specific scores one year after hip and knee replacement: a two-site cohort study"
    subtitle: "Synthetic data for teaching. Every patient in this report is invented."
---

```{r}
#| include: false
source("R/check_agree.R")
```

```{r}
#| echo: false
#| output: asis
# Stamp the data version into the page; tests/site/test_freshness.py checks it.
cat(sprintf("<!-- data-checksum: %s -->", unname(tools::md5sum("data/CHECKSUMS.md5"))))
```

::: {.content-visible when-format="html"}
This page puts the whole site together in one small study, from the messy abstraction workbook to the Methods and Results of a manuscript. Steps 1 to 7 do the work, in R and Python. Step 8 is the manuscript itself, and it's also a Word document: **MS Word**, under "Other Formats" in the right margin. The Word file contains only the manuscript, built from the same code every time the site is rendered.

::: {.callout-note}
## 💡 How this page works
Run the code blocks in order, from the top: later blocks use the packages and data loaded in the first one. Each step links to the page that explains its method.
:::

## 1 · The research question {#question}

Write the question down before you look at the outcome data, together with the primary outcome and the analysis that will answer it. Deciding these after seeing the results makes any p-value meaningless ([page 15](../beyond/15-post-hoc.qmd#planned-comparisons)). For this study:

- **Question:** do patients improve as much in the first year after a total knee replacement (TKA) as after a total hip replacement (THA)?
- **Primary outcome:** the change in the joint-specific score from before surgery to 1 year: HOOS JR after THA, KOOS JR after TKA, each scored 0 to 100, higher is better.
- **Primary analysis:** the difference in mean change between THA and TKA, with its 95% CI, from Welch's t test ([page 6](../catalog/06-two-unpaired-groups.qmd#unpaired-t)), if the changes look roughly symmetric within each group ([page 3](../foundations/03-distributions.qmd)). Otherwise the Mann-Whitney test.
- **Secondary outcome:** revision of any component, as a cumulative incidence with death as a competing risk ([page 13](../survival/13-kaplan-meier.qmd#competing-risks)).

::: {.callout-warning}
## ⚠️ Watch out: two questionnaires
HOOS JR and KOOS JR are different questionnaires. Both run from 0 to 100, but a 10-point gain on one isn't guaranteed to mean the same as a 10-point gain on the other. The comparison is still common in the literature, but say plainly in the Methods that it compares points on each joint's own scale. A stronger design uses a score every patient completes, such as the VR-12 physical component score.
:::

## 2 · Tidy the raw workbook {#tidy}

The data come from the abstraction workbook that [page 1](../foundations/01-tidy-data.qmd#tidying) tidies step by step: 60 cases from each site, with banner rows, merged headers, mixed dates, five spellings of "missing" and revisions marked only by a red fill. The code below is page 1's five steps in one block; open it to see the code, and go back to page 1 for why each step is there.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(readxl)
library(tidyxl)
library(gtsummary)
library(survival)
library(ggsurvfit)

path <- "data/messy_abstraction_workbook.xlsx"
```

```{r}
#| code-fold: true
#| code-summary: "The tidying code from page 1"
# Step 1: read both tabs as text; the group header says pre-op first, then 1 year
read_site <- function(sheet) {
  raw <- read_excel(path, sheet = sheet, skip = 3, col_types = "text", .name_repair = "minimal")
  names(raw) <- str_trim(names(raw))
  names(raw)[names(raw) == "Date"]  <- c("prom_preop_date", "prom_1yr_date")
  names(raw)[names(raw) == "Score"] <- c("prom_preop", "prom_1yr")
  raw |>
    janitor::clean_names() |>
    mutate(site = sheet)
}
raw <- bind_rows(read_site("Site A"), read_site("Site B"))   # stack the tabs by column name

# Steps 2 and 3: drop the totals rows, duplicates and identifiers; one way to say "missing"
missing_codes <- c("N/A", "unk", "-", "999")
step3 <- raw |>
  filter(is.na(pt_name) | pt_name != "TOTAL") |>
  distinct() |>
  select(-pt_name, -mrn, -mua) |>
  mutate(across(everything(), \(x) if_else(x %in% missing_codes, NA, x)))

# Step 4: revisions are marked only by a red fill on the Study ID cell
cells <- xlsx_cells(path)
fills <- xlsx_formats(path)$local$fill$patternFill$fgColor$rgb
revised_ids <- cells |>
  filter(fills[local_format_id] %in% "FFFF9999") |>
  pull(character) |>
  str_trim() |>
  unique()

# Step 5: give every column its real type
parse_messy_date <- function(x, orders = c("mdy", "ymd")) {
  serial <- !is.na(x) & str_detect(x, "^\\d{5}$")
  out <- as.Date(rep(NA, length(x)))
  out[serial]  <- janitor::excel_numeric_to_date(as.numeric(x[serial]))
  out[!serial] <- as.Date(parse_date_time(x[!serial], orders = orders, quiet = TRUE))
  out
}

tidy <- step3 |>
  rename(procedure_text = procedure) |>
  transmute(
    case_id      = str_trim(study_id),
    site,
    surgery_date = parse_messy_date(dos),
    age          = parse_number(age),
    sex          = case_when(str_detect(sex, regex("^f", ignore_case = TRUE)) ~ "Female",
                             str_detect(sex, regex("^m", ignore_case = TRUE)) ~ "Male"),
    bmi          = parse_number(bmi),
    asa          = as.integer(as.roman(str_remove(asa, "^ASA "))),
    diabetes     = as.integer(str_detect(comorbidities, regex("\\bDM\\b", ignore_case = TRUE))),
    hypertension = as.integer(str_detect(comorbidities, regex("\\bHTN\\b", ignore_case = TRUE))),
    sleep_apnea  = as.integer(str_detect(comorbidities, regex("\\bOSA\\b", ignore_case = TRUE))),
    procedure    = case_when(str_detect(procedure_text, regex("TKA|knee", ignore_case = TRUE)) ~ "TKA",
                             str_detect(procedure_text, regex("THA|hip", ignore_case = TRUE)) ~ "THA"),
    side         = case_when(str_detect(procedure_text, "\\b(L|Left)\\b") ~ "L",
                             str_detect(procedure_text, "\\b(R|Right)\\b") ~ "R"),
    los_days     = parse_number(los),
    revised      = as.integer(case_id %in% revised_ids),
    prom_preop_date = parse_messy_date(prom_preop_date),
    prom_preop      = parse_number(prom_preop),
    prom_1yr_date   = parse_messy_date(prom_1yr_date),
    prom_1yr        = parse_number(prom_1yr)
  ) |>
  arrange(site, case_id)

dim(tidy)
```

## Python

```{python}
import re
import numpy as np
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import pingouin as pg
import statsmodels.formula.api as smf
from scipy import stats
from scipy.stats import norm
from tableone import TableOne
from lifelines import KaplanMeierFitter
from lifelines.utils import qth_survival_times
from statsmodels.duration.survfunc import CumIncidenceRight

path = "data/messy_abstraction_workbook.xlsx"
```

```{python}
#| code-fold: true
#| code-summary: "The tidying code from page 1"
# Step 1: read both tabs as text; pandas names the repeated headers "Date.1" and "Score.1"
def read_site(sheet):
    raw = pd.read_excel(path, sheet_name=sheet, header=3, dtype=str)
    names = [str(c).strip() for c in raw.columns]
    pairs = {"Date": "prom_preop_date", "Score": "prom_preop",
             "Date.1": "prom_1yr_date", "Score.1": "prom_1yr"}
    names = [pairs.get(n, n) for n in names]
    raw.columns = [re.sub(r"[^0-9a-z]+", "_", n.lower()).strip("_") for n in names]
    return raw.assign(site=sheet)

raw = pd.concat([read_site("Site A"), read_site("Site B")], ignore_index=True)   # stack by column name

# Steps 2 and 3: drop the totals rows, duplicates and identifiers; one way to say "missing"
step3 = (raw[raw["pt_name"] != "TOTAL"]
         .drop_duplicates()
         .drop(columns=["pt_name", "mrn", "mua"])
         .replace(["N/A", "unk", "-", "999"], pd.NA))

# Step 4: revisions are marked only by a red fill on the Study ID cell
revised_ids = set()
for sheet in openpyxl.load_workbook(path).worksheets:
    for row in sheet.iter_rows(min_row=5):
        for cell in row:
            if cell.fill.fgColor.rgb == "FFFF9999":
                revised_ids.add(str(cell.value).strip())

# Step 5: give every column its real type
def number(text):
    return pd.to_numeric(text.str.extract(r"(\d+\.?\d*)")[0])

asa_roman = {"I": "1", "II": "2", "III": "3", "IV": "4"}
procedure_text = step3["procedure"]

tidy = pd.DataFrame({
    "case_id":      step3["study_id"].str.strip(),
    "site":         step3["site"],
    "surgery_date": pd.to_datetime(step3["dos"], format="mixed"),
    "age":          number(step3["age"]),
    "sex":          step3["sex"].str[0].str.lower().map({"f": "Female", "m": "Male"}),
    "bmi":          number(step3["bmi"]),
    "asa":          pd.to_numeric(step3["asa"].str.replace("ASA ", "").replace(asa_roman)),
    "diabetes":     step3["comorbidities"].str.contains(r"\bDM\b", case=False).astype(int),
    "hypertension": step3["comorbidities"].str.contains(r"\bHTN\b", case=False).astype(int),
    "sleep_apnea":  step3["comorbidities"].str.contains(r"\bOSA\b", case=False).astype(int),
    "procedure":    np.select([procedure_text.str.contains(r"TKA|knee", case=False),
                               procedure_text.str.contains(r"THA|hip", case=False)],
                              ["TKA", "THA"], default=None),
    "side":         np.select([procedure_text.str.contains(r"\b(?:L|Left)\b"),
                               procedure_text.str.contains(r"\b(?:R|Right)\b")],
                              ["L", "R"], default=None),
    "los_days":     number(step3["los"]),
    "revised":      step3["study_id"].str.strip().isin(revised_ids).astype(int),
    "prom_preop_date": pd.to_datetime(step3["prom_preop_date"], format="mixed"),
    "prom_preop":      number(step3["prom_preop"]),
    "prom_1yr_date":   pd.to_datetime(step3["prom_1yr_date"], format="mixed"),
    "prom_1yr":        number(step3["prom_1yr"]),
}).sort_values(["site", "case_id"]).reset_index(drop=True)

print(tidy.shape)
```
:::

```{r}
#| include: false
# Spec 8.4: the tidying must reproduce the answer key exactly, as on page 1.
key <- read_csv("data/answer-keys/abstraction_workbook_tidy.csv", show_col_types = FALSE)
stopifnot(isTRUE(all.equal(as.data.frame(tidy), as.data.frame(key), check.attributes = FALSE)))
```

```{python}
#| include: false
key = pd.read_csv("data/answer-keys/abstraction_workbook_tidy.csv",
                  parse_dates=["surgery_date", "prom_preop_date", "prom_1yr_date"])
pd.testing.assert_frame_equal(tidy, key, check_dtype=False)
```

120 cases, 18 columns. The workbook has no follow-up: it records whether a hip or knee was revised, but not when, and not whether the patient died. Follow-up comes from the joint registry, linked by study ID. In the practice data, `data/cohort.csv` plays the registry. Take only the columns you need from it:

::: {.panel-tabset group="language"}
## R

```{r}
registry <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  select(case_id, followup_years, event_status, revised_registry = revised)

study <- left_join(tidy, registry, by = "case_id")   # keeps every workbook case
nrow(study)
count(study, procedure)
```

## Python

```{python}
registry = (pd.read_csv("data/cohort.csv")[["case_id", "followup_years", "event_status", "revised"]]
            .rename(columns={"revised": "revised_registry"}))

study = tidy.merge(registry, on="case_id", how="left")   # keeps every workbook case
print(len(study))
print(study["procedure"].value_counts().sort_index().to_string())
```
:::

```{python}
#| include: false
chk = {"rows": float(len(study)), "tha": float((study["procedure"] == "THA").sum()),
       "revised": float(study["revised"].sum()), "mean_bmi": float(study["bmi"].mean())}
```

```{r}
#| include: false
check_agree(list(rows = nrow(study), tha = sum(study$procedure == "THA"), revised = sum(study$revised),
                 mean_bmi = mean(study$bmi, na.rm = TRUE)), reticulate::py$chk)
```

53 THAs and 67 TKAs. A left join keeps every workbook case even if the registry has no record of it; the next step checks that none is missing.

## 3 · Check the tidying {#integrity}

Before any analysis, check the tidy data against what you know must be true ([page 1](../foundations/01-tidy-data.qmd#integrity)). Write each check so that it **stops the script** when it fails: a check that only prints something is easy to scroll past.

::: {.panel-tabset group="language"}
## R

```{r}
# One row per case, and the 60 cases per site in the abstraction log
stopifnot(n_distinct(study$case_id) == nrow(study), all(count(study, site)$n == 60))

# Every value inside the range in the data dictionary (data/codebooks/abstraction_workbook_tidy.csv)
in_range <- function(x, low, high) all(is.na(x) | (x >= low & x <= high))
stopifnot(in_range(study$age, 40, 89), in_range(study$bmi, 18, 55), in_range(study$asa, 1, 4),
          in_range(study$los_days, 0, 30), in_range(study$prom_preop, 0, 100), in_range(study$prom_1yr, 0, 100))

# PROM dates inside the protocol's windows: pre-op within 30 days before surgery, 1 year at 10 to 14 months
stopifnot(in_range(as.numeric(study$surgery_date - study$prom_preop_date), 0, 30),
          in_range(as.numeric(study$prom_1yr_date - study$surgery_date), 300, 425))

# Every case found in the registry, and the workbook's red fills agree with its revisions
stopifnot(!anyNA(study$followup_years), all(study$revised == study$revised_registry))

# What's missing: count it now, report it later
n_missing <- colSums(is.na(study))
n_missing[n_missing > 0]
```

## Python

```{python}
# One row per case, and the 60 cases per site in the abstraction log
assert study["case_id"].is_unique and (study["site"].value_counts() == 60).all()

# Every value inside the range in the data dictionary (data/codebooks/abstraction_workbook_tidy.csv)
def in_range(values, low, high):
    return bool(values.dropna().between(low, high).all())

assert in_range(study["age"], 40, 89) and in_range(study["bmi"], 18, 55) and in_range(study["asa"], 1, 4)
assert in_range(study["los_days"], 0, 30) and in_range(study["prom_preop"], 0, 100) and in_range(study["prom_1yr"], 0, 100)

# PROM dates inside the protocol's windows: pre-op within 30 days before surgery, 1 year at 10 to 14 months
assert in_range((study["surgery_date"] - study["prom_preop_date"]).dt.days, 0, 30)
assert in_range((study["prom_1yr_date"] - study["surgery_date"]).dt.days, 300, 425)

# Every case found in the registry, and the workbook's red fills agree with its revisions
assert study["followup_years"].notna().all() and (study["revised"] == study["revised_registry"]).all()

# What's missing: count it now, report it later
n_missing = study.isna().sum()
print(n_missing[n_missing > 0].to_string())
```
:::

```{python}
#| include: false
chk = {"bmi": float(n_missing["bmi"]), "asa": float(n_missing["asa"]), "preop": float(n_missing["prom_preop"]),
       "one_year": float(n_missing["prom_1yr"])}
```

```{r}
#| include: false
check_agree(list(bmi = n_missing[["bmi"]], asa = n_missing[["asa"]], preop = n_missing[["prom_preop"]],
                 one_year = n_missing[["prom_1yr"]]), reticulate::py$chk)
```

Every check passed, so the code ran on. The workbook's red fills match the registry's revisions for all 120 cases. That's a check across two sources, and it would catch a fill the abstractor forgot or a case linked to the wrong registry record. The missing values are what the abstractor couldn't find: 8 BMIs, 3 ASA classes, 3 lengths of stay, 5 pre-op scores and 22 one-year scores. The analysis has to say how it handles them.

## 4 · Table 1 {#table-1}

Table 1 describes the patients before surgery, by procedure ([page 2](../foundations/02-demographics.qmd#by-group)). In an observational study, show **standardized mean differences** (SMDs) instead of p-values ([page 2](../foundations/02-demographics.qmd#smd)): the question is how different the groups are, not whether the difference is "significant". Keep a Missing row for every variable that has missing values.

::: {.panel-tabset group="language"}
## R

```{r}
study <- study |> mutate(asa = factor(asa))   # ASA class is a category

table_one <- study |>
  select(procedure, age, sex, bmi, asa, diabetes, hypertension, sleep_apnea, site, prom_preop) |>
  tbl_summary(
    by           = procedure,
    statistic    = all_continuous() ~ "{mean} ({sd})",
    digits       = all_continuous() ~ 1,
    label        = list(age ~ "Age, years", sex ~ "Sex", bmi ~ "BMI, kg/m²", asa ~ "ASA class",
                        diabetes ~ "Diabetes", hypertension ~ "Hypertension", sleep_apnea ~ "Sleep apnea",
                        site ~ "Site", prom_preop ~ "Pre-op score, points"),
    missing_text = "Missing"
  ) |>
  add_overall() |>
  add_difference(test = everything() ~ "smd") |>
  modify_header(estimate = "**SMD**")
table_one
```

## Python

```{python}
study["asa"] = study["asa"].astype("Int64").astype("string")   # a category; blanks stay missing

labels = {"age": "Age, years", "sex": "Sex", "bmi": "BMI, kg/m²", "asa": "ASA class",
          "diabetes": "Diabetes", "hypertension": "Hypertension", "sleep_apnea": "Sleep apnea",
          "site": "Site", "prom_preop": "Pre-op score, points"}
table_one = TableOne(study, columns=list(labels), groupby="procedure",
                     categorical=["sex", "asa", "diabetes", "hypertension", "sleep_apnea", "site"],
                     smd=True, missing=True, include_null=False, rename=labels)
print(table_one.tabulate(tablefmt="github"))
```
:::

```{python}
#| include: false
smd = table_one.smd_table.iloc[:, 0]
chk = {v: abs(float(smd[v])) for v in labels}
```

```{r}
#| include: false
smd_r <- table_one$table_body |> filter(row_type == "label")
# Continuous SMDs differ in the 3rd decimal: R's smd package divides the variances by n,
# tableone by n - 1 (page 2's R vs Python box).
check_agree(as.list(setNames(abs(smd_r$estimate), smd_r$variable)), reticulate::py$chk, tol = 0.005)
```

The groups differ most in sex: 72% of the THA patients were women against 49% of the TKA patients (SMD 0.47). Sleep apnea (0.31), ASA class (0.29) and the pre-op score (0.26) differ less; an SMD below 0.1 is usually read as a negligible difference. TKA patients started 2.9 points higher on average, which matters for an outcome measured as a change: a group that starts higher has less room to improve.

::: {.callout-tip}
## 🔀 R vs Python: SMDs
The SMDs agree to two decimals. R's smd package divides the variances by *n*, tableone by *n* − 1, so continuous SMDs can differ in the third decimal ([page 2](../foundations/02-demographics.qmd#smd)). The hidden check allows for it.
:::

## 5 · Check the distributions {#distributions}

The primary outcome is the change from the pre-op score to the 1-year score, so it exists only for patients with both. Look at its shape within each group before choosing the test ([page 3](../foundations/03-distributions.qmd)), and count the patients at the top of the scale.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4.5
analysed <- study |>
  mutate(change = prom_1yr - prom_preop) |>   # the primary outcome
  filter(!is.na(change))                      # patients with both scores

ggplot(analysed, aes(change)) +
  geom_histogram(binwidth = 5, boundary = 0) +
  facet_wrap(~ procedure, ncol = 1) +
  labs(x = "Change in score, pre-op to 1 year (points)", y = "Patients")

change_summary <- analysed |>
  group_by(procedure) |>
  summarise(n = n(), mean = mean(change), sd = sd(change), at_ceiling = sum(prom_1yr == 100))
change_summary
```

## Python

```{python}
analysed = study.assign(change=study["prom_1yr"] - study["prom_preop"])   # the primary outcome
analysed = analysed[analysed["change"].notna()]                           # patients with both scores

fig, axes = plt.subplots(2, 1, figsize=(7, 4.5), sharex=True)
for ax, (procedure, rows) in zip(axes, analysed.groupby("procedure")):
    ax.hist(rows["change"], bins=range(0, 80, 5))
    ax.set_title(procedure)
    ax.set_ylabel("Patients")
axes[1].set_xlabel("Change in score, pre-op to 1 year (points)")
plt.tight_layout()
plt.show()

summary = analysed.groupby("procedure").agg(n=("change", "size"), mean=("change", "mean"),
                                            sd=("change", "std"), at_ceiling=("prom_1yr", lambda s: int((s == 100).sum())))
print(summary.round(1).to_string())
```
:::

```{python}
#| include: false
chk = {"n_tha": float(summary.loc["THA", "n"]), "n_tka": float(summary.loc["TKA", "n"]),
       "mean_tha": float(summary.loc["THA", "mean"]), "sd_tka": float(summary.loc["TKA", "sd"]),
       "ceiling_tha": float(summary.loc["THA", "at_ceiling"])}
```

```{r}
#| include: false
check_agree(list(n_tha = change_summary$n[1], n_tka = change_summary$n[2], mean_tha = change_summary$mean[1],
                 sd_tka = change_summary$sd[2], ceiling_tha = change_summary$at_ceiling[1]), reticulate::py$chk)
```

93 of the 120 patients have both scores: 46 THA and 47 TKA. Within each group the changes are roughly symmetric, with no long tail, and each group has more than 30 patients, so Welch's t test fits ([page 3](../foundations/03-distributions.qmd)).

One thing to note for the Discussion: 15 of the 46 THA patients (32.6%) scored the maximum, 100, at 1 year, against 7 of the 47 TKA patients (14.9%). A patient at the ceiling might have improved more if the scale allowed it, so the THA improvement, and the difference between the groups, may be underestimated. Exercise 1 checks the result with a rank-based test.

## 6 · The primary analysis {#primary-analysis}

The pre-specified analysis: Welch's t test on the change, with the mean difference, its 95% CI and Hedges' g ([page 6](../catalog/06-two-unpaired-groups.qmd#unpaired-t)).

::: {.panel-tabset group="language"}
## R

```{r}
primary <- t.test(change ~ procedure, data = analysed)   # Welch's t test is R's default
primary

primary_g <- effectsize::hedges_g(change ~ procedure, data = analysed)
primary_g
```

## Python

```{python}
tha = analysed.loc[analysed["procedure"] == "THA", "change"]
tka = analysed.loc[analysed["procedure"] == "TKA", "change"]

primary = stats.ttest_ind(tha, tka, equal_var=False)   # equal_var=False: Welch's t test
primary_ci = primary.confidence_interval()
print(primary.statistic, primary.df, primary.pvalue)
print(tha.mean() - tka.mean(), primary_ci.low, primary_ci.high)

g = pg.compute_effsize(tha, tka, eftype="hedges")
print(g)
```
:::

```{python}
#| include: false
chk = {"t": float(primary.statistic), "df": float(primary.df), "p": float(primary.pvalue),
       "ci_low": float(primary_ci.low), "ci_high": float(primary_ci.high)}
chk_g = {"g": float(g)}
```

```{r}
#| include: false
check_agree(list(t = unname(primary$statistic), df = unname(primary$parameter), p = primary$p.value,
                 ci_low = primary$conf.int[1], ci_high = primary$conf.int[2]), reticulate::py$chk)
# effectsize corrects g for small samples exactly, pingouin with the usual approximation;
# with 93 patients they differ in the sixth decimal (see the R vs Python box)
check_agree(list(g = primary_g$Hedges_g), reticulate::py$chk_g, tol = 1e-5)
```

Reading it:
- **The difference:** THA patients improved by 42.4 points on average and TKA patients by 33.4, a difference of 9.0 points (95% CI 3.5 to 14.6). R puts THA first because it comes first alphabetically; the Python code subtracts in the same order.
- **p = 0.002:** if the procedures truly made no difference, a gap this large would be rare.
- **Hedges' g = 0.66** (95% CI 0.25 to 1.08): a medium-to-large difference, measured in standard deviations.

::: {.callout-tip}
## 🔀 R vs Python: Hedges' g
Hedges' g is Cohen's d shrunk slightly to correct for small samples. effectsize uses the exact correction, pingouin a close approximation, so with 93 patients they differ in the sixth decimal. pingouin's `compute_esci()` gives a CI by a simpler method than effectsize's; quote R's.
:::

## 7 · Revision: a survival analysis {#survival}

The secondary outcome is revision. First, how long were patients followed? Then, what proportion were revised over time? 18 patients died during follow-up without a revision, so death is a competing risk: the cumulative incidence gives the real proportion revised, where 1 − Kaplan-Meier would overstate it ([page 13](../survival/13-kaplan-meier.qmd#competing-risks)).

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4
study <- study |>
  mutate(status = factor(event_status, levels = c(0, 1, 2),
                         labels = c("censored", "revision", "death")))   # censored must come first
table(study$status)

# median follow-up and IQR: the reverse Kaplan-Meier method
reverse_km <- survfit(Surv(followup_years, event_status == 0) ~ 1, data = study)
follow_up <- quantile(reverse_km, probs = c(0.25, 0.5, 0.75), conf.int = FALSE)
follow_up

# the cumulative incidence of revision, with death as a competing risk
cif <- survfit2(Surv(followup_years, status) ~ 1, data = study, conf.type = "log-log")
revision_rows <- tidy_survfit(cif, times = c(2, 5)) |>
  filter(outcome == "revision") |>
  select(time, estimate, conf.low, conf.high)
revision_rows

revision_plot <- cif |>
  ggcuminc(outcome = "revision") +
  add_confidence_interval() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Cumulative incidence of revision")
revision_plot
```

## Python

```{python}
print(study["event_status"].value_counts().sort_index().to_string())   # 0 = censored, 1 = revision, 2 = death

# median follow-up and IQR: the reverse Kaplan-Meier method
reverse_km = KaplanMeierFitter().fit(study["followup_years"], event_observed=(study["event_status"] == 0))
follow_up = qth_survival_times([0.75, 0.5, 0.25], reverse_km.survival_function_).iloc[:, 0]   # 25th, 50th, 75th percentiles
print(follow_up.to_string())

# the cumulative incidence of revision, with death as a competing risk
cif = CumIncidenceRight(study["followup_years"], study["event_status"])
revision = pd.DataFrame({"cif": cif.cinc[0], "se": cif.cinc_se[0]}, index=cif.times)   # event type 1

z = norm.ppf(0.975)
revision_rows = revision.loc[[revision.index[revision.index <= years][-1] for years in [2, 5]]]   # last step before each time
spread = np.exp(z * revision_rows["se"] / (revision_rows["cif"] * np.log(revision_rows["cif"])))  # the log-log CI, as in R
revision_rows = revision_rows.assign(time=[2, 5], low=revision_rows["cif"] ** (1 / spread),
                                     high=revision_rows["cif"] ** spread)
print(revision_rows[["time", "cif", "low", "high"]].round(3).to_string(index=False))

fig, ax = plt.subplots(figsize=(7, 4))
ax.step(revision.index, revision["cif"], where="post")
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Cumulative incidence of revision")
plt.tight_layout()
plt.show()
```
:::

```{python}
#| include: false
chk = {"q1": float(follow_up.iloc[0]), "median": float(follow_up.iloc[1]), "q3": float(follow_up.iloc[2]),
       "cif_2": float(revision_rows["cif"].iloc[0]), "cif_5": float(revision_rows["cif"].iloc[1]),
       "low_5": float(revision_rows["low"].iloc[1]), "high_5": float(revision_rows["high"].iloc[1])}
```

```{r}
#| include: false
check_agree(list(q1 = follow_up[[1]], median = follow_up[[2]], q3 = follow_up[[3]],
                 cif_2 = revision_rows$estimate[1], cif_5 = revision_rows$estimate[2],
                 low_5 = revision_rows$conf.low[2], high_5 = revision_rows$conf.high[2]),
            reticulate::py$chk)
```

The median follow-up was 6.05 years (IQR 4.16 to 8.27). 18 patients were revised and 18 died without a revision. The cumulative incidence of revision was 3.4% (95% CI 1.1% to 7.8%) at 2 years and 12.6% (95% CI 7.0% to 19.8%) at 5 years. With 18 revisions, the CIs are wide: this cohort can describe revision, not compare it between procedures.

::: {.callout-tip}
## 🔀 R vs Python: the cumulative incidence
R's `survfit()` estimates it whenever the status has three levels. statsmodels' `CumIncidenceRight()` gives the same estimates and their standard errors, but no CI, so the Python code builds R's log-log CI by hand ([page 13](../survival/13-kaplan-meier.qmd#competing-risks)).
:::

## 8 · The manuscript {#manuscript}

Everything from here to the exercises is the manuscript, and it's what the Word version contains. Every number in it comes from the code above, and a hidden check stops the render if the text and the code ever disagree.

::: {.callout-note}
## 💡 What "done" looks like
- The question, outcome and analysis were written down before the analysis ran.
- The tidying is checked, and a failed check stops the script.
- Missing data are counted and reported, not dropped silently.
- Every estimate has a 95% CI, and the Methods name every test.
- The manuscript is rendered from the same file as the analysis, so a change to the data changes every number at once.
:::
:::

## Aim {#aim}

To compare the improvement in joint-specific patient-reported scores from before surgery to 1 year after primary total hip arthroplasty (THA) and total knee arthroplasty (TKA), and to describe the cumulative incidence of revision.

## Methods {#methods}

**Patients and data.** We studied 120 primary THAs and TKAs performed at two sites (60 at each) between January 2015 and November 2024. Patients' characteristics, the procedure and patient-reported scores were abstracted from the medical record into a standard sheet. Follow-up for revision and death came from the joint registry, linked by study ID.

**Outcomes.** The primary outcome was the change in the joint-specific score from before surgery to 1 year: the HOOS JR after THA and the KOOS JR after TKA, each scored from 0 to 100 (higher is better). Because the two are different instruments, the comparison is of points on each joint's own scale. The secondary outcome was revision of any component.

**Statistical analysis.** Continuous variables are reported as mean (SD) and categorical variables as n (%); differences between procedures at baseline are described with standardized mean differences. The change in score was compared between procedures with Welch's t test in patients with both scores, and summarized as the mean difference with its 95% CI and Hedges' g. Median follow-up was estimated with the reverse Kaplan-Meier method. The cumulative incidence of revision was estimated with the Aalen-Johansen method, treating death as a competing risk. Tests were two-sided. Analyses used R 4.6 and Python 3.13.

## Results {#results}

Of the 120 patients, 53 (44.2%) had a THA and 67 (55.8%) a TKA (@tbl-baseline). THA patients were more often women (38 of 53, 71.7%, against 33 of 67, 49.3%; SMD 0.47), and TKA patients started with a pre-op score 2.9 points higher (51.0 against 48.1 points; SMD 0.26).

Both scores were available for 93 patients (77.5%): 46 of 53 after THA (86.8%) and 47 of 67 after TKA (70.1%). The score improved by a mean of 42.4 points (SD 13.0) after THA and 33.4 points (SD 13.9) after TKA, a difference of 9.0 points (95% CI 3.5 to 14.6; Hedges' g 0.66, 95% CI 0.25 to 1.08; p = 0.002). At 1 year, 15 THA patients (32.6%) and 7 TKA patients (14.9%) had the maximum score.

Over a median follow-up of 6.05 years (IQR 4.16 to 8.27), 18 patients had a revision and 18 died without one. The cumulative incidence of revision was 3.4% (95% CI 1.1% to 7.8%) at 2 years and 12.6% (95% CI 7.0% to 19.8%) at 5 years (@fig-revision).

```{r}
#| echo: false
#| label: tbl-baseline
#| tbl-cap: "Patients' characteristics before surgery, by procedure. Mean (SD) or n (%); SMD, standardized mean difference."
table_one |>
  modify_column_hide(columns = conf.low) |>                  # the SMDs' CIs stay in the analysis
  remove_abbreviation("CI = Confidence Interval") |>
  as_flex_table()
```

```{r}
#| echo: false
#| label: fig-revision
#| fig-cap: "Cumulative incidence of revision, with death as a competing risk. The shaded band is the 95% CI."
#| fig-height: 4
revision_plot
```

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
smd_of <- function(v) round(abs(smd_r$estimate[smd_r$variable == v]), 2)
sex_counts <- table(study$procedure, study$sex)
ceiling_counts <- analysed |> group_by(procedure) |> summarise(n = sum(prom_1yr == 100), pct = 100 * mean(prom_1yr == 100))
both_counts <- study |> group_by(procedure) |> summarise(n = n(), both = sum(!is.na(prom_1yr - prom_preop)))
pre_means <- study |> group_by(procedure) |> summarise(mean = mean(prom_preop, na.rm = TRUE))
ancova <- lm(prom_1yr ~ prom_preop + procedure, data = analysed)
ancova_ci <- confint(ancova)["procedureTKA", ]
rank_check <- wilcox.test(change ~ procedure, data = analysed, exact = FALSE, conf.int = TRUE)
missing_test <- fisher.test(table(study$procedure, is.na(study$prom_1yr - study$prom_preop)))
stopifnot(
  nrow(study) == 120, all(table(study$site) == 60), ncol(tidy) == 18,
  format(min(study$surgery_date), "%B %Y") == "January 2015", format(max(study$surgery_date), "%B %Y") == "November 2024",
  as.vector(table(study$procedure)) == c(53, 67), round(100 * 53 / 120, 1) == 44.2, round(100 * 67 / 120, 1) == 55.8,
  n_missing[c("bmi", "asa", "los_days", "prom_preop", "prom_1yr")] == c(8, 3, 3, 5, 22),
  sex_counts["THA", "Female"] == 38, sex_counts["TKA", "Female"] == 33,
  round(100 * 38 / 53, 1) == 71.7, round(100 * 33 / 67, 1) == 49.3, round(100 * 38 / 53) == 72, round(100 * 33 / 67) == 49,
  smd_of("sex") == 0.47, smd_of("sleep_apnea") == 0.31, smd_of("asa") == 0.29, smd_of("prom_preop") == 0.26,
  round(pre_means$mean, 1) == c(48.1, 51.0), round(round(pre_means$mean[2], 1) - round(pre_means$mean[1], 1), 1) == 2.9,
  nrow(analysed) == 93, round(100 * 93 / 120, 1) == 77.5,
  both_counts$both == c(46, 47), round(100 * both_counts$both / both_counts$n, 1) == c(86.8, 70.1),
  round(change_summary$mean, 1) == c(42.4, 33.4), round(change_summary$sd, 1) == c(13.0, 13.9),
  round(diff(rev(primary$estimate)), 1) == 9.0, round(primary$conf.int, 1) == c(3.5, 14.6),
  round(primary$p.value, 3) == 0.002,
  round(primary_g$Hedges_g, 2) == 0.66, round(c(primary_g$CI_low, primary_g$CI_high), 2) == c(0.25, 1.08),
  ceiling_counts$n == c(15, 7), round(ceiling_counts$pct, 1) == c(32.6, 14.9),
  table(study$event_status) == c(84, 18, 18),
  round(unname(follow_up), 2) == c(4.16, 6.05, 8.27),
  round(100 * revision_rows$estimate, 1) == c(3.4, 12.6),
  round(100 * revision_rows$conf.low, 1) == c(1.1, 7.0), round(100 * revision_rows$conf.high, 1) == c(7.8, 19.8),
  R.version$major == "4", startsWith(R.version$minor, "6"),
  reticulate::py_config()$version == "3.13",
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(unname(rank_check$estimate), 1) == 9.5, round(rank_check$conf.int, 1) == c(3.6, 15.2),
  round(rank_check$p.value, 3) == 0.003,
  round(coef(ancova)[["procedureTKA"]], 1) == -7.4, round(ancova_ci, 1) == c(-11.9, -2.9),
  round(summary(ancova)$coefficients["procedureTKA", "Pr(>|t|)"], 3) == 0.002,
  20 + 47 == 67, 7 + 46 == 53, round(100 * c(7 / 53, 20 / 67), 1) == c(13.2, 29.9),
  round(missing_test$p.value, 3) == 0.046
)
```

::: {.content-visible when-format="html"}
## Exercises {#exercises}

The solutions use the packages, data and objects made in the steps above, so run the page from the top first.

**1.** Fifteen THA patients scored the maximum at 1 year. Check the primary result with a test that uses ranks instead of means: the Mann-Whitney test and the Hodges-Lehmann difference ([page 6](../catalog/06-two-unpaired-groups.qmd#mann-whitney)). Does the conclusion change?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
wilcox.test(change ~ procedure, data = analysed, exact = FALSE, conf.int = TRUE)
```

## Python

```{python}
rank_check = stats.mannwhitneyu(tha, tka, alternative="two-sided", method="asymptotic", use_continuity=True)
print(rank_check.statistic, rank_check.pvalue)
print(np.median(np.subtract.outer(tha.to_numpy(), tka.to_numpy())))   # the Hodges-Lehmann difference
```
:::

No: the Hodges-Lehmann difference is 9.5 points (95% CI 3.6 to 15.2), p = 0.003, close to the 9.0 points from the t test. Python gives the same estimate and p-value; its CI needs a bootstrap ([page 6](../catalog/06-two-unpaired-groups.qmd#mann-whitney)).
:::

**2.** A reviewer writes: "TKA patients started with higher scores, so they had less room to improve. Adjust for the pre-op score." Which analysis answers this, and what does it show?

::: {.callout-tip collapse="true"}
## Solution

Regress the 1-year score on the procedure and the pre-op score ([page 12](../catalog/12-predict-from-several.qmd#multiple-linear-regression)). The procedure's coefficient is the difference at 1 year between patients who started with the same score.

::: {.panel-tabset group="language"}
## R

```{r}
adjusted <- lm(prom_1yr ~ prom_preop + procedure, data = analysed)
summary(adjusted)$coefficients
confint(adjusted)
```

## Python

```{python}
adjusted = smf.ols("prom_1yr ~ prom_preop + procedure", data=analysed).fit()
print(adjusted.params.round(3).to_string())
print(adjusted.conf_int().round(3).to_string())
```
:::

For the same pre-op score, TKA patients scored 7.4 points lower at 1 year than THA patients (95% CI 2.9 to 11.9; p = 0.002). The difference shrinks a little from the unadjusted 9.0 points but doesn't go away, so the higher starting point explains only part of it.
:::

**3.** 27 patients have no change score. Did the 1-year score go missing more often after one procedure? Test it and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
no_change_score <- is.na(study$prom_1yr - study$prom_preop)
table(study$procedure, no_change_score)
fisher.test(table(study$procedure, no_change_score))$p.value
```

## Python

```{python}
no_change_score = (study["prom_1yr"] - study["prom_preop"]).isna().rename("no_change_score")
missing_table = pd.crosstab(study["procedure"], no_change_score)
print(missing_table.to_string())
print(stats.fisher_exact(missing_table).pvalue)
```
:::

The change score was missing for 7 of 53 THA patients (13.2%) and 20 of 67 TKA patients (29.9%; Fisher's exact test p = 0.046). If the TKA patients who didn't answer did worse than those who did, the TKA improvement is overestimated; the Discussion should say so.
:::
:::
````

- [ ] **Step 5: Render it and run the tests**

Run:

```bash
quarto render report/18-example-report.qmd
uv run pytest tests/site -q
git status --short
```

Expected:
- The render completes and writes both `_site/report/18-example-report.html` and `_site/report/18-example-report.docx`.
- Then `1 failed, 351 passed`: `test_freshness.py::test_just_data_re_renders_the_pages_that_read_data` fails with `` `just data` must re-render: ['report'] ``.
- `git status` shows the new `_freeze/report/` and `_freeze/site_libs/tabwid-1.1.3/` (flextable's web files: this is the first page to print a flextable on the site).

- [ ] **Step 6: Re-render `report/` in `just data`**

In `Justfile`, replace

```
    # (Rendering a folder always re-runs its code.) Add report when it gains code.
    quarto render foundations
    quarto render catalog
    quarto render survival
    quarto render beyond
```

with

```
    # (Rendering a folder always re-runs its code.)
    quarto render foundations
    quarto render catalog
    quarto render survival
    quarto render beyond
    quarto render report
```

Run: `uv run pytest tests/site -q`

Expected: `352 passed`.

- [ ] **Step 7: Prove the checks bite, then restore**

**(a) The R ⟷ Python check reads the visible code.** In the `#primary-analysis` section's Python block, change `primary = stats.ttest_ind(tha, tka, equal_var=False)` to `equal_var=True`. Run `quarto render report/18-example-report.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 't': R = 3.23509648, Python = 3.232682451`: scipy has switched to Student's t test. Change it back to `equal_var=False` and run `rm -rf report/18-example-report_files`.

**(b) The Word file holds only the manuscript.** Just above `## Exercises {#exercises}`, change `::: {.content-visible when-format="html"}` to `::: {.exercises-wrapper}`. Run:

```bash
quarto render report/18-example-report.qmd
uv run pytest tests/site/test_report.py -q
```

Expected: the render completes, then `2 failed, 14 passed`:
- `test_the_word_version_is_the_manuscript_only` fails on `Exercises`.
- `test_the_word_version_has_table_1_and_the_revision_figure` fails on `4 == 1`: Word draws each Solution callout's icon as an image.

Change the line back to `::: {.content-visible when-format="html"}`, then run:

```bash
quarto render report/18-example-report.qmd
uv run pytest tests/site -q
git diff --stat -- report/18-example-report.qmd
```

Expected: `352 passed`. The diff is the page as written in Step 4, with no trace of either mutation.

- [ ] **Step 8: Commit**

```bash
git add report/18-example-report.qmd _freeze/report/18-example-report _freeze/site_libs/tabwid-1.1.3 \
        tests/site/sitelib.py tests/site/test_free_form.py tests/site/test_report.py tests/site/test_sources.py Justfile
git commit -m "Write page 18, the example study report: workbook to manuscript in R and Python, with a Word version of the manuscript

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Record the Word-output convention and build the site the way CI does

**Files:**
- Modify: `CLAUDE.md`, `tests/python/test_repo_docs.py`

**Interfaces:**
- Consumes: Task 1's page and its `_freeze/` output.

- [ ] **Step 1: Write the failing test**

In `tests/python/test_repo_docs.py`, replace

```python
"Mixed models", "Multiple comparisons"]:
```

with

```python
"Mixed models", "Multiple comparisons", "Word output"]:
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `test_claude_md_states_the_golden_rules` FAILS on `Word output`.

- [ ] **Step 2: Update CLAUDE.md**

After golden rule 19,

```markdown
19. **Multiple comparisons.** Pairwise follow-ups adjust with Holm unless the method adjusts itself (Tukey, Games-Howell); unadjusted pairwise p-values appear only to show what adjusting does. A significant overall test isn't required first (page 15, `#overall-test-first`), and planned comparisons are named in the Methods.
```

add rule 20:

```markdown
20. **Word output.** Page 18 also renders to Word (`docx` under `format:` in its front matter), and the site links the file under "Other Formats". Everything that isn't the manuscript sits inside `::: {.content-visible when-format="html"}`, so the .docx holds only the Aim, Methods, Results, Table 1 and Figure 1. Freeze keeps each format's results separately (`execute-results/docx.json`, `figure-docx/`): commit them, because CI rebuilds the .docx from them without R. Freeze applies only to whole-project renders; `quarto render <page>` always runs the code. `tests/site/test_report.py` reads the .docx with `zipfile`, so the site tests need no Word package.
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `3 passed`.

- [ ] **Step 3: Run everything**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
quarto render
uv run pytest tests/site -q
lychee --offline --include-fragments --no-progress _site
git status --short
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- Python: `81 passed`
- `quarto render` re-executes nothing
- site: `352 passed`
- lychee: `0 Errors`
- `git status` shows only `CLAUDE.md` and `tests/python/test_repo_docs.py`

- [ ] **Step 4: Build the site as CI does, with R out of reach**

CI renders from `_freeze/` on a machine without R, then runs the site tests with only the dev packages. Do the same: put `quarto` alone on the `PATH` and point `QUARTO_R` at nothing, so any attempt to run R fails.

```bash
QBIN=$(mktemp -d) && ln -s "$(command -v quarto)" "$QBIN/quarto"
rm -rf _site
env -i HOME="$HOME" PATH="$QBIN:/usr/bin:/bin" QUARTO_R=/nonexistent/R quarto render
uv run --only-group dev pytest tests/site -q
rm -rf "$QBIN"
```

Expected: the render completes with no error, and then `352 passed`. If the render fails with `Failed to spawn 'Rscript'`, a page's freeze is missing or stale: re-render that page with R and commit its `_freeze/` directory.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md tests/python/test_repo_docs.py
git commit -m "CLAUDE.md: record the Word-output convention (page 18's docx, content-visible, freeze per format)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
