# Phase 2: Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three Part 1 stubs with finished tutorial pages:
- `foundations/01-tidy-data.qmd`: tidy principles, collecting tidy data, tidying the messy workbook and survey export, and integrity checks
- `foundations/02-demographics.qmd`: Table 1, p-values vs SMDs, missing data, export to Word
- `foundations/03-distributions.qmd`: looking at shape, Shapiro-Wilk's limits, choosing a column, and p-values vs effect sizes and CIs

All three pages run in R and Python with hidden agreement checks.

**Architecture:**
- Each page is a knitr-engine Quarto page with R ⟷ Python tabsets.
- Hidden chunks guard correctness in three ways:
  - R vs Python agreement via `check_agree()` and a `chk` dict
  - page 1's tidying must reproduce the answer keys exactly (spec §8.4)
  - a "prose guard" `stopifnot()`s every number quoted in the text
- Exercise solutions are executed chunks inside collapsed callouts.
- Site and source tests pin the structure.

**Tech Stack:**
- R: tidyverse, readxl, tidyxl, janitor (called as `janitor::`), gtsummary, flextable, smd
- Python: pandas, openpyxl, scipy, tableone, python-docx, matplotlib
- Quarto 1.9.37, with a Mermaid flowchart

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md` (§4 pages 1–3, §6 page anatomy, §8 quality checks)

## Global Constraints

- **`engine: knitr` per page.** Every page with code declares `engine: knitr` and `execute:` / `message: false` in its own front matter.
- **Tabsets:** `::: {.panel-tabset group="language"}`, `## R` first, then `## Python`.
- **Hidden agreement checks:**
  - A hidden Python chunk sets `chk = {name: float(...)}`.
  - A hidden R chunk then calls `check_agree(list(name = <R value>), reticulate::py$chk)`.
  - Never pass DataFrames, sets or `pd.NA` through `reticulate::py`.
- **Quiet output:** chunks that call `library()` add `#| warning: false`. No page may show stderr output. Never attach janitor; call `janitor::clean_names()` and `janitor::excel_numeric_to_date()`, because attaching janitor masks `stats::chisq.test()` and `fisher.test()`.
- **Spec §8.4:** page 1's reference tidying must reproduce `data/answer-keys/*.csv` exactly, in **both** languages, inside hidden chunks.
- **Prose guard:** each page has one hidden R chunk, headed `# Prose guard`, immediately before `## Exercises {#exercises}`. It `stopifnot()`s every number the prose quotes.
- **Solutions:** exercise solutions are `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`.
- **Freeze:** render every changed page and commit `_freeze/` (all of it).
- **Reporting conventions** (spec §4 page 0.2): mean (SD) or median (IQR); n (%); p to 3 decimals with a floor of "p < 0.001"; a 95% CI with every estimate.
- **Branching:** work on branch `phase-2-foundations`, in a worktree under `.worktrees/phase-2`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Someone regenerates the data (`just data`), so the numbers quoted in the prose go stale silently.** The prose guard must stop the render. Tests: `tests/site/test_sources.py::test_foundations_pages_guard_the_numbers_in_their_prose` and the mutation steps in Tasks 2–4.
2. **An exercise solution has a typo that never runs.** Solutions must be executed chunks. Test: `test_sources.py::test_foundations_exercise_solutions_are_executed`.
3. **A library update changes a statistical method,** for example tableone switching from Welch's t to ANOVA, or a change in gtsummary's quantile type. The hidden `check_agree()` must stop the render. This is exercised by every render in Tasks 2–4, and the lockfiles pin the versions.
4. **Package start-up messages, warnings, or a masking package leak onto the page.** Test: `tests/site/test_foundations.py::test_page_shows_no_warnings_or_package_messages`.
5. **An RA copies one tidying step on its own,** and it fails because it depends on earlier steps. The page must say to run the steps in order. Test: `test_foundations.py::test_tidy_page_says_to_run_the_steps_in_order`.

## Plan rulings (made while prototyping)

- **Density plots omitted** from page 3. Spec §4 lists "histograms, density plots, QQ plots", but a density plot shows the same shape as the histogram, so the page uses histograms plus QQ plots. A density panel is a one-line addition if wanted.
- **The THA-vs-TKA sex imbalance** (66% vs 50% female, p < 0.001) arose by chance from seed 20261008: sex is generated independently of procedure. Page 2 uses it as the example of why Table 1 p-values mislead, rather than regenerating the data again.
- **Equal-variance ANOVA is not used in Table 1.** tableone 0.10 reports Welch's t test for normal continuous variables, so R uses `t.test` (Welch) to match.
- **Continuous SMDs are checked with `tol = 0.005`.** R's `smd` package divides variances by n, tableone by n − 1. This is documented in the page's 🔀 box.
- **Never attach janitor;** call it as `janitor::`. Attaching it masks `stats::chisq.test()` and `fisher.test()`.

## Reference results (prototype, 2026-10-05, R 4.6.0 / Python 3.13)

Rendering all three pages passed every hidden check. The full suite gave:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 235 ]`
- pytest `tests/python`: 78 passed
- pytest `tests/site`: 47 passed
- lychee: 0 errors

The quoted numbers the prose guards pin include:
- page 1: 126 raw rows, 120 tidy rows
- page 2: THA 66% female vs TKA 50%; |SMD| 0.31 for sex and 0.33 for BMI
- page 3: Shapiro p = 0.001 for age and 0.17 for the first ten 1-year PROMs; BMI difference 1.8 kg/m² (95% CI 0.9 to 2.6)

---

### Task 1: Dependencies and setup checks for Phase 2

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `pyproject.toml`, `uv.lock`, `tests/testthat/test-environment.R`, `getting-started/check_setup.R`, `getting-started/check_setup.py`

**Interfaces:**
- Produces:
  - R packages tidyverse, janitor, tidyxl, gtsummary, flextable and smd, plus their dependencies; cardx is pulled in by gtsummary
  - Python packages scipy, tableone and python-docx (imported as `docx`)
  - Both `check_setup` scripts verify these packages

- [ ] **Step 1: Create the worktree and render the current site**

```bash
git checkout main && git pull
git worktree add .worktrees/phase-2 -b phase-2-foundations main
cd .worktrees/phase-2
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `30 passed` (the site tests need a full `_site/` build).

- [ ] **Step 2: Write the failing checks**

In `tests/testthat/test-environment.R`, replace

```r
  for (m in c("pandas", "numpy", "matplotlib")) {
```

with

```r
  for (m in c("pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx")) {
```

In `getting-started/check_setup.R`, replace

```r
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat")) {
```

with

```r
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat", "tidyverse", "readxl",
             "tidyxl", "gtsummary", "flextable")) {
```

In `getting-started/check_setup.py`, replace

```python
for name in ["pandas", "numpy", "matplotlib"]:
```

with

```python
for name in ["pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx"]:
```

- [ ] **Step 3: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "environment|check_setup")'
uv run pytest tests/python/test_check_setup.py -q
```

Expected:
- R: failures for `scipy`, `tableone` and `docx` (environment), and for `check_setup.R` (no "All good")
- Python: `test_passes_inside_the_project_environment` FAILS

- [ ] **Step 4: Install and lock the packages**

Replace `DESCRIPTION` with:

```
Type: project
Description: R dependencies for the TJS statistics tutorial site. Not a
    package; renv reads this file to decide what to lock.
Imports:
    dplyr,
    flextable,
    gtsummary,
    irr,
    janitor,
    knitr,
    openxlsx2,
    readr,
    readxl,
    reticulate,
    rmarkdown,
    smd,
    survival,
    testthat,
    tibble,
    tidyr,
    tidyverse,
    tidyxl,
    withr
```

Run:

```bash
Rscript -e 'renv::install(c("tidyverse", "janitor", "tidyxl", "gtsummary", "flextable", "smd"), prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
uv add scipy tableone python-docx
python3 -c "import json; d=json.load(open('renv.lock'))['Packages']; print(all(p in d for p in ['tidyverse','janitor','tidyxl','gtsummary','flextable','smd','cardx']))"
```

Expected: `True`. `pyproject.toml` now lists `scipy`, `tableone` and `python-docx`.

- [ ] **Step 5: Run them to verify they pass**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 235 ]`
- Python: `78 passed`

- [ ] **Step 6: Commit**

```bash
git add DESCRIPTION renv.lock pyproject.toml uv.lock tests/testthat/test-environment.R getting-started/check_setup.R getting-started/check_setup.py
git commit -m "Add Phase 2 packages (tidyverse, gtsummary, tableone, scipy, ...) and setup checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Page 1, Tidy data

**Files:**
- Modify: `foundations/01-tidy-data.qmd` (replace the stub)
- Create: `_freeze/foundations/01-tidy-data/` (render output; commit it)
- Test: create `tests/site/test_foundations.py`; append to `tests/site/test_sources.py`

**Interfaces:**
- Consumes:
  - `R/check_agree.R`
  - `data/messy_abstraction_workbook.xlsx`, `data/messy_survey_export.csv`
  - `data/answer-keys/*.csv`
  - `templates/data-collection-template.xlsx`
  - `tests/site/sitelib.py` (`ROOT`, `load`)
- Produces:
  - section anchors `#what-tidy-means`, `#collecting`, `#tidying`, `#reshaping`, `#integrity`, `#exercises`, which page 2 links to
  - `tests/site/test_foundations.py` with a `SECTIONS` dict that Tasks 3–4 extend
  - in `test_sources.py`: `HIDDEN_CHUNK` and `written_foundations()`

- [ ] **Step 1: Write the failing tests**

Create `tests/site/test_foundations.py`:

```python
"""Part 1 · Foundations: the tidy-data, Table 1 and distributions pages."""

import pytest

from sitelib import ROOT, load

SECTIONS = {
    "foundations/01-tidy-data.html": [
        "what-tidy-means", "collecting", "tidying", "reshaping", "integrity", "exercises"],
}


@pytest.mark.parametrize("page,sections", SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in load(page).select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", SECTIONS)
def test_page_runs_code_in_both_languages_and_is_frozen(site, page):
    tabsets = load(page).select("div.panel-tabset")
    executed = [t for t in tabsets if t.select(".cell-output, .cell-output-display")]
    assert len(executed) >= 3
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    noise = [o.get_text()[:80] for o in load(page).select(".cell-output-stderr")]
    assert noise == []


def test_tidy_page_says_to_run_the_steps_in_order(site):
    assert "Run the steps in order" in load("foundations/01-tidy-data.html").get_text(" ")
```

Append to `tests/site/test_sources.py` (after two blank lines):

```python
HIDDEN_CHUNK = re.compile(r"```\{(r|python)\}\n#\| include: false\n(.*?)\n```", re.DOTALL)


def test_tidy_page_checks_both_answer_keys_in_both_languages():
    """Spec 8.4: page 1's reference solutions must reproduce the answer keys exactly."""
    chunks = HIDDEN_CHUNK.findall((ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8"))
    for key in ["abstraction_workbook_tidy.csv", "survey_items_long.csv"]:
        assert any(lang == "r" and key in code and "stopifnot(isTRUE(all.equal(" in code
                   for lang, code in chunks), f"no hidden R check against {key}"
        assert any(lang == "python" and key in code and "assert_frame_equal" in code
                   for lang, code in chunks), f"no hidden Python check against {key}"


def written_foundations():
    """Foundations pages that are no longer "(coming soon)" stubs."""
    for path in sorted((ROOT / "foundations").glob("*.qmd")):
        text = path.read_text(encoding="utf-8")
        if "(coming soon)" not in front_matter(text):
            yield path.name, text


def test_foundations_exercise_solutions_are_executed():
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_foundations():
        exercises = text[text.index("## Exercises {#exercises}"):]
        assert "```r\n" not in exercises and "```python\n" not in exercises, name


def test_foundations_pages_guard_the_numbers_in_their_prose():
    for name, text in written_foundations():
        chunks = HIDDEN_CHUNK.findall(text)
        assert any(lang == "r" and "Prose guard" in code and "stopifnot(" in code
                   for lang, code in chunks), name
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected:
- `test_page_is_written_with_all_its_sections[...01-tidy-data...]` and the other tidy-page tests FAIL ("still a stub", or missing anchors)
- `test_tidy_page_checks_both_answer_keys_in_both_languages` FAILS ("no hidden R check")

- [ ] **Step 3: Write the page**

Replace `foundations/01-tidy-data.qmd` with:

````markdown
---
title: "1 · Tidy data"
description: "What tidy data is, how to collect it, how to tidy messy spreadsheets, and how to prove nothing changed."
engine: knitr
execute:
  message: false
---

```{r}
#| include: false
source("R/check_agree.R")
```

Most of the time in a research project goes into getting the data into shape, not into the statistics. Mistakes made here are the dangerous kind: the code runs, the tables look fine, and the numbers are wrong. This page shows how to collect data so it arrives clean, how to clean it when it doesn't, and how to prove your cleaning didn't change anything it shouldn't have.

## What tidy data means {#what-tidy-means}

Data are **tidy** when:

1. every **variable** is a column,
2. every **observation** is a row, and
3. every **kind of observational unit** gets its own table.

::: {.callout-note}
## 💡 In plain language
One fact per cell, one patient-thing per row, and never two kinds of rows mixed in one table. A spreadsheet that's easy for a person to read is often hard for a computer to analyze, and the other way round. Statistics software wants the second kind.
:::

Here's a typical untidy PROM sheet: one row per patient, with a column for each visit. The *visit* is a variable, but it's hiding in the column names.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

wide <- tibble(
  case_id = c("C0001", "C0002", "C0003"),
  preop   = c(41.2, 55.0, 38.7),
  `6wk`   = c(60.1, NA,   58.3),
  `1yr`   = c(88.0, 92.4, 79.5)
)
wide

# Tidy: one row per case per visit
long <- wide |>
  pivot_longer(-case_id, names_to = "visit", values_to = "prom_score")
long
```

## Python

```{python}
import pandas as pd

wide = pd.DataFrame({
    "case_id": ["C0001", "C0002", "C0003"],
    "preop":   [41.2, 55.0, 38.7],
    "6wk":     [60.1, None, 58.3],
    "1yr":     [88.0, 92.4, 79.5],
})
print(wide)

# Tidy: one row per case per visit
long = wide.melt(id_vars="case_id", var_name="visit", value_name="prom_score")
print(long)
```
:::

```{python}
#| include: false
chk = {"rows": float(len(long)), "mean": float(long["prom_score"].mean())}
```

```{r}
#| include: false
check_agree(list(rows = nrow(long), mean = mean(long$prom_score, na.rm = TRUE)), reticulate::py$chk)
```

In the long version, "Is the 6-week score missing?" is just a row with a blank, and "average score at each visit" is one line of code. In the wide version, every new visit means a new column and rewritten code.

Untidy patterns we see most often in TJS sheets, and the tidy fix for each:

| You see | Problem | Tidy fix |
|------|------|------|
| `DM, HTN, OSA` in one cell | Several values in one cell | One yes/no column per condition |
| `R TKA` | Two variables in one cell | Separate `side` and `procedure` columns |
| `32.1 kg/m2` | Units typed into a number | A number column; units go in the data dictionary |
| Red-filled cells mean "revised" | Color as data (invisible to software) | A `revised` column |
| `Date`, `Score`, `Date`, `Score` | Repeated columns per visit | Long format: one row per visit |
| `N/A`, `unk`, `-`, `999`, blank | Five ways to say "missing" | One: an empty cell |
| A title row, a totals row | Not data | Delete them; keep notes elsewhere |

## Collecting tidy data {#collecting}

The cheapest cleaning is the cleaning you never have to do. Before anyone abstracts a single chart, write the **data dictionary**: every variable's name, meaning, type, units and allowed values. Then build the collection sheet from the dictionary.

This site includes a template you can copy: [`templates/data-collection-template.xlsx`](https://github.com/Total-Joint-Specialists/example-stats-analysis/raw/main/templates/data-collection-template.xlsx). It has four sheets:

- **README** — the rules below, for whoever does the abstraction.
- **data** — one header row, and dropdowns or range checks on every column except the study ID, so typos can't get in.
- **dictionary** — what each column means.
- **missing_codes** — exactly what to enter when a value isn't in the chart.

The rules the template enforces:

1. One row per procedure, one column per variable, one value per cell.
2. A study ID, never the MRN or name. The MRN-to-study-ID crosswalk lives in a separate, secured file.
3. Categories from dropdowns only (no `F` vs `female`).
4. Numbers only in number columns; units live in the dictionary.
5. Real dates, not text.
6. Missing means: dropdown "Not recorded", or an empty number/date cell.
7. No colors, bold, comments, merged cells, title rows or totals rows.

You can read the dictionary sheet like any other data:

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(readxl)

dictionary <- read_excel("templates/data-collection-template.xlsx", sheet = "dictionary")
dictionary
```

## Python

```{python}
dictionary = pd.read_excel("templates/data-collection-template.xlsx", sheet_name="dictionary")
print(dictionary.to_string())
```
:::

```{python}
#| include: false
chk = {"rows": float(len(dictionary))}
```

```{r}
#| include: false
check_agree(list(rows = nrow(dictionary)), reticulate::py$chk)
```

## Tidying a messy workbook {#tidying}

Real abstraction sheets rarely follow those rules. `data/messy_abstraction_workbook.xlsx` copies the problems we see in TJS sheets. Open it in Excel and look before you run any code:

- two tabs, **Site A** and **Site B**, whose columns don't line up (Site B has an extra `MUA` column in the middle)
- two banner rows and a row of merged group headers above the real header
- a **TOTAL** row at the bottom of each tab
- two `Date` and two `Score` columns (pre-op and 1-year PROMs)
- mixed date formats, units in number cells, Roman-numeral ASA classes, five spellings of "missing"
- revisions marked only by a red fill on the Study ID cell
- duplicated rows

We'll fix it one step at a time. Every step is small enough to check. Run the steps in order: each one starts from the result of the step before.

### Step 1: read both tabs, as text

Read everything as text first. If you let the software guess types, it silently turns `32.1 kg/m2` into a missing value, and you never find out. We'll convert types deliberately in step 5.

::: {.panel-tabset group="language"}
## R

```{r}
path <- "data/messy_abstraction_workbook.xlsx"

read_site <- function(sheet) {
  # skip = 3 jumps over the two banner rows and the group-header row
  raw <- read_excel(path, sheet = sheet, skip = 3, col_types = "text",
                    .name_repair = "minimal")
  names(raw) <- str_trim(names(raw))   # "Study ID " has a trailing space on Site B

  # The two Date/Score pairs: the group header says pre-op first, then 1 year
  names(raw)[names(raw) == "Date"]  <- c("prom_preop_date", "prom_1yr_date")
  names(raw)[names(raw) == "Score"] <- c("prom_preop", "prom_1yr")

  raw |>
    janitor::clean_names() |> # "Pt Name" -> pt_name, "Study ID" -> study_id
    mutate(site = sheet)      # remember which tab each row came from
}

raw <- bind_rows(read_site("Site A"), read_site("Site B"))   # matches columns by name
nrow(raw)
names(raw)
```

## Python

```{python}
import re

path = "data/messy_abstraction_workbook.xlsx"

def read_site(sheet):
    # header=3 uses the 4th row as column names (after banners and group headers)
    raw = pd.read_excel(path, sheet_name=sheet, header=3, dtype=str)
    names = [str(c).strip() for c in raw.columns]   # "Study ID " has a trailing space on Site B

    # pandas renames repeated headers to "Date.1" and "Score.1"
    pairs = {"Date": "prom_preop_date", "Score": "prom_preop",
             "Date.1": "prom_1yr_date", "Score.1": "prom_1yr"}
    names = [pairs.get(n, n) for n in names]

    # "Pt Name" -> pt_name, "Study ID" -> study_id
    raw.columns = [re.sub(r"[^0-9a-z]+", "_", n.lower()).strip("_") for n in names]
    return raw.assign(site=sheet)   # remember which tab each row came from

raw = pd.concat([read_site("Site A"), read_site("Site B")], ignore_index=True)  # matches by name
print(len(raw))
print(list(raw.columns))
```
:::

```{python}
#| include: false
chk = {"rows": float(len(raw))}
```

```{r}
#| include: false
check_agree(list(rows = nrow(raw)), reticulate::py$chk)
```

126 rows: 60 patients per tab, plus 2 duplicates and a totals row in each. Because we stacked the tabs **by column name**, Site B's extra `MUA` column didn't shift anything. Site A rows simply have `mua` missing. Copying cells by position would have put LOS values under the wrong heading.

In R we call `janitor::clean_names()` with the package name in front instead of loading janitor with `library()`. Loading janitor replaces R's own `chisq.test()` and `fisher.test()` with its own versions, which would quietly change results on later pages.

::: {.callout-tip}
## 🔀 R vs Python: the same Excel file, read differently
- **Repeated headers.** R (with `.name_repair = "minimal"`) keeps both `Date` columns as `Date`. pandas renames the second to `Date.1`.
- **Real Excel dates.** Read as text, R gives the Excel serial number (`42010` means 6 Jan 2015). pandas gives `2015-01-06 00:00:00`. Step 5 handles both.
:::

### Step 2: drop rows and columns that aren't data

::: {.panel-tabset group="language"}
## R

```{r}
step2 <- raw |>
  filter(is.na(pt_name) | pt_name != "TOTAL") |>   # the totals rows
  distinct() |>                                      # exact duplicate rows
  select(-pt_name, -mrn, -mua)                       # identifiers, and a column we don't need

nrow(step2)
```

## Python

```{python}
step2 = (raw[raw["pt_name"] != "TOTAL"]           # the totals rows
         .drop_duplicates()                        # exact duplicate rows
         .drop(columns=["pt_name", "mrn", "mua"])) # identifiers, and a column we don't need
print(len(step2))
```
:::

```{python}
#| include: false
chk = {"rows": float(len(step2))}
```

```{r}
#| include: false
check_agree(list(rows = nrow(step2)), reticulate::py$chk)
```

Names and MRNs go as early as possible. Everything after this point works on a study ID only.

### Step 3: one way to say "missing"

::: {.panel-tabset group="language"}
## R

```{r}
missing_codes <- c("N/A", "unk", "-", "999")

step3 <- step2 |>
  mutate(across(everything(), \(x) if_else(x %in% missing_codes, NA, x)))

# How many BMI values are missing now?
sum(is.na(step3$bmi))
```

## Python

```{python}
missing_codes = ["N/A", "unk", "-", "999"]

step3 = step2.replace(missing_codes, pd.NA)

# How many BMI values are missing now?
print(step3["bmi"].isna().sum())
```
:::

```{python}
#| include: false
chk = {"missing_bmi": float(step3["bmi"].isna().sum())}
```

```{r}
#| include: false
check_agree(list(missing_bmi = sum(is.na(step3$bmi))), reticulate::py$chk)
```

::: {.callout-warning}
## ⚠️ Watch out: `999` is only a missing code if your dictionary says so
In this sheet `999` means "missing" in number columns. In another sheet it could be a real value. Write every missing code into the data dictionary *before* collection starts.
:::

### Step 4: recover the color-coded revisions

The sheet marks revised cases only with a red fill on the Study ID cell. Most software reading a spreadsheet can't see colors at all, which is exactly why color must never carry data. Here we have to dig it out.

::: {.panel-tabset group="language"}
## R

```{r}
library(tidyxl)

cells   <- xlsx_cells(path)                                 # one row per spreadsheet cell
fills   <- xlsx_formats(path)$local$fill$patternFill$fgColor$rgb  # fill color of each format

revised_ids <- cells |>
  filter(fills[local_format_id] %in% "FFFF9999") |>         # the red fill
  pull(character) |>
  str_trim() |>
  unique()

length(revised_ids)
```

## Python

```{python}
import openpyxl

workbook = openpyxl.load_workbook(path)

revised_ids = set()
for sheet in workbook.worksheets:
    for row in sheet.iter_rows(min_row=5):        # data starts on row 5
        for cell in row:
            if cell.fill.fgColor.rgb == "FFFF9999":   # the red fill
                revised_ids.add(str(cell.value).strip())

print(len(revised_ids))
```
:::

```{python}
#| include: false
chk = {"revised": float(len(revised_ids))}
```

```{r}
#| include: false
check_agree(list(revised = length(revised_ids)), reticulate::py$chk)
```

The `Notes` column mentions some revisions ("revised 2021 for loosening"), but not all of them. If we had trusted the notes we would have missed cases. Only the colors were complete.

### Step 5: give every column its real type

Now convert each text column into what it really is. One small function handles the mixed date formats.

::: {.panel-tabset group="language"}
## R

```{r}
# Dates arrive as Excel serial numbers ("42010"), "1/13/15", "2015-04-21",
# or "February 10 2015". Handle the serial numbers, then let lubridate try
# month-day-year and year-month-day for the rest.
parse_messy_date <- function(x, orders = c("mdy", "ymd")) {
  serial <- !is.na(x) & str_detect(x, "^\\d{5}$")
  out <- as.Date(rep(NA, length(x)))
  out[serial]  <- janitor::excel_numeric_to_date(as.numeric(x[serial]))
  out[!serial] <- as.Date(parse_date_time(x[!serial], orders = orders, quiet = TRUE))
  out
}

tidy <- step3 |>
  rename(procedure_text = procedure) |>   # keep the raw text until we've split it
  transmute(
    case_id      = str_trim(study_id),
    site,
    surgery_date = parse_messy_date(dos),
    age          = parse_number(age),            # "67 yo"      -> 67
    sex          = if_else(str_to_lower(str_sub(sex, 1, 1)) == "f", "Female", "Male"),
    bmi          = parse_number(bmi),            # "BMI 31.2"   -> 31.2
    asa          = as.integer(as.roman(str_remove(asa, "^ASA "))),  # "II", "ASA 2", "2" -> 2
    diabetes     = as.integer(str_detect(comorbidities, regex("\\bDM\\b", ignore_case = TRUE))),
    hypertension = as.integer(str_detect(comorbidities, regex("\\bHTN\\b", ignore_case = TRUE))),
    sleep_apnea  = as.integer(str_detect(comorbidities, regex("\\bOSA\\b", ignore_case = TRUE))),
    procedure    = if_else(str_detect(procedure_text, regex("TKA|knee", ignore_case = TRUE)), "TKA", "THA"),
    side         = if_else(str_detect(procedure_text, "\\b(L|Left)\\b"), "L", "R"),
    los_days     = parse_number(los),            # "0 (same day)" -> 0
    revised      = as.integer(case_id %in% revised_ids),
    prom_preop_date = parse_messy_date(prom_preop_date),
    prom_preop      = parse_number(prom_preop),
    prom_1yr_date   = parse_messy_date(prom_1yr_date),
    prom_1yr        = parse_number(prom_1yr)
  ) |>
  arrange(site, case_id)

glimpse(tidy)
```

## Python

```{python}
def number(text):
    # The first number in each cell: "67 yo" -> 67, "BMI 31.2" -> 31.2
    return pd.to_numeric(text.str.extract(r"(\d+\.?\d*)")[0])

asa_roman = {"I": "1", "II": "2", "III": "3", "IV": "4"}
procedure_text = step3["procedure"]   # keep the raw text until we've split it

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
    "procedure":    procedure_text.str.contains(r"TKA|knee", case=False).map({True: "TKA", False: "THA"}),
    "side":         procedure_text.str.contains(r"\b(?:L|Left)\b").map({True: "L", False: "R"}),
    "los_days":     number(step3["los"]),
    "revised":      step3["study_id"].str.strip().isin(revised_ids).astype(int),
    "prom_preop_date": pd.to_datetime(step3["prom_preop_date"], format="mixed"),
    "prom_preop":      number(step3["prom_preop"]),
    "prom_1yr_date":   pd.to_datetime(step3["prom_1yr_date"], format="mixed"),
    "prom_1yr":        number(step3["prom_1yr"]),
}).sort_values(["site", "case_id"]).reset_index(drop=True)

tidy.info()
```
:::

```{python}
#| include: false
chk = {"rows": float(len(tidy)), "mean_bmi": float(tidy["bmi"].mean()),
       "revised": float(tidy["revised"].sum()), "tka": float((tidy["procedure"] == "TKA").sum())}
```

```{r}
#| include: false
check_agree(list(rows = nrow(tidy), mean_bmi = mean(tidy$bmi, na.rm = TRUE),
                 revised = sum(tidy$revised), tka = sum(tidy$procedure == "TKA")), reticulate::py$chk)
```

```{r}
#| include: false
# Spec 8.4: the reference solution must reproduce the answer key exactly.
key <- read_csv("data/answer-keys/abstraction_workbook_tidy.csv", show_col_types = FALSE)
stopifnot(isTRUE(all.equal(as.data.frame(tidy), as.data.frame(key), check.attributes = FALSE)))
```

```{python}
#| include: false
key = pd.read_csv("data/answer-keys/abstraction_workbook_tidy.csv",
                  parse_dates=["surgery_date", "prom_preop_date", "prom_1yr_date"])
pd.testing.assert_frame_equal(tidy, key, check_dtype=False)
```

::: {.callout-tip}
## 🔀 R vs Python: dates
R needs a separate step for Excel serial numbers (`janitor::excel_numeric_to_date()`). pandas already turned those cells into date-times, so `pd.to_datetime(..., format="mixed")` handles every format in one go. `"1/13/15"` is read month-first in both: US style, which is what TJS sheets use.
:::

## Reshaping a survey export {#reshaping}

`data/messy_survey_export.csv` is what survey platforms produce: one row per patient, one column per question per visit (`KOOS_Q3_6wk`), and a second header row of question labels. To analyze it we need one row per patient, visit and item.

::: {.panel-tabset group="language"}
## R

```{r}
survey_path <- "data/messy_survey_export.csv"

header <- read_lines(survey_path, n_max = 1) |> str_split_1(",")
wide <- read_csv(survey_path, skip = 2, col_names = header,          # skip both header rows
                 col_types = cols(.default = "c"))

items <- wide |>
  pivot_longer(
    -c(ResponseId, case_id, instrument),
    names_to = c("inst", "item", "visit"),
    names_pattern = "(KOOS|HOOS)_Q(\\d)_(.*)",       # "KOOS_Q3_6wk" -> KOOS, 3, 6wk
    values_to = "response"
  ) |>
  filter(substr(instrument, 1, 4) == inst) |>         # keep each patient's own instrument
  mutate(item = as.integer(item), response = as.integer(response),
         visit_order = match(visit, c("preop", "6wk", "3mo", "1yr"))) |>
  arrange(case_id, visit_order, item) |>
  select(case_id, instrument, visit, item, response)

items
```

## Python

```{python}
survey_path = "data/messy_survey_export.csv"

wide = pd.read_csv(survey_path, skiprows=[1], dtype=str)   # skip the question-label row

items = wide.melt(id_vars=["ResponseId", "case_id", "instrument"],
                  var_name="column", value_name="response")
parts = items["column"].str.extract(r"(?P<inst>KOOS|HOOS)_Q(?P<item>\d)_(?P<visit>.+)")
items = pd.concat([items, parts], axis=1)
items = items[items["instrument"].str[:4] == items["inst"]]   # keep each patient's own instrument

visit_order = {"preop": 0, "6wk": 1, "3mo": 2, "1yr": 3}
items = (items.assign(item=items["item"].astype(int),
                      response=pd.to_numeric(items["response"]),
                      order=items["visit"].map(visit_order))
              .sort_values(["case_id", "order", "item"])
              [["case_id", "instrument", "visit", "item", "response"]]
              .reset_index(drop=True))
print(items)
```
:::

```{python}
#| include: false
chk = {"rows": float(len(items)), "mean": float(items["response"].mean())}
```

```{r}
#| include: false
check_agree(list(rows = nrow(items), mean = mean(items$response, na.rm = TRUE)), reticulate::py$chk)
survey_key <- read_csv("data/answer-keys/survey_items_long.csv", show_col_types = FALSE)
stopifnot(isTRUE(all.equal(as.data.frame(items), as.data.frame(survey_key), check.attributes = FALSE)))
```

```{python}
#| include: false
pd.testing.assert_frame_equal(items, pd.read_csv("data/answer-keys/survey_items_long.csv"),
                              check_dtype=False)
```

A KOOS JR patient now has 7 items × 4 visits = 28 rows. A missed visit still has its rows, with the response blank, so "expected but not answered" stays visible.

## Checking nothing changed {#integrity}

On a real project nobody hands you an answer key. These checks need nothing but the raw sheet and your result. Run them after every cleaning job.

**1. Rows and IDs.** You should have exactly one row per case, and the count should match what you expect.

::: {.panel-tabset group="language"}
## R

```{r}
nrow(tidy)                       # 60 per site
n_distinct(tidy$case_id)         # must equal nrow: no duplicate IDs
count(tidy, site)
```

## Python

```{python}
print(len(tidy))                       # 60 per site
print(tidy["case_id"].nunique())       # must equal len: no duplicate IDs
print(tidy["site"].value_counts())
```
:::

**2. Missing values didn't appear or disappear.** Every missing BMI in the result should trace back to a missing code or blank in the sheet.

::: {.panel-tabset group="language"}
## R

```{r}
missing_in_sheet  <- sum(is.na(step2$bmi) | step2$bmi %in% missing_codes)
missing_in_result <- sum(is.na(tidy$bmi))
c(sheet = missing_in_sheet, result = missing_in_result)
```

## Python

```{python}
missing_in_sheet = (step2["bmi"].isna() | step2["bmi"].isin(missing_codes)).sum()
missing_in_result = tidy["bmi"].isna().sum()
print(missing_in_sheet, missing_in_result)
```
:::

**3. Cross-tab every recode.** Each messy spelling should map to exactly one clean value, and nothing should map to missing by accident.

::: {.panel-tabset group="language"}
## R

```{r}
tibble(raw = step3$sex, clean = if_else(str_to_lower(str_sub(step3$sex, 1, 1)) == "f", "Female", "Male")) |>
  count(raw, clean)
```

## Python

```{python}
recode = pd.DataFrame({"raw": step3["sex"],
                       "clean": step3["sex"].str[0].str.lower().map({"f": "Female", "m": "Male"})})
print(recode.value_counts().sort_index())
```
:::

**4. Range and logic checks.** Values a person can't have, and dates in the wrong order.

::: {.panel-tabset group="language"}
## R

```{r}
tidy |>
  summarise(
    age_out_of_range  = sum(age < 18 | age > 110, na.rm = TRUE),
    bmi_out_of_range  = sum(bmi < 10 | bmi > 80, na.rm = TRUE),
    prom_out_of_range = sum(prom_preop < 0 | prom_preop > 100 | prom_1yr < 0 | prom_1yr > 100, na.rm = TRUE),
    preop_after_surgery = sum(prom_preop_date > surgery_date, na.rm = TRUE),
    one_year_before_surgery = sum(prom_1yr_date < surgery_date, na.rm = TRUE)
  )
```

## Python

```{python}
checks = {
    "age_out_of_range": ((tidy["age"] < 18) | (tidy["age"] > 110)).sum(),
    "bmi_out_of_range": ((tidy["bmi"] < 10) | (tidy["bmi"] > 80)).sum(),
    "prom_out_of_range": ((tidy["prom_preop"] < 0) | (tidy["prom_preop"] > 100) |
                          (tidy["prom_1yr"] < 0) | (tidy["prom_1yr"] > 100)).sum(),
    "preop_after_surgery": (tidy["prom_preop_date"] > tidy["surgery_date"]).sum(),
    "one_year_before_surgery": (tidy["prom_1yr_date"] < tidy["surgery_date"]).sum(),
}
print(pd.Series(checks))
```
:::

All zeros: good.

**5. Spot-check against the sheet.** Pick a few random rows and compare them, by eye, with the workbook.

::: {.panel-tabset group="language"}
## R

```{r}
set.seed(1)
tidy |> slice_sample(n = 3) |> select(case_id, site, surgery_date, age, bmi, procedure, side)
```

## Python

```{python}
print(tidy.sample(n=3, random_state=1)[["case_id", "site", "surgery_date", "age", "bmi", "procedure", "side"]])
```
:::

### What a failing check looks like

Suppose we had parsed the surgery dates day-first (European style) by mistake. Nothing crashes. Two of the checks above catch it: the missing count, and a logic check that every pre-op PROM falls within a month before surgery.

::: {.panel-tabset group="language"}
## R

```{r}
wrong <- parse_messy_date(step3$dos, orders = c("dmy", "ymd"))   # the mistake
preop <- parse_messy_date(step3$prom_preop_date)

outside_window <- function(surgery) {
  days_before <- as.numeric(surgery - preop)
  sum(days_before < 0 | days_before > 31, na.rm = TRUE)
}
c(missing_correct   = sum(is.na(tidy$surgery_date)),
  missing_day_first = sum(is.na(wrong)),
  window_correct    = outside_window(parse_messy_date(step3$dos)),
  window_day_first  = outside_window(wrong))
```

## Python

```{python}
wrong = pd.to_datetime(step3["dos"], format="mixed", dayfirst=True)   # the mistake
preop = pd.to_datetime(step3["prom_preop_date"], format="mixed")

def outside_window(surgery):
    days_before = (surgery - preop).dt.days
    return int(((days_before < 0) | (days_before > 31)).sum())

print(pd.Series({
    "missing_correct": tidy["surgery_date"].isna().sum(),
    "missing_day_first": wrong.isna().sum(),
    "window_correct": outside_window(pd.to_datetime(step3["dos"], format="mixed")),
    "window_day_first": outside_window(wrong),
}))
```
:::

With the correct parse, nothing is missing and every pre-op PROM falls in its window. With the day-first parse, R can't read `"1/13/15"` (there's no 13th month), so dates go missing. pandas quietly switches to month-first whenever day-first is impossible, so in Python nothing goes missing at all. In **both** languages, dates like `"3/4/24"` parse "successfully" as 3 April instead of 4 March, and the window check flags every one of them.

::: {.callout-warning}
## ⚠️ Watch out: one check is never enough
The missing-count check caught this bug in R but not in Python. The logic check caught it in both. Run all five checks every time; they catch different mistakes.
:::

### Finally: compare with the answer key

Because this is a teaching dataset, there *is* a known right answer: `data/answer-keys/abstraction_workbook_tidy.csv`. Our result matches it exactly.

::: {.panel-tabset group="language"}
## R

```{r}
answer <- read_csv("data/answer-keys/abstraction_workbook_tidy.csv", show_col_types = FALSE)
all.equal(as.data.frame(tidy), as.data.frame(answer), check.attributes = FALSE)
```

## Python

```{python}
answer = pd.read_csv("data/answer-keys/abstraction_workbook_tidy.csv",
                     parse_dates=["surgery_date", "prom_preop_date", "prom_1yr_date"])
pd.testing.assert_frame_equal(tidy, answer, check_dtype=False)   # silent means identical
print("identical")
```
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
koos_case <- items$case_id[items$instrument == "KOOS JR"][1]
stopifnot(
  nrow(raw) == 126,
  nrow(tidy) == 120,
  all(table(tidy$site) == 60),
  sum(items$case_id == koos_case) == 28
)
```

## Exercises {#exercises}

**1.** Use a cross-tab (check 3) to confirm the ASA recode: every raw spelling should map to one class from 1 to 4.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
tibble(raw = step3$asa,
       clean = as.integer(as.roman(str_remove(step3$asa, "^ASA ")))) |>
  count(raw, clean)
```

## Python

```{python}
asa = pd.DataFrame({"raw": step3["asa"],
                    "clean": pd.to_numeric(step3["asa"].str.replace("ASA ", "").replace(asa_roman))})
print(asa.value_counts(dropna=False).sort_index())
```
:::

`2`, `II` and `ASA 2` all become 2, and the missing codes stay missing.
:::

**2.** A colleague's sheet has one row per patient and the columns `koos_left_preop`, `koos_left_1yr`, `koos_right_preop`, `koos_right_1yr`. Is it tidy? If not, what should one row be?

::: {.callout-tip collapse="true"}
## Solution
Not tidy: *side* and *visit* are hiding in the column names. One row should be one knee at one visit, with columns `patient_id`, `side`, `visit`, `koos`. Reshape it with `pivot_longer()` (R) or `melt()` (Python), splitting each column name into side and visit, as we did for the survey export.
:::

**3.** How many cases have a 1-year PROM recorded but no pre-op PROM? Why would that matter for an analysis of improvement?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
tidy |> filter(!is.na(prom_1yr), is.na(prom_preop)) |> nrow()
```

## Python

```{python}
print(((tidy["prom_1yr"].notna()) & (tidy["prom_preop"].isna())).sum())
```
:::

Those patients have no baseline, so their improvement can't be computed. An analysis of change silently drops them. Report how many, so readers know.
:::
````

- [ ] **Step 4: Render and run the tests**

Run:

```bash
quarto render foundations/01-tidy-data.qmd
uv run pytest tests/site -q
```

Expected:
- The render succeeds. If any hidden check fails, it stops with `check_agree(): …`, a `stopifnot` message, or a pandas `AssertionError`.
- pytest: `38 passed`.

- [ ] **Step 5: Prove the guards bite**

1. In the prose-guard chunk, temporarily change `nrow(raw) == 126` to `nrow(raw) == 127` and run `quarto render foundations/01-tidy-data.qmd`.
   Expected: FAIL with `nrow(raw) == 127 is not TRUE`.
   Change it back.
2. In the R tidying chunk, temporarily change `str_remove(asa, "^ASA ")` to `asa` and render again.
   Expected: FAIL at the hidden answer-key check (`all.equal(...) is not TRUE`), or with a `check_agree()` mismatch.
   Change it back.
3. Render again. Expected: success.

- [ ] **Step 6: Commit**

```bash
git add foundations/01-tidy-data.qmd _freeze tests/site/test_foundations.py tests/site/test_sources.py
git commit -m "Write page 1, Tidy data: principles, collection template, tidying, integrity checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Page 2, Demographics (Table 1)

**Files:**
- Modify: `foundations/02-demographics.qmd` (replace the stub), `tests/site/test_foundations.py` (`SECTIONS`)
- Create: `_freeze/foundations/02-demographics/`

**Interfaces:**
- Consumes:
  - `data/cohort.csv`, `data/answer-keys/abstraction_workbook_tidy.csv`
  - page 1's anchors (it links to page 1); page 3 (it links to page 3)
  - the `catalog/06-two-unpaired-groups.qmd` anchors `#unpaired-t`, `#mann-whitney` and `#fisher-chi-square`
- Produces:
  - anchors `#setup`, `#one-group`, `#which-summary`, `#by-group`, `#smd`, `#missing`, `#export`, `#exercises`
  - `scratch/table1.docx` and `scratch/table1-python.docx`, written when the page renders (git ignores `scratch/`)

- [ ] **Step 1: Write the failing test**

In `tests/site/test_foundations.py`, add this entry to the `SECTIONS` dict, after the tidy-data entry:

```python
    "foundations/02-demographics.html": [
        "setup", "one-group", "which-summary", "by-group", "smd", "missing", "export", "exercises"],
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/site/test_foundations.py -q`
Expected: the four `…02-demographics…` tests FAIL (the page is still a stub).

- [ ] **Step 3: Write the page**

Replace `foundations/02-demographics.qmd` with:

````markdown
---
title: "2 · Demographics (Table 1)"
description: "Build a publication-ready Table 1 for one group or several: choosing summaries, comparing groups, standardized mean differences, missing data, and exporting to Word."
engine: knitr
execute:
  message: false
---

```{r}
#| include: false
source("R/check_agree.R")
```

Almost every clinical paper starts with **Table 1**: who was studied. Reviewers read it first, to decide whether your patients look like theirs and whether your groups were comparable to begin with. This page builds one from scratch.

::: {.callout-note}
## 💡 In plain language
Table 1 *describes* your patients. It doesn't answer your research question. Its job is to let a reader judge who your results apply to, and whether your groups started out alike.
:::

## Load the data and pick the variables {#setup}

We'll describe the practice cohort: 600 primary hip and knee replacements (THA and TKA). Table 1 usually holds the characteristics measured *before* surgery.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(gtsummary)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(asa = factor(asa))   # ASA class is a category, not a number

table1_vars <- c("age", "sex", "bmi", "asa", "diabetes", "smoker", "los_days")

labels <- list(age ~ "Age, years", sex ~ "Sex", bmi ~ "BMI, kg/m²", asa ~ "ASA class",
               diabetes ~ "Diabetes", smoker ~ "Smoking status",
               los_days ~ "Length of stay, days")
```

## Python

```{python}
import pandas as pd
from tableone import TableOne

cohort = pd.read_csv("data/cohort.csv")
cohort["asa"] = cohort["asa"].astype(str)   # ASA class is a category, not a number

table1_vars = ["age", "sex", "bmi", "asa", "diabetes", "smoker", "los_days"]
categorical = ["sex", "asa", "diabetes", "smoker"]

labels = {"age": "Age, years", "sex": "Sex", "bmi": "BMI, kg/m²", "asa": "ASA class",
          "diabetes": "Diabetes", "smoker": "Smoking status",
          "los_days": "Length of stay, days"}
```
:::

::: {.callout-warning}
## ⚠️ Watch out: one row per procedure, not per patient
The cohort has one row per *procedure*. 80 patients had both sides done, so 600 procedures come from 520 patients. Say which one your table counts, for example in a footnote: "600 procedures in 520 patients".
:::

## One group {#one-group}

::: {.panel-tabset group="language"}
## R

```{r}
table_one <- cohort |>
  select(all_of(table1_vars)) |>
  tbl_summary(
    type      = list(los_days ~ "continuous"),          # few distinct values, but still a number
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     los_days ~ "{median} ({p25}–{p75})"),
    label     = labels
  )
table_one
```

## Python

```{python}
table_one = TableOne(
    cohort,
    columns=table1_vars,
    categorical=categorical,
    nonnormal=["los_days"],      # report median [Q1, Q3] instead of mean (SD)
    rename=labels,
)
print(table_one.tabulate(tablefmt="github"))
```
:::

```{python}
#| include: false
chk = {"n": float(len(cohort)), "mean_age": float(cohort["age"].mean()),
       "sd_age": float(cohort["age"].std()), "female": float((cohort["sex"] == "Female").sum()),
       "median_los": float(cohort["los_days"].median())}
```

```{r}
#| include: false
check_agree(list(n = nrow(cohort), mean_age = mean(cohort$age), sd_age = sd(cohort$age),
                 female = sum(cohort$sex == "Female"), median_los = median(cohort$los_days)),
            reticulate::py$chk)
```

::: {.callout-warning}
## ⚠️ Watch out: tell the software what each variable is
Software guesses variable types, and the guesses are often wrong:

- **ASA class** looks like a number, so it gets averaged ("mean ASA 2.4"). It's a category.
- **Length of stay** has only a few distinct values, so gtsummary treats it as a category and lists "0 days, 1 day, 2 days…". It's a count.
- **0/1 columns** such as `diabetes` should show one "yes" row.

Set the type of every variable yourself (`type =` in R, `categorical =` in Python).
:::

## Mean (SD) or median (IQR)? {#which-summary}

- **Roughly symmetric** continuous variables (age, BMI): mean (SD).
- **Skewed or bounded** variables (length of stay, most PROMs): median (IQR). One patient with a 30-day stay drags the mean far more than the median.
- **Categories**: n (%).

How do you know whether a variable is skewed? Look at it: [Distributions & choosing a test](03-distributions.qmd) shows how. Length of stay is strongly right-skewed, which is why it gets a median.

::: {.callout-tip}
## 🔀 R vs Python: quartiles
gtsummary and tableone calculate quartiles slightly differently. gtsummary uses a method that always returns an observed value; tableone interpolates between values. With whole-number data like length of stay you can see the difference: the THA upper quartile is 2 days in R and 1.8 in Python. Neither is wrong. Say in your Methods which software you used.
:::

## Comparing groups {#by-group}

Most studies compare groups. Here: THA vs TKA.

::: {.panel-tabset group="language"}
## R

```{r}
by_procedure <- cohort |>
  select(procedure, all_of(table1_vars)) |>
  tbl_summary(
    by        = procedure,
    type      = list(los_days ~ "continuous"),
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     los_days ~ "{median} ({p25}–{p75})"),
    label     = labels
  ) |>
  add_overall() |>
  add_p(test = list(all_continuous() ~ "t.test",       # Welch's t test
                    los_days ~ "kruskal.test",          # rank-based, for the skewed variable
                    all_categorical() ~ "chisq.test"))  # chi-square
by_procedure
```

## Python

```{python}
by_procedure = TableOne(
    cohort,
    columns=table1_vars,
    categorical=categorical,
    nonnormal=["los_days"],
    groupby="procedure",
    pval=True,               # Welch's t test, Kruskal-Wallis, chi-square
    htest_name=True,         # show which test produced each p-value
    rename=labels,
)
print(by_procedure.tabulate(tablefmt="github"))
```
:::

```{python}
#| include: false
p_values = by_procedure.htest_table["P-Value"]
chk = {v: float(p_values[v]) for v in table1_vars}
```

```{r}
#| include: false
p_r <- by_procedure$table_body |> filter(row_type == "label")
check_agree(as.list(setNames(p_r$p.value, p_r$variable)), reticulate::py$chk)
```

Each p-value comes from a test you'll meet in the catalog: [Welch's t test](../catalog/06-two-unpaired-groups.qmd#unpaired-t) for the symmetric continuous variables, a [rank-based test](../catalog/06-two-unpaired-groups.qmd#mann-whitney) for length of stay (Kruskal-Wallis with two groups is the Mann-Whitney test), and the [chi-square test](../catalog/06-two-unpaired-groups.qmd#fisher-chi-square) for the categories.

## p-values or standardized mean differences? {#smd}

Look at sex in the table above: 66% of THA patients are women against 50% of TKA patients, p < 0.001. Is that a real difference between hip and knee patients?

In this practice dataset we know the answer, because we wrote the program that made it: sex was drawn **completely independently** of procedure. The difference is pure chance. (In real arthroplasty cohorts, TKA patients are usually *more* often female.) That's the first problem with p-values in Table 1: across a long table, chance differences turn up.

The second problem is that a p-value mixes up *how big* a difference is with *how many patients* you have. With 6,000 patients a trivial difference gets p < 0.001. With 30, a large one doesn't.

The **standardized mean difference (SMD)** measures only the size of the imbalance, in standard-deviation units, whatever the sample size. A common rule of thumb: |SMD| below 0.1 is negligible.

::: {.panel-tabset group="language"}
## R

```{r}
balance <- cohort |>
  select(procedure, all_of(table1_vars)) |>
  tbl_summary(
    by        = procedure,
    type      = list(los_days ~ "continuous"),
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     los_days ~ "{median} ({p25}–{p75})"),
    label     = labels
  ) |>
  add_difference(test = everything() ~ "smd")
balance
```

## Python

```{python}
balance = TableOne(
    cohort,
    columns=table1_vars,
    categorical=categorical,
    nonnormal=["los_days"],
    groupby="procedure",
    smd=True,
    rename=labels,
)
print(balance.smd_table)
```
:::

```{python}
#| include: false
smd = balance.smd_table.iloc[:, 0]
chk = {v: abs(float(smd[v])) for v in table1_vars}
```

```{r}
#| include: false
smd_r <- balance$table_body |> filter(row_type == "label")
# Continuous SMDs differ in the 3rd decimal (variance divided by n in R's smd
# package, n - 1 in tableone), documented in the R vs Python box below.
check_agree(as.list(setNames(abs(smd_r$estimate), smd_r$variable)), reticulate::py$chk, tol = 0.005)
```

Sex (SMD 0.31) and BMI (0.33) are the imbalances worth mentioning. The rest are small.

::: {.callout-tip}
## 🔀 R vs Python: SMDs differ slightly
- **Sign.** gtsummary subtracts TKA from THA; tableone subtracts THA from TKA. Report the absolute value, or say which group was subtracted from which.
- **Third decimal.** For continuous variables, R's `smd` package divides the variances by *n*, while tableone divides by *n − 1* (the usual textbook formula). Age comes out as 0.105 in both after rounding, but the raw values differ slightly. Categorical SMDs match exactly.
:::

**Which should you report?**

- **Matched or weighted cohorts** (propensity-score studies, such as TJS's age-80 matched study): SMDs only. The matching made the groups alike on purpose, so a test of "did they differ?" makes no sense.
- **Other observational comparisons**: many journals still expect p-values. Give SMDs alongside, and discuss differences by their size, not their p-value.

## Missing data {#missing}

The tidy version of the messy workbook from [page 1](01-tidy-data.qmd) has a few BMIs, ASA classes and lengths of stay that the abstractor couldn't find. Missing values must show up in Table 1. Never drop them silently.

::: {.panel-tabset group="language"}
## R

```{r}
abstraction <- read_csv("data/answer-keys/abstraction_workbook_tidy.csv", show_col_types = FALSE) |>
  mutate(asa = factor(asa))

abstraction |>
  select(site, age, bmi, asa, los_days) |>
  tbl_summary(by = site, type = list(los_days ~ "continuous"),
              statistic = list(all_continuous() ~ "{mean} ({sd})",
                               los_days ~ "{median} ({p25}–{p75})"),
              missing_text = "Missing")
```

## Python

```{python}
abstraction = pd.read_csv("data/answer-keys/abstraction_workbook_tidy.csv")
abstraction["asa"] = abstraction["asa"].astype("Int64").astype("string")   # a category; blanks stay missing

missing_table = TableOne(abstraction, columns=["age", "bmi", "asa", "los_days"],
                         categorical=["asa"], nonnormal=["los_days"],
                         groupby="site", missing=True,
                         include_null=False)   # count blanks as missing, not as a "None" category
print(missing_table.tabulate(tablefmt="github"))
```
:::

```{python}
#| include: false
chk = {"missing_bmi": float(abstraction["bmi"].isna().sum()),
       "missing_asa": float(abstraction["asa"].isna().sum())}
```

```{r}
#| include: false
check_agree(list(missing_bmi = sum(is.na(abstraction$bmi)),
                 missing_asa = sum(is.na(abstraction$asa))), reticulate::py$chk)
```

R adds a "Missing" row under each variable that has any. Python adds a "Missing" column. Either way, the percentages are of the patients with a value, and the reader can see how many were left out.

## Exporting to Word {#export}

Journals want Table 1 in Word. Save it into your `scratch/` folder (git ignores it), open it, and paste it into the manuscript.

::: {.panel-tabset group="language"}
## R

```{r}
by_procedure |>
  as_flex_table() |>
  flextable::save_as_docx(path = "scratch/table1.docx")
```

## Python

```{python}
from docx import Document

table = by_procedure.tableone.reset_index()
headers = [" ".join(str(part) for part in col if part).strip() for col in table.columns]

doc = Document()
grid = doc.add_table(rows=1, cols=len(headers))
for cell, header in zip(grid.rows[0].cells, headers):
    cell.text = header
for _, row in table.iterrows():
    for cell, value in zip(grid.add_row().cells, row):
        cell.text = "" if pd.isna(value) else str(value)
doc.save("scratch/table1-python.docx")
```
:::

In Word, tidy the formatting to the journal's style: usually no vertical lines, and a footnote that says which statistics are shown ("mean (SD); median (IQR); n (%)") and which tests produced the p-values.

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
pct <- function(x) round(100 * mean(x))
los_tha <- cohort$los_days[cohort$procedure == "THA"]
stopifnot(
  nrow(cohort) == 600, n_distinct(cohort$patient_id) == 520,
  sum(table(cohort$patient_id) == 2) == 80,
  sum(cohort$procedure == "THA") == 270, sum(cohort$procedure == "TKA") == 330,
  pct(cohort$sex[cohort$procedure == "THA"] == "Female") == 66,
  pct(cohort$sex[cohort$procedure == "TKA"] == "Female") == 50,
  round(mean(cohort$age), 1) == 65.5, round(sd(cohort$age), 1) == 9.4,
  sum(cohort$sex == "Female") == 343, pct(cohort$sex == "Female") == 57,
  median(cohort$los_days) == 1,
  all(quantile(cohort$los_days, c(0.25, 0.75), type = 2) == c(0, 1)),
  quantile(los_tha, 0.75, type = 2) == 2,
  round(quantile(los_tha, 0.75, type = 7), 1) == 1.8,
  round(abs(smd_r$estimate[smd_r$variable == "sex"]), 2) == 0.31,
  round(abs(smd_r$estimate[smd_r$variable == "bmi"]), 2) == 0.33
)
```

## Exercises {#exercises}

**1.** Make a Table 1 comparing **Site A with Site B** instead of THA with TKA. Which variable differs most between sites, by SMD?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
cohort |>
  select(site, all_of(table1_vars)) |>
  tbl_summary(by = site, type = list(los_days ~ "continuous"),
              statistic = list(all_continuous() ~ "{mean} ({sd})",
                               los_days ~ "{median} ({p25}–{p75})"),
              label = labels) |>
  add_difference(test = everything() ~ "smd")
```

## Python

```{python}
by_site = TableOne(cohort, columns=table1_vars, categorical=categorical,
                   nonnormal=["los_days"], groupby="site", smd=True, rename=labels)
print(by_site.smd_table)
```
:::

Site was assigned at random in this dataset, so every SMD should be small. If one isn't, it's chance again.
:::

**2.** A fellow is comparing patients aged 80 or older with younger patients, matched on sex, BMI and ASA class. Should the baseline table show p-values or SMDs? Why?

::: {.callout-tip collapse="true"}
## Solution
SMDs. The matching was designed to make the groups alike, so testing whether they differ answers a question nobody asked, and with matched data the p-value mostly reflects sample size. SMDs show how well the matching worked: aim for |SMD| below 0.1 on every matching variable.
:::

**3.** Write the first sentence of the Results describing this cohort, using the reporting conventions from [How to use this site](../getting-started/using-this-site.qmd).

::: {.callout-tip collapse="true"}
## Solution
"We included 600 primary arthroplasties (270 THA and 330 TKA) in 520 patients. Mean age was 65.5 (SD 9.4) years and 343 procedures (57%) were in women. Median length of stay was 1 (IQR 0–1) day."

Check every number against your own table: mean and SD for age, n (%) for sex, median (IQR) for length of stay.
:::
````

- [ ] **Step 4: Render and run the tests**

Run:

```bash
quarto render foundations/02-demographics.qmd
uv run pytest tests/site -q
ls scratch/
```

Expected:
- The render succeeds.
- pytest: `42 passed`.
- `scratch/` contains `table1.docx` and `table1-python.docx`.

- [ ] **Step 5: Prove the guard bites**

In the prose-guard chunk, temporarily change `== "Female") == 66` to `== "Female") == 67` and render.
Expected: FAIL with `… == 67 is not TRUE`.

Change it back and render again. Expected: success.

- [ ] **Step 6: Commit**

```bash
git add foundations/02-demographics.qmd _freeze tests/site/test_foundations.py
git commit -m "Write page 2, Table 1: gtsummary/tableone, p-values vs SMDs, missing data, Word export

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Page 3, Distributions & choosing a test

**Files:**
- Modify: `foundations/03-distributions.qmd` (replace the stub), `tests/site/test_foundations.py` (replace with the final version)
- Create: `_freeze/foundations/03-distributions/`

**Interfaces:**
- Consumes:
  - `data/cohort.csv`, `data/proms_long.csv`
  - catalog anchors `06…#unpaired-t`, `#mann-whitney`, `#fisher-chi-square`, `07…#wilcoxon-signed-rank`, `08…#kruskal-wallis`, `#cox`
- Produces:
  - anchors `#why`, `#look`, `#shapiro`, `#within-groups`, `#robustness`, `#transform`, `#ordinal`, `#paired`, `#flowchart`, `#effect-sizes`, `#exercises`
  - a Mermaid flowchart

- [ ] **Step 1: Write the failing tests**

Replace `tests/site/test_foundations.py` with the final version:

```python
"""Part 1 · Foundations: the tidy-data, Table 1 and distributions pages."""

import pytest

from sitelib import ROOT, load

SECTIONS = {
    "foundations/01-tidy-data.html": [
        "what-tidy-means", "collecting", "tidying", "reshaping", "integrity", "exercises"],
    "foundations/02-demographics.html": [
        "setup", "one-group", "which-summary", "by-group", "smd", "missing", "export", "exercises"],
    "foundations/03-distributions.html": [
        "why", "look", "shapiro", "within-groups", "robustness", "transform", "ordinal",
        "paired", "flowchart", "effect-sizes", "exercises"],
}


@pytest.mark.parametrize("page,sections", SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in load(page).select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", SECTIONS)
def test_page_runs_code_in_both_languages_and_is_frozen(site, page):
    tabsets = load(page).select("div.panel-tabset")
    executed = [t for t in tabsets if t.select(".cell-output, .cell-output-display")]
    assert len(executed) >= 3
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    noise = [o.get_text()[:80] for o in load(page).select(".cell-output-stderr")]
    assert noise == []


def test_distributions_page_has_the_flowchart(site):
    assert load("foundations/03-distributions.html").select_one(".mermaid, pre.mermaid-js") is not None


def test_tidy_page_says_to_run_the_steps_in_order(site):
    assert "Run the steps in order" in load("foundations/01-tidy-data.html").get_text(" ")
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_foundations.py -q`
Expected: the four `…03-distributions…` tests and `test_distributions_page_has_the_flowchart` FAIL.

- [ ] **Step 3: Write the page**

Replace `foundations/03-distributions.qmd` with:

````markdown
---
title: "3 · Distributions & choosing a test"
description: "Check whether data look normal, decide which column of the decision table you're in, and understand p-values, effect sizes and confidence intervals."
engine: knitr
execute:
  message: false
---

```{r}
#| include: false
source("R/check_agree.R")
```

The [decision table](../index.qmd) asks two questions: what's your **goal** (the row), and what **type of data** do you have (the column). This page is about the second question, especially the hardest part of it: is a measurement "Gaussian" (normally distributed) enough for the left-hand column?

## Why the shape of your data matters {#why}

The tests in the first column (t tests, ANOVA, Pearson correlation) compare **means**, and they assume the data within each group follow a roughly bell-shaped, normal distribution. The tests in the second column (Mann-Whitney, Wilcoxon, Kruskal-Wallis, Spearman) work on **ranks**. They make no assumption about the shape.

::: {.callout-note}
## 💡 In plain language
A mean is a fair summary of a bell-shaped pile of numbers. It's a poor summary of a lopsided one: a few very long hospital stays drag the mean far away from what's typical. Tests built on means inherit that problem. Rank-based tests only ask "which values are bigger?", so a few extreme values can't dominate.
:::

## Look first: histograms and QQ plots {#look}

Always plot before you test. Here are three variables from the practice data: age, length of stay, and the 1-year PROM score.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort   <- read_csv("data/cohort.csv", show_col_types = FALSE)
proms    <- read_csv("data/proms_long.csv", show_col_types = FALSE)
one_year <- proms |> filter(visit == "1yr", !is.na(prom_score))

shapes <- bind_rows(
  tibble(variable = "Age, years",           value = cohort$age),
  tibble(variable = "Length of stay, days", value = cohort$los_days),
  tibble(variable = "1-year PROM score",    value = one_year$prom_score)
)

ggplot(shapes, aes(value)) +
  geom_histogram(bins = 30) +
  facet_wrap(~ variable, scales = "free")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
proms = pd.read_csv("data/proms_long.csv")
one_year = proms[(proms["visit"] == "1yr") & proms["prom_score"].notna()]

shapes = {
    "Age, years": cohort["age"],
    "Length of stay, days": cohort["los_days"],
    "1-year PROM score": one_year["prom_score"],
}

fig, axes = plt.subplots(1, 3, figsize=(10, 3))
for ax, (name, values) in zip(axes, shapes.items()):
    ax.hist(values, bins=30)
    ax.set_title(name)
plt.tight_layout()
plt.show()
```
:::

- **Age** is a fairly symmetric bell.
- **Length of stay** piles up at 0 and 1 days and has a long tail to the right: **right-skewed**.
- **1-year PROM** piles up against the top of the scale (100), with a tail to the left: a **ceiling effect**.

A **QQ plot** makes the comparison with a normal distribution easier to see. If the data are normal, the points fall on the straight line.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 3
ggplot(shapes, aes(sample = value)) +
  geom_qq() +
  geom_qq_line() +
  facet_wrap(~ variable, scales = "free")
```

## Python

```{python}
fig, axes = plt.subplots(1, 3, figsize=(10, 3))
for ax, (name, values) in zip(axes, shapes.items()):
    stats.probplot(values, plot=ax)
    ax.set_title(name)
plt.tight_layout()
plt.show()
```
:::

How to read them:

- Points **on the line**: close to normal (age).
- Points **curving up at the right end**: right skew (length of stay). The flat steps are the many ties at 0, 1 and 2 days.
- Points **flattening at the top**: a ceiling (the PROM). Many patients share the maximum score.

A number for lopsidedness is the **skewness**: 0 for a symmetric shape, positive for a tail to the right, negative for a tail to the left.

::: {.panel-tabset group="language"}
## R

```{r}
skewness <- function(x) mean((x - mean(x))^3) / sd(x)^3

c(age      = skewness(cohort$age),
  los      = skewness(cohort$los_days),
  prom_1yr = skewness(one_year$prom_score))
```

## Python

```{python}
def skewness(x):
    return ((x - x.mean()) ** 3).mean() / x.std() ** 3

print(pd.Series({
    "age": skewness(cohort["age"]),
    "los": skewness(cohort["los_days"]),
    "prom_1yr": skewness(one_year["prom_score"]),
}))
```
:::

```{python}
#| include: false
chk = {"age": float(skewness(cohort["age"])), "los": float(skewness(cohort["los_days"])),
       "prom_1yr": float(skewness(one_year["prom_score"]))}
```

```{r}
#| include: false
check_agree(list(age = skewness(cohort$age), los = skewness(cohort$los_days),
                 prom_1yr = skewness(one_year$prom_score)), reticulate::py$chk)
```

::: {.callout-tip}
## 🔀 R vs Python: skewness functions
Packages define skewness in slightly different ways (`scipy.stats.skew()` and the R package `e1071` each use their own formula), so the third decimal can differ between them. We wrote the formula out by hand in both languages so the numbers match exactly.
:::

## Formal tests: Shapiro-Wilk, and why not to trust it alone {#shapiro}

The **Shapiro-Wilk test** asks: "Could these numbers plausibly come from a normal distribution?" A small p-value means "probably not". It's tempting to let it decide: p < 0.05 → rank test, otherwise → t test. That rule fails in both directions.

**It's too sensitive with large samples.** Our 600 ages look like a textbook bell curve, yet:

::: {.panel-tabset group="language"}
## R

```{r}
shapiro.test(cohort$age)
```

## Python

```{python}
print(stats.shapiro(cohort["age"]))
```
:::

p = 0.001: "not normal". With 600 values the test can detect departures far too small to matter. A t test on these ages would be perfectly fine.

**It's too weak with small samples.** Take just the first 10 patients' 1-year PROM scores, from a variable we *know* is skewed with a ceiling:

::: {.panel-tabset group="language"}
## R

```{r}
first_ten <- head(one_year$prom_score, 10)
first_ten
shapiro.test(first_ten)
```

## Python

```{python}
first_ten = one_year["prom_score"].head(10)
print(first_ten.tolist())
print(stats.shapiro(first_ten))
```
:::

```{python}
#| include: false
age_sw = stats.shapiro(cohort["age"])
ten_sw = stats.shapiro(first_ten)
chk = {"age_w": float(age_sw.statistic), "age_p": float(age_sw.pvalue),
       "ten_w": float(ten_sw.statistic), "ten_p": float(ten_sw.pvalue)}
```

```{r}
#| include: false
age_sw <- shapiro.test(cohort$age)
ten_sw <- shapiro.test(first_ten)
check_agree(list(age_w = unname(age_sw$statistic), age_p = age_sw$p.value,
                 ten_w = unname(ten_sw$statistic), ten_p = ten_sw$p.value), reticulate::py$chk)
```

p = 0.17: "no evidence against normality". Ten values simply can't reveal the shape, which is exactly when the shape matters most.

::: {.callout-warning}
## ⚠️ Watch out: don't let one p-value choose your test
Decide from the plots, from what you know about the measurement (a bounded score, a count of days), and from the sample size. Use Shapiro-Wilk as supporting evidence, not as the judge. Then say how you decided in your Methods.
:::

## Check within groups, not the pooled data {#within-groups}

The normality assumption is about the data **within each group** (or, for regression models, the **residuals**: what's left after the model's prediction). Pooling groups with different means can make normal data look non-normal.

BMI is a good example: TKA patients average about 1.8 kg/m² more than THA patients.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 3
shapiro.test(cohort$bmi)                         # pooled: looks borderline

cohort |>
  group_by(procedure) |>
  summarise(shapiro_p = shapiro.test(bmi)$p.value)   # each group on its own

fit <- lm(bmi ~ procedure, data = cohort)        # residual = BMI minus its group's mean
shapiro.test(residuals(fit))

ggplot(tibble(residual = residuals(fit)), aes(sample = residual)) +
  geom_qq() +
  geom_qq_line()
```

## Python

```{python}
print(stats.shapiro(cohort["bmi"]))              # pooled: looks borderline

for procedure, group in cohort.groupby("procedure"):    # each group on its own
    print(procedure, stats.shapiro(group["bmi"]).pvalue)

# residual = BMI minus its group's mean
residuals = cohort["bmi"] - cohort.groupby("procedure")["bmi"].transform("mean")
print(stats.shapiro(residuals))

fig, ax = plt.subplots(figsize=(4, 3))
stats.probplot(residuals, plot=ax)
plt.show()
```
:::

```{python}
#| include: false
chk = {"pooled": float(stats.shapiro(cohort["bmi"]).pvalue),
       "residuals": float(stats.shapiro(residuals).pvalue)}
```

```{r}
#| include: false
check_agree(list(pooled = shapiro.test(cohort$bmi)$p.value,
                 residuals = shapiro.test(residuals(fit))$p.value), reticulate::py$chk)
```

Pooled, BMI gets p = 0.04. Within each procedure, and in the residuals, it looks normal (residuals p = 0.31). The pooled test was reacting to the two groups having different centers, not to a non-normal shape.

## How much does normality matter? {#robustness}

Less than you might think, once groups are reasonably large. Tests on means rely on the **average** being roughly normal, not on every individual value. Thanks to the *central limit theorem*, averages of about 30 or more values are close to normal even when the values themselves are skewed.

A practical guide:

- **About 30 or more per group, moderate skew, no wild outliers:** t tests and ANOVA are fine. With very skewed data, the rank test is still often the better summary.
- **Small groups (under about 15–20), or strong skew, or outliers:** use the rank column.
- **Ordinal scales, or a ceiling or floor:** use the rank column whatever the sample size (below).

::: {.callout-note collapse="true"}
## 🔍 Under the hood: the central limit theorem
If you take many random samples of size *n* from almost any distribution and compute each sample's mean, those means form a distribution that gets closer to normal as *n* grows. Its spread shrinks in proportion to 1/√n. t tests are built on the distribution of the mean, which is why they tolerate non-normal raw data when *n* is large. "About 30" is a rule of thumb, not a law: the more skewed the data, the larger *n* needs to be.
:::

## Skew, ceilings and transformations {#transform}

A common fix for right skew is to analyze the **logarithm** of the values. For length of stay we have to use log(days + 1), because log(0) doesn't exist.

::: {.panel-tabset group="language"}
## R

```{r}
c(skew_raw      = skewness(cohort$los_days),
  skew_log      = skewness(log1p(cohort$los_days)),   # log1p(x) = log(1 + x)
  share_zero    = mean(cohort$los_days == 0),
  ceiling_1yr   = mean(one_year$prom_score == 100))
```

## Python

```{python}
import numpy as np

print(pd.Series({
    "skew_raw": skewness(cohort["los_days"]),
    "skew_log": skewness(np.log1p(cohort["los_days"])),   # log1p(x) = log(1 + x)
    "share_zero": (cohort["los_days"] == 0).mean(),
    "ceiling_1yr": (one_year["prom_score"] == 100).mean(),
}))
```
:::

```{python}
#| include: false
chk = {"skew_log": float(skewness(np.log1p(cohort["los_days"]))),
       "share_zero": float((cohort["los_days"] == 0).mean()),
       "ceiling_1yr": float((one_year["prom_score"] == 100).mean())}
```

```{r}
#| include: false
check_agree(list(skew_log = skewness(log1p(cohort$los_days)),
                 share_zero = mean(cohort$los_days == 0),
                 ceiling_1yr = mean(one_year$prom_score == 100)), reticulate::py$chk)
```

The log helps (skewness falls from about 1.6 to 0.6), but nearly half the stays are 0 days and no transformation can spread out a pile of identical values. Results on a log scale are also harder to explain ("a 0.3 difference in log(days + 1)"). Here the rank-based tests are simpler and more honest.

The same goes for the **ceiling**: 17% of patients score the maximum at 1 year, and no transformation can tell those patients apart. Compare groups with rank-based tests, or report the proportion reaching the ceiling (or a clinically important improvement) as a yes/no outcome.

## Ordinal data always go in the rank column {#ordinal}

**Ordinal** data have an order but no fixed spacing: satisfaction from 1 ("very dissatisfied") to 5 ("very satisfied"), ASA class, pain "none / mild / moderate / severe". The step from 4 to 5 isn't necessarily the same size as the step from 1 to 2, so averages are hard to interpret.

::: {.panel-tabset group="language"}
## R

```{r}
count(cohort, satisfaction_1yr)
```

## Python

```{python}
print(cohort["satisfaction_1yr"].value_counts(dropna=False).sort_index())
```
:::

```{python}
#| include: false
chk = {"very_satisfied": float((cohort["satisfaction_1yr"] == 5).sum()),
       "no_answer": float(cohort["satisfaction_1yr"].isna().sum())}
```

```{r}
#| include: false
check_agree(list(very_satisfied = sum(cohort$satisfaction_1yr == 5, na.rm = TRUE),
                 no_answer = sum(is.na(cohort$satisfaction_1yr))), reticulate::py$chk)
```

Report ordinal data as counts and percentages, or as a median (IQR), and compare groups with rank-based tests. Never compute a t test on Likert scores, however many patients you have.

## Paired or unpaired? Matched or unmatched? {#paired}

The decision table's rows also ask whether your groups are **independent** or **paired/matched**.

- **Unpaired (independent):** different patients in each group. THA vs TKA; Site A vs Site B; men vs women.
- **Paired:** the same patients measured twice, or natural pairs. Pre-op vs 1-year PROM in the same patients; left vs right knee in bilateral patients; two raters measuring the same X-rays.
- **Matched:** each patient in one group has been chosen to resemble a patient in the other group (by age, sex, BMI…). Treat matched sets like pairs.

Pairing matters because measurements on the same patient are related. A paired analysis uses each patient as their own control, which removes the patient-to-patient variation and usually gives a more precise answer. Analyzing paired data as if unpaired is one of the most common mistakes in the literature.

## From your question to a test {#flowchart}

```{mermaid}
flowchart TD
  A[What is your goal?] --> B[Describe one group]
  A --> C[Compare groups or measurements]
  A --> D[Association or prediction]
  C --> E{Same patients or matched?}
  E -->|No| F[Unpaired rows]
  E -->|Yes| G[Paired / matched rows]
  B --> H{What type of outcome?}
  F --> H
  G --> H
  D --> H
  H -->|Measurement, roughly normal within groups| I[Gaussian column]
  H -->|Skewed, bounded, ordinal, or small groups| J[Rank column]
  H -->|Yes / no| K[Binomial column]
  H -->|Time until an event| L[Survival column]
```

Then find your row and column in the [decision table](../index.qmd). Some worked examples from TJS-style questions:

| Question | Row | Column | Test |
|------|------|------|------|
| Do TKA patients have a higher BMI than THA patients? | Two unpaired groups | Gaussian | [Unpaired t test](../catalog/06-two-unpaired-groups.qmd#unpaired-t) |
| Is length of stay different between Site A and Site B? | Two unpaired groups | Rank (skewed) | [Mann-Whitney test](../catalog/06-two-unpaired-groups.qmd#mann-whitney) |
| Did KOOS JR improve from pre-op to 1 year? | Two paired groups | Rank (ceiling) | [Wilcoxon signed-rank test](../catalog/07-two-paired-groups.qmd#wilcoxon-signed-rank) |
| Is 90-day readmission more common in men? | Two unpaired groups | Binomial | [Fisher's exact test](../catalog/06-two-unpaired-groups.qmd#fisher-chi-square) |
| Does satisfaction differ between surgeons S1, S2 and S3? | Three or more unmatched groups | Rank (ordinal) | [Kruskal-Wallis test](../catalog/08-three-plus-unmatched.qmd#kruskal-wallis) |
| Does implant design affect revision-free survival? | Three or more unmatched groups | Survival | [Cox regression](../catalog/08-three-plus-unmatched.qmd#cox) |

## p-values, effect sizes and confidence intervals {#effect-sizes}

Every test on this site reports three things. They answer different questions, and a good Results section gives all three.

- The **effect size** answers *how big?* For example, the difference between two means.
- The **95% confidence interval (CI)** answers *how sure are we about that size?* It's the range of effect sizes compatible with the data.
- The **p-value** answers *how surprising would data like these be if there were really no difference at all?* It doesn't measure the size or importance of an effect.

Here's all three for BMI in TKA vs THA, using the unpaired (Welch's) t test from [page 6](../catalog/06-two-unpaired-groups.qmd#unpaired-t):

::: {.panel-tabset group="language"}
## R

```{r}
bmi_test <- t.test(bmi ~ procedure, data = cohort)   # Welch's t test (R's default)
bmi_test

difference <- unname(bmi_test$estimate[2] - bmi_test$estimate[1])   # TKA minus THA
ci <- -rev(bmi_test$conf.int)                                        # flip to TKA minus THA
tibble(difference = difference, ci_low = ci[1], ci_high = ci[2], p = bmi_test$p.value)
```

## Python

```{python}
tka = cohort.loc[cohort["procedure"] == "TKA", "bmi"]
tha = cohort.loc[cohort["procedure"] == "THA", "bmi"]

bmi_test = stats.ttest_ind(tka, tha, equal_var=False)   # Welch's t test
ci = bmi_test.confidence_interval()

print(pd.Series({"difference": tka.mean() - tha.mean(),
                 "ci_low": ci.low, "ci_high": ci.high, "p": bmi_test.pvalue}))
```
:::

```{python}
#| include: false
chk = {"difference": float(tka.mean() - tha.mean()), "ci_low": float(ci.low),
       "ci_high": float(ci.high), "p": float(bmi_test.pvalue)}
```

```{r}
#| include: false
check_agree(list(difference = difference, ci_low = ci[1], ci_high = ci[2], p = bmi_test$p.value),
            reticulate::py$chk)
```

> TKA patients had a higher BMI than THA patients (mean difference 1.8 kg/m², 95% CI 0.9 to 2.6; p < 0.001).

Is a difference of 1.8 kg/m² *clinically* important? The p-value can't tell you. That depends on clinical judgment, and on the CI: the whole interval (0.9 to 2.6) is small next to a typical BMI of 30. **Statistically significant** means "unlikely to be pure chance", not "important".

::: {.callout-warning}
## ⚠️ Watch out: two classic misreadings
- **"p = 0.20, so there's no difference."** No. It means the data couldn't rule out zero. Look at the CI: if it runs from "harmful" to "very helpful", the study was too small to say.
- **"p < 0.001, so the effect is large."** No. With enough patients, tiny differences get tiny p-values. Look at the effect size and CI.
:::

::: {.callout-tip}
## 🔀 R vs Python: which group comes first
R's `t.test(bmi ~ procedure)` subtracts in alphabetical order of the groups (THA minus TKA). `scipy`'s `ttest_ind(tka, tha)` subtracts the second argument from the first. Same answer, opposite sign. Always say which group was subtracted from which, as we did above.
:::

For PROMs, judge differences against the **minimal clinically important difference (MCID)**: the smallest change patients notice as meaningful. Published MCIDs vary with the study and the method used to derive them, so cite the one you use. A difference smaller than the MCID can be statistically significant and still clinically irrelevant.

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
preop_scores <- proms$prom_score[proms$visit == "preop" & !is.na(proms$prom_score)]
stopifnot(
  round(shapiro.test(cohort$age)$p.value, 3) == 0.001,
  round(shapiro.test(first_ten)$p.value, 2) == 0.17,
  round(shapiro.test(cohort$bmi)$p.value, 2) == 0.04,
  round(shapiro.test(residuals(fit))$p.value, 2) == 0.31,
  round(skewness(cohort$los_days), 1) == 1.6,
  round(skewness(log1p(cohort$los_days)), 1) == 0.6,
  mean(cohort$los_days == 0) > 0.45, mean(cohort$los_days == 0) < 0.5,
  round(100 * mean(one_year$prom_score == 100)) == 17,
  round(difference, 1) == 1.8, round(ci[1], 1) == 0.9, round(ci[2], 1) == 2.6,
  round(skewness(preop_scores), 1) == 0.1
)
```

## Exercises {#exercises}

**1.** Draw a histogram and a QQ plot of the **pre-op** PROM score. Is it closer to normal than the 1-year score? Why might that be?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
preop <- proms |> filter(visit == "preop", !is.na(prom_score))
ggplot(preop, aes(prom_score)) + geom_histogram(bins = 30)
ggplot(preop, aes(sample = prom_score)) + geom_qq() + geom_qq_line()
skewness(preop$prom_score)
```

## Python

```{python}
preop = proms[(proms["visit"] == "preop") & proms["prom_score"].notna()]
fig, axes = plt.subplots(1, 2, figsize=(8, 3))
axes[0].hist(preop["prom_score"], bins=30)
stats.probplot(preop["prom_score"], plot=axes[1])
plt.show()
print(skewness(preop["prom_score"]))
```
:::

Much closer to normal: skewness about 0.1 and the QQ points follow the line. Before surgery, scores sit in the middle of the scale, far from the ceiling. After a successful operation many patients hit the maximum, which creates the ceiling.
:::

**2.** A fellow wants to compare operative time between surgeons S1 and S2, about 40 cases each. The histogram is fairly symmetric, with a few long cases. Which column of the decision table would you use, and how would you justify it in the Methods?

::: {.callout-tip collapse="true"}
## Solution
The Gaussian column (an unpaired t test, Welch's version) is reasonable. With about 40 cases per group and a roughly symmetric shape, the t test is robust. Check the QQ plot within each surgeon, and check that the few long cases aren't extreme outliers. Methods: "Operative time was approximately normally distributed within each group on visual inspection of histograms and QQ plots, and was compared with Welch's t test." If the long cases were extreme, a Mann-Whitney test would be the safer choice; say so.
:::

**3.** A study reports: "1-year KOOS JR was 2.1 points higher with the new implant (95% CI −1.5 to 5.7; p = 0.25)." Suppose the MCID for KOOS JR is 14 points. Write one sentence interpreting this result.

::: {.callout-tip collapse="true"}
## Solution
"The study found no clear difference in 1-year KOOS JR between implants: the estimate (2.1 points) and the whole 95% CI (−1.5 to 5.7) fall well below the MCID, so a clinically important benefit of the new implant is unlikely."

Note that this is stronger than "not significant". The CI rules out an important difference, which is a useful finding in itself.
:::
````

- [ ] **Step 4: Render and run the tests**

Run:

```bash
quarto render foundations/03-distributions.qmd
uv run pytest tests/site -q
```

Expected:
- The render succeeds.
- pytest: `47 passed`.

- [ ] **Step 5: Prove the guard bites**

In the prose-guard chunk, temporarily change `round(shapiro.test(first_ten)$p.value, 2) == 0.17` to `== 0.18` and render.
Expected: FAIL with `… == 0.18 is not TRUE`.

Change it back and render again. Expected: success.

- [ ] **Step 6: Commit**

```bash
git add foundations/03-distributions.qmd _freeze tests/site/test_foundations.py
git commit -m "Write page 3, Distributions & choosing a test: shape, Shapiro-Wilk limits, flowchart, effect sizes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Record the page conventions and run everything

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Produces: golden rules 4 (revised) and 10–12, which Phases 3–6 follow.

- [ ] **Step 1: Update `CLAUDE.md`**

Replace `CLAUDE.md` with:

```markdown
# CLAUDE.md: TJS Statistics Tutorials

Public Quarto website and repository. It teaches TJS research assistants (beginners in both statistics and code) tidy data, Table 1, distribution checks, every test in the Motulsky decision table, survival analysis, and selected extras, in R and Python side by side.

- Design spec: `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`
- Plans: `docs/superpowers/plans/`

## Golden rules

1. **Synthetic data only. This repo is public.** Never add real patient data, real names, MRNs, real surgery dates, or screenshots of clinical systems. `.gitignore` blocks data-file extensions outside `data/` and `templates/`. Never `git add -f`.
2. **Every page with executable code declares `engine: knitr` in its own front matter.** Quarto ignores `engine` in `_quarto.yml` and `_metadata.yml`. Without it, a Python-only page silently runs in Jupyter on the system Python. `tests/site/test_sources.py` enforces this.
3. **Language tabsets are `::: {.panel-tabset group="language"}`** with `## R` first and `## Python` second. Each language block stands alone: it loads its own packages and data.
4. **Every R/Python pair ends with a hidden agreement check.** At the top of the page, a hidden chunk runs `source("R/check_agree.R")`. After each pair, a hidden Python chunk stores plain numbers, `chk = {"p": float(result.pvalue), ...}`, and a hidden R chunk compares them: `check_agree(list(p = r_result$p.value, ...), reticulate::py$chk)`. Never pull DataFrames, sets or `pd.NA` through `reticulate::py`; they don't convert cleanly. Where defaults differ (Welch vs Student, continuity corrections, exact vs asymptotic), set them explicitly in both languages and explain the difference in a 🔀 callout. Where two libraries genuinely use different formulas (for example the SMD variance divisor), document it in the callout and pass a looser `tol` with a comment.
5. **Render locally, commit `_freeze/`.** CI never runs R or Python. A page changed without re-rendering fails CI by design.
6. **Exercise solutions are collapsed:** `::: {.callout-tip collapse="true"}` titled `Solution`, with a language tabset inside.
7. **Stub pages** carry "(coming soon)" in the title and a `.coming-soon` callout. Remove both when the page is written.
8. **Reporting conventions** (spec section 4, page 0.2): mean (SD) or median (IQR); n (%); p to 3 decimals with a floor of "p < 0.001"; a 95% CI with every estimate.
9. **Never hand-edit `data/` or `templates/`.** Change `data-raw/` and run `just data`. Seeds and effect sizes are the default arguments of each `make_*()` function in `data-raw/R/`. Never loosen a test or change a seed or parameter just to make a test pass; if an effect weakens, strengthen it deliberately and record why.
10. **Quiet pages.** Pages with code set `execute: message: false` in their front matter, and chunks that call `library()` add `#| warning: false`. A site test fails on any stderr output. Don't attach packages that mask base functions (janitor masks `chisq.test()`/`fisher.test()`); call them as `pkg::fun()`.
11. **Prose guards.** Each page ends, just before Exercises, with a hidden R chunk headed `# Prose guard` that `stopifnot()`s every number quoted in the text. If the data change, the render stops until the text is updated.
12. **Exercise solutions are executed chunks** (`{r}` / `{python}`) inside the collapsed Solution callout, so they can't rot.

## Commands

| Command | Does |
|------|------|
| `just setup` | `renv::restore()` + `uv sync` |
| `just test` | testthat (`tests/testthat`) + pytest (`tests/python`) |
| `just render` / `just preview` | Quarto render / live preview |
| `just check` | render, then `pytest tests/site` + lychee (internal links and anchors) |

## Machine prerequisites (macOS)

- `sudo xcodebuild -license accept`, once. Without it, renv's compiler check fails during install and restore.
- lychee: install from the GitHub release binary into `~/.local/bin`. Homebrew needs the Xcode license too.

## Layout

- Pages: `index.qmd`, `getting-started/`, `foundations/`, `catalog/` (pages 4–12, one per table row), `survival/`, `beyond/`, `report/`
- `R/check_agree.R`: the agreement guard
- `tests/testthat/` (R), `tests/python/` (Python, data and repo), `tests/site/` (built site and sources)
- `data/`, `data-raw/`, `templates/`: synthetic data and its generator (Phase 1)
```

- [ ] **Step 2: Verify the docs test still holds**

Run: `uv run pytest tests/python/test_repo_docs.py -q`
Expected: `3 passed`. `check_agree`, `engine: knitr`, `group="language"`, `_freeze` and `Synthetic data only` are all still present.

- [ ] **Step 3: Run everything**

Run: `just test && just check`

Expected:
- testthat `PASS 235`
- pytest `tests/python`: `78 passed`
- pytest `tests/site`: `47 passed`
- lychee: `0 Errors`
- `git status --short` shows only `CLAUDE.md`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "CLAUDE.md: record Phase 2 page conventions (chk checks, quiet pages, prose guards, executed solutions)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

After this task, finish the branch with superpowers:finishing-a-development-branch.
