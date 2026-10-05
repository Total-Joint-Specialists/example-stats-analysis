# Phase 0: Site Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the public TJS statistics tutorial site. That means R/Python environments, the Quarto website with all 22 pages (the three Getting Started pages written, the rest as "coming soon" stubs), the clickable decision table, the R ⟷ Python agreement guard, CI, and GitHub Pages publishing.

**Architecture:** A Quarto website rendered with the knitr engine. Python runs inside the same render through `reticulate` against a `uv` virtualenv, so a hidden R chunk can compare R and Python results and halt the build on disagreement. Computed output is frozen (`_freeze/`, committed). GitHub Actions builds from the freeze with no R or Python, runs site tests and a link checker, and publishes to the `gh-pages` branch.

**Tech Stack:**
- R 4.6 + renv (explicit snapshot from `DESCRIPTION`); testthat, withr, reticulate, knitr, rmarkdown
- Python 3.13 via uv; pandas, numpy, matplotlib; dev: pytest, beautifulsoup4
- Quarto 1.9.37
- GitHub Actions: `actions/checkout@v7`, `quarto-dev/quarto-actions@v2`, `astral-sh/setup-uv@v10`, `lycheeverse/lychee-action@v2`
- lychee 0.24.2 (local link checker), just

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`

## Global Constraints

- **Public repo, synthetic data only.** Never commit real patient data, real names, MRNs, or real dates.
- **Repo and site:** repo `Total-Joint-Specialists/example-stats-analysis`; site `https://total-joint-specialists.github.io/example-stats-analysis/`.
- **Versions:** R ≥ 4.4 for users; the lockfile records 4.6.0. Python `requires-python >=3.12`, and `.python-version` is `3.13`. Quarto `1.9.37`, both locally and in CI.
- **`engine: knitr` per page.** Every `.qmd` with an executable chunk (```` ```{r} ```` or ```` ```{python} ````) declares `engine: knitr` in its **own** front matter. Quarto ignores `engine` in `_quarto.yml` and `_metadata.yml`.
- **Language tabsets:** `::: {.panel-tabset group="language"}` with exactly two tabs, `## R` first and `## Python` second.
- **Agreement guard:** each page sources `R/check_agree.R` in a hidden chunk at the top. Each R/Python pair is followed by a hidden R chunk that calls `check_agree(list(<R values>), list(<reticulate::py$... values>))`. Hidden means `#| include: false`.
- **Data paths are project-relative** (`data/...`); `execute-dir: project`.
- **Callouts:**

  | Callout | Quarto markup |
  |---|---|
  | 💡 In plain language | `callout-note` |
  | ⚠️ Watch out | `callout-warning` |
  | 🔀 R vs Python | `callout-tip` |
  | 🔍 Under the hood | `callout-note collapse="true"` |
  | Exercise solutions | `callout-tip collapse="true"`, titled `Solution` |

- **Reporting conventions:**
  - mean (SD) for roughly symmetric data; median (IQR) for skewed
  - n (%) for categories
  - p-values to 3 decimals, floor "p < 0.001", never "p = 0.000"
  - a 95% CI with every effect estimate
- **Stub pages** have "(coming soon)" at the end of the title and a `::: {.callout-note .coming-soon}` box.
- **Licenses:** code MIT (`LICENSE`); text, figures and data CC BY 4.0 (`LICENSE-CONTENT`). Copyright holder: "Total Joint Specialists".
- **Branching:** do Tasks 1–9 on branch `phase-0-scaffold`. Task 10 runs after that branch is merged to `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **An RA saves a real spreadsheet or CSV in the repo folder and runs `git add .`** It must be ignored everywhere except `data/` and `templates/`. Test: `tests/python/test_gitignore.py` (Task 1).
2. **An R-only RA never ran `uv sync`.** R must start cleanly and leave `RETICULATE_PYTHON` unset. Test: `tests/testthat/test-environment.R` (Task 1).
3. **A page with Python chunks forgets `engine: knitr`.** It would silently run in Jupyter on the system Python, so the source test must fail. Test: `tests/site/test_sources.py` (Task 3).
4. **A home-table link has a typo or points at a missing anchor.** The site test and lychee must fail. Tests: `tests/site/test_structure.py` (Task 3), `tests/site/test_home.py` (Task 4), and lychee in `just check` (Task 9).
5. **An RA's Mac has an unaccepted Xcode license**, so `renv::restore()` fails. The setup page must give the exact fix. Test: `tests/site/test_getting_started.py` (Task 6).

## Before you start (owner, once per Mac)

These need a password or a human decision, so the owner runs them. Do not run `sudo` yourself.

- [ ] **Accept the Xcode license.** It blocks `renv::install()` and `renv::restore()` (verified 2026-10-05). In a terminal:

```bash
sudo xcodebuild -license accept
```

Check: `Rscript -e 'system("R CMD config CC")'` prints a compiler name (e.g. `clang -arch arm64`) and no license message.

---

### Task 1: Project environments (R + Python) and safety ignores

**Files:**
- Create: `.gitignore` (overwrite the one-line version from the spec commit), `scratch/README.md`, `DESCRIPTION`, `.Rprofile` (renv creates it; you append), `renv/` (generated), `renv.lock` (generated), `pyproject.toml`, `.python-version`, `uv.lock` (generated)
- Test: `tests/python/test_gitignore.py`, `tests/testthat/test-environment.R`

**Interfaces:**
- Produces:
  - `.venv/bin/python`, the project Python that reticulate uses
  - `RETICULATE_PYTHON`, set by `.Rprofile` only when `.venv` exists
  - the R packages knitr, reticulate, rmarkdown, testthat and withr
  - the Python packages pandas, numpy and matplotlib, plus pytest and beautifulsoup4 in the `dev` group
  - the commands `uv run pytest ...` and `Rscript -e 'testthat::test_dir("tests/testthat")'`

- [ ] **Step 1: Create the branch**

```bash
git checkout -b phase-0-scaffold
```

- [ ] **Step 2: Write the Python project files**

`pyproject.toml`:

```toml
[project]
name = "tjs-stats-tutorials"
version = "0.1.0"
description = "Python environment for the TJS statistics tutorial site"
requires-python = ">=3.12"
dependencies = [
    "matplotlib>=3.9",
    "numpy>=2.0",
    "pandas>=2.2",
]

[dependency-groups]
dev = [
    "beautifulsoup4>=4.12",
    "pytest>=8.0",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
addopts = "-ra"
```

`.python-version`:

```
3.13
```

Run: `uv sync`
Expected: creates `.venv/` and `uv.lock`, then prints `Installed N packages`.

- [ ] **Step 3: Write the failing gitignore test**

`tests/python/test_gitignore.py`:

```python
"""This repo is public. Data files must never be committable outside data/
and templates/, and local environments and build output stay out of git."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def ignored(path: str) -> bool:
    result = subprocess.run(["git", "check-ignore", "--no-index", "-q", path], cwd=ROOT)
    return result.returncode == 0


@pytest.mark.parametrize(
    "path",
    [
        "patients.xlsx",
        "export.csv",
        "analysis/real_data.csv",
        "chart_pull.xls",
        "dataset.sav",
        "dataset.dta",
        "dataset.sas7bdat",
        "cohort.rds",
        "cohort.parquet",
        "IMG0001.dcm",
        "scratch/my_analysis.R",
        ".venv/bin/python",
        "_site/index.html",
        ".Renviron",
    ],
)
def test_risky_or_generated_files_are_ignored(path):
    assert ignored(path), f"{path} could be committed"


@pytest.mark.parametrize(
    "path",
    [
        "data/cohort.csv",
        "data/codebooks/cohort.csv",
        "data/answer-keys/survey_items_long.csv",
        "data/messy_abstraction_workbook.xlsx",
        "templates/data-collection-template.xlsx",
        "scratch/README.md",
        "_freeze/getting-started/using-this-site/execute-results/html.json",
        "renv.lock",
    ],
)
def test_project_files_are_not_ignored(path):
    assert not ignored(path), f"{path} is wrongly ignored"
```

- [ ] **Step 4: Run it to verify it fails**

Run: `uv run pytest tests/python/test_gitignore.py -q`
Expected: FAIL. Many risky paths are reported "could be committed", because the current `.gitignore` only lists `.DS_Store`.

- [ ] **Step 5: Write `.gitignore` and `scratch/README.md`**

`.gitignore`:

```gitignore
# --- Local environments and build output ---
.DS_Store
.Rhistory
.RData
.Rproj.user/
.Renviron
.venv/
__pycache__/
.pytest_cache/
.quarto/
_site/
/.luarc.json

# --- Practice space: everything in scratch/ stays on your computer ---
scratch/*
!scratch/README.md

# --- This repo is PUBLIC. Data files are blocked everywhere ... ---
*.csv
*.tsv
*.xlsx
*.xls
*.xlsm
*.sav
*.dta
*.sas7bdat
*.rds
*.rda
*.parquet
*.feather
*.dcm
*.zip
# --- ... except the synthetic files in data/ and templates/ ---
!/data/**
!/templates/**
```

`scratch/README.md`:

```markdown
# scratch/

Your practice space. Save exercise files here (for example `scratch/practice.R`
or `scratch/practice.py`).

Git ignores everything in this folder except this README, so nothing you save
here can be committed by accident.
```

- [ ] **Step 6: Run it to verify it passes**

Run: `uv run pytest tests/python/test_gitignore.py -q`
Expected: `22 passed`.

- [ ] **Step 7: Write `DESCRIPTION` and initialize renv**

`DESCRIPTION`:

```
Type: project
Description: R dependencies for the TJS statistics tutorial site. Not a
    package; renv reads this file to decide what to lock.
Imports:
    knitr,
    reticulate,
    rmarkdown,
    testthat,
    withr
```

Run:

```bash
Rscript -e 'renv::init(bare = TRUE); renv::settings$snapshot.type("explicit")'
```

Expected:
- the output includes `Using 'explicit' snapshot type`
- `renv/activate.R` and `renv/settings.json` exist
- `.Rprofile` contains `source("renv/activate.R")`

- [ ] **Step 8: Append the reticulate wiring to `.Rprofile`**

Append these lines **below** the existing `source("renv/activate.R")` line. The final `.Rprofile`:

```r
source("renv/activate.R")

# Point reticulate at this project's uv environment (created by `uv sync`).
# People who only use R, and never ran `uv sync`, are unaffected.
local({
  py <- if (.Platform$OS.type == "windows") {
    file.path(getwd(), ".venv", "Scripts", "python.exe")
  } else {
    file.path(getwd(), ".venv", "bin", "python")
  }
  if (file.exists(py)) Sys.setenv(RETICULATE_PYTHON = py)
})
```

- [ ] **Step 9: Write the failing environment test**

`tests/testthat/test-environment.R`:

```r
root <- normalizePath(testthat::test_path("..", ".."))
rscript <- file.path(R.home("bin"), "Rscript")

# Start a fresh R in `dir` (with RETICULATE_PYTHON cleared) and report what
# the project's .Rprofile set it to.
reticulate_python_seen_in <- function(dir) {
  withr::local_envvar(RETICULATE_PYTHON = NA)
  out <- withr::with_dir(dir, system2(
    rscript, c("-e", shQuote("cat('RP=', Sys.getenv('RETICULATE_PYTHON'), sep = '')")),
    stdout = TRUE, stderr = TRUE))
  sub("^RP=", "", grep("^RP=", out, value = TRUE))
}

# A throwaway project folder holding a copy of .Rprofile and a no-op renv.
fake_project <- function() {
  dir <- withr::local_tempdir(.local_envir = parent.frame())
  dir.create(file.path(dir, "renv"))
  writeLines("", file.path(dir, "renv", "activate.R"))
  file.copy(file.path(root, ".Rprofile"), dir)
  dir
}

test_that("R points reticulate at the project's uv environment", {
  py <- file.path(root, ".venv", "bin", "python")
  expect_true(file.exists(py), label = "run `uv sync` first; .venv/bin/python")
  expect_equal(normalizePath(Sys.getenv("RETICULATE_PYTHON")), normalizePath(py))
  expect_equal(normalizePath(reticulate::py_config()$python), normalizePath(py))
})

test_that("the Python packages the pages rely on import from R", {
  for (m in c("pandas", "numpy", "matplotlib")) {
    expect_true(reticulate::py_module_available(m), label = m)
  }
})

test_that("an R-only user without .venv gets a clean session", {
  dir <- fake_project()
  expect_equal(reticulate_python_seen_in(dir), "")
})

test_that("a user with .venv gets RETICULATE_PYTHON set", {
  dir <- fake_project()
  dir.create(file.path(dir, ".venv", "bin"), recursive = TRUE)
  file.create(file.path(dir, ".venv", "bin", "python"))
  expect_match(reticulate_python_seen_in(dir), "[.]venv/bin/python$")
})
```

- [ ] **Step 10: Run it to verify it fails**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "environment")'`
Expected: FAIL or error. The error is `there is no package called 'testthat'`, or else `reticulate`/`withr` is missing, because renv's project library is still empty.

- [ ] **Step 11: Install the R packages and snapshot**

```bash
Rscript -e 'renv::install(c("knitr", "reticulate", "rmarkdown", "testthat", "withr"), prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
```

Expected:
- `renv.lock` is written
- `python3 -c "import json; d=json.load(open('renv.lock')); print(all(p in d['Packages'] for p in ['knitr','reticulate','rmarkdown','testthat','withr']))"` prints `True`

If `renv::install` stops with `You have not agreed to the Xcode license`, stop. Ask the owner to complete "Before you start".

- [ ] **Step 12: Run it to verify it passes**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "environment", stop_on_failure = TRUE)'`
Expected: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 8 ]`

- [ ] **Step 13: Commit**

```bash
git add .gitignore scratch/README.md DESCRIPTION .Rprofile renv.lock renv/activate.R renv/settings.json renv/.gitignore pyproject.toml .python-version uv.lock tests/python/test_gitignore.py tests/testthat/test-environment.R
git commit -m "Set up R (renv) and Python (uv) environments with safety ignores

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `check_agree()`, the R ⟷ Python agreement guard

**Files:**
- Create: `R/check_agree.R`
- Test: `tests/testthat/test-check_agree.R`

**Interfaces:**
- Consumes: testthat (Task 1).
- Produces: `check_agree(r, py, tol = 1e-6)`.
  - `r` and `py` are named lists of single finite numbers.
  - It returns `invisible(TRUE)` on agreement and otherwise stops with a message that starts `check_agree():`.
  - Pages call it as `check_agree(list(x = r_x), list(x = reticulate::py$x))`.

- [ ] **Step 1: Write the failing test**

`tests/testthat/test-check_agree.R`:

```r
source(testthat::test_path("..", "..", "R", "check_agree.R"))

test_that("matching results pass silently", {
  expect_invisible(check_agree(list(t = 2.41, p = 0.017), list(p = 0.017, t = 2.41)))
})

test_that("tiny numerical noise is tolerated, relative to magnitude", {
  expect_true(check_agree(list(p = 0.0170000001), list(p = 0.017)))
  expect_true(check_agree(list(stat = 12345.6), list(stat = 12345.6 * (1 + 1e-8))))
})

test_that("integers from Python count as numbers", {
  expect_true(check_agree(list(df = 598), list(df = 598L)))
})

test_that("a real disagreement stops with both values in the message", {
  expect_error(check_agree(list(p = 0.017), list(p = 0.021)),
               "disagree on 'p': R = 0.017, Python = 0.021")
})

test_that("different result names stop", {
  expect_error(check_agree(list(t = 1, p = 0.5), list(t = 1)),
               "R has \\[p, t\\] but Python has \\[t\\]")
})

test_that("missing or infinite values never pass", {
  expect_error(check_agree(list(p = NA_real_), list(p = NA_real_)), "not a finite number")
  expect_error(check_agree(list(p = NaN), list(p = 0.5)), "not a finite number")
  expect_error(check_agree(list(z = Inf), list(z = Inf)), "not a finite number")
})

test_that("non-numbers and vectors stop", {
  expect_error(check_agree(list(p = "0.017"), list(p = 0.017)), "single number")
  expect_error(check_agree(list(p = c(0.1, 0.2)), list(p = 0.1)), "single number")
  expect_error(check_agree(list(sig = TRUE), list(sig = TRUE)), "single number")
})

test_that("unnamed input stops", {
  expect_error(check_agree(list(0.017), list(0.017)), "named lists")
})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_agree")'`
Expected: error `cannot open file '.../R/check_agree.R': No such file or directory`.

- [ ] **Step 3: Write the implementation**

`R/check_agree.R`:

```r
# check_agree(): the hidden guard at the end of each test section on a
# tutorial page. It stops the render when R and Python disagree.
#
#   r    named list of single numbers, e.g. list(t = 2.41, p = 0.017)
#   py   the same, from Python, e.g. list(t = reticulate::py$t_stat, ...)
#   tol  allowed difference, relative to the larger magnitude
#        (absolute for magnitudes below 1)

check_agree <- function(r, py, tol = 1e-6) {
  if (!is.list(r) || !is.list(py) || is.null(names(r)) || is.null(names(py))) {
    stop("check_agree(): both arguments must be named lists", call. = FALSE)
  }
  if (!setequal(names(r), names(py))) {
    stop(sprintf("check_agree(): R has [%s] but Python has [%s]",
                 paste(sort(names(r)), collapse = ", "),
                 paste(sort(names(py)), collapse = ", ")), call. = FALSE)
  }
  for (nm in names(r)) {
    a <- r[[nm]]
    b <- py[[nm]]
    if (!is.numeric(a) || length(a) != 1 || !is.numeric(b) || length(b) != 1) {
      stop(sprintf("check_agree(): '%s' must be a single number in both languages (wrap Python values in float())", nm),
           call. = FALSE)
    }
    if (!is.finite(a) || !is.finite(b)) {
      stop(sprintf("check_agree(): '%s' is not a finite number (R = %s, Python = %s)", nm, a, b),
           call. = FALSE)
    }
    if (abs(a - b) > tol * max(1, abs(a), abs(b))) {
      stop(sprintf("check_agree(): R and Python disagree on '%s': R = %.10g, Python = %.10g",
                   nm, a, b), call. = FALSE)
    }
  }
  invisible(TRUE)
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_agree", stop_on_failure = TRUE)'`
Expected: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 13 ]`

- [ ] **Step 5: Commit**

```bash
git add R/check_agree.R tests/testthat/test-check_agree.R
git commit -m "Add check_agree() guard that halts renders when R and Python disagree

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Quarto site skeleton, 22 pages, structure tests

**Files:**
- Create: `_quarto.yml`, `styles.css`, `index.qmd` (placeholder; Task 4 replaces it), 21 stub pages under `getting-started/`, `foundations/`, `catalog/`, `survival/`, `beyond/`, `report/`
- Test: `tests/site/sitelib.py`, `tests/site/conftest.py`, `tests/site/test_structure.py`, `tests/site/test_sources.py`

**Interfaces:**
- Consumes: the Python dev group (pytest, beautifulsoup4) from Task 1.
- Produces:
  - `tests/site/sitelib.py` exports `ROOT`, `SITE`, `PAGES` (list of 22 html paths), `CELL_ANCHORS` (dict: catalog html path → list of anchor ids) and `load(page) -> BeautifulSoup`.
  - The pytest fixture `site` (`tests/site/conftest.py`) fails with "Run `quarto render` first" when `_site/` is missing.
  - Every page path and anchor id listed below. Later tasks link to them.

- [ ] **Step 1: Write the test helpers**

`tests/site/sitelib.py`:

```python
"""Shared constants and helpers for the built-site tests."""

from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "_site"

PAGES = [
    "index.html",
    "getting-started/setup.html",
    "getting-started/using-this-site.html",
    "getting-started/real-data.html",
    "foundations/01-tidy-data.html",
    "foundations/02-demographics.html",
    "foundations/03-distributions.html",
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
    "catalog/11-predict-from-one.html",
    "catalog/12-predict-from-several.html",
    "survival/13-kaplan-meier.html",
    "survival/14-cox-regression.html",
    "beyond/15-post-hoc.html",
    "beyond/16-mixed-models.html",
    "beyond/17-agreement.html",
    "report/18-example-report.html",
]

# Spec section 3.2: every non-empty cell of the decision table, by row page.
CELL_ANCHORS = {
    "catalog/04-describe-one-group.html": ["mean-sd", "median-iqr", "proportion", "kaplan-meier"],
    "catalog/05-one-group-vs-hypothetical.html": [
        "one-sample-t", "wilcoxon-signed-rank", "chi-square-gof", "binomial-test"],
    "catalog/06-two-unpaired-groups.html": [
        "unpaired-t", "mann-whitney", "fisher-chi-square", "log-rank"],
    "catalog/07-two-paired-groups.html": [
        "paired-t", "wilcoxon-signed-rank", "mcnemar", "stratified-cox"],
    "catalog/08-three-plus-unmatched.html": [
        "one-way-anova", "kruskal-wallis", "chi-square", "cox"],
    "catalog/09-three-plus-matched.html": [
        "repeated-measures-anova", "friedman", "cochran-q", "stratified-cox"],
    "catalog/10-association.html": ["pearson", "spearman", "contingency-coefficients"],
    "catalog/11-predict-from-one.html": [
        "linear-regression", "nonlinear-regression", "nonparametric-regression",
        "logistic-regression", "cox"],
    "catalog/12-predict-from-several.html": [
        "multiple-linear-regression", "multiple-nonlinear-regression",
        "multiple-logistic-regression", "cox"],
}


def load(page: str) -> BeautifulSoup:
    return BeautifulSoup((SITE / page).read_text(encoding="utf-8"), "html.parser")


def strip_dot(href: str) -> str:
    return href.removeprefix("./")
```

`tests/site/conftest.py`:

```python
import pytest

from sitelib import SITE


@pytest.fixture(scope="session")
def site():
    if not (SITE / "index.html").exists():
        pytest.fail("No built site in _site/. Run `quarto render` first.")
    return SITE
```

- [ ] **Step 2: Write the failing structure and source tests**

`tests/site/test_structure.py`:

```python
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
```

`tests/site/test_sources.py`:

```python
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
```

- [ ] **Step 3: Run them to verify they fail**

Run: `uv run pytest tests/site -q`
Expected: the five `test_structure.py` tests FAIL with "No built site in _site/". `test_every_page_with_code_declares_knitr` FAILS with `FileNotFoundError` for `index.qmd`. The three `test_rule_*` tests pass.

- [ ] **Step 4: Write `_quarto.yml` and `styles.css`**

`_quarto.yml`:

```yaml
project:
  type: website
  output-dir: _site
  execute-dir: project
  render:
    - index.qmd
    - getting-started/*.qmd
    - foundations/*.qmd
    - catalog/*.qmd
    - survival/*.qmd
    - beyond/*.qmd
    - report/*.qmd

# Note: `engine: knitr` does NOT work here or in _metadata.yml. Each page
# with code declares it in its own front matter.
execute:
  freeze: auto

website:
  title: "TJS Statistics Tutorials"
  description: "Tidy data, Table 1, and every common statistical test, in R and Python, for Total Joint Specialists research assistants."
  site-url: "https://total-joint-specialists.github.io/example-stats-analysis/"
  repo-url: "https://github.com/Total-Joint-Specialists/example-stats-analysis"
  repo-actions: [issue]
  search: true
  page-navigation: true
  navbar:
    left:
      - text: "Decision table"
        href: index.qmd
      - text: "Getting started"
        href: getting-started/setup.qmd
    right:
      - icon: github
        href: "https://github.com/Total-Joint-Specialists/example-stats-analysis"
        aria-label: "GitHub repository"
  sidebar:
    style: docked
    contents:
      - text: "Decision table"
        href: index.qmd
      - section: "Getting started"
        contents:
          - getting-started/setup.qmd
          - getting-started/using-this-site.qmd
          - getting-started/real-data.qmd
      - section: "Part 1 · Foundations"
        contents:
          - foundations/01-tidy-data.qmd
          - foundations/02-demographics.qmd
          - foundations/03-distributions.qmd
      - section: "Part 2 · Test catalog"
        contents:
          - catalog/04-describe-one-group.qmd
          - catalog/05-one-group-vs-hypothetical.qmd
          - catalog/06-two-unpaired-groups.qmd
          - catalog/07-two-paired-groups.qmd
          - catalog/08-three-plus-unmatched.qmd
          - catalog/09-three-plus-matched.qmd
          - catalog/10-association.qmd
          - catalog/11-predict-from-one.qmd
          - catalog/12-predict-from-several.qmd
      - section: "Part 3 · Survival analysis"
        contents:
          - survival/13-kaplan-meier.qmd
          - survival/14-cox-regression.qmd
      - section: "Part 4 · Beyond the table"
        contents:
          - beyond/15-post-hoc.qmd
          - beyond/16-mixed-models.qmd
          - beyond/17-agreement.qmd
      - section: "Part 5 · Putting it together"
        contents:
          - report/18-example-report.qmd
  page-footer:
    left: "Synthetic data only. Never put patient data in a repository."
    right: "Text CC BY 4.0 · Code MIT"

format:
  html:
    theme:
      light: flatly
      dark: darkly
    css: styles.css
    toc: true
    toc-depth: 3
    code-copy: true
    code-overflow: wrap
```

`styles.css`:

```css
/* Home-page decision table */
.decision-table table {
  font-size: 0.9rem;
}

.decision-table td {
  vertical-align: top;
}

.decision-table td:first-child,
.decision-table th:first-child {
  min-width: 11rem;
}
```

- [ ] **Step 5: Write the placeholder home page and generate the 21 stubs**

`index.qmd` (placeholder; Task 4 replaces it):

```markdown
---
title: "TJS Statistics Tutorials"
---

The decision table arrives in the next commit.
```

Run this one-off script from the repo root. It writes every stub; don't commit it.

```bash
python3 - <<'EOF'
from pathlib import Path

BOX = """::: {.callout-note .coming-soon}
## Coming soon
This page is being written. Links from the decision table already point at its sections, so they will keep working when the content arrives.
:::
"""

# (path, title, description, [(heading, anchor), ...])
STUBS = [
    ("getting-started/setup.qmd", "Install & set up",
     "Everything you need on your computer to run the examples.", []),
    ("getting-started/using-this-site.qmd", "How to use this site",
     "Choosing R or Python, running examples, callouts, reporting, exercises.", []),
    ("getting-started/real-data.qmd", "Working with real TJS data",
     "Keeping patient data safe: what counts as PHI and where data may live.", []),
    ("foundations/01-tidy-data.qmd", "1 · Tidy data",
     "What tidy data is, how to collect it, how to tidy messy spreadsheets, and how to prove nothing changed.", []),
    ("foundations/02-demographics.qmd", "2 · Demographics (Table 1)",
     "Build a publication-ready Table 1 for one group or several.", []),
    ("foundations/03-distributions.qmd", "3 · Distributions & choosing a test",
     "Check whether data look normal, and use that to pick the right test.", []),
    ("catalog/04-describe-one-group.qmd", "4 · Describe one group",
     "Mean and SD, median and IQR, proportion, and the Kaplan-Meier curve.",
     [("Mean and standard deviation", "mean-sd"),
      ("Median and interquartile range", "median-iqr"),
      ("Proportion", "proportion"),
      ("Kaplan-Meier survival curve", "kaplan-meier")]),
    ("catalog/05-one-group-vs-hypothetical.qmd", "5 · Compare one group to a hypothetical value",
     "One-sample t test, Wilcoxon signed-rank test, chi-square goodness-of-fit, binomial test.",
     [("One-sample t test", "one-sample-t"),
      ("Wilcoxon signed-rank test", "wilcoxon-signed-rank"),
      ("Chi-square goodness-of-fit test", "chi-square-gof"),
      ("Binomial test", "binomial-test")]),
    ("catalog/06-two-unpaired-groups.qmd", "6 · Compare two unpaired groups",
     "Unpaired t test, Mann-Whitney test, Fisher's exact test, log-rank test.",
     [("Unpaired t test", "unpaired-t"),
      ("Mann-Whitney test", "mann-whitney"),
      ("Fisher's exact test and chi-square", "fisher-chi-square"),
      ("Log-rank test", "log-rank")]),
    ("catalog/07-two-paired-groups.qmd", "7 · Compare two paired groups",
     "Paired t test, Wilcoxon signed-rank test, McNemar's test, stratified Cox regression.",
     [("Paired t test", "paired-t"),
      ("Wilcoxon signed-rank test", "wilcoxon-signed-rank"),
      ("McNemar's test", "mcnemar"),
      ("Stratified Cox regression", "stratified-cox")]),
    ("catalog/08-three-plus-unmatched.qmd", "8 · Compare three or more unmatched groups",
     "One-way ANOVA, Kruskal-Wallis test, chi-square test, Cox regression.",
     [("One-way ANOVA", "one-way-anova"),
      ("Kruskal-Wallis test", "kruskal-wallis"),
      ("Chi-square test", "chi-square"),
      ("Cox regression", "cox")]),
    ("catalog/09-three-plus-matched.qmd", "9 · Compare three or more matched groups",
     "Repeated-measures ANOVA, Friedman test, Cochran's Q, stratified Cox regression.",
     [("Repeated-measures ANOVA", "repeated-measures-anova"),
      ("Friedman test", "friedman"),
      ("Cochran's Q test", "cochran-q"),
      ("Stratified Cox regression", "stratified-cox")]),
    ("catalog/10-association.qmd", "10 · Quantify association between two variables",
     "Pearson correlation, Spearman correlation, contingency coefficients.",
     [("Pearson correlation", "pearson"),
      ("Spearman correlation", "spearman"),
      ("Contingency coefficients", "contingency-coefficients")]),
    ("catalog/11-predict-from-one.qmd", "11 · Predict a value from another variable",
     "Simple linear and nonlinear regression, nonparametric regression, simple logistic regression, Cox regression.",
     [("Simple linear regression", "linear-regression"),
      ("Nonlinear regression", "nonlinear-regression"),
      ("Nonparametric regression", "nonparametric-regression"),
      ("Simple logistic regression", "logistic-regression"),
      ("Cox regression", "cox")]),
    ("catalog/12-predict-from-several.qmd", "12 · Predict a value from several variables",
     "Multiple linear and nonlinear regression, multiple logistic regression, Cox regression.",
     [("Multiple linear regression", "multiple-linear-regression"),
      ("Multiple nonlinear regression", "multiple-nonlinear-regression"),
      ("Multiple logistic regression", "multiple-logistic-regression"),
      ("Cox regression", "cox")]),
    ("survival/13-kaplan-meier.qmd", "13 · Kaplan-Meier & the log-rank test",
     "Censoring, KM curves with numbers at risk, survivorship, log-rank, competing risks.", []),
    ("survival/14-cox-regression.qmd", "14 · Cox proportional hazards regression",
     "Hazard ratios, multivariable Cox, checking proportional hazards, stratified Cox.", []),
    ("beyond/15-post-hoc.qmd", "15 · Post-hoc tests & multiple comparisons",
     "Which groups differ after ANOVA, Kruskal-Wallis, chi-square, or Friedman.", []),
    ("beyond/16-mixed-models.qmd", "16 · Mixed models for repeated PROMs",
     "PROMs at several visits, including patients who missed some.", []),
    ("beyond/17-agreement.qmd", "17 · Agreement & reliability",
     "ICC, Bland-Altman, and kappa for radiographic measurements.", []),
    ("report/18-example-report.qmd", "18 · Example study report",
     "A complete mini-study from raw workbook to manuscript-style Results.", []),
]

for path, title, desc, sections in STUBS:
    body = "\n".join(f"## {h} {{#{a}}}\n" for h, a in sections)
    text = f'---\ntitle: "{title} (coming soon)"\ndescription: "{desc}"\n---\n\n{BOX}\n{body}'
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("wrote", p)
EOF
```

Expected: 21 `wrote ...` lines.

- [ ] **Step 6: Render and run the tests**

Run: `quarto render && uv run pytest tests/site -q`
Expected:
- Quarto prints `Output created: _site/index.html`
- pytest reports `9 passed`

- [ ] **Step 7: Commit**

```bash
git add _quarto.yml styles.css index.qmd getting-started foundations catalog survival beyond report tests/site
git commit -m "Add Quarto site skeleton with all 22 pages as stubs and site tests

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Home page decision table

**Files:**
- Modify: `index.qmd` (replace entirely)
- Test: `tests/site/test_home.py`

**Interfaces:**
- Consumes: `CELL_ANCHORS`, `load` and `strip_dot` from `tests/site/sitelib.py`, and the stub anchors from Task 3.
- Produces: the home page every other page links back to.

- [ ] **Step 1: Write the failing test**

`tests/site/test_home.py`:

```python
from sitelib import CELL_ANCHORS, load, strip_dot

BEYOND_LINKS = [
    "survival/13-kaplan-meier.html",
    "survival/14-cox-regression.html",
    "beyond/15-post-hoc.html",
    "beyond/16-mixed-models.html",
    "beyond/17-agreement.html",
    "foundations/03-distributions.html",
]


def main_hrefs():
    return {strip_dot(a["href"]) for a in load("index.html").select("main a[href]")}


def main_text():
    return load("index.html").select_one("main").get_text(" ").replace("’", "'")


def test_every_table_cell_links_to_its_section(site):
    expected = {f"{page}#{a}" for page, anchors in CELL_ANCHORS.items() for a in anchors}
    assert expected - main_hrefs() == set()


def test_beyond_the_table_links(site):
    assert set(BEYOND_LINKS) - main_hrefs() == set()


def test_table_is_credited_and_spelled_right(site):
    text = main_text()
    assert "Motulsky" in text and "Intuitive Biostatistics" in text
    assert "Cochran's Q" in text
    assert "Cochrane" not in text
    assert "orthoteers" not in str(load("index.html"))


def test_synthetic_data_warning(site):
    assert "SYNTHETIC DATA" in main_text()


def test_decision_table_scrolls_on_small_screens(site):
    assert load("index.html").select_one("div.decision-table.table-responsive table") is not None
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/site/test_home.py -q`
Expected: FAIL (`5 failed`). The placeholder has no table, credits or warning.

- [ ] **Step 3: Write `index.qmd`**

```markdown
---
title: "TJS Statistics Tutorials"
subtitle: "Pick your goal and your type of data. Click the test."
---

::: {.callout-important}
## SYNTHETIC DATA
Every dataset on this site is invented. None of it describes real patients, and real patient data never goes in this repository. Before you touch real data, read [Working with real TJS data](getting-started/real-data.qmd).
:::

New here? Start with [Install & set up](getting-started/setup.qmd), then [How to use this site](getting-started/using-this-site.qmd).

## Which test do I need?

1. Find your **goal** in the left column (for example, *compare two unpaired groups*).
2. Find your **type of data** along the top. Not sure whether your measurements are Gaussian (normally distributed)? Read [Distributions & choosing a test](foundations/03-distributions.qmd) first.
3. Click the test.

::: {.decision-table .table-responsive}

| Goal | Measurement (Gaussian population) | Rank, score, or measurement (non-Gaussian population) | Binomial (two possible outcomes) | Survival time |
|------|------|------|------|------|
| **Describe one group** | [Mean, SD](catalog/04-describe-one-group.qmd#mean-sd) | [Median, interquartile range](catalog/04-describe-one-group.qmd#median-iqr) | [Proportion](catalog/04-describe-one-group.qmd#proportion) | [Kaplan-Meier survival curve](catalog/04-describe-one-group.qmd#kaplan-meier) |
| **Compare one group to a hypothetical value** | [One-sample t test](catalog/05-one-group-vs-hypothetical.qmd#one-sample-t) | [Wilcoxon signed-rank test](catalog/05-one-group-vs-hypothetical.qmd#wilcoxon-signed-rank) | [Chi-square](catalog/05-one-group-vs-hypothetical.qmd#chi-square-gof) or [binomial test](catalog/05-one-group-vs-hypothetical.qmd#binomial-test) | — |
| **Compare two unpaired groups** | [Unpaired t test](catalog/06-two-unpaired-groups.qmd#unpaired-t) | [Mann-Whitney test](catalog/06-two-unpaired-groups.qmd#mann-whitney) | [Fisher's exact test (chi-square for large samples)](catalog/06-two-unpaired-groups.qmd#fisher-chi-square) | [Log-rank (Mantel-Haenszel) test](catalog/06-two-unpaired-groups.qmd#log-rank) |
| **Compare two paired groups** | [Paired t test](catalog/07-two-paired-groups.qmd#paired-t) | [Wilcoxon signed-rank test](catalog/07-two-paired-groups.qmd#wilcoxon-signed-rank) | [McNemar's test](catalog/07-two-paired-groups.qmd#mcnemar) | [Conditional proportional hazards regression](catalog/07-two-paired-groups.qmd#stratified-cox) |
| **Compare three or more unmatched groups** | [One-way ANOVA](catalog/08-three-plus-unmatched.qmd#one-way-anova) | [Kruskal-Wallis test](catalog/08-three-plus-unmatched.qmd#kruskal-wallis) | [Chi-square test](catalog/08-three-plus-unmatched.qmd#chi-square) | [Cox proportional hazards regression](catalog/08-three-plus-unmatched.qmd#cox) |
| **Compare three or more matched groups** | [Repeated-measures ANOVA](catalog/09-three-plus-matched.qmd#repeated-measures-anova) | [Friedman test](catalog/09-three-plus-matched.qmd#friedman) | [Cochran's Q](catalog/09-three-plus-matched.qmd#cochran-q) | [Conditional proportional hazards regression](catalog/09-three-plus-matched.qmd#stratified-cox) |
| **Quantify association between two variables** | [Pearson correlation](catalog/10-association.qmd#pearson) | [Spearman correlation](catalog/10-association.qmd#spearman) | [Contingency coefficients](catalog/10-association.qmd#contingency-coefficients) | — |
| **Predict a value from another measured variable** | [Simple linear regression](catalog/11-predict-from-one.qmd#linear-regression) or [nonlinear regression](catalog/11-predict-from-one.qmd#nonlinear-regression) | [Nonparametric regression](catalog/11-predict-from-one.qmd#nonparametric-regression) | [Simple logistic regression](catalog/11-predict-from-one.qmd#logistic-regression) | [Cox proportional hazards regression](catalog/11-predict-from-one.qmd#cox) |
| **Predict a value from several measured or binomial variables** | [Multiple linear regression](catalog/12-predict-from-several.qmd#multiple-linear-regression) or [multiple nonlinear regression](catalog/12-predict-from-several.qmd#multiple-nonlinear-regression) | — | [Multiple logistic regression](catalog/12-predict-from-several.qmd#multiple-logistic-regression) | [Cox proportional hazards regression](catalog/12-predict-from-several.qmd#cox) |

:::

*Adapted from Harvey Motulsky,* Intuitive Biostatistics *(Oxford University Press), and the GraphPad Statistics Guide.*

## Beyond the table

| If you need to… | Read |
|------|------|
| Estimate survivorship, draw Kaplan-Meier curves with numbers at risk, or handle death as a competing risk | [13 · Kaplan-Meier & the log-rank test](survival/13-kaplan-meier.qmd) |
| Adjust a time-to-event comparison for several factors, or check proportional hazards | [14 · Cox proportional hazards regression](survival/14-cox-regression.qmd) |
| Find out *which* groups differ after ANOVA, Kruskal-Wallis, or chi-square | [15 · Post-hoc tests & multiple comparisons](beyond/15-post-hoc.qmd) |
| Analyze PROMs collected at several visits, including patients who missed some | [16 · Mixed models for repeated PROMs](beyond/16-mixed-models.qmd) |
| Measure how well two raters, or one rater on two days, agree on a measurement | [17 · Agreement & reliability](beyond/17-agreement.qmd) |

## New to statistics?

Work through the site in order: **Getting started**, then **Part 1 · Foundations**, then the catalog pages your project needs. Each page ends with short exercises and hidden solutions.
```

- [ ] **Step 4: Render and run the tests**

Run: `quarto render index.qmd && uv run pytest tests/site -q`
Expected: `14 passed`.

- [ ] **Step 5: Commit**

```bash
git add index.qmd tests/site/test_home.py
git commit -m "Add clickable decision table home page

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Page 0.2, "How to use this site" (first page with live R ⟷ Python code)

**Files:**
- Modify: `getting-started/using-this-site.qmd` (replace the stub entirely)
- Create: `_freeze/` (generated by render; commit all of it, since Quarto may also write shared `site_libs` there)
- Test: `tests/site/test_conventions.py`

**Interfaces:**
- Consumes: `R/check_agree.R` (Task 2), the reticulate wiring (Task 1), and `load`, `PAGES`, `SITE`, `ROOT` (Task 3).
- Produces: the canonical example of the page conventions that later phases copy. It covers the hidden `source()` chunk, the language tabset, the hidden `check_agree` chunk, the callout legend, and a collapsed solution.

- [ ] **Step 1: Write the failing test**

`tests/site/test_conventions.py`:

```python
"""Site-wide page conventions (spec section 6)."""

from sitelib import PAGES, ROOT, SITE, load


def test_language_tabs_are_grouped_and_ordered(site):
    for page in PAGES:
        for tabset in load(page).select("div.panel-tabset"):
            assert tabset.get("data-group") == "language", page
            labels = [a.get_text(strip=True)
                      for a in tabset.select(":scope > ul.nav-tabs a.nav-link")]
            assert labels == ["R", "Python"], f"{page}: tabs are {labels}"


def test_solutions_start_collapsed(site):
    for page in PAGES:
        for callout in load(page).select("div.callout"):
            header = callout.select_one(".callout-header")
            if header and header.get_text(strip=True).endswith("Solution"):
                body = callout.select_one(".callout-collapse")
                assert body is not None, f"{page}: a Solution box is not collapsible"
                assert "show" not in body.get("class", []), f"{page}: a Solution box starts open"


def test_hidden_checks_never_show(site):
    for page in PAGES:
        assert "check_agree" not in (SITE / page).read_text(encoding="utf-8"), page


def test_using_this_site_runs_both_languages(site):
    soup = load("getting-started/using-this-site.html")
    first = soup.select_one("div.panel-tabset")
    assert first is not None
    assert len(first.select(".cell-output")) >= 2, "R and Python should each print a result"
    assert (ROOT / "_freeze" / "getting-started" / "using-this-site").is_dir()


def test_callout_legend_shows_all_four_kinds(site):
    text = load("getting-started/using-this-site.html").get_text(" ")
    for title in ["In plain language", "Watch out", "R vs Python", "Under the hood"]:
        assert title in text, title
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/site/test_conventions.py -q`
Expected: `test_using_this_site_runs_both_languages` and `test_callout_legend_shows_all_four_kinds` FAIL. The other three pass, because no page has tabsets yet.

- [ ] **Step 3: Write `getting-started/using-this-site.qmd`**

````markdown
---
title: "How to use this site"
description: "Choosing R or Python, running the examples yourself, the callout boxes, how results are reported, and how exercises work."
engine: knitr
---

```{r}
#| include: false
source("R/check_agree.R")
```

## Pick your language once

Every example on this site is written twice: once in **R** and once in **Python**. Both give the same answer. Click a tab to choose. The site remembers your choice on every page, so you only pick once.

Here is a tiny example: five pretend patients' ages, their mean, and their standard deviation (SD).

::: {.panel-tabset group="language"}
## R

```{r}
ages <- c(64, 71, 58, 69, 75)   # five pretend patients' ages

mean_age <- mean(ages)           # the average
sd_age <- sd(ages)               # the standard deviation

mean_age
sd_age
```

## Python

```{python}
import pandas as pd

ages = pd.Series([64, 71, 58, 69, 75])   # five pretend patients' ages

mean_age = ages.mean()                    # the average
sd_age = ages.std()                       # the standard deviation

print(mean_age)
print(sd_age)
```
:::

```{r}
#| include: false
check_agree(
  list(mean = mean_age, sd = sd_age),
  list(mean = reticulate::py$mean_age, sd = reticulate::py$sd_age)
)
```

Both say the mean age is 67.4 years with an SD of 6.6 years.

::: {.callout-tip}
## 🔀 R vs Python: the standard deviation trap
Python has two common ways to compute an SD, and they disagree. `pandas` (`ages.std()`) divides by *n − 1*, like R's `sd()`. `numpy` (`np.std(ages)`) divides by *n* unless you write `np.std(ages, ddof=1)`. Medical papers report the *n − 1* version. Whenever the two languages' defaults differ, this site sets them explicitly and explains why in a box like this one.
:::

Behind the scenes, every page checks that the R and Python answers match. If they ever disagree, the site refuses to build, so you can trust that both tabs say the same thing.

## Running the code yourself

1. Open the repository folder in Positron (see [Install & set up](setup.qmd)).
2. Save practice files in the `scratch/` folder, for example `scratch/practice.R` or `scratch/practice.py`. Git ignores everything in `scratch/`, so practice files can never be committed by accident.
3. Copy code with the copy button that appears in the top-right corner of every code block.
4. Run a line with **Cmd+Enter** (Mac) or **Ctrl+Enter** (Windows). Positron sends it to the console.

Data paths such as `data/cohort.csv` are relative to the repository's top folder. Positron starts there when you open the folder, so the paths just work.

## The boxes you'll see

::: {.callout-note}
## 💡 In plain language
The idea without the jargon. If a page loses you, read these boxes first.
:::

::: {.callout-warning}
## ⚠️ Watch out
Mistakes we see often, and how to avoid them.
:::

::: {.callout-tip}
## 🔀 R vs Python
Where the two languages' defaults differ, and what this site does about it.
:::

::: {.callout-note collapse="true"}
## 🔍 Under the hood
The math, for the curious. These start closed: click to open. You never need them to use a test correctly.
:::

## How results are reported

Every "How to report it" paragraph on this site follows the same rules, which match what JOA and JBJS reviewers expect.

| What | Report it as | Example |
|------|------|------|
| Continuous, roughly symmetric | mean (SD) | age 67.4 (6.6) years |
| Continuous, skewed | median (IQR) | length of stay 1 (0–2) days |
| Categories | n (%) | 312 (52%) female |
| p-values | three decimals; never "p = 0.000" | p = 0.017; p < 0.001 |
| Effect estimates | with a 95% confidence interval | difference 1.6 kg/m² (95% CI 0.7 to 2.5) |

The examples in the table are illustrations, not results from our data. [Demographics (Table 1)](../foundations/02-demographics.qmd) shows the full Table 1 layout.

## Exercises

Each page ends with two to four short exercises on the practice data. They get harder in three steps: run the same analysis on a different variable, pick the right test for a short scenario, then write the Results sentence. Solutions are hidden in both languages. Try first, then check.

**Try it:** using the same five ages, find the **median**.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```r
ages <- c(64, 71, 58, 69, 75)
median(ages)   # 69
```

## Python

```python
import pandas as pd

ages = pd.Series([64, 71, 58, 69, 75])
ages.median()   # 69.0
```
:::

:::

## Getting help

- Something on this site is wrong or confusing? [Open an issue](https://github.com/Total-Joint-Specialists/example-stats-analysis/issues) on GitHub.
- A question about your own project? Ask your TJS project lead.
````

- [ ] **Step 4: Render and run all site tests**

Run: `quarto render getting-started/using-this-site.qmd && uv run pytest tests/site -q`
Expected:
- the render succeeds (if R and Python disagreed, it would stop with `check_agree(): R and Python disagree ...`)
- pytest reports `19 passed`

- [ ] **Step 5: Prove the guard bites**

Temporarily change the Python line `sd_age = ages.std()` to `sd_age = ages.std(ddof=0)`.

Run: `quarto render getting-started/using-this-site.qmd`
Expected: FAIL with `check_agree(): R and Python disagree on 'sd'`.

Revert the line, then run `quarto render getting-started/using-this-site.qmd` again.
Expected: success.

- [ ] **Step 6: Commit (including the freeze)**

```bash
git add getting-started/using-this-site.qmd _freeze tests/site/test_conventions.py
git commit -m "Write 'How to use this site' with live R/Python tabs and agreement check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Page 0.1, "Install & set up", plus the setup check scripts

**Files:**
- Modify: `getting-started/setup.qmd` (replace the stub entirely)
- Create: `getting-started/check_setup.R`, `getting-started/check_setup.py`
- Test: `tests/testthat/test-check_setup.R`, `tests/python/test_check_setup.py`, `tests/site/test_getting_started.py`

**Interfaces:**
- Consumes: the environments (Task 1) and `load` (Task 3).
- Produces:
  - `Rscript getting-started/check_setup.R`, which prints `All good - you are ready.` and exits 0, or prints `PROBLEM - <fix>` lines and exits 1. When run with `source()` in an interactive console, it doesn't quit R.
  - `uv run python getting-started/check_setup.py`, with the same contract.
  - Phase 1 extends both scripts with a data check.

- [ ] **Step 1: Write the failing tests**

`tests/testthat/test-check_setup.R`:

```r
root <- normalizePath(testthat::test_path("..", ".."))

test_that("check_setup.R passes in a working project", {
  out <- withr::with_dir(root, system2(file.path(R.home("bin"), "Rscript"),
                                      "getting-started/check_setup.R",
                                      stdout = TRUE, stderr = TRUE))
  expect_null(attr(out, "status"))
  expect_true(any(grepl("All good - you are ready.", out, fixed = TRUE)))
})
```

`tests/python/test_check_setup.py`:

```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "getting-started" / "check_setup.py"


def run(python: str) -> subprocess.CompletedProcess:
    return subprocess.run([python, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True)


def test_passes_inside_the_project_environment():
    result = run(sys.executable)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All good - you are ready." in result.stdout


def test_flags_a_python_outside_the_project_environment():
    base_python = Path(sys.base_prefix) / "bin" / "python3"
    result = run(str(base_python))
    assert result.returncode == 1
    assert "PROBLEM" in result.stdout
```

`tests/site/test_getting_started.py`:

```python
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
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_setup")'
uv run pytest tests/python/test_check_setup.py tests/site/test_getting_started.py -q
```

Expected:
- R: FAIL (`Fatal error: cannot open file 'getting-started/check_setup.R'`)
- Python: `test_check_setup.py` fails with exit code 2 (file not found); `test_getting_started.py` fails (the stub has none of the commands)

- [ ] **Step 3: Write the check scripts**

`getting-started/check_setup.R`:

```r
# Checks that R is ready for the tutorials.
# Run from the repository folder:  Rscript getting-started/check_setup.R
# or, in Positron's R console:     source("getting-started/check_setup.R")

ok <- TRUE
report <- function(label, pass, fix) {
  cat(sprintf("%-40s %s\n", label, if (pass) "OK" else paste("PROBLEM -", fix)))
  if (!pass) ok <<- FALSE
}

report(sprintf("R version %s", getRversion()), getRversion() >= "4.4",
       "install R 4.4 or newer from https://cloud.r-project.org")
report("project packages switched on (renv)", nzchar(Sys.getenv("RENV_PROJECT")),
       "start R inside the example-stats-analysis folder")
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat")) {
  report(paste("R package", pkg), requireNamespace(pkg, quietly = TRUE),
         "run renv::restore() in the R console")
}

cat(if (ok) "\nAll good - you are ready.\n" else "\nFix the problems above, then run this again.\n")
if (!interactive()) quit(status = if (ok) 0 else 1)
```

`getting-started/check_setup.py`:

```python
"""Checks that Python is ready for the tutorials.

Run from the repository folder:  uv run python getting-started/check_setup.py
"""

import importlib.util
import sys

ok = True


def report(label: str, passed: bool, fix: str) -> None:
    global ok
    print(f"{label:<40} {'OK' if passed else 'PROBLEM - ' + fix}")
    ok = ok and passed


version = ".".join(map(str, sys.version_info[:3]))
report(f"Python version {version}", sys.version_info >= (3, 12),
       "run `uv python install 3.13`, then `uv sync`")
report("using the project's .venv", ".venv" in sys.prefix,
       "run this with `uv run python ...` from the repository folder")
for name in ["pandas", "numpy", "matplotlib"]:
    report(f"Python package {name}", importlib.util.find_spec(name) is not None, "run `uv sync`")

print("\nAll good - you are ready." if ok else "\nFix the problems above, then run this again.")
sys.exit(0 if ok else 1)
```

- [ ] **Step 4: Write `getting-started/setup.qmd`**

````markdown
---
title: "Install & set up"
description: "Everything you need on your computer to run the examples: R, Python, Git, Positron, and this repository."
---

This takes 30–45 minutes the first time, and you only do it once per computer. Follow the steps in order. Each step ends with a quick check.

::: {.callout-note}
## 💡 In plain language
**R** and **Python** are the programming languages that do the statistics. **Positron** is the app you type code into. **Git** downloads this repository (a folder of code and data) and keeps track of changes. **uv** installs Python and its add-on packages.
:::

::: {.callout-tip}
## Just want to read?
You don't need to install anything to read this site. Install only when you're ready to run code yourself.
:::

## 1. Install R

1. Go to <https://cloud.r-project.org>.
2. Click **Download R for macOS** or **Download R for Windows**.
   - **Mac:** pick the installer for your chip. Apple menu → **About This Mac**: "Apple M…" means *Apple silicon (arm64)*, and "Intel" means *Intel (x86_64)*.
   - **Windows:** click **base**, then the download link at the top of the page.
3. Open the downloaded file and accept the defaults.

**Check:** Positron will find R in step 4. On a Mac you can also open Terminal and type `R --version`.

## 2. Install uv and Python

**Mac:** open Terminal and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:** open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close the window, open a new one, and install Python:

```bash
uv python install 3.13
```

**Check:** `uv --version` prints a version number.

## 3. Install Git

- **Mac:** in Terminal, run `xcode-select --install` and click **Install**. This installs Apple's command-line tools, which include Git.
- **Windows:** download Git from <https://git-scm.com/downloads> and accept the defaults.

**Check:** `git --version` prints a version number.

## 4. Install Positron

Download Positron from <https://positron.posit.co> and install it like any other app. Positron runs R and Python side by side. Prefer RStudio or VS Code? See [Other editors](#other-editors).

## 5. Get this repository

In Terminal (Mac) or PowerShell (Windows), go to the folder where you keep projects and download ("clone") the repository:

```bash
cd ~/Documents
git clone https://github.com/Total-Joint-Specialists/example-stats-analysis.git
```

Then, in Positron: **File → Open Folder…** and choose `example-stats-analysis`.

## 6. Install the R packages

In Positron, start an R console: use the language picker at the top right of the **Console** pane and choose **R**. Because R starts inside the repository folder, it switches on this project's package list. Then run:

```r
renv::restore()
```

Answer **Y** if asked. This installs every R package the tutorials use, at the exact versions we tested. It takes a few minutes.

## 7. Install the Python packages

Open Positron's terminal (**Terminal → New Terminal**). It opens in the repository folder. Run:

```bash
uv sync
```

This creates a private Python environment in the `.venv` folder with every package the tutorials use. Then tell Positron to use it: in the **Console** pane's language picker, choose the Python whose path includes `.venv`.

## 8. Check that everything works

In Positron's terminal, run both checks:

```bash
Rscript getting-started/check_setup.R
uv run python getting-started/check_setup.py
```

Each check ends with `All good - you are ready.` If a line says `PROBLEM`, it tells you what to do. Fix it and run the check again.

On Windows, if `Rscript` is "not recognized", run the R check from Positron's R console instead:

```r
source("getting-started/check_setup.R")
```

## Troubleshooting

| You see | Do this |
|------|------|
| `You have not agreed to the Xcode license` (Mac, during `renv::restore()`) | In Terminal, run `sudo xcodebuild -license accept` and type your Mac password. Then run `renv::restore()` again. |
| `there is no package called 'renv'` | In the R console, run `install.packages("renv")`. Restart R (**Session → Restart R**) and run `renv::restore()` again. |
| `uv: command not found`, or "not recognized" | Close the terminal window, open a new one, and try again. |
| `git: command not found` | Repeat step 3. |
| Python can't find `pandas` in Positron | Choose the `.venv` Python in the Console language picker (step 7), then restart the console. |
| Anything else | Copy the whole error message and send it to your TJS project lead. |

## Other editors {#other-editors}

- **RStudio** (<https://posit.co/download/rstudio-desktop/>) is great for R. It can run Python too, but Positron is simpler when you use both.
- **VS Code** (<https://code.visualstudio.com>) works too: install the R and Python extensions.

Everything else on this page stays the same.
````

- [ ] **Step 5: Run the tests to verify they pass**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_setup", stop_on_failure = TRUE)'
quarto render getting-started/setup.qmd
uv run pytest tests/python tests/site -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 2 ]`
- pytest: all pass. That is `24 passed` in `tests/python` (22 gitignore + 2 check_setup) plus `21 passed` in `tests/site`, so `45 passed` in total.

- [ ] **Step 6: Commit**

```bash
git add getting-started/setup.qmd getting-started/check_setup.R getting-started/check_setup.py tests/testthat/test-check_setup.R tests/python/test_check_setup.py tests/site/test_getting_started.py
git commit -m "Write 'Install & set up' page with R and Python setup checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Page 0.3, "Working with real TJS data"

**Files:**
- Modify: `getting-started/real-data.qmd` (replace the stub entirely)
- Modify: `tests/site/test_getting_started.py` (append tests)

**Interfaces:**
- Consumes: `load` (Task 3).
- Produces: the PHI-safety page that the home page's warning links to.

- [ ] **Step 1: Write the failing tests** (append to `tests/site/test_getting_started.py`)

```python
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
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_getting_started.py -q`
Expected: the three new tests FAIL. The page is still a stub.

- [ ] **Step 3: Write `getting-started/real-data.qmd`**

```markdown
---
title: "Working with real TJS data"
description: "Keeping patient data safe: what counts as PHI, where TJS data lives, and the checks to run before every commit."
---

Everything on this site uses invented data. Your real project won't. This page covers the rules that keep patients and TJS safe. Read it before you open any real dataset.

::: {.callout-warning}
## ⚠️ The one rule
**Patient data never goes into a git repository.** That includes private repositories, commits, GitHub issues, screenshots and chat messages. This site's repository is **public**: anything committed here can be read by anyone on the internet, forever.
:::

## What counts as protected health information (PHI)

US law (HIPAA) lists 18 kinds of identifiers. A dataset is only "de-identified" under the Safe Harbor method when **all 18** are removed:

::: {.phi-identifiers}
1. Names
2. Geographic units smaller than a state: street address, city, county, and ZIP code. The first three digits of a ZIP code may stay if that area holds more than 20,000 people.
3. All parts of dates except the year, when they relate to the patient: birth, admission, discharge, **surgery**, and death dates. Also any age older than 89 (group those patients as "90 or older").
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers (MRNs)
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate or license numbers
12. Vehicle identifiers and serial numbers, including license plates
13. Device identifiers and serial numbers, including **implant serial and lot numbers**
14. Web addresses (URLs)
15. IP addresses
16. Biometric identifiers, such as fingerprints and voice prints
17. Full-face photographs and comparable images
18. Any other unique identifying number, characteristic, or code
:::

## TJS-specific traps

- **Surgery dates are dates.** Use "days from surgery" or the surgery year instead.
- **Ages over 89.** Report them as "90 or older".
- **MRNs hide in file names.** Watch for names like `12345678_xray.png` or `chart_pull_MRN.xlsx`.
- **Implant stickers.** Lot and serial numbers are device identifiers.
- **Radiographs.** DICOM files carry the patient's name, MRN and dates in their headers, and some images have them burned into the pixels.
- **Free-text "notes" columns.** They collect names, phone numbers and dates.
- **Screenshots of the chart.** They're PHI too.

## Where TJS data lives

- Study data lives in TJS-controlled Google Sheets and Google Drive folders that your project lead shares with your TJS account.
- Project repositories read data at run time, either straight from the Google Sheet or from a local `data/` folder that is listed in `.gitignore` *before the first commit*.
- The crosswalk that links MRNs to study IDs lives only with the data, never in a repository.
- What leaves the secure environment is aggregate: tables, figures and model results. Your IRB protocol may require hiding small counts (for example, cells with fewer than 11 patients).

## How TJS projects handle data in code

These rules come from TJS project repositories. [Tidy data](../foundations/01-tidy-data.qmd) practices each one.

1. **Read everything as text at first.** Dates arrive in several formats, numbers contain stray text, and lists sit inside single cells. Convert types as a deliberate, recorded step, never silently while reading.
2. **Match columns by name, not position.** Two tabs of the same sheet can have different columns.
3. **Check what you changed.** After every cleaning step, compare row counts and summaries before and after.

## AI tools

**Never paste real patient data into an AI chatbot or any website.** That includes ChatGPT, Claude, Copilot and online "data cleaners". The only exception is a tool your project lead confirms is approved for PHI. The synthetic data on this site is fine to paste anywhere.

## Before every commit

Run these two commands and read the output:

```bash
git status
git diff --staged
```

Check that no data file, export or screenshot is listed. If you see one, unstage it with `git restore --staged <file>`.

## If something goes wrong

If PHI reaches a commit, a push or an issue:

1. **Stop.** Don't try to fix it with another commit. Git keeps the history.
2. **Tell your project lead right away.** The data has to be purged from history, and the incident may need to be reported under TJS policy.

Reporting quickly is always the right call, and nobody will be upset that you did.
```

- [ ] **Step 4: Render and run all site tests**

Run: `quarto render getting-started/real-data.qmd && uv run pytest tests/site -q`
Expected: `24 passed`.

- [ ] **Step 5: Commit**

```bash
git add getting-started/real-data.qmd tests/site/test_getting_started.py
git commit -m "Write 'Working with real TJS data' PHI-safety page

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: README, CLAUDE.md, licenses

**Files:**
- Create: `README.md`, `CLAUDE.md`, `LICENSE`, `LICENSE-CONTENT`
- Test: `tests/python/test_repo_docs.py`

**Interfaces:**
- Produces: the repo front door and the maintainer rules that future phases and agents follow.

- [ ] **Step 1: Write the failing test**

`tests/python/test_repo_docs.py`:

```python
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/python/test_repo_docs.py -q`
Expected: FAIL (`FileNotFoundError: ... README.md`).

- [ ] **Step 3: Write the four files**

`README.md`:

````markdown
# TJS Statistics Tutorials

Tutorials and worked examples that teach Total Joint Specialists (TJS) research assistants how to prepare data and run the statistical analyses used in TJS arthroplasty research, in R, Python, or both.

**Read the site:** https://total-joint-specialists.github.io/example-stats-analysis/

> **All data in this repository are synthetic.** No real patient data is ever committed here, and this repository is public.

## What's inside

| Part | Topics |
|------|------|
| Getting started | Installing R, Python, Git and Positron; how to use the site; working safely with real TJS data |
| 1 · Foundations | Tidy data, Table 1, distributions & choosing a test |
| 2 · Test catalog | Every test in the Motulsky decision table, R and Python side by side |
| 3 · Survival analysis | Kaplan-Meier, competing risks, Cox regression |
| 4 · Beyond the table | Post-hoc tests, mixed models, agreement & reliability |
| 5 · Putting it together | A complete example study report |

## Run the examples

```bash
git clone https://github.com/Total-Joint-Specialists/example-stats-analysis.git
cd example-stats-analysis
Rscript -e 'renv::restore()'
uv sync
```

Step-by-step instructions for beginners: [Install & set up](https://total-joint-specialists.github.io/example-stats-analysis/getting-started/setup.html).

## Repository layout

| Path | What it holds |
|------|------|
| `index.qmd`, `getting-started/`, `foundations/`, `catalog/`, `survival/`, `beyond/`, `report/` | The site's pages |
| `data/` | Synthetic datasets and codebooks |
| `templates/` | A data-collection template to copy for real projects |
| `R/` | Site helpers (`check_agree()`) |
| `tests/` | R (testthat), Python (pytest), and built-site tests |
| `_freeze/` | Saved results of every page's code (committed, so the site builds without R or Python) |
| `scratch/` | Your practice space; git ignores everything in it |
| `docs/superpowers/` | Design spec and implementation plans |

## For maintainers

You'll need R, uv, Quarto 1.9.37, [just](https://github.com/casey/just), and [lychee](https://github.com/lycheeverse/lychee).

```bash
just setup     # renv::restore() + uv sync
just test      # R and Python unit tests
just preview   # live preview while writing
just check     # render, then site tests + link check
```

Render locally and commit `_freeze/`. CI builds the site from `_freeze/` without running R or Python, runs the site checks, and publishes `main` to GitHub Pages.

## License

Text, figures and synthetic data: [CC BY 4.0](LICENSE-CONTENT). Code: [MIT](LICENSE).
````

`CLAUDE.md`:

```markdown
# CLAUDE.md: TJS Statistics Tutorials

Public Quarto website and repository. It teaches TJS research assistants (beginners in both statistics and code) tidy data, Table 1, distribution checks, every test in the Motulsky decision table, survival analysis, and selected extras, in R and Python side by side.

- Design spec: `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`
- Plans: `docs/superpowers/plans/`

## Golden rules

1. **Synthetic data only. This repo is public.** Never add real patient data, real names, MRNs, real surgery dates, or screenshots of clinical systems. `.gitignore` blocks data-file extensions outside `data/` and `templates/`. Never `git add -f`.
2. **Every page with executable code declares `engine: knitr` in its own front matter.** Quarto ignores `engine` in `_quarto.yml` and `_metadata.yml`. Without it, a Python-only page silently runs in Jupyter on the system Python. `tests/site/test_sources.py` enforces this.
3. **Language tabsets are `::: {.panel-tabset group="language"}`** with `## R` first and `## Python` second. Each language block stands alone: it loads its own packages and data.
4. **Every R/Python pair ends with a hidden agreement check.** At the top of the page, a hidden chunk runs `source("R/check_agree.R")`. After each pair, a hidden `#| include: false` R chunk calls `check_agree(list(x = <R value>), list(x = reticulate::py$<python variable>))`. The Python values must be plain numbers. Where defaults differ (Welch vs Student, continuity corrections, exact vs asymptotic), set them explicitly in both languages and explain the difference in a 🔀 callout.
5. **Render locally, commit `_freeze/`.** CI never runs R or Python. A page changed without re-rendering fails CI by design.
6. **Exercise solutions are collapsed:** `::: {.callout-tip collapse="true"}` titled `Solution`, with a language tabset inside.
7. **Stub pages** carry "(coming soon)" in the title and a `.coming-soon` callout. Remove both when the page is written.
8. **Reporting conventions** (spec section 4, page 0.2): mean (SD) or median (IQR); n (%); p to 3 decimals with a floor of "p < 0.001"; a 95% CI with every estimate.

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

`LICENSE`:

```
MIT License

Copyright (c) 2026 Total Joint Specialists

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`LICENSE-CONTENT`:

```
Copyright (c) 2026 Total Joint Specialists

The text, figures, and synthetic datasets in this repository are licensed
under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

You may share and adapt this material for any purpose, including
commercially, as long as you give appropriate credit, link to the license,
and indicate if changes were made.

Summary:      https://creativecommons.org/licenses/by/4.0/
Legal code:   https://creativecommons.org/licenses/by/4.0/legalcode

Code (R, Python, and configuration files) is licensed separately under the
MIT License; see LICENSE.
```

- [ ] **Step 4: Run it to verify it passes**

Run: `uv run pytest tests/python/test_repo_docs.py -q`
Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add README.md CLAUDE.md LICENSE LICENSE-CONTENT tests/python/test_repo_docs.py
git commit -m "Add README, CLAUDE.md, and MIT / CC BY 4.0 licenses

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Maintainer commands and CI

**Files:**
- Create: `Justfile`, `.github/workflows/publish.yml`, `.github/workflows/checks.yml`
- Test: the `just check` and `just test` runs, plus YAML parsing of the workflows

**Interfaces:**
- Consumes: every test suite above.
- Produces:
  - `just setup|test|render|preview|check`. Phase 1 adds `just data`.
  - The CI jobs "Publish site" (push to `main`) and "Site checks" (PRs and pushes).

- [ ] **Step 1: Install lychee locally (maintainer machine, Apple silicon)**

```bash
tmp=$(mktemp -d)
gh release download -R lycheeverse/lychee -p 'lychee-aarch64-apple-darwin.tar.gz' -p 'lychee-aarch64-apple-darwin.tar.gz.sha256' -D "$tmp"
(cd "$tmp" && shasum -a 256 -c lychee-aarch64-apple-darwin.tar.gz.sha256)
tar xzf "$tmp/lychee-aarch64-apple-darwin.tar.gz" -C "$tmp"
mkdir -p ~/.local/bin && mv "$tmp/lychee-aarch64-apple-darwin/lychee" ~/.local/bin/
lychee --version
```

Expected:
- `lychee-aarch64-apple-darwin.tar.gz: OK`
- `lychee 0.24.2` (or newer)

- [ ] **Step 2: Write `Justfile`**

```just
# Maintainer commands. Research assistants never need these.

# Install R packages (renv) and Python packages (uv)
setup:
    Rscript -e 'renv::restore(prompt = FALSE)'
    uv sync

# R and Python unit tests
test:
    Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
    uv run pytest tests/python -q

# Render the whole site (runs changed pages, updates _freeze/)
render:
    quarto render

# Live preview while writing
preview:
    quarto preview

# Render, then check the built site's structure, internal links, and anchors
check: render
    uv run pytest tests/site -q
    lychee --offline --include-fragments --no-progress _site
```

- [ ] **Step 3: Write the workflows**

`.github/workflows/publish.yml`:

```yaml
name: Publish site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: quarto-dev/quarto-actions/setup@v2
        with:
          version: 1.9.37

      # Builds from _freeze/ (no R or Python). If a page changed without its
      # freeze being refreshed, this step fails because R is not installed.
      - uses: quarto-dev/quarto-actions/publish@v2
        with:
          target: gh-pages
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`.github/workflows/checks.yml`:

```yaml
name: Site checks

on:
  pull_request:
  push:
    branches: [main]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: quarto-dev/quarto-actions/setup@v2
        with:
          version: 1.9.37

      - name: Build the site from frozen results (no R or Python)
        run: quarto render

      - uses: astral-sh/setup-uv@v10

      - name: Site tests
        run: uv run --only-group dev pytest tests/site -q

      - name: Repo tests (gitignore, docs)
        run: uv run pytest tests/python/test_gitignore.py tests/python/test_repo_docs.py -q

      - name: Internal links and #anchors
        uses: lycheeverse/lychee-action@v2
        with:
          args: --offline --include-fragments --no-progress _site
```

- [ ] **Step 4: Validate the workflow YAML**

Run: `uv run --with pyyaml python -c "import sys, yaml; [yaml.safe_load(open(f)) for f in sys.argv[1:]]; print('ok')" .github/workflows/*.yml`
Expected: `ok`

- [ ] **Step 5: Run everything locally**

Run: `just test && just check`
Expected:
- `just test`: testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 23 ]` (8 environment + 13 check_agree + 2 check_setup), then pytest `27 passed`
- `just check`: pytest `24 passed`, then lychee ending `🚫 0 Errors`

- [ ] **Step 6: Prove the link check bites**

In `index.qmd`, temporarily change `#unpaired-t` to `#unpaired-tt`. Then run:

```bash
quarto render index.qmd
uv run pytest tests/site/test_home.py -q
lychee --offline --include-fragments --no-progress _site
```

Expected:
- pytest: `test_every_table_cell_links_to_its_section` FAILS
- lychee: reports `Cannot find fragment` for `catalog/06-two-unpaired-groups.html#unpaired-tt` and exits non-zero

Revert the change and run `just check` again. Expected: passes.

- [ ] **Step 7: Commit**

```bash
git add Justfile .github/workflows/publish.yml .github/workflows/checks.yml
git commit -m "Add maintainer Justfile and CI: site checks and Pages publish

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Create the public GitHub repo and publish (after merging to `main`)

**Precondition:** branch `phase-0-scaffold` has been reviewed and merged to `main` (superpowers:finishing-a-development-branch), and `just test && just check` pass on `main`.

**Files:**
- Create: `_publish.yml` (written by `quarto publish`)

**Interfaces:**
- Produces: a public repo with `main` and `gh-pages`, a live site URL, and green CI.

- [ ] **Step 1: STOP and get explicit owner confirmation**

These actions are public and outward-facing. Ask the owner, word for word:

> "Ready to create the **public** repo `Total-Joint-Specialists/example-stats-analysis`, push `main`, and turn on GitHub Pages at https://total-joint-specialists.github.io/example-stats-analysis/? It will be the org's first public repo. Everything in it is synthetic. OK to proceed?"

Proceed only on an explicit yes.

- [ ] **Step 2: Create the repo and push `main`**

```bash
gh repo create Total-Joint-Specialists/example-stats-analysis --public \
  --description "Statistics tutorials for TJS research assistants: tidy data, Table 1, and every common test in R and Python (synthetic data)" \
  --homepage "https://total-joint-specialists.github.io/example-stats-analysis/" \
  --source . --remote origin --push
```

Expected: a URL `https://github.com/Total-Joint-Specialists/example-stats-analysis` is printed.

- [ ] **Step 3: Create the `gh-pages` branch with a first publish**

```bash
quarto publish gh-pages --no-prompt --no-browser
```

Expected:
- Quarto renders from `_freeze/`, pushes the `gh-pages` branch, and writes `_publish.yml`
- it prints the site URL

- [ ] **Step 4: Make sure Pages serves from `gh-pages`**

```bash
gh api repos/Total-Joint-Specialists/example-stats-analysis/pages --jq '.source' \
  || gh api -X POST repos/Total-Joint-Specialists/example-stats-analysis/pages \
       -f "source[branch]=gh-pages" -f "source[path]=/"
```

Expected: JSON showing `"branch": "gh-pages"`, `"path": "/"`.

- [ ] **Step 5: Commit `_publish.yml` and push, then watch CI**

```bash
git add _publish.yml
git commit -m "Record GitHub Pages publish target

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push
gh run list --limit 2
gh run watch "$(gh run list --workflow 'Publish site' --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status
gh run watch "$(gh run list --workflow 'Site checks' --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status
```

Expected: both runs finish with `completed` / `success`.

- [ ] **Step 6: Verify the live site**

```bash
curl -fsS https://total-joint-specialists.github.io/example-stats-analysis/ | grep -c "Which test do I need?"
curl -fsS -o /dev/null -w "%{http_code}\n" https://total-joint-specialists.github.io/example-stats-analysis/getting-started/using-this-site.html
```

Expected: `1` and `200`. If you get a 404 within the first couple of minutes, wait for the Pages build (`gh api repos/Total-Joint-Specialists/example-stats-analysis/pages/builds/latest --jq .status` shows `built`) and retry.

- [ ] **Step 7: Report to the owner**

Send the site URL, the repo URL, and the CI run links.
