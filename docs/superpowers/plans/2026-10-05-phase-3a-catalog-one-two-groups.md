# Phase 3a: Test Catalog, One and Two Groups (Pages 4–7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace four catalog stubs with finished pages, one per row of the decision table:
- `catalog/04-describe-one-group.qmd`: mean and SD, median and IQR, a proportion, a Kaplan-Meier curve
- `catalog/05-one-group-vs-hypothetical.qmd`: one-sample t, Wilcoxon signed-rank, chi-square goodness-of-fit, binomial test
- `catalog/06-two-unpaired-groups.qmd`: Welch's t, Mann-Whitney, Fisher's exact and chi-square, log-rank
- `catalog/07-two-paired-groups.qmd`: paired t, Wilcoxon signed-rank, McNemar, stratified Cox

Every section runs in R and Python, with hidden agreement checks and an effect size with its 95% CI.

**Architecture:**
- Each page is a knitr-engine Quarto page. Each decision-table cell is an `##` section with the anchor the home page already links to.
- Each section follows the spec §6 anatomy as `###` steps, and its first tabset loads its own packages and data, because readers arrive from the decision table straight at a section.
- Hidden chunks guard correctness, as on the Phase 2 pages:
  - `check_agree()` compares R and Python
  - a `# Prose guard` `stopifnot()`s every quoted number
  - a data-checksum stamp catches stale renders
- New tests:
  - `tests/site/test_catalog.py` pins the page anatomy
  - `tests/site/test_sources.py` gains rules for catalog sections and for a reticulate pitfall this phase found

**Tech Stack:**
- R: tidyverse, survival, ggsurvfit, effectsize, DescTools (called as `DescTools::`)
- Python: pandas 3, scipy, statsmodels, pingouin, lifelines, matplotlib
- Quarto 1.9.37

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md` (§3.2 cell → anchor map, §4 effect-size table for pages 4–12, §6 page anatomy, §8 quality checks)

## Phase 3 is split into three plans

Spec §9 makes pages 4–12 one phase. It is 35 test sections, so it ships as three plans, each with its own PR:

- **3a (this plan):** pages 4–7. It also adds the catalog test harness and the Python statistics and survival packages.
- **3b:** pages 8–9 (three or more groups), ending with "Which groups differ?" pointers to page 15.
- **3c:** pages 10–12 (association, prediction and regression).

## Global Constraints

- **`engine: knitr` per page.** Every page with code declares `engine: knitr`, `toc-depth: 2` and `execute:` / `message: false` in its own front matter.
- **Tabsets:** `::: {.panel-tabset group="language"}`, with `## R` first and `## Python` second.
- **Hidden agreement checks:**
  - A hidden Python chunk sets `chk = {name: float(...)}`.
  - A hidden R chunk then calls `check_agree(list(name = <R value>), reticulate::py$chk)`.
  - Never pass DataFrames, sets or `pd.NA` through `reticulate::py`.
  - A looser `tol` always carries a comment saying why.
- **Quiet output:**
  - Chunks that call `library()` add `#| warning: false`. No page may show stderr output.
  - Call DescTools and effectsize as `pkg::fun()`; don't attach them.
  - **Never assign to `_` in a Python chunk** (see Task 2).
- **Section anatomy (spec §6):**
  - A `**The question:**` line comes first.
  - Then these `###` steps, in order: When to use it, Look at the data first, Run it, Read the output, Effect size and 95% CI (not on page 4), How to report it.
  - How to report it holds a `> **Methods:**` and a `> **Results:**` blockquote.
  - Each section has a ⚠️ box.
  - Add a 🔀 box wherever R and Python defaults differ.
- **Self-contained sections:** a section's first R block calls `library()` and `read_csv("data/...")`. Its first Python block imports and calls `pd.read_csv("data/...")`.
- **Prose guard:** each page has one hidden R chunk headed `# Prose guard`, immediately before `## Exercises {#exercises}`.
  - It `stopifnot()`s every number the prose quotes, including the numbers in exercise solutions.
  - It recomputes those numbers itself, because it runs before the solution chunks.
- **Data stamp:** each page has the visible-to-nobody `<!-- data-checksum: … -->` chunk.
- **Solutions:** exercise solutions are `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`.
- **Freeze:** render every changed page and commit its `_freeze/` directory. After a deliberately failed render, delete the leftover `catalog/<page>_files/` folder.
- **Reporting conventions** (spec §4 page 0.2):
  - mean (SD) or median (IQR)
  - n (%)
  - p to 3 decimals, with a floor of "p < 0.001" and a ceiling of "p > 0.999"
  - a 95% CI with every estimate
- **Branching:** work on branch `phase-3a-catalog`, in a worktree under `.worktrees/phase-3a`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A reader arrives from the decision table at one section and copies only its code.** It must run on its own. Test: `tests/site/test_sources.py::test_each_catalog_section_loads_its_own_packages_and_data` (Task 3).
2. **A Python chunk assigns to `_`, and reticulate silently drops every later Python output on the page.** The page renders, every hidden check passes, and the Python tabs just show code. Tests (Task 2):
   - `test_sources.py::test_no_python_chunk_assigns_to_underscore`
   - `test_conventions.py::test_every_python_print_shows_its_output`
3. **A library default changes,** for example scipy's `equal_var`, statsmodels' `mcnemar(exact=...)`, Wilcoxon continuity corrections, or lifelines convergence. The hidden `check_agree()` must stop the render. Every section has one (`test_sources.py::test_every_catalog_section_checks_r_against_python`), and the mutation steps in Tasks 5–6 prove two of them bite.
4. **Someone runs `just data`, and the catalog's quoted numbers go stale.** Tests (Task 3):
   - the prose guards
   - `tests/site/test_freshness.py`, whose Justfile test now derives the folders to re-render from the pages that read `data/`
5. **lifelines runs on pandas 3 despite its declared `pandas<3` pin, or a re-lock silently drops pandas to 2.** Tests:
   - `check_agree()` compares every lifelines number with R's survival package
   - `tests/python/test_check_setup.py::test_project_python_uses_pandas_3` (Task 1)

## Plan rulings (made while prototyping)

- **lifelines with a uv override to pandas 3.**
  - **The conflict:** lifelines 0.30.3 (the latest) declares `pandas<3.0`. Adding it downgrades pandas to 2.3.3, and page 1's tidying code then fails (`str.contains` returns NaN for missing values in pandas 2, and `.astype(int)` breaks).
  - **The alternative fails:** statsmodels has no pointwise Kaplan-Meier CI, and the spec forbids hand-rolling one.
  - **What lifelines does on pandas 3:** it gives identical numbers on both pandas versions. Its only complaint is `Pandas4Warning` deprecation notices, which Python hides by default; no page shows one.
  - **The decision:** `pyproject.toml` gets `override-dependencies = ["pandas>=3.0"]`, and `check_agree()` compares every lifelines number with R.
- **Never assign to `_` in Python chunks.**
  - **The cause:** reticulate 1.47 decides whether to print a statement's value by reading Python's last value, `_`. Code that assigns `_` itself hides reticulate's placeholder. Once `_` holds a plot object (`_ = ax.hist(...)` returns a matplotlib container), reticulate treats every later output as a plot and drops it, for the rest of the page.
  - **Page 3:** its three `_ =` lines are harmless only by luck, because their values aren't plot objects. Task 2 replaces them.
  - **The fix:** bare matplotlib calls print nothing anyway; name any other result (`qq = stats.probplot(...)`).
- **Effect sizes:**
  - **Rank-biserial r and Hedges' g:** Python gets them from pingouin; R from effectsize.
  - **Cohen's d~z~:** computed directly in Python, because pingouin's paired "cohen" is d~av~ (2.08 vs d~z~ 1.49 on page 7). Page 7 says so.
- **Hodges-Lehmann estimates.**
  - **In R:** `wilcox.test(conf.int = TRUE)`. R finds the estimate by root-finding, so its check uses `tol = 1e-4`, with a comment.
  - **In Python:** the median of Walsh averages (one sample) or of pairwise differences (two samples), with a CI from `scipy.stats.bootstrap` (BCa, 9999 resamples, seed 2026).
  - **Agreement:** the spec says CIs from different methods are documented, not checked. The 🔀 boxes quote both, and the prose guard pins the bootstrap values.
- **Fisher's odds ratio:**
  - Python uses `scipy.stats.contingency.odds_ratio(kind="conditional")` to match R's conditional MLE and exact CI.
  - Both programs find these by root-finding, so the check uses `tol = 1e-4`.
  - scipy's `fisher_exact()` statistic is the sample odds ratio; page 6's 🔀 box explains.
- **Kaplan-Meier CIs:** R sets `conf.type = "log-log"` to match lifelines.
- **Stratified Cox:** lifelines needs `fit_options={"precision": 1e-9}`, because its default stops at HR 3.4997 instead of R's 3.5.
- **Page 4 has no "Effect size" step.** Describing a group has no comparison; the estimate and its CI are the result.
- **`toc-depth: 2` on catalog pages.** Each page repeats the same six `###` step names four times, which would clutter the table of contents.
- **Imports go at the top of each section's first Python block,** not only the page's first block (spec §6 code style), because spec §6 step 4 wants every section's code to run on its own.
- **Examples:**
  - **PROM examples use KOOS JR (TKA) only,** not KOOS JR pooled with HOOS JR, because they are different instruments.
  - **Mann-Whitney uses 1-year KOOS JR by sex,** not length of stay by site. With whole days and heavy ties, the Hodges-Lehmann estimate for LOS is 0 even though p = 0.020; that case became exercise 2 on page 6, with the explanation.
  - **Hypothetical values are labeled made-up** ("Suppose a registry reports …"), never presented as real figures.
- **Page 7's paired Wilcoxon example has every patient improving.** All 246 TKA patients improved, which is synthetic-data tidiness (r = 1). The page says real data are rarely this tidy, and exercise 3 (3 months → 1 year: 176 better, 46 worse) shows the realistic case. Changing the generator was rejected: it would move numbers on pages 1–3.
- **Fisher's p = 1 is reported as "p > 0.999".**
- **Examples use all 600 cases, including bilateral patients.** Each page's intro box says so and points to page 3's advice.
- **Ordinal outcomes:** the Wilcoxon signed-rank sections point ordinal scales to the sign test (the binomial test on signs) rather than claiming the signed-rank test suits them.

## Reference results (prototype, 2026-10-05, R 4.6.0 / Python 3.13 / pandas 3.0.6)

All four pages rendered with every hidden check passing. Full suite:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- pytest `tests/python`: 80 passed
- pytest `tests/site`: 117 passed
- lychee: 0 errors (1313 links)

Mutation checks that stopped the render:
- a wrong number in page 4's and page 5's prose guards
- scipy's Student's t on page 6 (`check_agree(): … disagree on 't'`)
- statsmodels' exact McNemar on page 7 (`disagree on 'chisq'`)

Key numbers the prose guards pin:

| Page | Numbers |
|---|---|
| 4 | age 65.5 (SD 9.4; CI 64.8 to 66.3); 1-year KOOS JR median 85.8 (IQR 74.7 to 93.9; CI 84.0 to 88.2); complications 8.5% (6.5% to 11.0%); 5-year revision-free survival 86.3% (82.8% to 89.2%) |
| 5 | operative time 5.5 min below 90 (4.2 to 6.8); KOOS JR vs 80: Hodges-Lehmann 84.4 (82.7 to 86.1), r = 0.34; ASA χ² = 27.0; readmission 4.5% vs 6%, p = 0.143 |
| 6 | BMI +1.8 kg/m² (0.9 to 2.6), g = 0.33; KOOS JR men vs women 0.8 (−1.6 to 4.4), p = 0.432; readmission OR 1.07 (0.45 to 2.50), p > 0.999; implant C vs A HR 3.04 (1.83 to 5.04) |
| 7 | PCS +13.7 (12.8 to 14.5), d~z~ = 1.49; KOOS JR +34.1 (32.3 to 35.9); walking aid OR 2.76 (2.09 to 3.68); matched pairs HR 3.50 (1.15 to 10.63), p = 0.027 |

---

### Task 1: Dependencies and setup checks for Phase 3a

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `pyproject.toml`, `uv.lock`
- Modify: `getting-started/check_setup.R`, `getting-started/check_setup.py`
- Modify: `tests/testthat/test-environment.R`, `tests/python/test_check_setup.py`

**Interfaces:**
- Produces:
  - R packages effectsize, DescTools and ggsurvfit, plus their dependencies; survival is already locked
  - Python packages statsmodels, pingouin and lifelines, on pandas 3
  - both `check_setup` scripts verifying them

- [ ] **Step 1: Create the worktree and build the current site**

```bash
git checkout main && git pull
git worktree add .worktrees/phase-3a -b phase-3a-catalog main
cd .worktrees/phase-3a
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `59 passed`.

- [ ] **Step 2: Write the failing checks**

In `tests/testthat/test-environment.R`, replace

```r
  for (m in c("pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx")) {
```

with

```r
  for (m in c("pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx",
             "statsmodels", "pingouin", "lifelines")) {
```

In `getting-started/check_setup.R`, replace

```r
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat", "tidyverse", "readxl",
             "tidyxl", "janitor", "gtsummary", "flextable", "smd")) {
```

with

```r
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat", "tidyverse", "readxl",
             "tidyxl", "janitor", "gtsummary", "flextable", "smd", "effectsize",
             "DescTools", "survival", "ggsurvfit")) {
```

In `getting-started/check_setup.py`, replace

```python
for name in ["pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx"]:
```

with

```python
for name in ["pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx",
             "statsmodels", "pingouin", "lifelines"]:
```

In `tests/python/test_check_setup.py`, replace

```python
    for pkg in ["tidyverse", "readxl", "tidyxl", "janitor", "gtsummary", "flextable", "smd"]:
```

with

```python
    for pkg in ["tidyverse", "readxl", "tidyxl", "janitor", "gtsummary", "flextable", "smd",
                "effectsize", "DescTools", "survival", "ggsurvfit"]:
```

and append (after two blank lines):

```python
def test_project_python_uses_pandas_3():
    """The pages are written for pandas 3. lifelines declares pandas<3, so pyproject.toml overrides it."""
    import pandas

    assert int(pandas.__version__.split(".")[0]) >= 3, pandas.__version__
```

- [ ] **Step 3: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "environment|check_setup")'
uv run pytest tests/python/test_check_setup.py -q
```

Expected:
- R: failures for `pingouin` and `lifelines` (environment; statsmodels is already installed through tableone). `check_setup.R` reports PROBLEM for effectsize, DescTools and ggsurvfit, so "check_setup.R passes in a working project" fails.
- Python: `test_passes_inside_the_project_environment` FAILS. `test_project_python_uses_pandas_3` passes (pandas is still 3.0.6).

- [ ] **Step 4: Install and lock the R packages**

Replace `DESCRIPTION` with:

```
Type: project
Description: R dependencies for the TJS statistics tutorial site. Not a
    package; renv reads this file to decide what to lock.
Imports:
    DescTools,
    dplyr,
    effectsize,
    flextable,
    ggsurvfit,
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
Rscript -e 'renv::install(c("effectsize", "DescTools", "ggsurvfit"), prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
python3 -c "import json; d=json.load(open('renv.lock'))['Packages']; print(all(p in d for p in ['effectsize','DescTools','ggsurvfit','survival']))"
```

Expected: `True`.

- [ ] **Step 5: Add the Python packages and watch pandas drop to 2**

Run:

```bash
uv add statsmodels pingouin lifelines
uv run pytest tests/python/test_check_setup.py::test_project_python_uses_pandas_3 -q
```

Expected: FAIL with `AssertionError: 2.3.3`. lifelines declares `pandas<3.0`.

- [ ] **Step 6: Override lifelines' pandas pin**

In `pyproject.toml`, replace

```toml
[tool.uv]
package = false
```

with

```toml
[tool.uv]
package = false
# lifelines 0.30.3 declares pandas<3.0 but works with pandas 3 (every survival
# number on the site is checked against R on each render). Remove this when
# lifelines supports pandas 3 officially.
override-dependencies = ["pandas>=3.0"]
```

Run:

```bash
uv sync
uv run pytest tests/python/test_check_setup.py -q
```

Expected: `4 passed`. `pyproject.toml`'s dependencies now list `lifelines`, `pingouin` and `statsmodels`.

- [ ] **Step 7: Confirm the new environment changes no Phase 2 result**

Rendering a folder always re-runs its code. Re-render the foundations pages and compare their frozen results:

```bash
quarto render foundations
git status --short _freeze
```

Expected: only `_freeze/foundations/02-demographics/execute-results/html.json` changed. gtsummary gives each gt table a random HTML id on every render, and that is the whole difference (`git diff` shows only `id="…"` changes). Pages 1 and 3 reproduce byte for byte. Restore page 2's freeze:

```bash
git checkout -- _freeze/foundations/02-demographics
```

- [ ] **Step 8: Run all the tests**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
uv run pytest tests/site -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- Python: `80 passed`
- site: `59 passed`

- [ ] **Step 9: Commit**

```bash
git add DESCRIPTION renv.lock pyproject.toml uv.lock getting-started/check_setup.R getting-started/check_setup.py tests/testthat/test-environment.R tests/python/test_check_setup.py
git commit -m "Add Phase 3a packages (effectsize, DescTools, ggsurvfit, statsmodels, pingouin, lifelines)

lifelines declares pandas<3; override it so the site stays on pandas 3.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Python chunks never assign to `_`

reticulate prints a statement's value by reading Python's last value, `_`. Code that assigns `_` hides reticulate's placeholder. Once `_` holds a matplotlib object, every later Python output on the page is silently dropped, and the hidden checks still pass. This task adds a source rule, a site test for the symptom, and fixes page 3, whose `_ =` lines are harmless today only by luck.

**Files:**
- Modify: `tests/site/test_sources.py` (append), `tests/site/test_conventions.py` (append)
- Modify: `foundations/03-distributions.qmd`
- Modify: `_freeze/foundations/03-distributions/` (re-render; commit it)

**Interfaces:**
- Produces: `test_sources.py`'s `PYTHON_CHUNK` regex and `assigns_underscore(text) -> bool`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/site/test_sources.py` (after two blank lines):

```python
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
```

Append to `tests/site/test_conventions.py` (after two blank lines):

```python
def test_every_python_print_shows_its_output(site):
    """reticulate can drop Python output silently (see test_sources.py); catch the symptom too."""
    for page in PAGES:
        for cell in load(page).select("div.cell"):
            code = cell.select_one("pre.sourceCode.python")
            if code is not None and "print(" in code.get_text():
                assert cell.select(".cell-output-stdout"), f"{page}: no output for {code.get_text()[:60]!r}"
```

- [ ] **Step 2: Run them to verify the source rule fails**

Run: `uv run pytest tests/site -q`

Expected:
- `test_no_python_chunk_assigns_to_underscore` FAILS, naming `foundations/03-distributions.qmd`.
- The two rule tests and `test_every_python_print_shows_its_output` pass. Page 3 still shows all its output, because its `_` values happen not to be plot objects; the site test guards the symptom on later pages.

- [ ] **Step 3: Fix page 3**

In `foundations/03-distributions.qmd`, replace

```python
fig, ax = plt.subplots(figsize=(4, 3))
_ = stats.probplot(residuals, plot=ax)                   # "_ =" hides probplot's returned numbers
plt.show()
```

with

```python
fig, ax = plt.subplots(figsize=(4, 3))
qq = stats.probplot(residuals, plot=ax)                  # naming the result keeps its numbers out of the output
plt.show()
```

and replace

```python
_ = axes[0].hist(preop["prom_score"], bins=30)   # "_ =" hides the returned counts
_ = stats.probplot(preop["prom_score"], plot=axes[1])
```

with

```python
axes[0].hist(preop["prom_score"], bins=30)
qq = stats.probplot(preop["prom_score"], plot=axes[1])   # naming the result keeps its numbers out of the output
```

- [ ] **Step 4: Render page 3 and run the tests**

Run:

```bash
quarto render foundations/03-distributions.qmd
uv run pytest tests/site -q
git diff --stat _freeze
```

Expected: `63 passed`. Only `_freeze/foundations/03-distributions/execute-results/html.json` changed, and its diff touches only the edited code lines.

- [ ] **Step 5: Commit**

```bash
git add tests/site/test_sources.py tests/site/test_conventions.py foundations/03-distributions.qmd _freeze/foundations/03-distributions
git commit -m "Never assign to _ in Python chunks: reticulate drops all later output

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Page 4, Describe one group, and the catalog test harness

**Files:**
- Modify: `catalog/04-describe-one-group.qmd` (replace the stub)
- Create: `_freeze/catalog/04-describe-one-group/` (render output; commit it)
- Create: `tests/site/test_catalog.py`
- Modify: `tests/site/test_sources.py`, `tests/site/test_freshness.py`, `Justfile`

**Interfaces:**
- Consumes:
  - `R/check_agree.R`
  - `data/cohort.csv`, `data/proms_long.csv`
  - `tests/site/sitelib.py` (`CELL_ANCHORS`, `ROOT`, `load`)
  - `test_sources.py`'s `HIDDEN_CHUNK`, `front_matter`
- Produces:
  - `tests/site/test_catalog.py` with a `WRITTEN` list that Tasks 4–6 extend
  - `test_sources.py`'s `written_pages(*dirs)` and `catalog_sections()`
  - page 4 anchors `#mean-sd`, `#median-iqr`, `#proportion` and `#kaplan-meier`, which pages 5 and 6 link to

- [ ] **Step 1: Write the failing tests**

Create `tests/site/test_catalog.py`:

```python
"""Part 2 · Test catalog: one page per row of the decision table, one section per cell."""

import pytest

from sitelib import CELL_ANCHORS, ROOT, load

# Catalog pages written so far. Later phases add pages 8-12 here.
WRITTEN = [
    "catalog/04-describe-one-group.html",
]

# Spec section 6, steps 2-7, as h3 headings in this order. Page 4 describes a
# group rather than testing it: its estimate and CI are the result, so it has
# no separate effect-size step.
ANATOMY = ["When to use it", "Look at the data first", "Run it", "Read the output",
           "Effect size and 95% CI", "How to report it"]
DESCRIBE = [step for step in ANATOMY if step != "Effect size and 95% CI"]

SECTIONS = [(page, anchor) for page in WRITTEN for anchor in CELL_ANCHORS[page]]

# Survival cells give a short worked example and point to the full treatment.
SURVIVAL_LINKS = {cell: target for cell, target in {
    ("catalog/04-describe-one-group.html", "kaplan-meier"): "survival/13-kaplan-meier.html",
    ("catalog/06-two-unpaired-groups.html", "log-rank"): "survival/14-cox-regression.html",
    ("catalog/07-two-paired-groups.html", "stratified-cox"): "survival/14-cox-regression.html",
}.items() if cell[0] in WRITTEN}


def text_of(element):
    """Text with smart quotes straightened and runs of whitespace collapsed."""
    return " ".join(element.get_text(" ").replace("’", "'").split())


def section(page, anchor):
    found = load(page).select_one(f"section#{anchor}")
    assert found is not None, f"{page} has no section #{anchor}"
    return found


@pytest.mark.parametrize("page", WRITTEN)
def test_page_is_written_and_frozen(site, page):
    assert load(page).select_one(".coming-soon") is None, f"{page} is still a stub"
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page,anchor", SECTIONS)
def test_section_follows_the_page_anatomy(site, page, anchor):
    found = section(page, anchor)
    steps = [h.get_text(strip=True) for h in found.select("section.level3 > h3")]
    assert steps == (DESCRIBE if page.startswith("catalog/04-") else ANATOMY)
    text = text_of(found)
    assert "The question:" in text                                      # step 1
    report = " ".join(text_of(q) for q in found.select("blockquote"))
    assert "Methods:" in report and "Results:" in report                # step 7
    assert found.select("div.callout-warning"), "no ⚠️ Watch out box"   # step 8


@pytest.mark.parametrize("page,anchor", SECTIONS)
def test_section_shows_output_in_both_languages(site, page, anchor):
    ran = [tabset for tabset in section(page, anchor).select("div.panel-tabset")
           if all(pane.select(".cell-output, .cell-output-display")
                  for pane in tabset.select("div.tab-pane"))]
    assert ran, f"{page}#{anchor}: no tabset shows output in both R and Python"


@pytest.mark.parametrize("page", WRITTEN)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    exercises = load(page).select_one("section#exercises")
    headers = [h.get_text(strip=True) for h in exercises.select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", WRITTEN)
def test_page_shows_no_warnings_or_package_messages(site, page):
    assert [out.get_text()[:80] for out in load(page).select(".cell-output-stderr")] == []


@pytest.mark.parametrize("page", WRITTEN)
def test_outputs_are_short_and_never_dump_objects(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text and "<matplotlib." not in text, f"{page}: object dumped: {text[:80]}"
        assert len(text.splitlines()) <= 40, f"{page}: {len(text.splitlines())}-line output"


@pytest.mark.parametrize("cell,target", SURVIVAL_LINKS.items())
def test_survival_sections_point_to_the_full_treatment(site, cell, target):
    page, anchor = cell
    hrefs = [a["href"] for a in section(page, anchor).select("a[href]")]
    assert any(href.endswith(target) for href in hrefs)
```

In `tests/site/test_sources.py`, replace

```python
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

with

```python
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
```

and append (after two blank lines):

```python
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
```

In `tests/site/test_freshness.py`, replace

```python
def test_just_data_re_renders_the_pages_that_read_data():
    justfile = (ROOT / "Justfile").read_text(encoding="utf-8")
    recipe = justfile[justfile.index("\ndata:"):]
    assert "quarto render foundations" in recipe
```

with

```python
def test_just_data_re_renders_the_pages_that_read_data():
    justfile = (ROOT / "Justfile").read_text(encoding="utf-8")
    recipe = justfile[justfile.index("\ndata:"):]
    folders = sorted({page.parts[0] for page in data_pages()})
    missing = [f for f in folders if not re.search(rf"^\s*quarto render {f}\s*$", recipe, re.MULTILINE)]
    assert missing == [], f"`just data` must re-render: {missing}"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: 11 of the 13 `test_catalog.py` tests FAIL ("still a stub", missing steps, no exercises). The no-warnings and short-outputs tests pass trivially on a stub. Everything else passes; the two catalog source tests pass only because no catalog page is written yet, and Step 7 proves they bite.

- [ ] **Step 3: Write the page**

Replace `catalog/04-describe-one-group.qmd` with:

````markdown
---
title: "4 · Describe one group"
description: "Mean and SD, median and IQR, a proportion, and a Kaplan-Meier survival curve, each with a 95% confidence interval."
engine: knitr
toc-depth: 2
execute:
  message: false
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

Before you compare anything, describe it. This page covers the first row of the [decision table](../index.qmd): one number (or one curve) that sums up a group of patients, with a 95% confidence interval that says how precisely you know it. Which summary you use depends on the column, the type of data you have. [Page 3](../foundations/03-distributions.qmd) explains how to choose.

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

## Mean and standard deviation {#mean-sd}

**The question:** How old are our patients, and how much do their ages vary?

### When to use it

- The variable is a **measurement** (age, BMI, operative time), not a category.
- Its distribution is **roughly symmetric**, without extreme outliers. Check with a histogram ([page 3](../foundations/03-distributions.qmd#look)).
- If it's **skewed**, has a **ceiling or floor**, or is **ordinal** → use the [median and IQR](#median-iqr) instead.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

ggplot(cohort, aes(age)) +
  geom_histogram(binwidth = 2) +
  geom_vline(xintercept = mean(cohort$age), linetype = "dashed") +   # the mean
  labs(x = "Age at surgery, years", y = "Patients")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(cohort["age"], bins=range(40, 90, 2))
ax.axvline(cohort["age"].mean(), linestyle="--")       # the mean
ax.set_xlabel("Age at surgery, years")
ax.set_ylabel("Patients")
plt.show()
```
:::

A single, roughly symmetric hump: the mean sits in the middle of it, so it's a fair summary.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
age_summary <- cohort |>
  summarise(n = n(), mean = mean(age), sd = sd(age))
age_summary

age_ci <- t.test(cohort$age)$conf.int   # 95% CI for the mean
age_ci
```

## Python

```{python}
n = cohort["age"].count()
mean = cohort["age"].mean()
sd = cohort["age"].std()                 # pandas divides by n - 1, like R

# 95% CI for the mean: mean ± t × (SD / √n)
age_ci = stats.t.interval(0.95, df=n - 1, loc=mean, scale=sd / n ** 0.5)

print(f"n = {n}, mean = {mean:.2f}, sd = {sd:.2f}")
print(f"95% CI {age_ci[0]:.2f} to {age_ci[1]:.2f}")
```
:::

```{python}
#| include: false
chk = {"n": float(n), "mean": float(mean), "sd": float(sd),
       "ci_low": float(age_ci[0]), "ci_high": float(age_ci[1])}
```

```{r}
#| include: false
check_agree(list(n = age_summary$n, mean = age_summary$mean, sd = age_summary$sd,
                 ci_low = age_ci[1], ci_high = age_ci[2]), reticulate::py$chk)
```

### Read the output

- **n = 600:** the number of cases with an age recorded.
- **Mean = 65.5 years:** the average age.
- **SD = 9.4 years:** the standard deviation, the typical distance of a patient's age from the mean. In a bell-shaped distribution about 95% of patients lie within 2 SDs of the mean, here roughly 47 to 84 years.
- **95% CI 64.8 to 66.3:** the confidence interval for the **mean**. It tells you how precisely 600 patients pin down the average age of patients like ours. It says nothing about how spread out individual patients are; that's the SD's job.

::: {.callout-note collapse="true"}
## 🔍 Under the hood: the CI for a mean
The **standard error** of the mean is SD / √n = 9.4 / √600 ≈ 0.39 years. The 95% CI is the mean ± *t* × standard error, where *t* ≈ 1.96 for large samples (it's a little bigger for small ones). Quadruple the sample size and the standard error halves; the SD stays about the same.
:::

### How to report it

> **Methods:** Continuous variables are reported as mean (standard deviation, SD) when approximately normally distributed.
>
> **Results:** The mean age at surgery was 65.5 years (SD 9.4; 95% CI for the mean 64.8 to 66.3).

::: {.callout-warning}
## ⚠️ Watch out: SD or SEM?
The **standard error of the mean (SEM)** is much smaller than the SD (0.39 vs 9.4 years here), which is why some papers report "mean ± SEM": it looks tidier. But it describes the precision of the mean, not your patients. Use the **SD** to describe patients and a **95% CI** to show the precision of an estimate. Never report a bare "±" without saying which one it is.
:::

::: {.callout-tip}
## 🔀 R vs Python: dividing by n or n − 1
R's `sd()` and pandas' `.std()` divide by n − 1 (the "sample" SD), which is what you want. **NumPy's `np.std()` divides by n** unless you write `np.std(x, ddof=1)`. With 600 patients the difference is tiny; with 10 it isn't.
:::

## Median and interquartile range {#median-iqr}

**The question:** What's a typical KOOS JR score 1 year after knee replacement, and how much do scores vary?

### When to use it

- The variable is **skewed**, has a **ceiling or floor**, has **outliers**, or is **ordinal** (an ordered scale such as satisfaction from 1 to 5).
- The median is the middle value: half the patients are above it and half below. The **interquartile range (IQR)** runs from the 25th to the 75th percentile (the first and third quartiles), so it holds the middle half of the patients.
- If the variable is a roughly symmetric measurement → the [mean and SD](#mean-sd) are fine and more familiar.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)
koos_1yr <- proms |>
  filter(instrument == "KOOS JR", visit == "1yr", !is.na(prom_score)) |>
  pull(prom_score)

ggplot(tibble(score = koos_1yr), aes(score)) +
  geom_histogram(binwidth = 2.5) +
  labs(x = "KOOS JR at 1 year (100 = best)", y = "Patients")
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

proms = pd.read_csv("data/proms_long.csv")
koos_1yr = proms.loc[(proms["instrument"] == "KOOS JR") & (proms["visit"] == "1yr"),
                     "prom_score"].dropna()

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(koos_1yr, bins=np.arange(35, 102.5, 2.5))
ax.set_xlabel("KOOS JR at 1 year (100 = best)")
ax.set_ylabel("Patients")
plt.show()
```
:::

Scores pile up against the maximum of 100 (a **ceiling**), with a long tail of patients who did less well. A mean would be dragged down by that tail; the median isn't.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
length(koos_1yr)                                # how many patients
quantile(koos_1yr, probs = c(0.25, 0.50, 0.75)) # first quartile, median, third quartile

DescTools::MedianCI(koos_1yr, method = "exact") # the median with its 95% CI
```

## Python

```{python}
print(len(koos_1yr))                                     # how many patients
print(np.quantile(koos_1yr, [0.25, 0.50, 0.75]))         # first quartile, median, third quartile

# scipy has no "median CI" function, but quantile_test() reports one.
# Its q argument is the value it would test against; it doesn't change the CI.
median_ci = stats.quantile_test(koos_1yr, q=koos_1yr.median(), p=0.5).confidence_interval()
print(median_ci)
```
:::

```{python}
#| include: false
q = np.quantile(koos_1yr, [0.25, 0.50, 0.75])
chk = {"n": float(len(koos_1yr)), "q1": float(q[0]), "median": float(q[1]), "q3": float(q[2]),
       "ci_low": float(median_ci.low), "ci_high": float(median_ci.high)}
```

```{r}
#| include: false
q <- quantile(koos_1yr, probs = c(0.25, 0.50, 0.75))
m_ci <- DescTools::MedianCI(koos_1yr, method = "exact")
check_agree(list(n = length(koos_1yr), q1 = q[[1]], median = q[[2]], q3 = q[[3]],
                 ci_low = m_ci[["lwr.ci"]], ci_high = m_ci[["upr.ci"]]), reticulate::py$chk)
```

### Read the output

- **n = 260:** TKA patients with a 1-year KOOS JR score.
- **Median = 85.8:** half the patients scored above 85.8, half below.
- **IQR 74.7 to 93.9:** the middle half of patients scored between these two values. A quarter scored below 74.7.
- **95% CI for the median 84.0 to 88.2:** how precisely 260 patients pin down the median.

::: {.callout-note collapse="true"}
## 🔍 Under the hood: where the median's CI comes from
The CI for a median uses no formula with an SD in it. It counts instead. Sort the scores, then pick two positions such that, if the study were repeated many times, the true median would fall between the scores at those positions at least 95% of the time. The binomial distribution says which positions those are, and the CI is the pair of scores sitting there. Because positions are whole numbers, the actual confidence is a little over 95% (R reports 0.9595 here). This "exact" method needs no assumption about the shape of the data.
:::

### How to report it

> **Methods:** Continuous variables that were skewed or bounded are reported as median (interquartile range, IQR).
>
> **Results:** The median 1-year KOOS JR was 85.8 points (IQR 74.7 to 93.9; 95% CI for the median 84.0 to 88.2).

::: {.callout-warning}
## ⚠️ Watch out: report the IQR as two numbers
Write "IQR 74.7 to 93.9", not "IQR 19.2" (the width). Readers want to know where the middle half of patients sits, not just how wide it is. And don't report a median with an SD: they belong to different summaries.
:::

::: {.callout-tip}
## 🔀 R vs Python: quartiles
R's `quantile()` and NumPy's `np.quantile()` use the same default method (R calls it "type 7"), so they agree. Other software doesn't always: gtsummary, SPSS and SAS can give slightly different quartiles on the same data ([page 2](../foundations/02-demographics.qmd#which-summary) shows an example). Say which software you used.
:::

## Proportion {#proportion}

**The question:** What proportion of patients had a complication within 90 days of surgery?

### When to use it

- The outcome is **yes/no** (binomial): complication, readmission, discharge home.
- Report the count, the percentage, and a 95% CI for the percentage.
- If patients were followed for **different lengths of time** and the event can happen at any time (revision, death) → use a [Kaplan-Meier curve](#kaplan-meier) instead.

### Look at the data first

For a yes/no variable, "looking" means counting, including the missing values.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

count(cohort, complication_90d)   # 1 = yes, 0 = no
```

## Python

```{python}
import pandas as pd
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")

print(cohort["complication_90d"].value_counts(dropna=False))   # 1 = yes, 0 = no
```
:::

No missing values, and only the two codes the codebook allows (0 and 1).

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
events   <- sum(cohort$complication_90d == 1)
patients <- nrow(cohort)

events / patients                                           # the proportion

# Wilson 95% CI: prop.test() without the continuity correction
prop.test(events, patients, correct = FALSE)$conf.int
```

## Python

```{python}
events = int((cohort["complication_90d"] == 1).sum())
patients = len(cohort)

print(events / patients)                                    # the proportion

# Wilson 95% CI
print(stats.binomtest(events, patients).proportion_ci(method="wilson"))
```
:::

```{python}
#| include: false
wilson = stats.binomtest(events, patients).proportion_ci(method="wilson")
chk = {"events": float(events), "patients": float(patients),
       "ci_low": float(wilson.low), "ci_high": float(wilson.high)}
```

```{r}
#| include: false
wilson <- prop.test(events, patients, correct = FALSE)$conf.int
check_agree(list(events = events, patients = patients, ci_low = wilson[1], ci_high = wilson[2]),
            reticulate::py$chk)
```

### Read the output

- **51 of 600 = 0.085:** 8.5% of patients had a complication.
- **95% CI 0.065 to 0.110:** the true complication rate for patients like ours is plausibly anywhere from 6.5% to 11.0%.

### How to report it

> **Methods:** Categorical variables are reported as number (percentage). 95% confidence intervals for proportions were calculated with the Wilson score method.
>
> **Results:** Fifty-one patients (8.5%; 95% CI 6.5% to 11.0%) had a complication within 90 days.

::: {.callout-warning}
## ⚠️ Watch out: percent of what?
- **Say what the denominator is.** Here it's 600 *procedures*. Our 80 bilateral patients count twice, so it isn't a percentage of patients. If some outcomes were missing, the denominator is the patients with a known outcome; say how many were missing.
- **Don't use the simple "± 1.96 standard errors" CI** (the Wald interval) for proportions. For rare events it can dip below 0%. The Wilson interval doesn't.
:::

::: {.callout-tip}
## 🔀 R vs Python: which CI for a proportion?
R's `prop.test()` gives the Wilson interval, but adds a continuity correction unless you set `correct = FALSE`. scipy's `proportion_ci()` calls the uncorrected version `"wilson"` and the corrected one `"wilsoncc"`. R's `binom.test()` and scipy's `method="exact"` give the more conservative Clopper-Pearson interval ([page 5](05-one-group-vs-hypothetical.qmd#binomial-test) uses it). All are acceptable; say which you used.
:::

## Kaplan-Meier survival curve {#kaplan-meier}

**The question:** What proportion of implants are still unrevised 5 years after surgery?

### When to use it

- The outcome is **time until an event** (revision, death), and patients were followed for **different lengths of time**.
- Some patients are **censored**: their follow-up ended (the study closed, they moved away, they died) before any revision. We know they went *at least* that long without one.
- A plain percentage ("13.5% were revised") ignores follow-up time: a patient operated on last year hasn't had time to need a revision. The Kaplan-Meier method uses each patient's follow-up for as long as it lasts.

[Page 13](../survival/13-kaplan-meier.qmd) covers survival analysis in depth. This section shows the basic curve.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)
library(ggsurvfit)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

# followup_years: time from surgery to revision or censoring; revised: 1 = revised, 0 = censored
cohort |> select(case_id, followup_years, revised) |> head(4)
cohort |> summarise(patients = n(), revisions = sum(revised),
                    median_followup = median(followup_years))
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts

cohort = pd.read_csv("data/cohort.csv")

# followup_years: time from surgery to revision or censoring; revised: 1 = revised, 0 = censored
print(cohort[["case_id", "followup_years", "revised"]].head(4))
print(len(cohort), cohort["revised"].sum(), cohort["followup_years"].median())
```
:::

Each row needs exactly two things: **how long** the patient was followed and **whether** the follow-up ended with the event (1) or was censored (0). The first case was followed for 6.2 years without a revision; the fifth was revised at 5.8 years.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4.5
km <- survfit2(Surv(followup_years, revised) ~ 1, data = cohort,
               conf.type = "log-log")              # the CI method lifelines uses

km |>
  ggsurvfit() +
  add_confidence_interval() +
  add_risktable() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Revision-free survival")

summary(km, times = 5)                             # the estimate at 5 years
```

## Python

```{python}
km = KaplanMeierFitter()
km.fit(cohort["followup_years"], event_observed=cohort["revised"])

fig, ax = plt.subplots(figsize=(7, 4.5))
km.plot_survival_function(ax=ax, legend=False)
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Revision-free survival")
add_at_risk_counts(km, ax=ax)
plt.tight_layout()
plt.show()

# the estimate and its 95% CI at 5 years
at_5 = km.survival_function_at_times(5).iloc[0]
ci_5 = km.confidence_interval_survival_function_.loc[:5].iloc[-1]   # last step at or before 5 years
print(at_5, ci_5.to_list())
```
:::

```{python}
#| include: false
chk = {"surv_5": float(at_5), "ci_low": float(ci_5.iloc[0]), "ci_high": float(ci_5.iloc[1])}
```

```{r}
#| include: false
km_5 <- summary(km, times = 5)
check_agree(list(surv_5 = km_5$surv, ci_low = km_5$lower, ci_high = km_5$upper), reticulate::py$chk)
```

### Read the output

- **The curve** starts at 100% and steps down at each revision. Censored patients don't make it step; they just leave the group "at risk".
- **The shaded band** is the 95% CI. It widens to the right as fewer patients remain under follow-up.
- **The numbers at risk** under the plot show how many patients were still being followed at each time. Trust the right-hand end of the curve less: by 10 years only a handful remain.
- **At 5 years:** survival 0.863 (95% CI 0.828 to 0.892), with 263 patients still at risk.

### How to report it

> **Methods:** Implant survivorship was estimated with the Kaplan-Meier method, with revision for any reason as the end point. Patients were censored at death or at their last follow-up.
>
> **Results:** Revision-free survival at 5 years was 86.3% (95% CI 82.8% to 89.2%; 263 patients at risk).

::: {.callout-warning}
## ⚠️ Watch out: death isn't just "lost to follow-up"
Treating deaths as censored, as here, assumes the patients who died would have gone on to be revised at the same rate as everyone else. They can't be: a patient who has died can never be revised. When many patients die during follow-up, 1 minus the Kaplan-Meier estimate **overstates** the risk of revision. [Page 13](../survival/13-kaplan-meier.qmd) shows the competing-risks method that fixes this.
:::

::: {.callout-tip}
## 🔀 R vs Python: the confidence band
R's `survfit()` uses a "log" CI by default; lifelines uses "log-log". The estimates are identical but the CIs differ slightly. We set `conf.type = "log-log"` in R so the two match. Log-log keeps the CI between 0% and 100%; say which you used.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
stopifnot(
  nrow(cohort) == 600,
  round(mean(cohort$age), 1) == 65.5, round(sd(cohort$age), 1) == 9.4,
  round(mean(cohort$age) - 2 * sd(cohort$age)) == 47, round(mean(cohort$age) + 2 * sd(cohort$age)) == 84,
  round(age_ci[1], 1) == 64.8, round(age_ci[2], 1) == 66.3,
  round(sd(cohort$age) / sqrt(600), 2) == 0.39,
  length(koos_1yr) == 260,
  round(q[[1]], 1) == 74.7, round(q[[2]], 1) == 85.8, round(q[[3]], 1) == 93.9,
  round(q[[3]] - q[[1]], 1) == 19.2,
  round(m_ci[["lwr.ci"]], 1) == 84.0, round(m_ci[["upr.ci"]], 1) == 88.2,
  round(attr(m_ci, "conf.level"), 4) == 0.9595,
  events == 51, round(100 * events / patients, 1) == 8.5,
  round(100 * wilson[1], 1) == 6.5, round(100 * wilson[2], 1) == 11.0,
  sum(table(cohort$patient_id) == 2) == 80,
  round(100 * mean(cohort$revised), 1) == 13.5,
  cohort$followup_years[1] > 6.2, cohort$followup_years[1] < 6.25, cohort$revised[1] == 0,
  round(cohort$followup_years[5], 1) == 5.8, cohort$revised[5] == 1,
  round(km_5$surv, 3) == 0.863, round(km_5$lower, 3) == 0.828, round(km_5$upper, 3) == 0.892,
  km_5$n.risk == 263,
  # exercise solutions
  round(mean(cohort$bmi), 1) == 30.4, round(sd(cohort$bmi), 1) == 5.4,
  round(t.test(cohort$bmi)$conf.int[1], 1) == 30.0, round(t.test(cohort$bmi)$conf.int[2], 1) == 30.9,
  round(mean(cohort$los_days), 1) == 0.9, round(sd(cohort$los_days), 1) == 1.1,
  all(quantile(cohort$los_days, c(0.25, 0.5, 0.75)) == c(0, 1, 1)),
  round(100 * prop.test(27, 600, correct = FALSE)$conf.int, 1) == c(3.1, 6.5),
  sum(cohort$readmit_90d) == 27
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Describe **BMI** in the cohort with a mean, SD and 95% CI for the mean. Check the histogram first: is the mean a fair summary?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
ggplot(cohort, aes(bmi)) + geom_histogram(binwidth = 1)
cohort |> summarise(n = n(), mean = mean(bmi), sd = sd(bmi))
t.test(cohort$bmi)$conf.int
```

## Python

```{python}
fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(cohort["bmi"], bins=range(18, 46))
plt.show()
n, mean, sd = cohort["bmi"].count(), cohort["bmi"].mean(), cohort["bmi"].std()
print(n, mean, sd, stats.t.interval(0.95, df=n - 1, loc=mean, scale=sd / n ** 0.5))
```
:::

The histogram is roughly symmetric, so the mean is fair: mean BMI 30.4 kg/m² (SD 5.4; 95% CI for the mean 30.0 to 30.9).
:::

**2.** A resident wants to summarize **length of stay** in a Table 1 as "0.9 ± 1.1 days". What would you suggest instead, and why? Compute it.

::: {.callout-tip collapse="true"}
## Solution
Length of stay is strongly right-skewed (most patients go home on day 0 or 1, a few stay 4 to 6 days), so report the median (IQR). "±" is also ambiguous: SD or SEM?

::: {.panel-tabset group="language"}
## R

```{r}
quantile(cohort$los_days, probs = c(0.25, 0.50, 0.75))
```

## Python

```{python}
import numpy as np
print(np.quantile(cohort["los_days"], [0.25, 0.50, 0.75]))
```
:::

Median 1 day (IQR 0 to 1).
:::

**3.** Twenty-seven of the 600 patients were readmitted within 90 days. Write the Results sentence, with a Wilson 95% CI.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
prop.test(27, 600, correct = FALSE)$conf.int
```

## Python

```{python}
print(stats.binomtest(27, 600).proportion_ci(method="wilson"))
```
:::

"Twenty-seven patients (4.5%; 95% CI 3.1% to 6.5%) were readmitted within 90 days."
:::
````

- [ ] **Step 4: Render it**

Run: `quarto render catalog/04-describe-one-group.qmd`

Expected: the render completes. No `check_agree()` disagreement, and no prose-guard `stopifnot` error.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/site -q`

Expected: all pass except `test_just_data_re_renders_the_pages_that_read_data`, which FAILS with ``` `just data` must re-render: ['catalog'] ```. Page 4 now reads `data/`.

- [ ] **Step 6: Re-render the catalog in `just data`**

In `Justfile`, replace

```
    # Freeze only notices .qmd changes, so re-render every folder whose pages read data/.
    # (Rendering a folder always re-runs its code.) Add catalog, survival, ... as they gain code.
    quarto render foundations
```

with

```
    # Freeze only notices .qmd changes, so re-render every folder whose pages read data/.
    # (Rendering a folder always re-runs its code.) Add survival, beyond, ... as they gain code.
    quarto render foundations
    quarto render catalog
```

Run: `uv run pytest tests/site -q`

Expected: `78 passed`.

- [ ] **Step 7: Prove the guards bite, then restore**

1. In the page's `# Prose guard` chunk, change `round(km_5$surv, 3) == 0.863` to `== 0.864`, then run `quarto render catalog/04-describe-one-group.qmd`. Expected: the render FAILS with `round(km_5$surv, 3) == 0.864 is not TRUE`. Undo the change.
2. In the `#proportion` section's first R block, delete the line `cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)`, then run `uv run pytest tests/site/test_sources.py -q`. Expected: `test_each_catalog_section_loads_its_own_packages_and_data` FAILS, naming `catalog/04-describe-one-group.qmd#proportion`. Undo the change.

Then run:

```bash
rm -rf catalog/04-describe-one-group_files
quarto render catalog/04-describe-one-group.qmd
uv run pytest tests/site -q
git status --short
```

Expected: `78 passed`. `git status` lists only this task's files.

- [ ] **Step 8: Commit**

```bash
git add catalog/04-describe-one-group.qmd _freeze/catalog/04-describe-one-group tests/site/test_catalog.py tests/site/test_sources.py tests/site/test_freshness.py Justfile
git commit -m "Write page 4, Describe one group: mean/SD, median/IQR, proportion, Kaplan-Meier

Adds the catalog test harness (section anatomy, self-contained sections, R/Python checks).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Page 5, Compare one group to a hypothetical value

**Files:**
- Modify: `catalog/05-one-group-vs-hypothetical.qmd` (replace the stub)
- Create: `_freeze/catalog/05-one-group-vs-hypothetical/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Task 3's `WRITTEN` list and test harness
  - page 4's `#proportion` anchor
  - page 6's `#mann-whitney` and page 7's `#wilcoxon-signed-rank` anchors (the stubs already have them)
- Produces: page 5 anchors `#one-sample-t`, `#wilcoxon-signed-rank`, `#chi-square-gof` and `#binomial-test`. Page 7 links to `#binomial-test`.

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_catalog.py -q`

Expected: 10 of the 12 new page-5 tests FAIL; the no-warnings and short-outputs tests pass trivially on a stub. The 13 page-4 tests pass.

- [ ] **Step 3: Write the page**

Replace `catalog/05-one-group-vs-hypothetical.qmd` with:

````markdown
---
title: "5 · Compare one group to a hypothetical value"
description: "One-sample t test, Wilcoxon signed-rank test, chi-square goodness-of-fit test and binomial test: is our group different from a target or published value?"
engine: knitr
toc-depth: 2
execute:
  message: false
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

Sometimes there is only one group of patients, and the comparison is with a number that comes from **outside** your data: a target set by the hospital, a value published by a registry, a benchmark in a quality report. Is our group different from that number?

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom. The "hypothetical" values below are made up for teaching; they aren't real registry figures.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

::: {.callout-warning}
## ⚠️ Watch out: the value must come from outside your data
Choose the hypothetical value **before** you look at your data, and say where it came from. A value picked after seeing the results ("our mean is 84; let's test against 90") makes the p-value meaningless. If the comparison value comes from another group of patients whose data you have, compare the two groups instead ([page 6](06-two-unpaired-groups.qmd)).
:::

## One-sample t test {#one-sample-t}

**The question:** The operating room books 90 minutes for every primary joint replacement. Is our average operative time different from 90 minutes?

### When to use it

- The outcome is a **measurement** (minutes, kg/m², points).
- It's **roughly normal**, or the sample is large (about 30 or more) and not badly skewed ([page 3](../foundations/03-distributions.qmd#robustness)).
- Each patient is counted once and patients are independent of each other.
- If the data are skewed, bounded or ordinal → the [Wilcoxon signed-rank test](#wilcoxon-signed-rank).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

ggplot(cohort, aes(op_time_min)) +
  geom_histogram(binwidth = 5) +
  geom_vline(xintercept = 90, linetype = "dashed") +   # the booked time
  labs(x = "Operative time, minutes", y = "Patients")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(cohort["op_time_min"], bins=range(45, 145, 5))
ax.axvline(90, linestyle="--")                        # the booked time
ax.set_xlabel("Operative time, minutes")
ax.set_ylabel("Patients")
plt.show()
```
:::

A roughly symmetric hump, centered a little to the left of the dashed line at 90 minutes.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
op_test <- t.test(cohort$op_time_min, mu = 90)   # mu = the hypothetical mean
op_test
```

## Python

```{python}
op_test = stats.ttest_1samp(cohort["op_time_min"], popmean=90)   # popmean = the hypothetical mean
print(op_test)
print(cohort["op_time_min"].mean(), op_test.confidence_interval())
```
:::

```{python}
#| include: false
op_ci = op_test.confidence_interval()
chk = {"t": float(op_test.statistic), "df": float(op_test.df), "p": float(op_test.pvalue),
       "ci_low": float(op_ci.low), "ci_high": float(op_ci.high)}
```

```{r}
#| include: false
check_agree(list(t = unname(op_test$statistic), df = unname(op_test$parameter), p = op_test$p.value,
                 ci_low = op_test$conf.int[1], ci_high = op_test$conf.int[2]), reticulate::py$chk)
```

### Read the output

- **t = −8.23:** the observed mean is 8.2 standard errors below 90. The sign says which side.
- **df = 599:** degrees of freedom, n − 1.
- **p < 0.001:** a mean this far from 90 would be very unlikely if the true average were 90 minutes.
- **mean of x = 84.48:** our average operative time.
- **95% CI 83.2 to 85.8:** the CI for our **mean**, not for the difference from 90.

### Effect size and 95% CI

The effect size is simply the difference from the hypothetical value: subtract 90 from the mean and from both ends of its CI.

::: {.panel-tabset group="language"}
## R

```{r}
op_test$estimate - 90    # mean difference
op_test$conf.int - 90    # its 95% CI
```

## Python

```{python}
print(cohort["op_time_min"].mean() - 90)                        # mean difference
print(op_test.confidence_interval().low - 90, op_test.confidence_interval().high - 90)   # its 95% CI
```
:::

```{python}
#| include: false
chk = {"diff": float(cohort["op_time_min"].mean() - 90),
       "diff_low": float(op_ci.low - 90), "diff_high": float(op_ci.high - 90)}
```

```{r}
#| include: false
check_agree(list(diff = unname(op_test$estimate - 90), diff_low = op_test$conf.int[1] - 90,
                 diff_high = op_test$conf.int[2] - 90), reticulate::py$chk)
```

Operations took 5.5 minutes less than the booked 90 on average (95% CI 4.2 to 6.8 minutes less). Whether that matters is a scheduling question, not a statistical one: over a day of four joints, it adds up to about 20 minutes.

### How to report it

> **Methods:** Mean operative time was compared with the 90 minutes booked per case using a one-sample t test.
>
> **Results:** Mean operative time was 84.5 minutes (SD 16.4), 5.5 minutes shorter than the 90 minutes booked (95% CI 4.2 to 6.8 minutes shorter; p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: a published mean has its own uncertainty
A one-sample test treats the hypothetical value as exact. A registry mean is itself an estimate with a CI. If you're comparing your patients with a published series and its CI is wide, say so, and don't over-read a small difference.
:::

::: {.callout-tip}
## 🔀 R vs Python: what the CI is a CI for
Both R's `t.test(x, mu = 90)` and scipy's `ttest_1samp(x, popmean=90)` report the CI for the **mean** (83.2 to 85.8), not for the difference from 90. Subtract the hypothetical value yourself, as above.
:::

## Wilcoxon signed-rank test {#wilcoxon-signed-rank}

**The question:** Suppose our practice's target is a 1-year KOOS JR of 80 points after knee replacement. Is our typical patient's score different from 80?

### When to use it

- The outcome is **skewed** or has a **ceiling or floor**, so a mean isn't a fair summary ([page 3](../foundations/03-distributions.qmd#transform)).
- It ranks how far each patient is above or below the hypothetical value. It doesn't assume a normal distribution, but it does need distances that can be compared, so the outcome must be a measurement.
- For an **ordinal** scale (satisfaction from 1 to 5), count the patients above and below the value and compare the two counts with a [binomial test](#binomial-test). This is called the **sign test**.
- Strictly, it tests the **pseudomedian** (the Hodges-Lehmann estimate below), which equals the median only for a symmetric distribution. With a ceiling the two differ a little; report both.
- If the data are roughly normal → the [one-sample t test](#one-sample-t) is more familiar and slightly more powerful.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)
koos_1yr <- proms |>
  filter(instrument == "KOOS JR", visit == "1yr", !is.na(prom_score)) |>
  pull(prom_score)

ggplot(tibble(score = koos_1yr), aes(score)) +
  geom_histogram(binwidth = 2.5) +
  geom_vline(xintercept = 80, linetype = "dashed") +   # the target
  labs(x = "KOOS JR at 1 year (100 = best)", y = "Patients")
```

## Python

```{python}
import numpy as np
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
from scipy import stats

proms = pd.read_csv("data/proms_long.csv")
koos_1yr = proms.loc[(proms["instrument"] == "KOOS JR") & (proms["visit"] == "1yr"),
                     "prom_score"].dropna()

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(koos_1yr, bins=np.arange(35, 102.5, 2.5))
ax.axvline(80, linestyle="--")                         # the target
ax.set_xlabel("KOOS JR at 1 year (100 = best)")
ax.set_ylabel("Patients")
plt.show()
```
:::

A ceiling at 100 and a long tail to the left: the rank-based test is the safer choice.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
koos_test <- wilcox.test(koos_1yr, mu = 80,
                         exact = FALSE, correct = FALSE,   # see the R vs Python box
                         conf.int = TRUE)                  # adds the Hodges-Lehmann estimate and CI
koos_test
```

## Python

```{python}
# pg.wilcoxon() runs scipy's test and adds the rank-biserial effect size
koos_test = pg.wilcoxon(koos_1yr - 80, method="approx", correction=False)   # see the R vs Python box
print(koos_test)
```
:::

```{python}
#| include: false
chk = {"p": float(koos_test["p_val"].iloc[0])}
```

```{r}
#| include: false
check_agree(list(p = koos_test$p.value), reticulate::py$chk)
```

### Read the output

- **V = 22698** (R) or **W_val = 11231.5** (Python): the test statistic, a sum of ranks. The two programs report different sums (see the R vs Python box); the p-values are the same.
- **p < 0.001:** scores this far from 80 would be very unlikely if the typical patient really scored 80.
- **(pseudo)median 84.35, 95% CI 82.7 to 86.1** (R only): the Hodges-Lehmann estimate of the center of the scores, with its CI.
- **RBC = 0.34** (Python): the rank-biserial effect size, below.

### Effect size and 95% CI

Two effect sizes are useful here:

- The **Hodges-Lehmann estimate** (the pseudomedian): a center of the scores, in points. It's the median of all the averages of pairs of scores, so it's less affected by the ceiling than a mean.
- The **rank-biserial correlation (r)**: from −1 (every patient below 80) through 0 (balanced) to +1 (every patient above 80). As a rough guide, 0.1 is small, 0.3 moderate and 0.5 large.

::: {.panel-tabset group="language"}
## R

```{r}
koos_test$estimate                                   # Hodges-Lehmann estimate
koos_test$conf.int                                   # its 95% CI

effectsize::rank_biserial(koos_1yr, mu = 80)         # rank-biserial r and 95% CI
```

## Python

```{python}
# Hodges-Lehmann estimate: the median of the averages of every pair of scores
def hodges_lehmann(x):
    x = np.asarray(x)
    i, j = np.triu_indices(len(x))          # every pair, including each score with itself
    return np.median((x[i] + x[j]) / 2)

print(hodges_lehmann(koos_1yr))

# scipy has no CI for it, so use a bootstrap: recompute it on 9999 resampled datasets
boot = stats.bootstrap((koos_1yr.to_numpy(),), hodges_lehmann, vectorized=False,
                       rng=np.random.default_rng(2026))
print(boot.confidence_interval)

print(koos_test["RBC"])                               # rank-biserial r
```
:::

```{python}
#| include: false
chk = {"hl": float(hodges_lehmann(koos_1yr)), "rbc": float(koos_test["RBC"].iloc[0])}
```

```{r}
#| include: false
koos_rb <- effectsize::rank_biserial(koos_1yr, mu = 80)
check_agree(list(hl = unname(koos_test$estimate), rbc = koos_rb$r_rank_biserial), reticulate::py$chk,
            tol = 1e-4)   # R finds the Hodges-Lehmann estimate by root-finding, accurate to about 1e-5
```

The typical 1-year score was about 4 points above the target (Hodges-Lehmann estimate 84.4), and the rank-biserial r of 0.34 is a moderate effect: noticeably more patients scored above 80 than below.

### How to report it

> **Methods:** Because 1-year KOOS JR scores showed a ceiling effect, they were compared with the 80-point target using a Wilcoxon signed-rank test, with the Hodges-Lehmann estimate and its 95% CI as the effect size.
>
> **Results:** The median 1-year KOOS JR was 85.8 points (IQR 74.7 to 93.9), above the 80-point target (Hodges-Lehmann estimate 84.4, 95% CI 82.7 to 86.1; rank-biserial r = 0.34; p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: two different "Wilcoxon" tests
The **Wilcoxon signed-rank test** (this one) compares one group with a value, or two **paired** measurements ([page 7](07-two-paired-groups.qmd#wilcoxon-signed-rank)). The **Wilcoxon rank-sum test** compares two **independent** groups; it's the same as the [Mann-Whitney test](06-two-unpaired-groups.qmd#mann-whitney). Always write the full name.

Also: patients who score **exactly** 80 carry no information about the direction and are dropped from the test.
:::

::: {.callout-tip}
## 🔀 R vs Python: Wilcoxon defaults
- **The statistic.** R reports V, the sum of the ranks of patients **above** 80 (22698.5, printed as 22698). scipy (and pingouin) report the **smaller** of the two sums (11231.5). The two sums always add up to n(n + 1)/2, here 260 × 261 / 2 = 33,930, so they carry the same information and give the same p-value.
- **Exact or approximate.** For small samples without ties, both programs compute an exact p-value; otherwise they use a normal approximation. R adds a **continuity correction** to the approximation by default; scipy doesn't. We set `exact = FALSE, correct = FALSE` in R and `method="approx", correction=False` in Python so they match.
- **The Hodges-Lehmann CI.** R computes it by inverting the test. scipy has no function for it, so the Python code uses a bootstrap, a different method, so the two CIs differ slightly (82.75 to 86.10 in R, 82.70 to 86.05 from the bootstrap).
:::

## Chi-square goodness-of-fit test {#chi-square-gof}

**The question:** Suppose a national registry reports that its patients are 10% ASA class 1, 55% class 2, 33% class 3 and 2% class 4. Is our mix of ASA classes the same?

### When to use it

- The outcome is **categorical** with two or more categories, and you have hypothetical proportions for every category.
- Each patient falls in exactly one category, and is counted once.
- The **expected count** in every category (total × hypothetical proportion) should be at least 5. Otherwise combine small categories, or with only two categories use the [binomial test](#binomial-test).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)
registry <- c(0.10, 0.55, 0.33, 0.02)                 # the hypothetical proportions, ASA 1 to 4

asa_counts <- table(cohort$asa)
tibble(asa = names(asa_counts), observed = as.vector(asa_counts),
       expected = sum(asa_counts) * registry)
```

## Python

```{python}
import pandas as pd
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
registry = [0.10, 0.55, 0.33, 0.02]                   # the hypothetical proportions, ASA 1 to 4

asa_counts = cohort["asa"].value_counts().sort_index()
print(pd.DataFrame({"observed": asa_counts, "expected": asa_counts.sum() * pd.Series(registry, index=asa_counts.index)}))
```
:::

All four expected counts are at least 5 (the smallest is 12). We have fewer ASA 1 and more ASA 3 patients than the registry would predict.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
asa_test <- chisq.test(asa_counts, p = registry)   # p = the hypothetical proportions
asa_test
```

## Python

```{python}
expected = asa_counts.sum() * pd.Series(registry, index=asa_counts.index)
asa_test = stats.chisquare(asa_counts, f_exp=expected)   # f_exp = the expected COUNTS
print(asa_test)
```
:::

```{python}
#| include: false
chk = {"chisq": float(asa_test.statistic), "p": float(asa_test.pvalue)}
```

```{r}
#| include: false
check_agree(list(chisq = unname(asa_test$statistic), p = asa_test$p.value), reticulate::py$chk)
```

### Read the output

- **X-squared = 26.96:** the chi-square statistic, adding up how far each observed count is from its expected count.
- **df = 3:** degrees of freedom, the number of categories minus 1.
- **p < 0.001:** a mix this different from the registry's would be very unlikely if our patients came from the same mix.

### Effect size and 95% CI

The test says the mix differs, not where. Look at each category's observed percentage, with a 95% CI, next to the registry's.

::: {.panel-tabset group="language"}
## R

```{r}
asa_ci <- sapply(asa_counts, function(k) prop.test(k, sum(asa_counts), correct = FALSE)$conf.int)

tibble(asa = names(asa_counts),
       observed_pct = 100 * as.vector(asa_counts) / sum(asa_counts),
       ci_low = 100 * asa_ci[1, ], ci_high = 100 * asa_ci[2, ],   # Wilson CIs, as on page 4
       registry_pct = 100 * registry)
```

## Python

```{python}
n = asa_counts.sum()
cis = [stats.binomtest(int(k), int(n)).proportion_ci(method="wilson") for k in asa_counts]

print(pd.DataFrame({
    "observed_pct": 100 * asa_counts / n,
    "ci_low": [100 * ci.low for ci in cis],                     # Wilson CIs, as on page 4
    "ci_high": [100 * ci.high for ci in cis],
    "registry_pct": [100 * p for p in registry],
}, index=asa_counts.index))
```
:::

```{python}
#| include: false
chk = {f"low_{k}": float(ci.low) for k, ci in zip(asa_counts.index, cis)} | \
      {f"high_{k}": float(ci.high) for k, ci in zip(asa_counts.index, cis)}
```

```{r}
#| include: false
check_agree(c(setNames(as.list(asa_ci[1, ]), paste0("low_", names(asa_counts))),
              setNames(as.list(asa_ci[2, ]), paste0("high_", names(asa_counts)))), reticulate::py$chk)
```

ASA 3 makes the biggest difference: 41.0% of our patients (95% CI 37.1% to 45.0%) against 33% in the registry. The CI doesn't include 33%.

### How to report it

> **Methods:** The distribution of ASA classes was compared with the registry's using a chi-square goodness-of-fit test.
>
> **Results:** Our patients' ASA classes differed from the registry's (χ² = 27.0, df = 3, p < 0.001). More of our patients were ASA class 3 (41.0%, 95% CI 37.1% to 45.0%, vs 33% in the registry) and fewer were ASA class 1 (6.0% vs 10%).

::: {.callout-warning}
## ⚠️ Watch out: counts, not percentages
The test needs the **counts** of patients in each category. Feeding it percentages ("6, 50, 41, 3") gives a wrong p-value, because the test's precision depends on how many patients there are.
:::

::: {.callout-tip}
## 🔀 R vs Python: proportions or counts
R's `chisq.test(counts, p = ...)` takes the hypothetical **proportions** (they must add up to 1). scipy's `chisquare(counts, f_exp=...)` takes the expected **counts** (they must add up to the observed total). Same test, different inputs.
:::

## Binomial test {#binomial-test}

**The question:** Suppose a state quality report gives a 90-day readmission rate of 6% after primary joint replacement. Is our rate different?

### When to use it

- The outcome is **yes/no**, and you're comparing one group's proportion with a hypothetical proportion.
- Each patient is counted once.
- The binomial test is **exact**: it works for any sample size, including small numbers of events. (The chi-square goodness-of-fit test with two categories is its large-sample approximation.)

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

count(cohort, readmit_90d)   # 1 = readmitted within 90 days
```

## Python

```{python}
import pandas as pd
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")

print(cohort["readmit_90d"].value_counts(dropna=False))   # 1 = readmitted within 90 days
```
:::

27 readmissions among 600 patients, with no missing values.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
readmitted <- sum(cohort$readmit_90d == 1)
patients   <- nrow(cohort)

readmit_test <- binom.test(readmitted, patients, p = 0.06)   # p = the hypothetical proportion
readmit_test
```

## Python

```{python}
readmitted = int((cohort["readmit_90d"] == 1).sum())
patients = len(cohort)

readmit_test = stats.binomtest(readmitted, patients, p=0.06)   # p = the hypothetical proportion
print(readmit_test)
print(readmit_test.proportion_ci(method="exact"))
```
:::

```{python}
#| include: false
readmit_ci = readmit_test.proportion_ci(method="exact")
chk = {"p": float(readmit_test.pvalue), "estimate": float(readmit_test.statistic),
       "ci_low": float(readmit_ci.low), "ci_high": float(readmit_ci.high)}
```

```{r}
#| include: false
check_agree(list(p = readmit_test$p.value, estimate = unname(readmit_test$estimate),
                 ci_low = readmit_test$conf.int[1], ci_high = readmit_test$conf.int[2]), reticulate::py$chk)
```

### Read the output

- **number of successes = 27, number of trials = 600:** 27 readmissions ("successes" is just the software's word for the outcome you counted).
- **p = 0.143:** a rate this far from 6% wouldn't be unusual if our true rate were 6%.
- **probability of success = 0.045:** our readmission rate, 4.5%.
- **95% CI 0.030 to 0.065:** our true rate is plausibly anywhere from 3.0% to 6.5%. This is the exact (Clopper-Pearson) interval.

### Effect size and 95% CI

The effect size is the difference from the hypothetical rate: 4.5% − 6% = −1.5 percentage points. Its 95% CI is the CI for our rate minus 6%: −3.0 to +0.5 percentage points. It includes 0, which matches the p-value above 0.05.

### How to report it

> **Methods:** The 90-day readmission rate was compared with the state benchmark of 6% using an exact binomial test. 95% CIs for proportions are exact (Clopper-Pearson).
>
> **Results:** Twenty-seven patients (4.5%; 95% CI 3.0% to 6.5%) were readmitted within 90 days. This did not differ significantly from the 6% benchmark (p = 0.143).

::: {.callout-warning}
## ⚠️ Watch out: "not significantly different" doesn't mean "the same"
Our rate could be as low as 3.0% (half the benchmark) or as high as 6.5%. The data are compatible with being better than the benchmark *and* with being about the same. Don't write "our readmission rate was equivalent to the benchmark", and don't write "lower" either; report the CI and let it speak.
:::

::: {.callout-tip}
## 🔀 R vs Python: exact CIs
R's `binom.test()` and scipy's `binomtest()` agree on the p-value. R prints the exact (Clopper-Pearson) CI automatically; in scipy, ask for it with `proportion_ci(method="exact")`. It's a little wider than the Wilson interval on [page 4](04-describe-one-group.qmd#proportion) (3.1% to 6.5% for the same 27 patients). Either is fine; say which you used.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
asa_pct <- 100 * as.vector(asa_counts) / sum(asa_counts)
stopifnot(
  sum(table(cohort$patient_id) == 2) == 80,
  round(unname(op_test$statistic), 2) == -8.23, unname(op_test$parameter) == 599, op_test$p.value < 0.001,
  round(unname(op_test$estimate), 2) == 84.48, round(mean(cohort$op_time_min), 1) == 84.5,
  round(sd(cohort$op_time_min), 1) == 16.4,
  round(op_test$conf.int, 1) == c(83.2, 85.8),
  round(unname(op_test$estimate) - 90, 1) == -5.5, round(op_test$conf.int - 90, 1) == c(-6.8, -4.2),
  length(koos_1yr) == 260,
  unname(koos_test$statistic) == 22698.5, koos_test$p.value < 0.001,
  sum(koos_1yr != 80) == 260, 260 * 261 / 2 - unname(koos_test$statistic) == 11231.5,
  round(unname(koos_test$estimate), 2) == 84.35, round(unname(koos_test$estimate), 1) == 84.4,
  round(koos_test$conf.int, 1) == c(82.7, 86.1), round(koos_test$conf.int, 2) == c(82.75, 86.10),
  round(reticulate::py_eval("[float(boot.confidence_interval.low), float(boot.confidence_interval.high)]"), 2) == c(82.70, 86.05),
  round(koos_rb$r_rank_biserial, 2) == 0.34,
  round(median(koos_1yr), 1) == 85.8, round(quantile(koos_1yr, c(0.25, 0.75)), 1) == c(74.7, 93.9),
  as.vector(asa_counts) == c(36, 300, 246, 18),
  min(sum(asa_counts) * registry) == 12,
  round(unname(asa_test$statistic), 2) == 26.96, round(unname(asa_test$statistic), 1) == 27.0,
  unname(asa_test$parameter) == 3, asa_test$p.value < 0.001,
  round(asa_pct, 1) == c(6.0, 50.0, 41.0, 3.0),
  round(100 * asa_ci[, "3"], 1) == c(37.1, 45.0),
  readmitted == 27, patients == 600,
  round(readmit_test$p.value, 3) == 0.143,
  round(unname(readmit_test$estimate), 3) == 0.045,
  round(readmit_test$conf.int, 3) == c(0.030, 0.065),
  round(100 * (readmit_test$conf.int - 0.06), 1) == c(-3.0, 0.5),
  round(100 * prop.test(27, 600, correct = FALSE)$conf.int, 1) == c(3.1, 6.5),
  # exercise solutions
  round(mean(cohort$age), 1) == 65.5, round(mean(cohort$age) - 66, 1) == -0.5,
  round(t.test(cohort$age, mu = 66)$conf.int - 66, 1) == c(-1.2, 0.3),
  round(t.test(cohort$age, mu = 66)$p.value, 3) == 0.213,
  sum(cohort$discharge == "home") == 570,
  round(100 * binom.test(570, 600)$conf.int, 1) == c(92.9, 96.6), binom.test(570, 600, p = 0.90)$p.value < 0.001,
  round(100 * prop.table(table(cohort$smoker))[c("never", "former", "current")], 1) == c(53.5, 38.3, 8.2),
  round(unname(chisq.test(table(cohort$smoker)[c("never", "former", "current")], p = c(0.5, 0.4, 0.1))$statistic), 1) == 3.9,
  round(chisq.test(table(cohort$smoker)[c("never", "former", "current")], p = c(0.5, 0.4, 0.1))$p.value, 3) == 0.142
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Suppose a registry reports a mean age of 66 years at primary joint replacement. Is our patients' mean age different? Run the test and report the mean difference with its 95% CI.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
age_test <- t.test(cohort$age, mu = 66)
age_test
age_test$conf.int - 66
```

## Python

```{python}
age_test = stats.ttest_1samp(cohort["age"], popmean=66)
print(age_test)
ci = age_test.confidence_interval()
print(cohort["age"].mean() - 66, ci.low - 66, ci.high - 66)
```
:::

Mean age was 65.5 years, 0.5 years younger than the registry (95% CI 1.2 years younger to 0.3 years older; p = 0.213). The data are compatible with no difference, and the CI rules out a difference of more than about a year.
:::

**2.** A state report says 90% of joint replacement patients go home rather than to a facility. 570 of our 600 patients went home. Which test would you use, and what do you conclude?

::: {.callout-tip collapse="true"}
## Solution
A yes/no outcome compared with a hypothetical proportion: the **binomial test**.

::: {.panel-tabset group="language"}
## R

```{r}
binom.test(570, 600, p = 0.90)
```

## Python

```{python}
home = stats.binomtest(570, 600, p=0.90)
print(home.pvalue, home.proportion_ci(method="exact"))
```
:::

95.0% of our patients went home (95% CI 92.9% to 96.6%), more than the 90% in the report (p < 0.001).
:::

**3.** Suppose a survey of joint replacement patients found 50% never smokers, 40% former smokers and 10% current smokers. Test whether our smoking mix differs, and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
smoking <- table(factor(cohort$smoker, levels = c("never", "former", "current")))
smoking
chisq.test(smoking, p = c(0.50, 0.40, 0.10))
```

## Python

```{python}
smoking = cohort["smoker"].value_counts()[["never", "former", "current"]]
print(smoking)
print(stats.chisquare(smoking, f_exp=smoking.sum() * pd.Series([0.50, 0.40, 0.10], index=smoking.index)))
```
:::

"Our patients' smoking status (53.5% never, 38.3% former, 8.2% current smokers) did not differ significantly from the survey's (χ² = 3.9, df = 2, p = 0.142)."
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/05-one-group-vs-hypothetical.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `90 passed`.

- [ ] **Step 5: Prove the prose guard bites, then restore**

In the page's `# Prose guard` chunk, change `round(readmit_test$p.value, 3) == 0.143` to `== 0.144`, then run `quarto render catalog/05-one-group-vs-hypothetical.qmd`. Expected: the render FAILS with `round(readmit_test$p.value, 3) == 0.144 is not TRUE`. Undo the change, then run:

```bash
rm -rf catalog/05-one-group-vs-hypothetical_files
quarto render catalog/05-one-group-vs-hypothetical.qmd
uv run pytest tests/site -q
```

Expected: `90 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/05-one-group-vs-hypothetical.qmd _freeze/catalog/05-one-group-vs-hypothetical tests/site/test_catalog.py
git commit -m "Write page 5, one group vs a hypothetical value: one-sample t, Wilcoxon, goodness-of-fit, binomial

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Page 6, Compare two unpaired groups

**Files:**
- Modify: `catalog/06-two-unpaired-groups.qmd` (replace the stub)
- Create: `_freeze/catalog/06-two-unpaired-groups/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes: Task 3's harness, and page 4's `#kaplan-meier` anchor.
- Produces: page 6 anchors `#unpaired-t`, `#mann-whitney`, `#fisher-chi-square` and `#log-rank`. Page 7 links to `#mann-whitney`; page 3 already links to all four.

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
]
```

and append (after two blank lines):

```python
def test_log_rank_section_names_the_mantel_haenszel_test(site):
    assert "Mantel-Haenszel" in text_of(section("catalog/06-two-unpaired-groups.html", "log-rank"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_catalog.py -q`

Expected: 12 of the 14 new page-6 tests FAIL; the no-warnings and short-outputs tests pass trivially on a stub. The 25 earlier tests pass.

- [ ] **Step 3: Write the page**

Replace `catalog/06-two-unpaired-groups.qmd` with:

````markdown
---
title: "6 · Compare two unpaired groups"
description: "Unpaired (Welch's) t test, Mann-Whitney test, Fisher's exact and chi-square tests, and the log-rank test, each with an effect size and 95% CI."
engine: knitr
toc-depth: 2
execute:
  message: false
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

Two groups of **different** patients: THA vs TKA, men vs women, implant A vs implant C. This is the most common comparison in clinical research. If the same patients are measured twice, or patients were matched in pairs, use [page 7](07-two-paired-groups.qmd) instead.

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

## Unpaired t test {#unpaired-t}

**The question:** Do TKA patients have a higher BMI than THA patients?

### When to use it

- The outcome is a **measurement**, compared between **two independent groups**.
- Within **each group** it's roughly normal, or each group is large (about 30 or more) and not badly skewed ([page 3](../foundations/03-distributions.qmd#within-groups)).
- Use **Welch's** version, which doesn't assume the two groups have the same spread. It's R's default, but not Python's (see the R vs Python box).
- If the outcome is skewed, bounded or ordinal → the [Mann-Whitney test](#mann-whitney).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 4
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(procedure = factor(procedure, levels = c("TKA", "THA")))   # TKA first: differences are TKA minus THA

ggplot(cohort, aes(bmi)) +
  geom_histogram(binwidth = 1) +
  facet_wrap(~ procedure, ncol = 1) +
  labs(x = "BMI, kg/m²", y = "Patients")

cohort |>
  group_by(procedure) |>
  summarise(n = n(), mean = mean(bmi), sd = sd(bmi))
```

## Python

```{python}
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
tka = cohort.loc[cohort["procedure"] == "TKA", "bmi"]
tha = cohort.loc[cohort["procedure"] == "THA", "bmi"]

fig, axes = plt.subplots(2, 1, figsize=(6, 4), sharex=True)
axes[0].hist(tka, bins=range(18, 46))
axes[0].set_title("TKA")
axes[1].hist(tha, bins=range(18, 46))
axes[1].set_title("THA")
axes[1].set_xlabel("BMI, kg/m²")
plt.tight_layout()
plt.show()

print(cohort.groupby("procedure")["bmi"].agg(["count", "mean", "std"]))
```
:::

Both groups are roughly bell-shaped with similar spreads, and both are large. TKA patients sit a little to the right.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
bmi_test <- t.test(bmi ~ procedure, data = cohort)   # Welch's t test is R's default
bmi_test
```

## Python

```{python}
bmi_test = stats.ttest_ind(tka, tha, equal_var=False)   # equal_var=False: Welch's t test
print(bmi_test)
print(tka.mean() - tha.mean(), bmi_test.confidence_interval())
```
:::

```{python}
#| include: false
bmi_ci = bmi_test.confidence_interval()
chk = {"t": float(bmi_test.statistic), "df": float(bmi_test.df), "p": float(bmi_test.pvalue),
       "ci_low": float(bmi_ci.low), "ci_high": float(bmi_ci.high)}
```

```{r}
#| include: false
check_agree(list(t = unname(bmi_test$statistic), df = unname(bmi_test$parameter), p = bmi_test$p.value,
                 ci_low = bmi_test$conf.int[1], ci_high = bmi_test$conf.int[2]), reticulate::py$chk)
```

### Read the output

- **t = 4.07:** the difference between the means is about 4 standard errors.
- **df = 580.09:** Welch's test adjusts the degrees of freedom for unequal spreads, so they aren't a whole number.
- **p < 0.001:** a difference this large would be very unlikely if the two groups had the same mean BMI.
- **95% CI 0.92 to 2.65:** the CI for the **difference in means**, TKA minus THA.
- **mean in group TKA 31.2, mean in group THA 29.5:** the two means.

### Effect size and 95% CI

- The **mean difference** with its CI is the effect size readers understand best: 1.8 kg/m² (95% CI 0.9 to 2.6).
- **Hedges' g** expresses the difference in standard deviations, which lets you compare effects measured on different scales. As a rough guide, 0.2 is small, 0.5 medium and 0.8 large.

::: {.panel-tabset group="language"}
## R

```{r}
effectsize::hedges_g(bmi ~ procedure, data = cohort)
```

## Python

```{python}
g = pg.compute_effsize(tka, tha, eftype="hedges")
print(g)
print(pg.compute_esci(stat=g, nx=len(tka), ny=len(tha), eftype="hedges", decimals=3))   # its 95% CI
```
:::

```{python}
#| include: false
chk = {"g": float(g)}
```

```{r}
#| include: false
bmi_g <- effectsize::hedges_g(bmi ~ procedure, data = cohort)
check_agree(list(g = bmi_g$Hedges_g), reticulate::py$chk)
```

Hedges' g is 0.33: TKA patients' BMI is about a third of a standard deviation higher, a small effect.

### How to report it

> **Methods:** BMI was compared between procedures with Welch's unpaired t test.
>
> **Results:** TKA patients had a higher BMI than THA patients (mean 31.2 vs 29.5 kg/m²; difference 1.8 kg/m², 95% CI 0.9 to 2.6; Hedges' g = 0.33; p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: don't test the variances first
An old habit is to run a test of equal variances (such as Levene's) and then choose Student's or Welch's t test depending on the result. Don't: the two-step procedure distorts the p-value. Use Welch's test from the start. When the variances really are equal, it gives almost the same answer as Student's.
:::

::: {.callout-tip}
## 🔀 R vs Python: Student's or Welch's?
- **The default differs.** R's `t.test()` runs **Welch's** test unless you add `var.equal = TRUE`. scipy's `ttest_ind()` runs **Student's** test unless you add `equal_var=False`. Always set it explicitly in Python.
- **The order of the groups.** R subtracts in the order of the factor levels (we put TKA first); scipy subtracts the second argument from the first.
- **The CI for Hedges' g.** effectsize uses an exact method and pingouin an approximation, so the CIs can differ slightly (0.17 to 0.49 in R, 0.17 to 0.495 in Python). The estimates agree.
:::

## Mann-Whitney test {#mann-whitney}

**The question:** Do men and women report different KOOS JR scores 1 year after knee replacement?

### When to use it

- The outcome is **skewed**, has a **ceiling or floor**, or is **ordinal**, and you're comparing **two independent groups**.
- It asks whether values in one group tend to be **larger** than in the other: if you picked one patient from each group at random, how likely is the first to score higher?
- It's the same test as the **Wilcoxon rank-sum test**. R calls it `wilcox.test()`.
- If the outcome is roughly normal within each group → the [unpaired t test](#unpaired-t).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)
proms  <- read_csv("data/proms_long.csv", show_col_types = FALSE)

koos_1yr <- proms |>
  filter(instrument == "KOOS JR", visit == "1yr", !is.na(prom_score)) |>
  left_join(select(cohort, case_id, sex), by = "case_id") |>
  mutate(sex = factor(sex, levels = c("Male", "Female")))   # men first: differences are men minus women

ggplot(koos_1yr, aes(sex, prom_score)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.4) +
  labs(x = NULL, y = "KOOS JR at 1 year")

koos_1yr |>
  group_by(sex) |>
  summarise(n = n(), median = median(prom_score),
            q1 = quantile(prom_score, 0.25), q3 = quantile(prom_score, 0.75))
```

## Python

```{python}
import numpy as np
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
proms = pd.read_csv("data/proms_long.csv")

koos_1yr = proms[(proms["instrument"] == "KOOS JR") & (proms["visit"] == "1yr")].dropna(subset=["prom_score"])
koos_1yr = koos_1yr.merge(cohort[["case_id", "sex"]], on="case_id")
men = koos_1yr.loc[koos_1yr["sex"] == "Male", "prom_score"]
women = koos_1yr.loc[koos_1yr["sex"] == "Female", "prom_score"]

fig, ax = plt.subplots(figsize=(5, 3))
parts = ax.boxplot([men, women], tick_labels=["Male", "Female"])   # naming the result keeps it out of the output
ax.set_ylabel("KOOS JR at 1 year")
plt.show()

print(koos_1yr.groupby("sex")["prom_score"].describe()[["count", "25%", "50%", "75%"]])
```
:::

Both groups pile up toward the ceiling of 100, so medians are the fair summary. They're within 2 points of each other.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
koos_test <- wilcox.test(prom_score ~ sex, data = koos_1yr,
                         exact = FALSE, correct = TRUE,   # see the R vs Python box
                         conf.int = TRUE)                 # adds the Hodges-Lehmann estimate and CI
koos_test
```

## Python

```{python}
# pg.mwu() runs scipy's Mann-Whitney test and adds the rank-biserial effect size
koos_test = pg.mwu(men, women, method="asymptotic", use_continuity=True)   # see the R vs Python box
print(koos_test)
```
:::

```{python}
#| include: false
chk = {"u": float(koos_test["U_val"].iloc[0]), "p": float(koos_test["p_val"].iloc[0])}
```

```{r}
#| include: false
check_agree(list(u = unname(koos_test$statistic), p = koos_test$p.value), reticulate::py$chk)
```

### Read the output

- **W = 8926.5** (R) or **U_val = 8926.5** (Python): the Mann-Whitney U statistic for men, the number of (man, woman) pairs in which the man scored higher, counting ties as half. R calls it W.
- **p = 0.432:** a difference like this would be common if men and women had the same distribution of scores.
- **difference in location 0.80, 95% CI −1.60 to 4.40** (R only): the Hodges-Lehmann estimate, below.
- **RBC = 0.056** (Python): the rank-biserial effect size, below.

### Effect size and 95% CI

- The **Hodges-Lehmann estimate** is the median of the differences between every man's score and every woman's score: a typical difference, in points.
- The **rank-biserial correlation (r)** runs from −1 (every woman scored higher than every man) to +1 (the reverse). 0 means no tendency either way.

::: {.panel-tabset group="language"}
## R

```{r}
koos_test$estimate                                       # Hodges-Lehmann estimate, men minus women
koos_test$conf.int                                       # its 95% CI

effectsize::rank_biserial(prom_score ~ sex, data = koos_1yr)
```

## Python

```{python}
# Hodges-Lehmann estimate: the median of every man-minus-woman difference
def hodges_lehmann(x, y):
    return np.median(np.subtract.outer(np.asarray(x), np.asarray(y)))

print(hodges_lehmann(men, women))

# scipy has no CI for it, so use a bootstrap: recompute it on 9999 resampled datasets
boot = stats.bootstrap((men.to_numpy(), women.to_numpy()), hodges_lehmann, vectorized=False,
                       rng=np.random.default_rng(2026))
print(boot.confidence_interval)

print(koos_test["RBC"])                                  # rank-biserial r
```
:::

```{python}
#| include: false
chk = {"hl": float(hodges_lehmann(men, women)), "rbc": float(koos_test["RBC"].iloc[0])}
```

```{r}
#| include: false
koos_rb <- effectsize::rank_biserial(prom_score ~ sex, data = koos_1yr)
check_agree(list(hl = unname(koos_test$estimate), rbc = koos_rb$r_rank_biserial), reticulate::py$chk,
            tol = 1e-4)   # R finds the Hodges-Lehmann estimate by root-finding, accurate to about 1e-5
```

Men scored 0.8 points higher (95% CI 1.6 points lower to 4.4 points higher), and r = 0.06 is close to zero. A difference of a few points either way is compatible with the data; a large one isn't.

### How to report it

> **Methods:** Because 1-year KOOS JR scores showed a ceiling effect, they were compared between men and women with the Mann-Whitney test, with the Hodges-Lehmann estimate of the difference and its 95% CI as the effect size.
>
> **Results:** 1-year KOOS JR did not differ significantly between men and women (median 87.0 vs 85.0 points; Hodges-Lehmann difference 0.8 points, 95% CI −1.6 to 4.4; rank-biserial r = 0.06; p = 0.432).

::: {.callout-warning}
## ⚠️ Watch out: it isn't a test of medians
The Mann-Whitney test asks whether one group's values **tend to be larger**, not whether the medians differ. Two groups can have the same median and a significant Mann-Whitney test (if their shapes differ), or different medians and a non-significant one. Report the medians to describe the groups, but don't write "the medians differed significantly".
:::

::: {.callout-tip}
## 🔀 R vs Python: Mann-Whitney defaults
- **Exact or approximate.** With ties (as here) both programs use a normal approximation. Without ties, R computes an exact p-value for groups under 50, scipy only for very small groups. We set `exact = FALSE` in R and `method="asymptotic"` in Python so they always match.
- **Continuity correction.** Both programs apply it by default for the approximation; we set it explicitly anyway.
- **The Hodges-Lehmann CI.** R computes it by inverting the test; the Python code uses a bootstrap, a different method, so the two CIs differ slightly (−1.60 to 4.40 in R, −1.70 to 4.40 from the bootstrap).
:::

## Fisher's exact test and chi-square {#fisher-chi-square}

**The question:** Are men more likely than women to be readmitted within 90 days?

### When to use it

- The outcome is **yes/no**, compared between **two independent groups**: a 2 × 2 table.
- **Fisher's exact test** is valid for any sample size. The **chi-square test** is a large-sample approximation: use it only when every *expected* count is at least 5. When in doubt, use Fisher's test.
- If patients were followed for different lengths of time and the event can happen at any time → the [log-rank test](#log-rank).

### Look at the data first

For two yes/no variables, "looking" means the 2 × 2 table, with the percentage in each group.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

# Put the comparison group first and the outcome "yes" first
readmit_table <- table(
  sex        = factor(cohort$sex, levels = c("Male", "Female")),
  readmitted = factor(cohort$readmit_90d, levels = c(1, 0), labels = c("yes", "no"))
)
readmit_table
prop.table(readmit_table, margin = 1)    # row percentages: readmitted within each sex
```

## Python

```{python}
import pandas as pd
from scipy import stats
from scipy.stats.contingency import odds_ratio
from statsmodels.stats.proportion import confint_proportions_2indep

cohort = pd.read_csv("data/cohort.csv")

# Put the comparison group first and the outcome "yes" (1) first
readmit_table = pd.crosstab(cohort["sex"], cohort["readmit_90d"]).loc[["Male", "Female"], [1, 0]]
print(readmit_table)
print(pd.crosstab(cohort["sex"], cohort["readmit_90d"], normalize="index"))   # row percentages
```
:::

12 of 257 men (4.7%) and 15 of 343 women (4.4%) were readmitted.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
readmit_fisher <- fisher.test(readmit_table)
readmit_fisher

chisq.test(readmit_table)$expected       # all at least 5, so chi-square is also fine
readmit_chisq <- chisq.test(readmit_table)
readmit_chisq
```

## Python

```{python}
readmit_fisher = stats.fisher_exact(readmit_table)
print(readmit_fisher.pvalue)

readmit_chisq = stats.chi2_contingency(readmit_table)   # includes the expected counts
print(readmit_chisq.expected_freq)
print(readmit_chisq.statistic, readmit_chisq.pvalue)
```
:::

```{python}
#| include: false
chk = {"fisher_p": float(readmit_fisher.pvalue), "chisq": float(readmit_chisq.statistic),
       "chisq_p": float(readmit_chisq.pvalue)}
```

```{r}
#| include: false
check_agree(list(fisher_p = readmit_fisher$p.value, chisq = unname(readmit_chisq$statistic),
                 chisq_p = readmit_chisq$p.value), reticulate::py$chk)
```

### Read the output

- **Fisher's test, p-value = 1:** this table is exactly what you'd most expect if readmission were unrelated to sex. We report it as p > 0.999.
- **odds ratio 1.07, 95% CI 0.45 to 2.50** (R): the effect size, below.
- **Expected counts:** what each cell would hold if readmission were unrelated to sex. All are at least 5 (the smallest is 11.6), so the chi-square test is valid too.
- **X-squared ≈ 0, p-value = 1:** the chi-square test, with Yates' continuity correction, agrees.

::: {.callout-note collapse="true"}
## 🔍 Under the hood: Yates' continuity correction
The chi-square test treats counts as if they could take any value, but counts are whole numbers. For a 2 × 2 table, **Yates' correction** subtracts 0.5 from each |observed − expected| difference before squaring, which makes the p-value a little larger (more cautious) and closer to Fisher's. Here the observed counts are within 0.5 of the expected counts, so the corrected statistic is 0. Both R's `chisq.test()` and scipy's `chi2_contingency()` apply it to 2 × 2 tables by default; without it (`correct = FALSE`, `correction=False`) p = 0.863. Either is acceptable if you say which you used; with small counts, prefer Fisher's test.
:::

### Effect size and 95% CI

Two effect sizes, and it's worth reporting both:

- The **risk difference**: the difference between the two percentages, in percentage points. It's what patients and clinicians understand.
- The **odds ratio**: the odds of readmission for men divided by the odds for women. It's what logistic regression reports ([page 11](11-predict-from-one.qmd#logistic-regression)), so it's useful for comparing with other studies.

::: {.panel-tabset group="language"}
## R

```{r}
readmit_fisher$estimate                  # odds ratio, men vs women
readmit_fisher$conf.int                  # its 95% CI

risk <- prop.test(readmit_table, correct = FALSE)
risk$estimate                            # readmission rate in men, then in women
risk$conf.int                            # 95% CI for the risk difference, men minus women
```

## Python

```{python}
readmit_or = odds_ratio(readmit_table.to_numpy(), kind="conditional")   # the same odds ratio as R
print(readmit_or.statistic, readmit_or.confidence_interval())

men_yes, men_no = readmit_table.loc["Male"]
women_yes, women_no = readmit_table.loc["Female"]
print(men_yes / (men_yes + men_no), women_yes / (women_yes + women_no))   # readmission rates
print(confint_proportions_2indep(men_yes, men_yes + men_no, women_yes, women_yes + women_no,
                                 method="wald", compare="diff"))           # 95% CI, men minus women
```
:::

```{python}
#| include: false
or_ci = readmit_or.confidence_interval()
rd_ci = confint_proportions_2indep(men_yes, men_yes + men_no, women_yes, women_yes + women_no,
                                   method="wald", compare="diff")
chk = {"or": float(readmit_or.statistic), "or_low": float(or_ci.low), "or_high": float(or_ci.high),
       "rd_low": float(rd_ci[0]), "rd_high": float(rd_ci[1])}
```

```{r}
#| include: false
check_agree(list(or = unname(readmit_fisher$estimate), or_low = readmit_fisher$conf.int[1],
                 or_high = readmit_fisher$conf.int[2], rd_low = risk$conf.int[1], rd_high = risk$conf.int[2]),
            reticulate::py$chk,
            tol = 1e-4)   # both programs find the odds ratio and its CI by root-finding, accurate to about 1e-5
```

Men's readmission rate was 0.3 percentage points higher (95% CI 3.1 points lower to 3.7 points higher), an odds ratio of 1.07 (95% CI 0.45 to 2.50).

### How to report it

> **Methods:** Categorical outcomes were compared with Fisher's exact test. Effect sizes are reported as risk differences with Wald 95% CIs and as odds ratios with exact 95% CIs.
>
> **Results:** Ninety-day readmission did not differ significantly between men and women (4.7% vs 4.4%; risk difference 0.3 percentage points, 95% CI −3.1 to 3.7; odds ratio 1.07, 95% CI 0.45 to 2.50; p > 0.999).

::: {.callout-warning}
## ⚠️ Watch out: "no difference" needs a narrow CI
The p-value is as large as it can be, but the odds ratio's CI runs from 0.45 to 2.50: the data are compatible with men having half the odds of readmission, or two and a half times the odds. With only 27 readmissions, this study can't tell. "No significant difference" is the honest wording; "men and women have the same risk" isn't.
:::

::: {.callout-tip}
## 🔀 R vs Python: two different odds ratios
scipy's `fisher_exact()` reports the simple **sample** odds ratio (a × d) / (b × c), 1.0710 here. R's `fisher.test()` reports the **conditional maximum-likelihood** odds ratio, 1.0709, which goes with its exact CI. Use `scipy.stats.contingency.odds_ratio(..., kind="conditional")` to get R's number and CI. The two are always close; say which you report.
:::

## Log-rank test {#log-rank}

**The question:** Is revision-free survival different between implant A and implant C?

### When to use it

- The outcome is **time until an event** (revision), patients were followed for different lengths of time, and you're comparing **two independent groups**.
- It compares the whole survival curves, not the survival at one time point.
- The **Mantel-Haenszel test** (or Mantel-Cox test) in the decision table is the same test under another name.
- It's most powerful when one group's risk is a steady multiple of the other's over time (proportional hazards). If the curves cross, see [page 14](../survival/14-cox-regression.qmd).
- To compare three or more groups, or to adjust for other variables → [Cox regression](08-three-plus-unmatched.qmd#cox).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 4.5
library(tidyverse)
library(survival)
library(ggsurvfit)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)
a_vs_c <- cohort |> filter(implant %in% c("A", "C"))   # two groups; page 8 compares all three

survfit2(Surv(followup_years, revised) ~ implant, data = a_vs_c, conf.type = "log-log") |>
  ggsurvfit() +
  add_confidence_interval() +
  add_risktable() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Revision-free survival")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
from lifelines.plotting import add_at_risk_counts

cohort = pd.read_csv("data/cohort.csv")
a_vs_c = cohort[cohort["implant"].isin(["A", "C"])]   # two groups; page 8 compares all three
a = a_vs_c[a_vs_c["implant"] == "A"]
c = a_vs_c[a_vs_c["implant"] == "C"]

fig, ax = plt.subplots(figsize=(7, 4.5))
km_a = KaplanMeierFitter(label="A").fit(a["followup_years"], a["revised"])
km_c = KaplanMeierFitter(label="C").fit(c["followup_years"], c["revised"])
km_a.plot_survival_function(ax=ax)
km_c.plot_survival_function(ax=ax)
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Revision-free survival")
add_at_risk_counts(km_a, km_c, ax=ax)
plt.tight_layout()
plt.show()
```
:::

Implant C's curve falls faster from the start, and the gap keeps growing.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
implant_logrank <- survdiff(Surv(followup_years, revised) ~ implant, data = a_vs_c)
implant_logrank
```

## Python

```{python}
implant_logrank = logrank_test(a["followup_years"], c["followup_years"],
                               event_observed_A=a["revised"], event_observed_B=c["revised"])
print(implant_logrank.test_statistic, implant_logrank.p_value)
```
:::

```{python}
#| include: false
chk = {"chisq": float(implant_logrank.test_statistic), "p": float(implant_logrank.p_value)}
```

```{r}
#| include: false
check_agree(list(chisq = implant_logrank$chisq, p = implant_logrank$pvalue), reticulate::py$chk)
```

### Read the output

- **N:** patients in each group (246 with implant A, 137 with C).
- **Observed / Expected:** the revisions each group had, and the number it would have had if both implants carried the same risk. Implant C had 38 revisions where 21.1 were expected; implant A had 25 where 41.9 were expected.
- **Chisq = 20.5 on 1 degree of freedom, p < 0.001:** curves this different would be very unlikely if the implants had the same revision risk.

### Effect size and 95% CI

The log-rank test has no effect size of its own. The usual one is the **hazard ratio** from a Cox model: how many times higher the risk of revision is, at any moment, with implant C than with implant A. [Page 14](../survival/14-cox-regression.qmd) explains Cox regression in full.

::: {.panel-tabset group="language"}
## R

```{r}
implant_cox <- coxph(Surv(followup_years, revised) ~ implant, data = a_vs_c)
summary(implant_cox)$conf.int    # exp(coef) is the hazard ratio, C vs A
```

## Python

```{python}
implant_cox = CoxPHFitter().fit(a_vs_c[["followup_years", "revised", "implant"]],
                                duration_col="followup_years", event_col="revised", formula="implant")
print(implant_cox.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

```{python}
#| include: false
hr_row = implant_cox.summary.iloc[0]
chk = {"hr": float(hr_row["exp(coef)"]), "hr_low": float(hr_row["exp(coef) lower 95%"]),
       "hr_high": float(hr_row["exp(coef) upper 95%"])}
```

```{r}
#| include: false
hr <- summary(implant_cox)$conf.int
check_agree(list(hr = hr[1, "exp(coef)"], hr_low = hr[1, "lower .95"], hr_high = hr[1, "upper .95"]),
            reticulate::py$chk)
```

The hazard of revision was about three times higher with implant C (hazard ratio 3.04, 95% CI 1.83 to 5.04).

### How to report it

> **Methods:** Revision-free survival was estimated with the Kaplan-Meier method and compared between implants with the log-rank test. Hazard ratios were estimated with Cox proportional hazards regression.
>
> **Results:** Revision-free survival was lower with implant C than with implant A (5-year survival 71.1% vs 89.9%; log-rank p < 0.001; hazard ratio 3.04, 95% CI 1.83 to 5.04).

::: {.callout-warning}
## ⚠️ Watch out: overlapping CIs aren't a test
Comparing the two curves' CIs at one time point ("the 5-year CIs overlap, so there's no difference") isn't a valid test, and neither is comparing the crude percentages revised. Use the log-rank test on the whole curves. And as on [page 4](04-describe-one-group.qmd#kaplan-meier), deaths here are treated as censored; [page 13](../survival/13-kaplan-meier.qmd) covers competing risks.
:::

::: {.callout-tip}
## 🔀 R vs Python: one formula or two groups
R's `survdiff()` takes a formula with a grouping variable. lifelines' `logrank_test()` takes each group's follow-up times and events separately (`multivariate_logrank_test()` takes a grouping column). They compute the same test. Both Cox models handle tied revision times with Efron's method, so the hazard ratios agree.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
bmi_means <- tapply(cohort$bmi, cohort$procedure, mean)
koos_medians <- tapply(koos_1yr$prom_score, koos_1yr$sex, median)
km5 <- summary(survfit(Surv(followup_years, revised) ~ implant, data = a_vs_c), times = 5)
expected_counts <- chisq.test(readmit_table)$expected
op_tka <- cohort$op_time_min[cohort$procedure == "TKA"]
op_tha <- cohort$op_time_min[cohort$procedure == "THA"]
comp <- table(factor(cohort$anesthesia, levels = c("general", "spinal")),
              factor(cohort$complication_90d, levels = c(1, 0), labels = c("yes", "no")))
stopifnot(
  sum(table(cohort$patient_id) == 2) == 80,
  round(unname(bmi_test$statistic), 2) == 4.07, round(unname(bmi_test$parameter), 2) == 580.09,
  bmi_test$p.value < 0.001,
  round(bmi_test$conf.int, 2) == c(0.92, 2.65), round(bmi_test$conf.int, 1) == c(0.9, 2.6),
  round(bmi_means[c("TKA", "THA")], 1) == c(31.2, 29.5), round(bmi_means[["TKA"]] - bmi_means[["THA"]], 1) == 1.8,
  round(bmi_g$Hedges_g, 2) == 0.33, round(bmi_g$CI_low, 2) == 0.17, round(bmi_g$CI_high, 2) == 0.49,
  reticulate::py_eval("float(pg.compute_esci(stat=g, nx=len(tka), ny=len(tha), eftype='hedges', decimals=3)[1])") == 0.495,
  unname(koos_test$statistic) == 8926.5, round(koos_test$p.value, 3) == 0.432,
  round(unname(koos_test$estimate), 2) == 0.80, round(koos_test$conf.int, 2) == c(-1.60, 4.40),
  round(reticulate::py_eval("[float(boot.confidence_interval.low), float(boot.confidence_interval.high)]"), 2) == c(-1.70, 4.40),
  round(koos_rb$r_rank_biserial, 3) == 0.056, round(koos_rb$r_rank_biserial, 2) == 0.06,
  round(koos_medians[c("Male", "Female")], 1) == c(87.0, 85.0), max(abs(diff(koos_medians))) < 2,
  readmit_table["Male", "yes"] == 12, sum(readmit_table["Male", ]) == 257,
  readmit_table["Female", "yes"] == 15, sum(readmit_table["Female", ]) == 343,
  round(100 * prop.table(readmit_table, 1)[, "yes"], 1) == c(4.7, 4.4),
  readmit_fisher$p.value > 0.999,
  min(expected_counts) >= 5, round(min(expected_counts), 1) == 11.6,
  unname(readmit_chisq$statistic) < 1e-6,
  round(chisq.test(readmit_table, correct = FALSE)$p.value, 3) == 0.863,
  round(unname(readmit_fisher$estimate), 2) == 1.07, round(readmit_fisher$conf.int, 2) == c(0.45, 2.50),
  round(unname(readmit_fisher$estimate), 4) == 1.0709,
  round(12 * 328 / (15 * 245), 4) == 1.0710,
  round(100 * unname(diff(rev(risk$estimate))), 1) == 0.3, round(100 * risk$conf.int, 1) == c(-3.1, 3.7),
  implant_logrank$n == c(246, 137), implant_logrank$obs == c(25, 38),
  round(implant_logrank$exp, 1) == c(41.9, 21.1),
  round(implant_logrank$chisq, 1) == 20.5, implant_logrank$pvalue < 0.001,
  round(hr[1, c("exp(coef)", "lower .95", "upper .95")], 2) == c(3.04, 1.83, 5.04),
  round(100 * km5$surv, 1) == c(89.9, 71.1),
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(c(mean(op_tka), mean(op_tha)), 1) == c(88.3, 79.8), round(mean(op_tka) - mean(op_tha), 1) == 8.5,
  round(t.test(op_tka, op_tha)$conf.int, 1) == c(6.0, 11.1),
  round(wilcox.test(los_days ~ site, data = cohort, exact = FALSE)$p.value, 3) == 0.020,
  round(effectsize::rank_biserial(los_days ~ site, data = cohort)$r_rank_biserial, 2) == 0.10,
  median(outer(cohort$los_days[cohort$site == "Site A"], cohort$los_days[cohort$site == "Site B"], "-")) == 0,
  round(100 * prop.table(comp, 1)[, "yes"], 1) == c(12.0, 7.3),
  round(100 * (prop.table(comp, 1)["general", "yes"] - prop.table(comp, 1)["spinal", "yes"]), 1) == 4.7,
  round(100 * prop.test(comp, correct = FALSE)$conf.int, 1) == c(-1.1, 10.4),
  round(unname(fisher.test(comp)$estimate), 2) == 1.72, round(fisher.test(comp)$conf.int, 2) == c(0.88, 3.27),
  round(fisher.test(comp)$p.value, 3) == 0.090
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Compare **operative time** between TKA and THA with Welch's t test. Report the mean difference with its 95% CI.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
op_data <- cohort |> mutate(procedure = factor(procedure, levels = c("TKA", "THA")))   # TKA first
t.test(op_time_min ~ procedure, data = op_data)
```

## Python

```{python}
op_tka = cohort.loc[cohort["procedure"] == "TKA", "op_time_min"]
op_tha = cohort.loc[cohort["procedure"] == "THA", "op_time_min"]
op_test = stats.ttest_ind(op_tka, op_tha, equal_var=False)
print(op_test, op_tka.mean() - op_tha.mean(), op_test.confidence_interval())
```
:::

TKAs took longer (mean 88.3 vs 79.8 minutes; difference 8.5 minutes, 95% CI 6.0 to 11.1; p < 0.001).
:::

**2.** A colleague wants to know whether **length of stay** differs between Site A and Site B. Which test would you choose, and what do you find?

::: {.callout-tip collapse="true"}
## Solution
Length of stay is strongly skewed, with most patients going home on day 0 or 1: the **Mann-Whitney test**.

::: {.panel-tabset group="language"}
## R

```{r}
los_test <- wilcox.test(los_days ~ site, data = cohort, exact = FALSE, correct = TRUE)
los_test
effectsize::rank_biserial(los_days ~ site, data = cohort)
cohort |> group_by(site) |> summarise(median = median(los_days),
                                      q1 = quantile(los_days, 0.25), q3 = quantile(los_days, 0.75))
```

## Python

```{python}
site_a = cohort.loc[cohort["site"] == "Site A", "los_days"]
site_b = cohort.loc[cohort["site"] == "Site B", "los_days"]
print(pg.mwu(site_a, site_b, method="asymptotic", use_continuity=True))
print(cohort.groupby("site")["los_days"].describe()[["25%", "50%", "75%"]])
```
:::

Stays were longer at Site A (median 1 day, IQR 0 to 2) than at Site B (median 0 days, IQR 0 to 1; rank-biserial r = 0.10; p = 0.020).

Notice that we didn't report a Hodges-Lehmann estimate. With whole days and so many ties, most of the Site A − Site B differences are exactly 0 days, so the estimate is 0 even though Site A's stays tend to run longer. For data like these, the medians with IQRs and the rank-biserial r describe the difference better.
:::

**3.** Is the 90-day complication rate different after general and spinal anesthesia? Choose the test, run it, and write the Results sentence with the risk difference and odds ratio.

::: {.callout-tip collapse="true"}
## Solution
Yes/no outcome, two independent groups: **Fisher's exact test**.

::: {.panel-tabset group="language"}
## R

```{r}
comp_table <- table(anesthesia = factor(cohort$anesthesia, levels = c("general", "spinal")),
                    complication = factor(cohort$complication_90d, levels = c(1, 0), labels = c("yes", "no")))
comp_table
fisher.test(comp_table)
prop.test(comp_table, correct = FALSE)
```

## Python

```{python}
comp_table = pd.crosstab(cohort["anesthesia"], cohort["complication_90d"]).loc[["general", "spinal"], [1, 0]]
print(comp_table)
print(stats.fisher_exact(comp_table).pvalue)
comp_or = odds_ratio(comp_table.to_numpy(), kind="conditional")
print(comp_or.statistic, comp_or.confidence_interval())
print(confint_proportions_2indep(18, 150, 33, 450, method="wald", compare="diff"))
```
:::

"Complications within 90 days were more frequent after general than spinal anesthesia, but the difference was not statistically significant (12.0% vs 7.3%; risk difference 4.7 percentage points, 95% CI −1.1 to 10.4; odds ratio 1.72, 95% CI 0.88 to 3.27; p = 0.090)."
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/06-two-unpaired-groups.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `104 passed`.

- [ ] **Step 5: Prove the agreement check bites, then restore**

In the `#unpaired-t` section's Run-it Python block, change `bmi_test = stats.ttest_ind(tka, tha, equal_var=False)` to `bmi_test = stats.ttest_ind(tka, tha)` (scipy's default, Student's t), then run `quarto render catalog/06-two-unpaired-groups.qmd`. Expected: the render FAILS with `check_agree(): R and Python disagree on 't'`. Undo the change, then run:

```bash
rm -rf catalog/06-two-unpaired-groups_files
quarto render catalog/06-two-unpaired-groups.qmd
uv run pytest tests/site -q
```

Expected: `104 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/06-two-unpaired-groups.qmd _freeze/catalog/06-two-unpaired-groups tests/site/test_catalog.py
git commit -m "Write page 6, two unpaired groups: Welch t, Mann-Whitney, Fisher/chi-square, log-rank

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Page 7, Compare two paired groups

**Files:**
- Modify: `catalog/07-two-paired-groups.qmd` (replace the stub)
- Create: `_freeze/catalog/07-two-paired-groups/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Task 3's harness
  - `data/matched_sets.csv`, `data/radiographic_reliability.csv`
  - page 5's `#binomial-test` and page 6's `#mann-whitney` anchors
- Produces: page 7 anchors `#paired-t`, `#wilcoxon-signed-rank`, `#mcnemar` and `#stratified-cox`.

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_catalog.py -q`

Expected: 11 of the 13 new page-7 tests FAIL; the no-warnings and short-outputs tests pass trivially on a stub. The 39 earlier tests pass.

- [ ] **Step 3: Write the page**

Replace `catalog/07-two-paired-groups.qmd` with:

````markdown
---
title: "7 · Compare two paired groups"
description: "Paired t test, Wilcoxon signed-rank test, McNemar's test and stratified Cox regression: the same patients measured twice, or matched pairs."
engine: knitr
toc-depth: 2
execute:
  message: false
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

**Paired** data come in twos that belong together: the same patient before and after surgery, two raters measuring the same X-ray, or two patients matched to each other on age, sex and BMI. Paired tests compare each patient with themselves (or with their match), which removes the patient-to-patient variation that unpaired tests have to wade through. If your two groups are different patients, use [page 6](06-two-unpaired-groups.qmd) instead.

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice data. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

::: {.callout-warning}
## ⚠️ Watch out: only complete pairs count
A paired test can only use patients measured at **both** times. Patients who missed a visit drop out, and if they differ from the rest (for example, the patients who did badly stop coming back), the result is biased. Always report how many patients had both measurements. [Mixed models](../beyond/16-mixed-models.qmd) can use everyone's data, including incomplete follow-up.
:::

## Paired t test {#paired-t}

**The question:** Does patients' physical health, measured by the VR-12 physical component score (PCS), improve from before surgery to 1 year after?

### When to use it

- Each patient (or matched pair) gives **two measurements** of the same thing.
- The **differences** between the two measurements are roughly normal, or there are about 30 or more pairs. The assumption is about the differences, not about each measurement on its own.
- Pairs are independent of each other.
- If the differences are skewed, or the measurements are bounded or ordinal → the [Wilcoxon signed-rank test](#wilcoxon-signed-rank).

### Look at the data first

Paired data need to be **wide**: one row per patient, with the two measurements side by side ([page 1](../foundations/01-tidy-data.qmd#reshaping) shows how to reshape).

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

pcs <- proms |>
  filter(visit %in% c("preop", "1yr")) |>
  select(case_id, visit, vr12_pcs) |>
  pivot_wider(names_from = visit, values_from = vr12_pcs, names_prefix = "pcs_") |>   # one row per patient
  filter(!is.na(pcs_preop), !is.na(pcs_1yr)) |>                                       # complete pairs only
  mutate(change = pcs_1yr - pcs_preop)

nrow(pcs)

ggplot(pcs, aes(change)) +
  geom_histogram(binwidth = 2) +
  geom_vline(xintercept = 0, linetype = "dashed") +   # no change
  labs(x = "Change in VR-12 PCS, 1 year minus pre-op", y = "Patients")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

proms = pd.read_csv("data/proms_long.csv")

pcs = (proms[proms["visit"].isin(["preop", "1yr"])]
       .pivot(index="case_id", columns="visit", values="vr12_pcs")   # one row per patient
       .dropna())                                                      # complete pairs only
pcs["change"] = pcs["1yr"] - pcs["preop"]

print(len(pcs))

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(pcs["change"], bins=range(-20, 46, 2))
ax.axvline(0, linestyle="--")                                          # no change
ax.set_xlabel("Change in VR-12 PCS, 1 year minus pre-op")
ax.set_ylabel("Patients")
plt.show()
```
:::

436 patients have both scores. The changes form a roughly symmetric bell, centered well to the right of zero.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
pcs_test <- t.test(pcs$pcs_1yr, pcs$pcs_preop, paired = TRUE)   # 1 year minus pre-op
pcs_test
```

## Python

```{python}
pcs_test = stats.ttest_rel(pcs["1yr"], pcs["preop"])           # 1 year minus pre-op
print(pcs_test)
print(pcs["change"].mean(), pcs_test.confidence_interval())
```
:::

```{python}
#| include: false
pcs_ci = pcs_test.confidence_interval()
chk = {"t": float(pcs_test.statistic), "df": float(pcs_test.df), "p": float(pcs_test.pvalue),
       "mean_change": float(pcs["change"].mean()), "ci_low": float(pcs_ci.low), "ci_high": float(pcs_ci.high)}
```

```{r}
#| include: false
check_agree(list(t = unname(pcs_test$statistic), df = unname(pcs_test$parameter), p = pcs_test$p.value,
                 mean_change = unname(pcs_test$estimate), ci_low = pcs_test$conf.int[1],
                 ci_high = pcs_test$conf.int[2]), reticulate::py$chk)
```

### Read the output

- **t = 31.2, df = 435:** the mean change is 31 standard errors away from zero; df is the number of pairs minus 1.
- **p < 0.001** (R prints "p < 2.2e-16", the smallest p-value it displays): a change this large would be essentially impossible if PCS didn't change on average.
- **mean difference 13.7:** PCS rose by 13.7 points on average.
- **95% CI 12.8 to 14.5:** the CI for the mean change.

### Effect size and 95% CI

- The **mean change** with its CI, in points: 13.7 (95% CI 12.8 to 14.5).
- **Cohen's d~z~** divides the mean change by the standard deviation of the changes: how consistent the improvement was across patients. The usual guide (0.2 small, 0.5 medium, 0.8 large) applies.

::: {.panel-tabset group="language"}
## R

```{r}
effectsize::repeated_measures_d(pcs$pcs_1yr, pcs$pcs_preop, method = "z", adjust = FALSE)
```

## Python

```{python}
d_z = pcs["change"].mean() / pcs["change"].std()   # mean change / SD of the changes
print(d_z)
```
:::

```{python}
#| include: false
chk = {"d_z": float(d_z)}
```

```{r}
#| include: false
pcs_d <- effectsize::repeated_measures_d(pcs$pcs_1yr, pcs$pcs_preop, method = "z", adjust = FALSE)
check_agree(list(d_z = pcs_d$d_z), reticulate::py$chk)
```

d~z~ = 1.49 is a very large effect: 93% of patients' PCS went up.

### How to report it

> **Methods:** Change in VR-12 PCS from before surgery to 1 year was assessed with a paired t test in patients with both measurements.
>
> **Results:** Of 574 patients with a pre-op PCS, 436 also had a 1-year score. PCS improved from a mean of 31.2 (SD 6.3) to 44.9 (SD 6.8) (mean change 13.7 points, 95% CI 12.8 to 14.5; d~z~ = 1.49; p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: don't analyze paired data as unpaired
Running an unpaired t test on the pre-op and 1-year columns ignores which scores belong to the same patient. That's wrong even when it happens to give a similar answer, because the test's standard error assumes 872 independent patients when there are only 436. When the two measurements are correlated, as they usually are, the paired test is also more precise.
:::

::: {.callout-tip}
## 🔀 R vs Python: paired effect sizes
pingouin's `compute_effsize(x, y, paired=True)` does **not** return d~z~: it returns d~av~ (the mean change divided by the average of the two SDs), 2.08 here. Both are legitimate, but they answer different questions and aren't interchangeable. We compute d~z~ directly so the two languages match; say which one you report.
:::

## Wilcoxon signed-rank test {#wilcoxon-signed-rank}

**The question:** Did KOOS JR improve from before surgery to 1 year after knee replacement?

### When to use it

- Two paired measurements, and the outcome is **skewed** or has a **ceiling or floor**. The 1-year KOOS JR has a ceiling ([page 3](../foundations/03-distributions.qmd#transform)).
- For an **ordinal** scale (satisfaction from 1 to 5), count the patients who went up and down and compare the two counts with a binomial test (the **sign test**, [page 5](05-one-group-vs-hypothetical.qmd#binomial-test)).
- It ranks the sizes of the changes and compares the ranks of improvements with the ranks of declines.
- Changes of exactly zero carry no information about direction and are dropped.
- If the changes are roughly normal → the [paired t test](#paired-t).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

koos <- proms |>
  filter(instrument == "KOOS JR", visit %in% c("preop", "1yr")) |>
  select(case_id, visit, prom_score) |>
  pivot_wider(names_from = visit, values_from = prom_score, names_prefix = "koos_") |>
  filter(!is.na(koos_preop), !is.na(koos_1yr)) |>
  mutate(change = koos_1yr - koos_preop)

ggplot(koos, aes(change)) +
  geom_histogram(binwidth = 2.5) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  labs(x = "Change in KOOS JR, 1 year minus pre-op", y = "Patients")

koos |> summarise(n = n(), improved = sum(change > 0),
                  median_preop = median(koos_preop), median_1yr = median(koos_1yr))
```

## Python

```{python}
import numpy as np
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
from scipy import stats

proms = pd.read_csv("data/proms_long.csv")

koos = (proms[(proms["instrument"] == "KOOS JR") & proms["visit"].isin(["preop", "1yr"])]
        .pivot(index="case_id", columns="visit", values="prom_score")
        .dropna())
koos["change"] = koos["1yr"] - koos["preop"]

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(koos["change"], bins=np.arange(0, 72.5, 2.5))
ax.axvline(0, linestyle="--")
ax.set_xlabel("Change in KOOS JR, 1 year minus pre-op")
ax.set_ylabel("Patients")
plt.show()

print(len(koos), (koos["change"] > 0).sum(), koos["preop"].median(), koos["1yr"].median())
```
:::

All 246 patients with both scores improved. (Real data are rarely this tidy: usually a minority of patients get worse. These data are synthetic.)

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
koos_test <- wilcox.test(koos$koos_1yr, koos$koos_preop, paired = TRUE,
                         exact = FALSE, correct = FALSE,   # see the R vs Python box
                         conf.int = TRUE)                  # adds the Hodges-Lehmann estimate and CI
koos_test
```

## Python

```{python}
# pg.wilcoxon() runs scipy's test and adds the rank-biserial effect size
koos_test = pg.wilcoxon(koos["1yr"], koos["preop"], method="approx", correction=False)   # see the R vs Python box
print(koos_test)
```
:::

```{python}
#| include: false
chk = {"p": float(koos_test["p_val"].iloc[0]), "rbc": float(koos_test["RBC"].iloc[0])}
```

```{r}
#| include: false
koos_rb <- effectsize::rank_biserial(koos$koos_1yr, koos$koos_preop, paired = TRUE)
check_agree(list(p = koos_test$p.value, rbc = koos_rb$r_rank_biserial), reticulate::py$chk)
```

### Read the output

- **V = 30381** (R): the sum of the ranks of the improvements. With 246 patients the ranks add up to 246 × 247 / 2 = 30381, so every rank belongs to an improvement. Python reports the smaller sum, the declines: **W_val = 0**.
- **p < 0.001.**
- **(pseudo)median 34.1, 95% CI 32.3 to 35.9:** the Hodges-Lehmann estimate of the typical change, below.
- **RBC = 1.0** (Python): the rank-biserial effect size, below.

### Effect size and 95% CI

- The **Hodges-Lehmann estimate** of the change (the median of the averages of every pair of changes), with its CI, in points.
- The **matched-pairs rank-biserial correlation (r)**: +1 if every patient improved, −1 if every patient got worse, 0 if improvements and declines balance out. Here it's exactly 1.

::: {.panel-tabset group="language"}
## R

```{r}
koos_test$estimate                                                # Hodges-Lehmann estimate of the change
koos_test$conf.int                                                # its 95% CI

effectsize::rank_biserial(koos$koos_1yr, koos$koos_preop, paired = TRUE)
```

## Python

```{python}
# Hodges-Lehmann estimate: the median of the averages of every pair of changes
def hodges_lehmann(x):
    x = np.asarray(x)
    i, j = np.triu_indices(len(x))          # every pair, including each change with itself
    return np.median((x[i] + x[j]) / 2)

print(hodges_lehmann(koos["change"]))

# scipy has no CI for it, so use a bootstrap: recompute it on 9999 resampled datasets
boot = stats.bootstrap((koos["change"].to_numpy(),), hodges_lehmann, vectorized=False,
                       rng=np.random.default_rng(2026))
print(boot.confidence_interval)

print(koos_test["RBC"])                                           # rank-biserial r
```
:::

```{python}
#| include: false
chk = {"hl": float(hodges_lehmann(koos["change"]))}
```

```{r}
#| include: false
check_agree(list(hl = unname(koos_test$estimate)), reticulate::py$chk,
            tol = 1e-4)   # R finds the Hodges-Lehmann estimate by root-finding, accurate to about 1e-5
```

### How to report it

> **Methods:** Because 1-year KOOS JR scores showed a ceiling effect, change from before surgery was assessed with the Wilcoxon signed-rank test, with the Hodges-Lehmann estimate of the change and its 95% CI as the effect size.
>
> **Results:** All 246 patients with both scores improved. Median KOOS JR rose from 50.0 (IQR 40.8 to 58.2) before surgery to 85.8 (IQR 75.0 to 94.0) at 1 year (Hodges-Lehmann estimate of the change 34.1 points, 95% CI 32.3 to 35.9; p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: "significant improvement" isn't the whole story
A tiny p-value says the scores went up on average; it doesn't say how many patients improved by a **meaningful** amount. For PROMs, also report the proportion of patients whose change reached the minimal clinically important difference (MCID), a within-patient threshold ([page 3](../foundations/03-distributions.qmd#effect-sizes)).
:::

::: {.callout-tip}
## 🔀 R vs Python: Wilcoxon defaults
- **The statistic.** R reports V, the sum of the ranks of the positive changes. scipy (and pingouin) report the **smaller** of the two sums. The p-values agree.
- **Exact or approximate.** R uses an exact p-value for fewer than 50 pairs without ties and adds a continuity correction to the normal approximation; scipy's defaults differ. We set `exact = FALSE, correct = FALSE` in R and `method="approx", correction=False` in Python so they match.
- **The Hodges-Lehmann CI.** R computes it by inverting the test; the Python code uses a bootstrap, a different method. Here they agree to two decimals (32.30 to 35.90); on [page 6](06-two-unpaired-groups.qmd#mann-whitney) they differ a little.
:::

## McNemar's test {#mcnemar}

**The question:** Are patients more likely to use a walking aid 6 weeks after surgery than before it?

### When to use it

- A **yes/no** outcome measured **twice in the same patients** (or once in each member of a matched pair).
- It uses only the **discordant pairs**: the patients who changed (no → yes, or yes → no). Patients who stayed the same tell you nothing about the direction of change.
- The chi-square version needs at least about 10 discordant pairs in total. With fewer, use the **exact** version (see the R vs Python box).

### Look at the data first

For paired yes/no data, "looking" means a 2 × 2 table of **before × after**: each patient appears once.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

aid <- proms |>
  filter(visit %in% c("preop", "6wk")) |>
  select(case_id, visit, walking_aid) |>
  pivot_wider(names_from = visit, values_from = walking_aid, names_prefix = "aid_") |>
  filter(!is.na(aid_preop), !is.na(aid_6wk))

aid_table <- table(preop = aid$aid_preop, six_weeks = aid$aid_6wk)   # 1 = uses a walking aid
aid_table
colMeans(aid[, c("aid_preop", "aid_6wk")])                          # proportion using an aid
```

## Python

```{python}
import pandas as pd
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar

proms = pd.read_csv("data/proms_long.csv")

aid = (proms[proms["visit"].isin(["preop", "6wk"])]
       .pivot(index="case_id", columns="visit", values="walking_aid")
       .dropna())

aid_table = pd.crosstab(aid["preop"], aid["6wk"])   # 1 = uses a walking aid
print(aid_table)
print(aid[["preop", "6wk"]].mean())                 # proportion using an aid
```
:::

Of 505 patients seen at both visits, 134 never used an aid and 108 used one at both times. The other 263 changed: **193 started** using an aid and **70 stopped**.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
aid_test <- mcnemar.test(aid_table)   # with a continuity correction, R's default
aid_test
```

## Python

```{python}
aid_test = mcnemar(aid_table.to_numpy(), exact=False, correction=True)   # chi-square version, as in R
print(aid_test)
```
:::

```{python}
#| include: false
chk = {"chisq": float(aid_test.statistic), "p": float(aid_test.pvalue)}
```

```{r}
#| include: false
check_agree(list(chisq = unname(aid_test$statistic), p = aid_test$p.value), reticulate::py$chk)
```

### Read the output

- **McNemar's chi-squared = 56.6, df = 1:** how lopsided the 193 vs 70 split is, compared with the even split you'd expect if walking-aid use hadn't changed.
- **p < 0.001.**

### Effect size and 95% CI

The effect size for McNemar's test is the **discordant-pair odds ratio**: patients who started using an aid divided by patients who stopped, 193 / 70. Its exact CI comes from a binomial test on the discordant pairs.

::: {.panel-tabset group="language"}
## R

```{r}
started <- aid_table["0", "1"]    # no aid before, aid at 6 weeks
stopped <- aid_table["1", "0"]    # aid before, no aid at 6 weeks

started / stopped                                    # discordant-pair odds ratio

ci <- binom.test(started, started + stopped)$conf.int  # CI for the share of changers who started
ci / (1 - ci)                                        # turned into a CI for the odds ratio
```

## Python

```{python}
started = int(aid_table.loc[0, 1])    # no aid before, aid at 6 weeks
stopped = int(aid_table.loc[1, 0])    # aid before, no aid at 6 weeks

print(started / stopped)                                                # discordant-pair odds ratio

ci = stats.binomtest(started, started + stopped).proportion_ci(method="exact")   # share of changers who started
print(ci.low / (1 - ci.low), ci.high / (1 - ci.high))                   # turned into a CI for the odds ratio
```
:::

```{python}
#| include: false
chk = {"or": float(started / stopped), "or_low": float(ci.low / (1 - ci.low)),
       "or_high": float(ci.high / (1 - ci.high))}
```

```{r}
#| include: false
check_agree(list(or = started / stopped, or_low = ci[1] / (1 - ci[1]), or_high = ci[2] / (1 - ci[2])),
            reticulate::py$chk)
```

Patients were 2.8 times as likely to start using an aid as to stop (95% CI 2.1 to 3.7).

### How to report it

> **Methods:** Walking-aid use before surgery and at 6 weeks was compared with McNemar's test, with the discordant-pair odds ratio and its exact 95% CI as the effect size.
>
> **Results:** Among 505 patients assessed at both visits, walking-aid use increased from 35.2% before surgery to 59.6% at 6 weeks: 193 patients started and 70 stopped using an aid (discordant-pair odds ratio 2.76, 95% CI 2.09 to 3.68; p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: no chi-square or Fisher's test on paired yes/no data
A common mistake is to tabulate "aid yes/no" against "pre-op / 6 weeks" and run an ordinary chi-square test. That table counts each patient twice, as if 1010 independent patients had been studied. McNemar's test uses each patient once, through the before × after table.
:::

::: {.callout-tip}
## 🔀 R vs Python: chi-square or exact?
R's `mcnemar.test()` gives the chi-square version, with a continuity correction unless `correct = FALSE`. statsmodels' `mcnemar()` gives the **exact** (binomial) version unless you set `exact=False`. With few discordant pairs (under about 10), the exact version is the right one: in R, run `binom.test(started, started + stopped)`.
:::

## Stratified Cox regression {#stratified-cox}

**The question:** Among patients matched on procedure, age, sex, BMI and ASA class, is the revision risk higher with implant C than with implant A?

### When to use it

- The outcome is **time until an event**, and the patients come in **matched pairs** (or sets), or the two "patients" are the two joints of one person.
- A Cox model **stratified** by pair lets each pair have its own baseline risk, and compares implants only **within** pairs. The decision table calls this *conditional proportional hazards regression*.
- Only pairs in which one patient was revised while the other was still being followed tell the model anything; with few events, expect a wide CI.
- [Page 14](../survival/14-cox-regression.qmd) covers Cox regression in full.

### Look at the data first

The matched file has one row per patient and a `set_id` shared by each matched set. Each set holds one patient with each implant (A, B and C); here we keep A and C, which makes pairs.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)

matched <- read_csv("data/matched_sets.csv", show_col_types = FALSE)

pairs <- matched |>
  filter(implant %in% c("A", "C")) |>
  mutate(revised = as.integer(event_status == 1))   # 1 = revised; deaths and censoring = 0

pairs |> select(set_id, implant, age, sex, bmi, followup_years, revised) |> head(4)
pairs |> group_by(implant) |> summarise(patients = n(), revisions = sum(revised))
```

## Python

```{python}
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

matched = pd.read_csv("data/matched_sets.csv")

pairs = matched[matched["implant"].isin(["A", "C"])].copy()
pairs["revised"] = (pairs["event_status"] == 1).astype(int)   # 1 = revised; deaths and censoring = 0

print(pairs[["set_id", "implant", "age", "sex", "bmi", "followup_years", "revised"]].head(4))
print(pairs.groupby("implant")["revised"].agg(["count", "sum"]))
```
:::

52 pairs: 5 revisions with implant A and 17 with implant C.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
pair_cox <- coxph(Surv(followup_years, revised) ~ implant + strata(set_id), data = pairs)
summary(pair_cox)
```

## Python

```{python}
pair_cox = CoxPHFitter().fit(
    pairs[["followup_years", "revised", "implant", "set_id"]],
    duration_col="followup_years", event_col="revised",
    formula="implant", strata=["set_id"],    # one stratum per matched pair
    fit_options={"precision": 1e-9},         # stop only when fully converged; see the R vs Python box
)
print(pair_cox.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]])
```
:::

```{python}
#| include: false
row = pair_cox.summary.iloc[0]
chk = {"hr": float(row["exp(coef)"]), "hr_low": float(row["exp(coef) lower 95%"]),
       "hr_high": float(row["exp(coef) upper 95%"]), "p": float(row["p"])}
```

```{r}
#| include: false
pair_hr <- summary(pair_cox)$conf.int
check_agree(list(hr = pair_hr[1, "exp(coef)"], hr_low = pair_hr[1, "lower .95"], hr_high = pair_hr[1, "upper .95"],
                 p = summary(pair_cox)$coefficients[1, "Pr(>|z|)"]), reticulate::py$chk)
```

### Read the output

- **n = 104, number of events = 22:** 52 pairs, 22 revisions.
- **exp(coef) = 3.5:** the hazard ratio, implant C vs implant A, within pairs.
- **lower .95 = 1.15, upper .95 = 10.63:** its 95% CI. Wide, because only 22 revisions inform it.
- **Pr(>|z|) = 0.027:** the p-value for implant.
- R also prints a likelihood ratio, Wald and score test for the whole model; with one predictor they all test the same thing.

### Effect size and 95% CI

The **hazard ratio** is the effect size: within matched pairs, the hazard of revision was 3.5 times as high with implant C (95% CI 1.15 to 10.63).

### How to report it

> **Methods:** Revision risk was compared between implants in matched pairs using Cox regression stratified by pair.
>
> **Results:** In 52 pairs matched on procedure, age, sex, BMI and ASA class, implant C had a higher hazard of revision than implant A (17 vs 5 revisions; hazard ratio 3.50, 95% CI 1.15 to 10.63; p = 0.027).

::: {.callout-warning}
## ⚠️ Watch out: don't ignore the matching
An ordinary Cox model on the same 104 patients (without `strata()`) treats them as unrelated. That throws away the matching you worked to create. Here it gives a slightly different answer (hazard ratio 3.60); with stronger matching factors the difference can be large. Analyze matched data as matched.
:::

::: {.callout-tip}
## 🔀 R vs Python: strata and convergence
R puts `strata(set_id)` in the model formula; lifelines takes `strata=["set_id"]` as a separate argument. With so few events and many strata, lifelines' default convergence rule stops a little early (a hazard ratio of 3.4997 instead of 3.5), so we tighten it with `fit_options={"precision": 1e-9}`.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
n_pcs_preop <- sum(!is.na(proms$vr12_pcs[proms$visit == "preop"]))
wide_pair <- function(data, value, first, second) {   # complete pairs of two visits, one row per case
  data |> filter(visit %in% c(first, second)) |> select(case_id, visit, value = all_of(value)) |>
    pivot_wider(names_from = visit, values_from = value) |> filter(!is.na(.data[[first]]), !is.na(.data[[second]]))
}
ex_mcs_wide <- wide_pair(proms, "vr12_mcs", "preop", "1yr")
ex_mcs <- t.test(ex_mcs_wide$`1yr`, ex_mcs_wide$preop, paired = TRUE)
ex_mcs_change <- ex_mcs_wide$`1yr` - ex_mcs_wide$preop
ex_hka <- read_csv("data/radiographic_reliability.csv", show_col_types = FALSE) |>
  filter(session == 1) |> select(knee_id, rater, hka_deg) |> pivot_wider(names_from = rater, values_from = hka_deg)
ex_hka_test <- t.test(ex_hka$R2, ex_hka$R1, paired = TRUE)
ex_later <- wide_pair(filter(proms, instrument == "KOOS JR"), "prom_score", "3mo", "1yr") |>
  rename(koos_3mo = `3mo`, koos_1yr = `1yr`)
ex_later_test <- wilcox.test(ex_later$koos_1yr, ex_later$koos_3mo, paired = TRUE, exact = FALSE, correct = FALSE,
                             conf.int = TRUE)
stopifnot(
  sum(table(distinct(proms, case_id, patient_id)$patient_id) == 2) == 80,
  nrow(pcs) == 436, n_pcs_preop == 574,
  round(unname(pcs_test$statistic), 1) == 31.2, unname(pcs_test$parameter) == 435, pcs_test$p.value < 0.001,
  round(unname(pcs_test$estimate), 1) == 13.7, round(pcs_test$conf.int, 1) == c(12.8, 14.5),
  round(c(mean(pcs$pcs_preop), sd(pcs$pcs_preop), mean(pcs$pcs_1yr), sd(pcs$pcs_1yr)), 1) == c(31.2, 6.3, 44.9, 6.8),
  round(pcs_d$d_z, 2) == 1.49, round(100 * mean(pcs$change > 0)) == 93,
  round(reticulate::py_eval("float(pg.compute_effsize(pcs['1yr'], pcs['preop'], paired=True, eftype='cohen'))"), 2) == 2.08,
  nrow(koos) == 246, all(koos$change > 0),
  unname(koos_test$statistic) == 246 * 247 / 2, unname(koos_test$statistic) == 30381,
  koos_test$p.value < 0.001,
  round(unname(koos_test$estimate), 1) == 34.1, round(koos_test$conf.int, 1) == c(32.3, 35.9),
  round(koos_test$conf.int, 2) == c(32.30, 35.90),
  round(reticulate::py_eval("[float(boot.confidence_interval.low), float(boot.confidence_interval.high)]"), 2) == c(32.30, 35.90),
  koos_rb$r_rank_biserial == 1,
  round(median(koos$koos_preop), 1) == 50.0, round(quantile(koos$koos_preop, c(0.25, 0.75)), 1) == c(40.8, 58.2),
  round(median(koos$koos_1yr), 1) == 85.8, round(quantile(koos$koos_1yr, c(0.25, 0.75)), 1) == c(75.0, 94.0),
  nrow(aid) == 505, aid_table["0", "0"] == 134, aid_table["1", "1"] == 108,
  started == 193, stopped == 70, started + stopped == 263,
  round(unname(aid_test$statistic), 1) == 56.6, aid_test$p.value < 0.001,
  round(100 * mean(aid$aid_preop), 1) == 35.2, round(100 * mean(aid$aid_6wk), 1) == 59.6,
  round(started / stopped, 2) == 2.76, round(ci / (1 - ci), 2) == c(2.09, 3.68), round(ci / (1 - ci), 1) == c(2.1, 3.7),
  round(started / stopped, 1) == 2.8,
  n_distinct(pairs$set_id) == 52, nrow(pairs) == 104, sum(pairs$revised) == 22,
  sum(pairs$revised[pairs$implant == "A"]) == 5, sum(pairs$revised[pairs$implant == "C"]) == 17,
  round(pair_hr[1, "exp(coef)"], 2) == 3.50, round(pair_hr[1, c("lower .95", "upper .95")], 2) == c(1.15, 10.63),
  round(summary(pair_cox)$coefficients[1, "Pr(>|z|)"], 3) == 0.027,
  round(exp(coef(coxph(Surv(followup_years, revised) ~ implant, data = pairs))), 2) == 3.60,
  round(reticulate::py_eval("float(np.exp(CoxPHFitter().fit(pairs[['followup_years', 'revised', 'implant', 'set_id']], duration_col='followup_years', event_col='revised', formula='implant', strata=['set_id']).params_.iloc[0]))"), 4) == 3.4997,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(unname(ex_mcs$estimate), 1) == 3.4, round(ex_mcs$conf.int, 1) == c(2.3, 4.6), ex_mcs$p.value < 0.001,
  round(mean(ex_mcs_change) / sd(ex_mcs_change), 2) == 0.28,
  nrow(ex_hka) == 60, round(unname(ex_hka_test$estimate), 2) == 0.50,
  round(ex_hka_test$conf.int, 2) == c(0.08, 0.93), round(ex_hka_test$p.value, 3) == 0.022,
  nrow(ex_later) == 225, sum(ex_later$koos_1yr > ex_later$koos_3mo) == 176, sum(ex_later$koos_1yr < ex_later$koos_3mo) == 46,
  round(c(median(ex_later$koos_3mo), median(ex_later$koos_1yr)), 1) == c(73.1, 85.2),
  round(unname(ex_later_test$estimate), 1) == 9.9, round(ex_later_test$conf.int, 1) == c(8.2, 11.6),
  ex_later_test$p.value < 0.001,
  round(effectsize::rank_biserial(ex_later$koos_1yr, ex_later$koos_3mo, paired = TRUE)$r_rank_biserial, 2) == 0.74
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Repeat the paired t test for the VR-12 **mental** component score (`vr12_mcs`), pre-op vs 1 year. Report the mean change with its 95% CI and d~z~.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
mcs <- proms |>
  filter(visit %in% c("preop", "1yr")) |>
  select(case_id, visit, vr12_mcs) |>
  pivot_wider(names_from = visit, values_from = vr12_mcs, names_prefix = "mcs_") |>
  filter(!is.na(mcs_preop), !is.na(mcs_1yr))

t.test(mcs$mcs_1yr, mcs$mcs_preop, paired = TRUE)
effectsize::repeated_measures_d(mcs$mcs_1yr, mcs$mcs_preop, method = "z", adjust = FALSE)
```

## Python

```{python}
mcs = proms[proms["visit"].isin(["preop", "1yr"])].pivot(index="case_id", columns="visit", values="vr12_mcs").dropna()
mcs_test = stats.ttest_rel(mcs["1yr"], mcs["preop"])
change = mcs["1yr"] - mcs["preop"]
print(mcs_test, change.mean(), mcs_test.confidence_interval(), change.mean() / change.std())
```
:::

The mental component improved much less than the physical one: mean change 3.4 points (95% CI 2.3 to 4.6; d~z~ = 0.28, a small effect; p < 0.001).
:::

**2.** Two raters measured the hip-knee-ankle (HKA) angle on the same 60 knee X-rays (`radiographic_reliability.csv`, session 1). Does rater 2 measure systematically higher than rater 1? Choose the test and run it.

::: {.callout-tip collapse="true"}
## Solution
Two measurements of the same X-ray are **paired**, and HKA angles are measurements that are roughly normal: the **paired t test**.

::: {.panel-tabset group="language"}
## R

```{r}
readings <- read_csv("data/radiographic_reliability.csv", show_col_types = FALSE) |>
  filter(session == 1) |>
  select(knee_id, rater, hka_deg) |>
  pivot_wider(names_from = rater, values_from = hka_deg)

t.test(readings$R2, readings$R1, paired = TRUE)   # rater 2 minus rater 1
```

## Python

```{python}
readings = pd.read_csv("data/radiographic_reliability.csv")
readings = readings[readings["session"] == 1].pivot(index="knee_id", columns="rater", values="hka_deg")
hka_test = stats.ttest_rel(readings["R2"], readings["R1"])   # rater 2 minus rater 1
print(hka_test, (readings["R2"] - readings["R1"]).mean(), hka_test.confidence_interval())
```
:::

Rater 2 measured 0.50° higher on average (95% CI 0.08° to 0.93°; p = 0.022). A systematic difference this small may not matter clinically; [page 17](../beyond/17-agreement.qmd) shows how to judge agreement between raters properly.
:::

**3.** Patients improve a lot in the first 3 months. Do they keep improving between 3 months and 1 year? Test it for KOOS JR and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution
KOOS JR has a ceiling at 1 year, so use the **Wilcoxon signed-rank test**.

::: {.panel-tabset group="language"}
## R

```{r}
later <- proms |>
  filter(instrument == "KOOS JR", visit %in% c("3mo", "1yr")) |>
  select(case_id, visit, prom_score) |>
  pivot_wider(names_from = visit, values_from = prom_score, names_prefix = "koos_") |>
  filter(!is.na(koos_3mo), !is.na(koos_1yr))

wilcox.test(later$koos_1yr, later$koos_3mo, paired = TRUE, exact = FALSE, correct = FALSE, conf.int = TRUE)
effectsize::rank_biserial(later$koos_1yr, later$koos_3mo, paired = TRUE)
later |> summarise(n = n(), better = sum(koos_1yr > koos_3mo), worse = sum(koos_1yr < koos_3mo),
                   median_3mo = median(koos_3mo), median_1yr = median(koos_1yr))
```

## Python

```{python}
later = (proms[(proms["instrument"] == "KOOS JR") & proms["visit"].isin(["3mo", "1yr"])]
         .pivot(index="case_id", columns="visit", values="prom_score").dropna())
print(pg.wilcoxon(later["1yr"], later["3mo"], method="approx", correction=False))
print(len(later), (later["1yr"] > later["3mo"]).sum(), (later["1yr"] < later["3mo"]).sum())
```
:::

"Between 3 months and 1 year, KOOS JR improved further in 176 of 225 patients and declined in 46 (median 73.1 to 85.2; Hodges-Lehmann estimate of the change 9.9 points, 95% CI 8.2 to 11.6; rank-biserial r = 0.74; p < 0.001)."
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/07-two-paired-groups.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `117 passed`.

- [ ] **Step 5: Prove the agreement check bites, then restore**

In the `#mcnemar` section's Run-it Python block, change `aid_test = mcnemar(aid_table.to_numpy(), exact=False, correction=True)` to `aid_test = mcnemar(aid_table.to_numpy())` (statsmodels' default, the exact test), then run `quarto render catalog/07-two-paired-groups.qmd`. Expected: the render FAILS with `check_agree(): R and Python disagree on 'chisq'`. Undo the change, then run:

```bash
rm -rf catalog/07-two-paired-groups_files
quarto render catalog/07-two-paired-groups.qmd
uv run pytest tests/site -q
```

Expected: `117 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/07-two-paired-groups.qmd _freeze/catalog/07-two-paired-groups tests/site/test_catalog.py
git commit -m "Write page 7, two paired groups: paired t, Wilcoxon signed-rank, McNemar, stratified Cox

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Record the conventions and run everything

**Files:**
- Modify: `CLAUDE.md`, `tests/python/test_repo_docs.py`

- [ ] **Step 1: Write the failing test**

In `tests/python/test_repo_docs.py`, replace

```python
    for rule in ["engine: knitr", "group=\"language\"", "check_agree", "_freeze", "Synthetic data only"]:
```

with

```python
    for rule in ["engine: knitr", "group=\"language\"", "check_agree", "_freeze", "Synthetic data only",
                 "never assign to `_`", "**The question:**", "override-dependencies"]:
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `test_claude_md_states_the_golden_rules` FAILS on `never assign to `_``.

- [ ] **Step 2: Update CLAUDE.md**

In `CLAUDE.md`'s golden rule 10, replace

```markdown
10. **Quiet pages.** Pages with code set `execute: message: false` in their front matter, and chunks that call `library()` add `#| warning: false`. A site test fails on any stderr output. Don't attach packages that mask base functions (janitor masks `chisq.test()`/`fisher.test()`); call them as `pkg::fun()`.
```

with

```markdown
10. **Quiet pages.** Pages with code set `execute: message: false` in their front matter, and chunks that call `library()` add `#| warning: false`. A site test fails on any stderr output. Don't attach packages that mask base functions (janitor masks `chisq.test()`/`fisher.test()`); call them as `pkg::fun()`. In Python chunks, never assign to `_` (as in `_ = ax.hist(...)`): reticulate reads `_` to decide what to print, and once `_` holds a plot object every later Python output on the page silently disappears. Bare matplotlib calls print nothing; give any other result you want to hide a name (`qq = stats.probplot(...)`). `tests/site/test_sources.py` enforces this.
```

and replace golden rule 12

```markdown
12. **Exercise solutions are executed chunks** (`{r}` / `{python}`) inside the collapsed Solution callout, so they can't rot.
```

with

```markdown
12. **Exercise solutions are executed chunks** (`{r}` / `{python}`) inside the collapsed Solution callout, so they can't rot.
13. **Catalog sections follow spec §6.** Each decision-table section opens with a `**The question:**` line, then these `###` steps in order: When to use it, Look at the data first, Run it, Read the output, Effect size and 95% CI (not on page 4, where the estimate is the result), How to report it (a Methods and a Results blockquote). Each section also has a ⚠️ box. A section's first tabset loads its own packages and data, because readers jump straight to it from the decision table. Catalog pages set `toc-depth: 2`. `tests/site/test_catalog.py` and `tests/site/test_sources.py` enforce this.
14. **Python survival uses lifelines on pandas 3.** lifelines declares `pandas<3`, but the pages are written for pandas 3 (page 1's tidying breaks on pandas 2), so `pyproject.toml` sets `override-dependencies = ["pandas>=3.0"]`. Every lifelines number on a page is checked against R's survival package by `check_agree()`. Remove the override once lifelines supports pandas 3.
```

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
- Python: `80 passed`
- `quarto render` re-executes nothing (every page's freeze is current)
- site: `117 passed`
- lychee: `0 Errors`
- `git status` shows only `CLAUDE.md` and `tests/python/test_repo_docs.py`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md tests/python/test_repo_docs.py
git commit -m "CLAUDE.md: record Phase 3a conventions (catalog anatomy, no _ in Python chunks, lifelines on pandas 3)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
