# Phase 3b: Test Catalog, Three or More Groups (Pages 8–9) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace two catalog stubs with finished pages, one per row of the decision table:
- `catalog/08-three-plus-unmatched.qmd`: one-way ANOVA, Kruskal-Wallis, chi-square (r × c) and Cox regression
- `catalog/09-three-plus-matched.qmd`: repeated-measures ANOVA, Friedman, Cochran's Q and stratified Cox

Each page ends with a "Which groups differ?" section that points to page 15. The plan also hardens the catalog test harness and documents the "p > 0.999" convention, two minors deferred from Phase 3a.

**Architecture:**
- Same structure as Phase 3a:
  - knitr-engine pages, each decision-table cell an `##` section with the spec §6 anatomy as `###` steps
  - hidden `check_agree()` R ⟷ Python checks, a `# Prose guard`, and a data-checksum stamp
  - exercise solutions that are executed chunks
- The catalog source rules now apply only to decision-table cell sections, so a page can carry other `##` sections such as "Which groups differ?".
- New source rules:
  - each section's visible Python must define every name it uses
  - effectsize's bootstrap CIs must be seeded

**Tech Stack:**
- R: tidyverse, survival, ggsurvfit, effectsize, DescTools and rstatix (new; called as `pkg::`)
- Python: pandas 3, scipy, pingouin, statsmodels, lifelines
- Quarto 1.9.37

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`, especially:
- §3.2: rows 8–9 anchors
- §4: effect sizes (ω², ε², Cramér's V, partial η² with generalized η² noted, Kendall's W, Cochran's Q proportions), the "Which groups differ?" sections, and page 9's missed-visit note linking to page 16
- §6: page anatomy
- §8: quality checks

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
  - Call DescTools, effectsize and rstatix as `pkg::fun()`; don't attach them.
  - Never assign to `_` in a Python chunk; give a matplotlib return value a name (`parts = ax.boxplot(...)`).
- **Section anatomy (spec §6, CLAUDE.md rule 13):**
  - A `**The question:**` line comes first.
  - Then these `###` steps, in order: When to use it, Look at the data first, Run it, Read the output, Effect size and 95% CI, How to report it.
  - How to report it holds a `> **Methods:**` and a `> **Results:**` blockquote.
  - Each section has a ⚠️ box, and a 🔀 box wherever R and Python defaults differ.
- **Self-contained sections:** a section's first R block calls `library()` and `read_csv("data/...")`. Its first Python block imports and calls `pd.read_csv("data/...")`. Every name its visible Python uses is defined within the section.
- **Prose guard:** one hidden R chunk headed `# Prose guard`, immediately before `## Exercises {#exercises}`. It `stopifnot()`s every quoted number, including the numbers in exercise solutions, and recomputes those itself because it runs before the solution chunks.
- **Bootstrap CIs:** call `set.seed(2026)` before `effectsize::rank_epsilon_squared()` and `effectsize::kendalls_w()`, or pass `ci = NULL`.
- **Data stamp:** each page has the `<!-- data-checksum: … -->` chunk.
- **Solutions:** exercise solutions are executed `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`, after the sentence "The solutions use the packages and data loaded in the sections above, so run the page from the top first."
- **Freeze:** render every changed page and commit its `_freeze/` directory. After a deliberately failed render, delete the leftover `catalog/<page>_files/` folder.
- **Reporting conventions:**
  - mean (SD) or median (IQR)
  - n (%)
  - p to 3 decimals, with a floor of "p < 0.001" and a ceiling of "p > 0.999"
  - a 95% CI with every estimate; one-sided effect-size CIs are labeled "one-sided"
- **Branching:** work on branch `phase-3b-catalog`, in a worktree under `.worktrees/phase-3b`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A reader copies one section's Python, and it uses a name defined only in another section.** Test: `tests/site/test_sources.py::test_each_catalog_section_python_runs_on_its_own` (Task 2).
2. **A bootstrap CI changes on every render,** so the quoted CI goes stale or the freeze churns. Test: `test_sources.py::test_bootstrap_cis_are_seeded` (Task 2).
3. **Repeated-measures tests silently drop every patient with a missed visit,** and the reader doesn't notice that 246 of 574 patients are gone. Tests:
   - `tests/site/test_catalog.py::test_matched_page_warns_that_missed_visits_drop_patients` (Task 4)
   - the prose guard pins 574 vs 328
4. **A library default changes,** for example effectsize's `cramers_v(adjust=)`, the opposite defaults of `oneway.test()` and `aov()`, or lifelines' convergence. The hidden `check_agree()` must stop the render. The Task 3 mutation step proves the Cramér's V check bites.
5. **Someone runs `just data`, and the quoted numbers go stale.** The prose guards and `tests/site/test_freshness.py` cover this; `just data` already re-renders `catalog/`.

## Plan rulings (made while prototyping)

- **Examples:**
  - **One-way ANOVA: age by ASA class,** not operative time by surgeon (p = 0.84). A significant example gives "Which groups differ?" something to answer, and the SDs are similar (8.7 to 9.3), so classic ANOVA is appropriate.
  - **Kruskal-Wallis: satisfaction by surgeon,** the example page 3's flowchart table already promises.
  - **Chi-square: complications by surgeon,** where every expected count is at least 13. Complications by ASA class, where two expected counts are below 5, became exercise 3: combine classes, then use Fisher's test.
  - **Cox: implants A, B and C.**
  - **Page 9:**
    - VR-12 PCS at four visits (328 complete)
    - KOOS JR at 6 weeks, 3 months and 1 year (205 complete)
    - walking aid at four visits (328 complete)
    - matched triplets for stratified Cox
- **Classic one-way ANOVA is the table's test; Welch's ANOVA appears in the 🔀 box and is checked too.** ω² and Tukey's post-hoc test go with the classic ANOVA. Page 6 says to use Welch's t from the start; here the box explains when to switch, and that R's `oneway.test()` defaults to Welch while `aov()` doesn't.
- **R uses rstatix for repeated-measures ANOVA.** It reports Mauchly's test, the Greenhouse-Geisser correction and both partial and generalized η² in one call, matching pingouin's `rm_anova()`.
  - rstatix stores its results rounded to 3 decimals.
  - So the hidden check takes F and partial η² from base `aov()` and effectsize, which are exact, and checks rstatix's epsilon and Mauchly values with `tol = 1e-3`, with a comment.
- **Python computes ω² and ε² from the ANOVA table and H.** pingouin and scipy have no function for them. Each formula's value is checked against effectsize.
- **Bootstrap CIs are seeded.** effectsize's CIs for ε² and Kendall's W come from `boot::boot()`, so they changed on every render; the prototype's prose guard caught it. Visible code calls `set.seed(2026)` with a comment; prose guards pass `ci = NULL`. A source rule enforces this.
- **The Kendall's W tie warning is hidden.** That chunk has `#| warning: false` and a code comment: effectsize warns when a patient has tied scores, but the tie correction already handles them (W matches pingouin's 0.618).
- **Page 8's exercise 3 hides `chisq.test()`'s "may be incorrect" warning** with `#| warning: false`. That warning is the exercise's lesson, so the solution prose quotes it.
- **Cramér's V is unadjusted** (`adjust = FALSE`) to match scipy. effectsize's default bias-adjusted value (0.05) is explained in the 🔀 box.
- **One-sided effect-size CIs are R-only.** effectsize gives one-sided CIs for ω², ε², V, η²~p~ and W, and they are quoted with the word "one-sided". The prose says scipy and pingouin don't compute them.
- **lifelines convergence:**
  - **Cohort (page 8):** the 3-group Cox needs `fit_options={"precision": 1e-9}`, because the default is 4e-5 off R.
  - **Matched triplets (page 9):** the default matches R exactly, so page 9 omits the option, and its 🔀 box says when to tighten it.
- **Cochran's Q effect size:**
  - **Reported:** each visit's proportion with a Wilson CI, plus percentage-point changes between visits.
  - **Not here:** pairwise McNemar tests and their CIs belong to page 15. There is no tested paired-difference CI to use instead of hand-rolling one.
- **"Which groups differ?" sections:**
  - **Form:** prose plus a table pointing to pages 15, 14 and 16, with no code.
  - **Anchor:** `which-groups-differ` on both pages; page 9's heading reads "Which visits differ?".
  - **Effect on tests:** the catalog source rules now skip non-cell sections.
- **Self-containment, R side:** this stays the Phase 3a heuristic (first block has `library()` and `read_csv`). Only Python gets the undefined-names check, which needs no R in CI.
- **"p > 0.999" is now documented** in the reporting-conventions table and CLAUDE.md rule 8. Spec §4 page 0.2 names only the floor; page 6 already reports p > 0.999.

## Reference results (prototype, 2026-10-06, R 4.6.0 / Python 3.13 / pandas 3.0.6)

Both pages rendered with every hidden check passing. Full suite:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- pytest `tests/python`: 80 passed
- pytest `tests/site`: 157 passed
- lychee: 0 errors

Mutation checks:
- The render stopped on each of these:
  - effectsize's default Cramér's V (`disagree on 'v'`)
  - a wrong prose number on page 9
  - the unseeded Kendall's W CI, caught by the prototype's own prose guard
- Deleting `from scipy import stats` from a section failed `test_each_catalog_section_python_runs_on_its_own`.

| Page | Numbers |
|---|---|
| 8 | age by ASA: F(3, 596) = 23.9, ω² = 0.10; satisfaction by surgeon: H = 0.68, p = 0.713, ε² = 0.001; complications by surgeon: χ² = 3.62, p = 0.163, V = 0.08; implant C vs A HR 3.07 (1.85 to 5.09), LR χ² = 27.6 |
| 9 | PCS: F(3, 981) = 317.1, η²~p~ = 0.49, Mauchly p = 0.324; KOOS JR: Friedman χ² = 253.6, W = 0.62; walking aid: Q = 186.8; triplets: implant C HR 3.91 (1.28 to 11.95) |

---

### Task 1: rstatix and the setup checks

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `getting-started/check_setup.R`, `tests/python/test_check_setup.py`

**Interfaces:**
- Produces: the R package rstatix and its dependencies, which page 9 uses for repeated-measures ANOVA.

- [ ] **Step 1: Create the worktree and build the current site**

```bash
git checkout main && git pull
git worktree add .worktrees/phase-3b -b phase-3b-catalog main
cd .worktrees/phase-3b
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `122 passed`.

- [ ] **Step 2: Write the failing checks**

In `getting-started/check_setup.R`, replace

```r
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat", "tidyverse", "readxl",
             "tidyxl", "janitor", "gtsummary", "flextable", "smd", "effectsize",
             "DescTools", "survival", "ggsurvfit")) {
```

with

```r
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat", "tidyverse", "readxl",
             "tidyxl", "janitor", "gtsummary", "flextable", "smd", "effectsize",
             "DescTools", "survival", "ggsurvfit", "rstatix")) {
```

In `tests/python/test_check_setup.py`, replace

```python
    for pkg in ["tidyverse", "readxl", "tidyxl", "janitor", "gtsummary", "flextable", "smd",
                "effectsize", "DescTools", "survival", "ggsurvfit"]:
```

with

```python
    for pkg in ["tidyverse", "readxl", "tidyxl", "janitor", "gtsummary", "flextable", "smd",
                "effectsize", "DescTools", "survival", "ggsurvfit", "rstatix"]:
```

- [ ] **Step 3: Run them to verify they fail**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_setup")'`

Expected: "check_setup.R passes in a working project" FAILS, with the output reporting `R package rstatix PROBLEM`.

- [ ] **Step 4: Install and lock rstatix**

In `DESCRIPTION`, replace

```
    rmarkdown,
    smd,
```

with

```
    rmarkdown,
    rstatix,
    smd,
```

Run:

```bash
Rscript -e 'renv::install("rstatix", prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
python3 -c "import json; print('rstatix' in json.load(open('renv.lock'))['Packages'])"
```

Expected: `True`.

- [ ] **Step 5: Run all the tests**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
uv run pytest tests/site -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- Python: `80 passed`
- site: `122 passed`

- [ ] **Step 6: Commit**

```bash
git add DESCRIPTION renv.lock getting-started/check_setup.R tests/python/test_check_setup.py
git commit -m "Add rstatix (repeated-measures ANOVA with sphericity corrections) and its setup check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Harder catalog rules, and the "p > 0.999" convention

Four changes to the test harness and conventions:
- **Cell sections only:** catalog source rules apply to decision-table cell sections, not to other `##` sections such as "Which groups differ?".
- **Python runs alone:** each section's Python must define every name it uses (deferred from Phase 3a).
- **Seeded bootstrap CIs:** effectsize's bootstrap CIs must be seeded.
- **"p > 0.999":** the ceiling is documented (deferred from Phase 3a).

**Files:**
- Modify: `tests/site/test_sources.py`, `tests/site/test_getting_started.py`, `tests/python/test_repo_docs.py`
- Modify: `getting-started/using-this-site.qmd`, `CLAUDE.md`
- Modify: `_freeze/getting-started/using-this-site/` (re-render; commit it)

**Interfaces:**
- Consumes: `test_sources.py`'s `CELL_HEADING`, `VISIBLE_CHUNK`, `HIDDEN_CHUNK`, `written_pages()` and `qmd_files()` (Phase 3a).
- Produces:
  - `cell_sections(page, text)`
  - `catalog_sections()`, now limited to `sitelib.CELL_ANCHORS`
  - `undefined_names(code) -> set`
  - `unseeded_bootstrap(text) -> bool`

- [ ] **Step 1: Write the tests**

In `tests/site/test_sources.py`, replace

```python
import re

from sitelib import ROOT
```

with

```python
import ast
import builtins
import re

from sitelib import CELL_ANCHORS, ROOT
```

replace

```python
def catalog_sections():
    """(page, anchor, source) for every decision-table section of the written catalog pages."""
    for name, text in written_pages("catalog"):
        marks = list(CELL_HEADING.finditer(text))
        for mark, following in zip(marks, marks[1:] + [None]):
            if mark.group(1) != "exercises":
                yield name, mark.group(1), text[mark.end():following.start() if following else len(text)]
```

with

```python
def cell_sections(page, text):
    """(anchor, source) for each decision-table cell section of one catalog page, skipping
    other sections such as "Which groups differ?" and the exercises."""
    marks = list(CELL_HEADING.finditer(text))
    for mark, following in zip(marks, marks[1:] + [None]):
        if mark.group(1) in CELL_ANCHORS[page]:
            yield mark.group(1), text[mark.end():following.start() if following else len(text)]


def catalog_sections():
    """(page, anchor, source) for every decision-table section of the written catalog pages."""
    for name, text in written_pages("catalog"):
        for anchor, body in cell_sections(name.replace(".qmd", ".html"), text):
            yield name, anchor, body


def test_cell_sections_skip_sections_that_are_not_table_cells():
    text = "## Cox regression {#cox}\nA\n## Which groups differ? {#which-groups-differ}\nB\n## Exercises {#exercises}\nC\n"
    assert [a for a, _ in cell_sections("catalog/08-three-plus-unmatched.html", text)] == ["cox"]
```

and append (after two blank lines):

```python
# ---- each section's Python runs on its own -------------------------------

def undefined_names(code):
    """Names the code reads but never imports, assigns or defines (statement order ignored)."""
    defined, used = set(dir(builtins)), set()
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Name):
            (used if isinstance(node.ctx, ast.Load) else defined).add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            defined.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
    return used - defined


def test_rule_finds_names_a_section_never_defines():
    assert undefined_names("import pandas as pd\nprint(np.mean(scores))") == {"np", "scores"}
    assert undefined_names("import numpy as np\nx = [1]\nf = lambda v: v + 1\nprint(np.mean(x), f(2))") == set()


def test_each_catalog_section_python_runs_on_its_own():
    """Every name a section's visible Python uses is created in that section, so it can be copied alone."""
    for name, anchor, body in catalog_sections():
        code = "\n".join(chunk for lang, chunk in VISIBLE_CHUNK.findall(body) if lang == "python")
        assert undefined_names(code) == set(), f"{name}#{anchor} uses {sorted(undefined_names(code))}"


# ---- bootstrap CIs need a seed ---------------------------------------------
# effectsize computes the CIs of these effect sizes by bootstrap (random resampling),
# so without set.seed() the printed CI changes on every render.

BOOTSTRAP_CI_FUNCTIONS = ("rank_epsilon_squared(", "kendalls_w(")
R_CHUNK = re.compile(r"```\{r[^}]*\}\n(.*?)\n```", re.DOTALL)


def unseeded_bootstrap(text):
    for code in R_CHUNK.findall(text):
        for line in code.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if any(f in line for f in BOOTSTRAP_CI_FUNCTIONS) and "ci = NULL" not in line:
                if "set.seed(" not in code[:code.index(line)]:
                    return True
    return False


def test_rule_catches_an_unseeded_bootstrap_ci():
    assert unseeded_bootstrap("```{r}\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
    assert not unseeded_bootstrap("```{r}\nset.seed(1)\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
    assert not unseeded_bootstrap("```{r}\neffectsize::kendalls_w(y ~ v | id, data = d, ci = NULL)\n```")
    assert not unseeded_bootstrap("```{r}\n# kendalls_w() warns about ties\nx <- 1\n```")


def test_bootstrap_cis_are_seeded():
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files() if unseeded_bootstrap(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Call set.seed() before (or pass ci = NULL to) a bootstrap CI in: " + ", ".join(offenders)
```

Append to `tests/site/test_getting_started.py` (after two blank lines):

```python
def test_reporting_conventions_cap_large_p_values(site):
    text = load("getting-started/using-this-site.html").get_text(" ")
    assert "p > 0.999" in text and "p = 1.000" in text
```

In `tests/python/test_repo_docs.py`, replace

```python
                 "never assign to `_`", "**The question:**", "override-dependencies"]:
```

with

```python
                 "never assign to `_`", "**The question:**", "override-dependencies",
                 'a ceiling of "p > 0.999"']:
```

- [ ] **Step 2: Run them to verify which fail**

Run:

```bash
uv run pytest tests/site -q
uv run pytest tests/python/test_repo_docs.py -q
```

Expected:
- `test_reporting_conventions_cap_large_p_values` FAILS.
- `test_claude_md_states_the_golden_rules` FAILS on `a ceiling of "p > 0.999"`.
- The other 127 site tests pass. Pages 4–7 already satisfy the new source rules, and no page calls a bootstrap CI yet. Step 3 proves the undefined-names rule bites.

- [ ] **Step 3: Prove the undefined-names rule bites, then restore**

In `catalog/05-one-group-vs-hypothetical.qmd`, delete the line `from scipy import stats` from the first Python block of the `#chi-square-gof` section, then run `uv run pytest tests/site/test_sources.py -q`.

Expected: `test_each_catalog_section_python_runs_on_its_own` FAILS with `catalog/05-one-group-vs-hypothetical.qmd#chi-square-gof uses ['stats']`. Undo the change (`git checkout -- catalog/05-one-group-vs-hypothetical.qmd`).

- [ ] **Step 4: Document the ceiling**

In `getting-started/using-this-site.qmd`, replace

```markdown
| p-values | three decimals; never "p = 0.000" | p = 0.017; p < 0.001 |
```

with

```markdown
| p-values | three decimals; never "p = 0.000" or "p = 1.000" | p = 0.017; p < 0.001; p > 0.999 |
```

In `CLAUDE.md`'s golden rule 8, replace

```markdown
8. **Reporting conventions** (spec section 4, page 0.2): mean (SD) or median (IQR); n (%); p to 3 decimals with a floor of "p < 0.001"; a 95% CI with every estimate.
```

with

```markdown
8. **Reporting conventions** (spec section 4, page 0.2): mean (SD) or median (IQR); n (%); p to 3 decimals with a floor of "p < 0.001" and a ceiling of "p > 0.999"; a 95% CI with every estimate.
```

- [ ] **Step 5: Render the page and run the tests**

Run:

```bash
quarto render getting-started/using-this-site.qmd
uv run pytest tests/site -q
uv run pytest tests/python -q
git status --short
```

Expected:
- site: `128 passed`
- Python: `80 passed`
- `git status` lists only this task's files, plus `_freeze/getting-started/using-this-site/`

- [ ] **Step 6: Commit**

```bash
git add tests/site/test_sources.py tests/site/test_getting_started.py tests/python/test_repo_docs.py getting-started/using-this-site.qmd CLAUDE.md _freeze/getting-started/using-this-site
git commit -m "Catalog rules: cell sections only, self-contained Python, seeded bootstrap CIs; document p > 0.999

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Page 8, Compare three or more unmatched groups

**Files:**
- Modify: `catalog/08-three-plus-unmatched.qmd` (replace the stub)
- Create: `_freeze/catalog/08-three-plus-unmatched/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Phase 3a's `test_catalog.py` (`WRITTEN`, `SURVIVAL_LINKS`, `section()`, `text_of()`)
  - Task 2's cell-only `catalog_sections()`
  - `data/cohort.csv`
- Produces:
  - page 8 anchors `#one-way-anova`, `#kruskal-wallis`, `#chi-square`, `#cox` and `#which-groups-differ`
  - `test_catalog.py`'s `THREE_GROUP_PAGES`
  - page 9 links to `08-three-plus-unmatched.qmd`

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
]
```

replace

```python
    ("catalog/07-two-paired-groups.html", "stratified-cox"): "survival/14-cox-regression.html",
}.items()
```

with

```python
    ("catalog/07-two-paired-groups.html", "stratified-cox"): "survival/14-cox-regression.html",
    ("catalog/08-three-plus-unmatched.html", "cox"): "survival/14-cox-regression.html",
    ("catalog/09-three-plus-matched.html", "stratified-cox"): "survival/14-cox-regression.html",
}.items()
```

and append (after two blank lines):

```python
# ---- three or more groups -------------------------------------------------

THREE_GROUP_PAGES = [page for page in WRITTEN if page.startswith(("catalog/08-", "catalog/09-"))]


@pytest.mark.parametrize("page", THREE_GROUP_PAGES)
def test_three_group_pages_end_with_which_groups_differ(site, page):
    hrefs = [a["href"] for a in section(page, "which-groups-differ").select("a[href]")]
    assert any(href.endswith("beyond/15-post-hoc.html") for href in hrefs)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_catalog.py -q`

Expected: 12 of the 14 new page-8 tests FAIL; the no-warnings and short-outputs tests pass trivially on a stub. The 57 earlier tests pass.

- [ ] **Step 3: Write the page**

Replace `catalog/08-three-plus-unmatched.qmd` with:

````markdown
---
title: "8 · Compare three or more unmatched groups"
description: "One-way ANOVA, Kruskal-Wallis test, chi-square test and Cox regression: three or more groups of different patients."
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

Three or more groups of **different** patients: the four ASA classes, the three surgeons, implants A, B and C. You could compare every pair of groups with the tests on [page 6](06-two-unpaired-groups.qmd), but each extra test is another chance of a false positive. The tests on this page ask one question first: **is there any difference among the groups at all?** If the answer is yes, [Which groups differ?](#which-groups-differ) explains the next step.

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

## One-way ANOVA {#one-way-anova}

**The question:** Does age at surgery differ across ASA classes 1 to 4?

### When to use it

- The outcome is a **measurement**, compared across **three or more independent groups**.
- Within **each group** it's roughly normal, or each group is reasonably large and not badly skewed ([page 3](../foundations/03-distributions.qmd#within-groups)).
- The groups have **similar spreads**: as a rule of thumb, the largest SD is no more than about twice the smallest. If not, use **Welch's ANOVA** (see the R vs Python box), especially when the group sizes are unequal.
- If the outcome is skewed, bounded or ordinal → the [Kruskal-Wallis test](#kruskal-wallis).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(asa = factor(asa))   # ASA class is a group, not a number

ggplot(cohort, aes(asa, age)) +
  geom_boxplot() +
  labs(x = "ASA class", y = "Age at surgery, years")

cohort |>
  group_by(asa) |>
  summarise(n = n(), mean = mean(age), sd = sd(age))
```

## Python

```{python}
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
ages = [group["age"] for asa, group in cohort.groupby("asa")]   # one list of ages per ASA class

fig, ax = plt.subplots(figsize=(6, 3))
parts = ax.boxplot(ages, tick_labels=["1", "2", "3", "4"])   # naming the result keeps it out of the output
ax.set_xlabel("ASA class")
ax.set_ylabel("Age at surgery, years")
plt.show()

print(cohort.groupby("asa")["age"].agg(["count", "mean", "std"]))
```
:::

Age rises steadily with ASA class. The SDs are all close to 9 years, so the spreads are similar. The groups are very different in size, though: 300 patients in ASA 2, only 18 in ASA 4.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
age_anova <- aov(age ~ asa, data = cohort)   # aov() fits the classic one-way ANOVA
summary(age_anova)
```

## Python

```{python}
age_anova = pg.anova(data=cohort, dv="age", between="asa", detailed=True)   # classic one-way ANOVA
print(age_anova)
```
:::

```{python}
#| include: false
chk = {"f": float(age_anova.loc[0, "F"]), "ss_between": float(age_anova.loc[0, "SS"]),
       "ss_within": float(age_anova.loc[1, "SS"]), "df_within": float(age_anova.loc[1, "DF"])}
```

```{r}
#| include: false
age_table <- summary(age_anova)[[1]]
check_agree(list(f = age_table[1, "F value"], ss_between = age_table[1, "Sum Sq"],
                 ss_within = age_table[2, "Sum Sq"], df_within = age_table[2, "Df"]), reticulate::py$chk)
```

### Read the output

- **asa row:** the variation **between** the group means. **Df = 3** (four groups minus one), **Sum Sq = 5727**.
- **Residuals** (R) or **Within** (Python): the variation of patients **within** their groups. **Df = 596** (600 patients minus four groups).
- **F = 23.9:** the between-group variation divided by the within-group variation, each per degree of freedom. If the groups had the same mean, F would be close to 1.
- **p < 0.001** (R prints `1.28e-14`): ages this different across groups would be very unlikely if every ASA class had the same mean age.

### Effect size and 95% CI

**Omega squared (ω²)** is the share of the variation in age that ASA class accounts for, corrected for the small upward bias of the simpler eta squared (η²). As a rough guide, 0.01 is small, 0.06 medium and 0.14 large.

::: {.panel-tabset group="language"}
## R

```{r}
effectsize::omega_squared(age_anova, partial = FALSE)   # plain (not partial) omega squared
```

## Python

```{python}
# omega squared from the ANOVA table: (SS between - df between × MS within) / (SS total + MS within)
ss_between, ss_within = age_anova.loc[0, "SS"], age_anova.loc[1, "SS"]
df_between, ms_within = age_anova.loc[0, "DF"], age_anova.loc[1, "MS"]
omega2 = (ss_between - df_between * ms_within) / (ss_between + ss_within + ms_within)
print(omega2)
```
:::

```{python}
#| include: false
chk = {"omega2": float(omega2)}
```

```{r}
#| include: false
age_omega <- effectsize::omega_squared(age_anova, partial = FALSE)
check_agree(list(omega2 = age_omega$Omega2), reticulate::py$chk)
```

ω² = 0.10: ASA class accounts for about a tenth of the variation in age, a medium effect. R also prints a one-sided 95% CI (0.06 to 1.00): ω² can't be negative, so only its lower bound is informative. scipy and pingouin don't compute this CI. The ANOVA doesn't say *which* classes differ: see [Which groups differ?](#which-groups-differ).

### How to report it

> **Methods:** Age was compared across ASA classes with one-way analysis of variance (ANOVA), with omega squared (ω²) as the effect size.
>
> **Results:** Mean age rose with ASA class, from 59.8 years (SD 8.7) in ASA 1 to 73.7 years (SD 9.3) in ASA 4 (one-way ANOVA, F(3, 596) = 23.9, p < 0.001; ω² = 0.10, one-sided 95% CI 0.06 to 1.00).

::: {.callout-warning}
## ⚠️ Watch out: ANOVA doesn't tell you which groups differ
A significant ANOVA means at least one group mean differs from another, not that every group differs from every other. Don't follow it with a string of unadjusted t tests: that brings back the false-positive problem the ANOVA was meant to avoid. Use a post-hoc test ([page 15](../beyond/15-post-hoc.qmd)).
:::

::: {.callout-tip}
## 🔀 R vs Python: classic or Welch's ANOVA
- **Classic ANOVA** assumes the groups have the same spread. R's `aov()`, scipy's `f_oneway()` and pingouin's `anova()` all run it by default.
- **Welch's ANOVA** doesn't assume equal spreads. R's `oneway.test()` runs **Welch's** version by default (add `var.equal = TRUE` for the classic one), the opposite of `aov()`. In Python use `pg.welch_anova()` or `stats.f_oneway(..., equal_var=False)`.
- Here the SDs are similar, and Welch's ANOVA agrees: F = 23.5, p < 0.001.
:::

```{python}
#| include: false
welch = pg.welch_anova(data=cohort, dv="age", between="asa")
chk = {"f": float(welch.loc[0, "F"]), "df_denom": float(welch.loc[0, "ddof2"])}
```

```{r}
#| include: false
welch <- oneway.test(age ~ asa, data = cohort)
check_agree(list(f = unname(welch$statistic), df_denom = unname(welch$parameter[2])), reticulate::py$chk)
```

## Kruskal-Wallis test {#kruskal-wallis}

**The question:** Does satisfaction 1 year after surgery differ between surgeons S1, S2 and S3?

### When to use it

- The outcome is **ordinal** (satisfaction from 1 to 5), **skewed**, or has a **ceiling or floor**, compared across **three or more independent groups**.
- Like the [Mann-Whitney test](06-two-unpaired-groups.qmd#mann-whitney), it works on ranks: it asks whether values in some groups tend to be larger than in others.
- With two groups it gives essentially the same result as the Mann-Whitney test.
- If the outcome is a roughly normal measurement → [one-way ANOVA](#one-way-anova).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)
satisfied <- cohort |> filter(!is.na(satisfaction_1yr))   # patients who answered

count(satisfied, surgeon, satisfaction_1yr) |>
  pivot_wider(names_from = satisfaction_1yr, values_from = n)   # one row per surgeon

satisfied |>
  group_by(surgeon) |>
  summarise(n = n(), median = median(satisfaction_1yr),
            q1 = quantile(satisfaction_1yr, 0.25), q3 = quantile(satisfaction_1yr, 0.75))
```

## Python

```{python}
import pandas as pd
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
satisfied = cohort.dropna(subset=["satisfaction_1yr"])   # patients who answered

print(pd.crosstab(satisfied["surgeon"], satisfied["satisfaction_1yr"]))
print(satisfied.groupby("surgeon")["satisfaction_1yr"].describe()[["count", "25%", "50%", "75%"]])
```
:::

502 of the 600 patients answered. Most were satisfied (4) or very satisfied (5) with every surgeon, and the three distributions look much alike.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
satisfaction_test <- kruskal.test(satisfaction_1yr ~ surgeon, data = satisfied)
satisfaction_test
```

## Python

```{python}
scores = [group["satisfaction_1yr"] for surgeon, group in satisfied.groupby("surgeon")]   # one list per surgeon
satisfaction_test = stats.kruskal(*scores)
print(satisfaction_test)
```
:::

```{python}
#| include: false
chk = {"h": float(satisfaction_test.statistic), "p": float(satisfaction_test.pvalue)}
```

```{r}
#| include: false
check_agree(list(h = unname(satisfaction_test$statistic), p = satisfaction_test$p.value), reticulate::py$chk)
```

### Read the output

- **Kruskal-Wallis chi-squared = 0.68** (R) or **statistic** (Python): the H statistic. It measures how far apart the groups' average ranks are. Both programs correct it for the many tied scores.
- **df = 2:** three groups minus one.
- **p = 0.713:** satisfaction this similar, or less, would be very common if the surgeons' patients were equally satisfied.

### Effect size and 95% CI

**Epsilon squared (ε²)** is the rank-based counterpart of ω²: the share of the variation in the ranks that the groups account for, from 0 to 1. It is H divided by (n − 1).

::: {.panel-tabset group="language"}
## R

```{r}
set.seed(2026)   # its CI comes from a bootstrap (random resampling); a seed makes it repeatable
effectsize::rank_epsilon_squared(satisfaction_1yr ~ surgeon, data = satisfied)
```

## Python

```{python}
epsilon2 = satisfaction_test.statistic / (len(satisfied) - 1)   # H / (n - 1)
print(epsilon2)
```
:::

```{python}
#| include: false
chk = {"epsilon2": float(epsilon2)}
```

```{r}
#| include: false
set.seed(2026)
satisfaction_eps <- effectsize::rank_epsilon_squared(satisfaction_1yr ~ surgeon, data = satisfied)
check_agree(list(epsilon2 = satisfaction_eps$rank_epsilon_squared), reticulate::py$chk)
```

ε² = 0.001: surgeon accounts for essentially none of the variation in satisfaction. R's one-sided CI runs from 0.00 to 1.00; it comes from a bootstrap, which is why the code sets a seed. scipy has no function for it.

### How to report it

> **Methods:** Satisfaction at 1 year (a 5-point ordinal scale) was compared across surgeons with the Kruskal-Wallis test, with epsilon squared (ε²) as the effect size.
>
> **Results:** Of 600 patients, 502 reported their satisfaction at 1 year. The median was 4 (IQR 4 to 5) for surgeon S1 and 5 (IQR 4 to 5) for surgeons S2 and S3, with no significant difference between surgeons (Kruskal-Wallis H = 0.68, df = 2, p = 0.713; ε² = 0.001, one-sided 95% CI 0.00 to 1.00).

::: {.callout-warning}
## ⚠️ Watch out: missing answers aren't random
98 patients didn't report their satisfaction. If unhappy patients were less likely to answer, every surgeon looks better than they are, and the comparison can be biased too. Always report how many answered in each group, and consider whether non-response differs between groups.
:::

::: {.callout-tip}
## 🔀 R vs Python: ties and the data format
Both `kruskal.test()` and `stats.kruskal()` correct H for ties, so they agree even with a 5-point scale full of tied scores. R takes a formula (`outcome ~ group`); scipy takes one list of values per group, which is why the Python code builds `scores` first.
:::

## Chi-square test {#chi-square}

**The question:** Do 90-day complication rates differ between surgeons S1, S2 and S3?

### When to use it

- The outcome is **categorical** (here yes/no), compared across **three or more independent groups**: an r × c table.
- Every **expected** count should be at least 5. If not, combine categories that make sense together, or use Fisher's exact test, which R's `fisher.test()` runs on larger tables too (scipy's only handles 2 × 2).
- With two groups and a yes/no outcome → [Fisher's exact test](06-two-unpaired-groups.qmd#fisher-chi-square).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

complication_table <- table(
  surgeon      = cohort$surgeon,
  complication = factor(cohort$complication_90d, levels = c(1, 0), labels = c("yes", "no"))
)
complication_table
prop.table(complication_table, margin = 1)   # row percentages: complications per surgeon
```

## Python

```{python}
import pandas as pd
from scipy import stats
from scipy.stats.contingency import association

cohort = pd.read_csv("data/cohort.csv")

complication_table = pd.crosstab(cohort["surgeon"], cohort["complication_90d"]).loc[:, [1, 0]]   # "yes" first
print(complication_table)
print(pd.crosstab(cohort["surgeon"], cohort["complication_90d"], normalize="index"))   # row percentages
```
:::

Complications followed 6.5% of S1's procedures, 11.4% of S2's and 7.6% of S3's.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
complication_test <- chisq.test(complication_table)
complication_test$expected      # all at least 5, so the chi-square test is valid
complication_test
```

## Python

```{python}
complication_test = stats.chi2_contingency(complication_table)
print(complication_test.expected_freq)   # all at least 5, so the chi-square test is valid
print(complication_test.statistic, complication_test.dof, complication_test.pvalue)
```
:::

```{python}
#| include: false
chk = {"chisq": float(complication_test.statistic), "df": float(complication_test.dof),
       "p": float(complication_test.pvalue)}
```

```{r}
#| include: false
check_agree(list(chisq = unname(complication_test$statistic), df = unname(complication_test$parameter),
                 p = complication_test$p.value), reticulate::py$chk)
```

### Read the output

- **Expected counts:** what each cell would hold if complication rates were the same for every surgeon. The smallest is 13.3, so the test is valid.
- **X-squared = 3.62, df = 2:** the chi-square statistic, with (3 surgeons − 1) × (2 outcomes − 1) = 2 degrees of freedom.
- **p = 0.163:** differences like these would be fairly common if the three surgeons had the same complication rate.

### Effect size and 95% CI

**Cramér's V** measures the strength of association in a table, from 0 (none) to 1 (perfect). For a table with 2 columns, about 0.1 is small, 0.3 medium and 0.5 large.

::: {.panel-tabset group="language"}
## R

```{r}
effectsize::cramers_v(complication_table, adjust = FALSE)   # see the R vs Python box
```

## Python

```{python}
print(association(complication_table, method="cramer"))
```
:::

```{python}
#| include: false
chk = {"v": float(association(complication_table, method="cramer"))}
```

```{r}
#| include: false
complication_v <- effectsize::cramers_v(complication_table, adjust = FALSE)
check_agree(list(v = complication_v$Cramers_v), reticulate::py$chk)
```

V = 0.08, a small association. For yes/no outcomes, the complication rate in each group (with its CI, as on [page 4](04-describe-one-group.qmd#proportion)) is usually more informative than V.

### How to report it

> **Methods:** Complication rates were compared across surgeons with the chi-square test, with Cramér's V as the effect size.
>
> **Results:** Complications within 90 days followed 15 of 232 procedures by surgeon S1 (6.5%), 24 of 211 by S2 (11.4%) and 12 of 157 by S3 (7.6%). The difference was not statistically significant (χ² = 3.62, df = 2, p = 0.163; Cramér's V = 0.08, one-sided 95% CI 0.00 to 1.00).

::: {.callout-warning}
## ⚠️ Watch out: no Yates' correction here, and check the expected counts
Yates' continuity correction ([page 6](06-two-unpaired-groups.qmd#fisher-chi-square)) only applies to 2 × 2 tables, so both programs skip it for this 3 × 2 table. The expected-count rule still applies: Exercise 3 shows a table that breaks it, and what to do.
:::

::: {.callout-tip}
## 🔀 R vs Python: two versions of Cramér's V
effectsize's `cramers_v()` applies a small-sample **bias correction** by default (0.05 here). scipy's `association()` doesn't (0.08). We set `adjust = FALSE` in R so the two match. Either is acceptable; say which you report.
:::

## Cox regression {#cox}

**The question:** Does the risk of revision differ between implants A, B and C?

### When to use it

- The outcome is **time until an event** (revision), compared across **three or more independent groups**.
- The **log-rank test** extends to three or more groups and answers "do the curves differ?". **Cox regression** also gives a hazard ratio for each group against a reference group, and can adjust for other variables.
- It assumes each group's risk is a steady multiple of the reference group's over time (**proportional hazards**). [Page 14](../survival/14-cox-regression.qmd) shows how to check that and covers Cox regression in full.

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

survfit2(Surv(followup_years, revised) ~ implant, data = cohort, conf.type = "log-log") |>
  ggsurvfit() +
  add_risktable() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Revision-free survival")
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import multivariate_logrank_test
from lifelines.plotting import add_at_risk_counts

cohort = pd.read_csv("data/cohort.csv")

fig, ax = plt.subplots(figsize=(7, 4.5))
curves = []
for implant, group in cohort.groupby("implant"):
    km = KaplanMeierFitter(label=implant).fit(group["followup_years"], group["revised"])
    km.plot_survival_function(ax=ax, ci_show=False)
    curves.append(km)
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Revision-free survival")
add_at_risk_counts(*curves, ax=ax)
plt.tight_layout()
plt.show()
```
:::

Implants A and B track each other closely; implant C falls away from both.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
implant_cox <- coxph(Surv(followup_years, revised) ~ implant, data = cohort)   # implant A is the reference
summary(implant_cox)
```

## Python

```{python}
implant_cox = CoxPHFitter().fit(
    cohort[["followup_years", "revised", "implant"]],
    duration_col="followup_years", event_col="revised", formula="implant",   # implant A is the reference
    fit_options={"precision": 1e-9},   # stop only when fully converged; see the R vs Python box
)
print(implant_cox.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]])
print(implant_cox.log_likelihood_ratio_test().test_statistic)            # overall test, all implants
print(multivariate_logrank_test(cohort["followup_years"], cohort["implant"], cohort["revised"]).test_statistic)
```
:::

```{python}
#| include: false
rows = implant_cox.summary
chk = {"hr_b": float(rows.loc["implant[T.B]", "exp(coef)"]), "hr_c": float(rows.loc["implant[T.C]", "exp(coef)"]),
       "low_c": float(rows.loc["implant[T.C]", "exp(coef) lower 95%"]),
       "high_c": float(rows.loc["implant[T.C]", "exp(coef) upper 95%"]),
       "lr": float(implant_cox.log_likelihood_ratio_test().test_statistic),
       "logrank": float(multivariate_logrank_test(cohort["followup_years"], cohort["implant"], cohort["revised"]).test_statistic)}
```

```{r}
#| include: false
implant_hr <- summary(implant_cox)$conf.int
implant_logrank <- survdiff(Surv(followup_years, revised) ~ implant, data = cohort)
check_agree(list(hr_b = implant_hr["implantB", "exp(coef)"], hr_c = implant_hr["implantC", "exp(coef)"],
                 low_c = implant_hr["implantC", "lower .95"], high_c = implant_hr["implantC", "upper .95"],
                 lr = unname(summary(implant_cox)$logtest["test"]), logrank = implant_logrank$chisq),
            reticulate::py$chk)
```

### Read the output

- **exp(coef):** the hazard ratio of each implant against implant A, the reference. Implant B: 0.82; implant C: 3.07.
- **lower .95 / upper .95:** the 95% CIs. Implant B's (0.45 to 1.50) includes 1, so the data are compatible with no difference from A. Implant C's (1.85 to 5.09) doesn't.
- **Pr(>|z|):** the p-value for each implant against A (p = 0.514 for B, p < 0.001 for C).
- **Likelihood ratio test = 27.6 on 2 df, p < 0.001:** the overall test that implant matters at all, the Cox counterpart of the ANOVA's F test. Python prints it as the second number.
- **Score (logrank) test = 33.5:** the log-rank test for all three implants, which Python prints last. (The Cox score test and the log-rank test handle tied revision times slightly differently, so they agree to one decimal, not exactly.)

### Effect size and 95% CI

The **hazard ratios** with their 95% CIs are the effect sizes: implant C carried about three times the hazard of revision of implant A (3.07, 95% CI 1.85 to 5.09), while implant B didn't differ clearly from A (0.82, 95% CI 0.45 to 1.50).

### How to report it

> **Methods:** Revision-free survival was compared across implants with Cox proportional hazards regression, with implant A as the reference.
>
> **Results:** Implant type was associated with revision (likelihood ratio test, χ² = 27.6, df = 2, p < 0.001). Compared with implant A, the hazard of revision was higher with implant C (hazard ratio 3.07, 95% CI 1.85 to 5.09) and similar with implant B (hazard ratio 0.82, 95% CI 0.45 to 1.50).

::: {.callout-warning}
## ⚠️ Watch out: the reference group shapes the story
Every hazard ratio here is relative to implant A, so the output doesn't compare B with C directly. Choose the reference group on purpose (the standard implant, the largest group) and say which it is. And as on [page 4](04-describe-one-group.qmd#kaplan-meier), deaths here are treated as censored; [page 13](../survival/13-kaplan-meier.qmd) covers competing risks.
:::

::: {.callout-tip}
## 🔀 R vs Python: convergence and the reference group
Both programs use the first group alphabetically (A) as the reference and handle tied revision times with Efron's method. lifelines' default convergence rule stops a little early here (a hazard ratio of 0.81713 for implant B instead of 0.81709), so we tighten it with `fit_options={"precision": 1e-9}`.
:::

## Which groups differ? {#which-groups-differ}

The tests above answer "is there any difference among the groups?". When the answer is yes, the next question is which groups differ from which. Comparing every pair with an ordinary test inflates the chance of a false positive: with four ASA classes there are six pairs, and six tests at p < 0.05 give roughly a one-in-four chance of at least one false alarm even when nothing is going on.

**Post-hoc tests** compare the pairs while keeping that overall error rate at 5%:

| After | Use | Page |
|---|---|---|
| One-way ANOVA | Tukey's HSD (Games-Howell if the spreads differ) | [15](../beyond/15-post-hoc.qmd) |
| Kruskal-Wallis | Dunn's test with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
| Chi-square | Pairwise Fisher or chi-square tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
| Cox regression | Hazard ratios against a chosen reference, or contrasts between groups | [14](../survival/14-cox-regression.qmd) |

Only run post-hoc tests when the overall test is significant, or when you planned specific comparisons before seeing the data; say which in your Methods.

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
age_by_asa <- cohort |> group_by(asa) |> summarise(n = n(), mean = mean(age), sd = sd(age))
satisfied_n <- sum(!is.na(cohort$satisfaction_1yr))
asa_grouped <- table(factor(ifelse(cohort$asa >= 3, "ASA 3-4", "ASA 1-2"), levels = c("ASA 3-4", "ASA 1-2")),
                     factor(cohort$complication_90d, levels = c(1, 0), labels = c("yes", "no")))
sat_quartiles <- satisfied |> group_by(surgeon) |>
  summarise(median = median(satisfaction_1yr), q1 = quantile(satisfaction_1yr, 0.25), q3 = quantile(satisfaction_1yr, 0.75))
stopifnot(
  sum(table(cohort$patient_id) == 2) == 80,
  age_by_asa$n == c(36, 300, 246, 18),
  round(age_by_asa$mean[c(1, 4)], 1) == c(59.8, 73.7), round(age_by_asa$sd[c(1, 4)], 1) == c(8.7, 9.3),
  round(age_by_asa$sd) == c(9, 9, 9, 9),
  age_table[1, "Df"] == 3, round(age_table[1, "Sum Sq"]) == 5727, age_table[2, "Df"] == 596,
  round(age_table[1, "F value"], 1) == 23.9, age_table[1, "Pr(>F)"] < 0.001,
  signif(age_table[1, "Pr(>F)"], 3) == 1.28e-14,
  round(age_omega$Omega2, 2) == 0.10, round(age_omega$CI_low, 2) == 0.06,
  round(unname(welch$statistic), 1) == 23.5, welch$p.value < 0.001,
  satisfied_n == 502, sum(is.na(cohort$satisfaction_1yr)) == 98,
  round(unname(satisfaction_test$statistic), 2) == 0.68, unname(satisfaction_test$parameter) == 2,
  round(satisfaction_test$p.value, 3) == 0.713,
  round(satisfaction_eps$rank_epsilon_squared, 3) == 0.001,
  sat_quartiles$median == c(4, 5, 5), sat_quartiles$q1 == c(4, 4, 4), sat_quartiles$q3 == c(5, 5, 5),
  complication_table[, "yes"] == c(15, 24, 12), rowSums(complication_table) == c(232, 211, 157),
  round(100 * prop.table(complication_table, 1)[, "yes"], 1) == c(6.5, 11.4, 7.6),
  round(min(complication_test$expected), 1) == 13.3,
  round(unname(complication_test$statistic), 2) == 3.62, unname(complication_test$parameter) == 2,
  round(complication_test$p.value, 3) == 0.163,
  round(complication_v$Cramers_v, 2) == 0.08,
  round(effectsize::cramers_v(complication_table)$Cramers_v, 2) == 0.05,
  round(implant_hr[, "exp(coef)"], 2) == c(0.82, 3.07),
  round(implant_hr["implantB", c("lower .95", "upper .95")], 2) == c(0.45, 1.50),
  round(implant_hr["implantC", c("lower .95", "upper .95")], 2) == c(1.85, 5.09),
  round(summary(implant_cox)$coefficients[, "Pr(>|z|)"], 3)[1] == 0.514, round(implant_logrank$chisq, 1) == 33.5,
  round(satisfaction_eps$CI_low, 2) == 0, round(complication_v$CI_low, 2) == 0,
  summary(implant_cox)$coefficients["implantC", "Pr(>|z|)"] < 0.001,
  round(unname(summary(implant_cox)$logtest["test"]), 1) == 27.6, summary(implant_cox)$logtest["pvalue"] < 0.001,
  round(unname(summary(implant_cox)$sctest["test"]), 1) == 33.5,
  round(reticulate::py_eval("float(np.exp(CoxPHFitter().fit(cohort[['followup_years', 'revised', 'implant']], duration_col='followup_years', event_col='revised', formula='implant').params_.iloc[0]))"), 5) == 0.81713,
  round(implant_hr["implantB", "exp(coef)"], 5) == 0.81709,
  choose(4, 2) == 6, round(1 - 0.95^6, 2) == 0.26,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(summary(aov(bmi ~ asa, data = mutate(cohort, asa = factor(asa))))[[1]][1, "F value"], 1) == 31.1,
  round(effectsize::omega_squared(aov(bmi ~ asa, data = mutate(cohort, asa = factor(asa))), partial = FALSE)$Omega2, 2) == 0.13,
  round(tapply(cohort$bmi, cohort$asa, mean)[c(1, 4)], 1) == c(26.3, 36.2),
  round(kruskal.test(los_days ~ surgeon, data = cohort)$p.value, 3) == 0.694,
  round(effectsize::rank_epsilon_squared(los_days ~ surgeon, data = cohort, ci = NULL)$rank_epsilon_squared, 3) == 0.001,
  min(chisq.test(table(cohort$asa, cohort$complication_90d))$expected) < 5,
  round(100 * prop.table(asa_grouped, 1)[, "yes"], 1) == c(11.4, 6.2), round(100 * diff(rev(prop.table(asa_grouped, 1)[, "yes"])), 1) == 5.1,
  round(sort(chisq.test(table(cohort$asa, cohort$complication_90d))$expected[, "1"])[1:2], 1) == c(1.5, 3.1),
  round(unname(fisher.test(asa_grouped)$estimate), 2) == 1.92, round(fisher.test(asa_grouped)$conf.int, 2) == c(1.03, 3.63),
  round(fisher.test(asa_grouped)$p.value, 3) == 0.028,
  round(100 * prop.test(asa_grouped, correct = FALSE)$conf.int, 1) == c(0.5, 9.7)
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Does **BMI** differ across ASA classes? Run a one-way ANOVA and report ω².

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
bmi_data <- cohort |> mutate(asa = factor(asa))
bmi_anova <- aov(bmi ~ asa, data = bmi_data)
summary(bmi_anova)
effectsize::omega_squared(bmi_anova, partial = FALSE)
bmi_data |> group_by(asa) |> summarise(mean = mean(bmi), sd = sd(bmi))
```

## Python

```{python}
bmi_anova = pg.anova(data=cohort, dv="bmi", between="asa", detailed=True)
print(bmi_anova)
ss_b, ss_w, df_b, ms_w = bmi_anova.loc[0, "SS"], bmi_anova.loc[1, "SS"], bmi_anova.loc[0, "DF"], bmi_anova.loc[1, "MS"]
print((ss_b - df_b * ms_w) / (ss_b + ss_w + ms_w))
print(cohort.groupby("asa")["bmi"].agg(["mean", "std"]))
```
:::

BMI rose with ASA class, from a mean of 26.3 kg/m² in ASA 1 to 36.2 kg/m² in ASA 4 (F(3, 596) = 31.1, p < 0.001; ω² = 0.13). That's no surprise: obesity is one of the things anesthesiologists weigh when they assign an ASA class.
:::

**2.** A colleague asks whether **length of stay** differs between the three surgeons. Which test would you use, and what do you find?

::: {.callout-tip collapse="true"}
## Solution
Length of stay is strongly right-skewed with many ties ([page 3](../foundations/03-distributions.qmd#transform)), and there are three independent groups: the **Kruskal-Wallis test**.

::: {.panel-tabset group="language"}
## R

```{r}
kruskal.test(los_days ~ surgeon, data = cohort)
set.seed(2026)
effectsize::rank_epsilon_squared(los_days ~ surgeon, data = cohort)
```

## Python

```{python}
stays = [group["los_days"] for surgeon, group in cohort.groupby("surgeon")]
los_test = stats.kruskal(*stays)
print(los_test, los_test.statistic / (len(cohort) - 1))
```
:::

No difference: p = 0.694, ε² = 0.001.
:::

**3.** Test whether 90-day complications differ across the four **ASA classes**. Check the expected counts first. What do you do, and what do you find?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
# R also warns here: "Chi-squared approximation may be incorrect"
chisq.test(table(cohort$asa, cohort$complication_90d))$expected   # two expected counts are below 5

asa_grouped <- table(
  asa          = factor(ifelse(cohort$asa >= 3, "ASA 3-4", "ASA 1-2"), levels = c("ASA 3-4", "ASA 1-2")),
  complication = factor(cohort$complication_90d, levels = c(1, 0), labels = c("yes", "no"))
)
asa_grouped
fisher.test(asa_grouped)
prop.test(asa_grouped, correct = FALSE)$conf.int   # risk difference, ASA 3-4 minus ASA 1-2
```

## Python

```{python}
from scipy.stats.contingency import odds_ratio
from statsmodels.stats.proportion import confint_proportions_2indep

print(stats.chi2_contingency(pd.crosstab(cohort["asa"], cohort["complication_90d"])).expected_freq)

cohort["asa_group"] = cohort["asa"].map(lambda asa: "ASA 3-4" if asa >= 3 else "ASA 1-2")
asa_grouped = pd.crosstab(cohort["asa_group"], cohort["complication_90d"]).loc[["ASA 3-4", "ASA 1-2"], [1, 0]]
print(asa_grouped)
print(stats.fisher_exact(asa_grouped).pvalue)
print(odds_ratio(asa_grouped.to_numpy(), kind="conditional").confidence_interval())
high_yes, high_no = asa_grouped.loc["ASA 3-4"]
low_yes, low_no = asa_grouped.loc["ASA 1-2"]
print(confint_proportions_2indep(high_yes, high_yes + high_no, low_yes, low_yes + low_no, method="wald", compare="diff"))
```
:::

ASA 1 and ASA 4 each have an expected count of complications below 5 (3.1 and 1.5), so the chi-square test isn't reliable; R says so itself, with the warning "Chi-squared approximation may be incorrect". Combining classes into ASA 1–2 and ASA 3–4 makes clinical sense and gives a 2 × 2 table for Fisher's exact test:

"Complications within 90 days followed 11.4% of procedures in ASA 3–4 patients and 6.2% in ASA 1–2 patients (risk difference 5.1 percentage points, 95% CI 0.5 to 9.7; odds ratio 1.92, 95% CI 1.03 to 3.63; p = 0.028)."

Say in your Methods that you combined the classes, and why.
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/08-three-plus-unmatched.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `142 passed`.

- [ ] **Step 5: Prove the agreement check bites, then restore**

In the `#chi-square` section's hidden R check, change `complication_v <- effectsize::cramers_v(complication_table, adjust = FALSE)` to `complication_v <- effectsize::cramers_v(complication_table)`, which is effectsize's default bias-adjusted V. Then run `quarto render catalog/08-three-plus-unmatched.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'v'`. Undo the change, then run:

```bash
rm -rf catalog/08-three-plus-unmatched_files
quarto render catalog/08-three-plus-unmatched.qmd
uv run pytest tests/site -q
```

Expected: `142 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/08-three-plus-unmatched.qmd _freeze/catalog/08-three-plus-unmatched tests/site/test_catalog.py
git commit -m "Write page 8, three or more unmatched groups: ANOVA, Kruskal-Wallis, chi-square, Cox

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Page 9, Compare three or more matched groups

**Files:**
- Modify: `catalog/09-three-plus-matched.qmd` (replace the stub)
- Create: `_freeze/catalog/09-three-plus-matched/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Task 3's `WRITTEN` and `THREE_GROUP_PAGES`
  - Task 1's rstatix
  - `data/proms_long.csv`, `data/matched_sets.csv`
  - page 7's `#mcnemar` and `#stratified-cox` anchors, and page 8
- Produces: page 9 anchors `#repeated-measures-anova`, `#friedman`, `#cochran-q`, `#stratified-cox` and `#which-groups-differ`.

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
]
```

and append (after two blank lines):

```python
def test_matched_page_warns_that_missed_visits_drop_patients(site):
    soup = load("catalog/09-three-plus-matched.html")
    warnings = [box for box in soup.select("div.callout-warning") if "missed visit" in text_of(box)]
    assert warnings, "no warning about missed visits"
    assert any(a["href"].endswith("beyond/16-mixed-models.html") for a in warnings[0].select("a[href]"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site/test_catalog.py -q`

Expected: 13 of the 15 new page-9 tests FAIL; the no-warnings and short-outputs tests pass trivially on a stub. The 71 earlier tests pass.

- [ ] **Step 3: Write the page**

Replace `catalog/09-three-plus-matched.qmd` with:

````markdown
---
title: "9 · Compare three or more matched groups"
description: "Repeated-measures ANOVA, Friedman test, Cochran's Q and stratified Cox regression: the same patients measured three or more times, or matched sets."
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

The same patients measured **three or more times** (before surgery, then at 6 weeks, 3 months and 1 year), or **matched sets** of three or more patients. This is [page 7](07-two-paired-groups.qmd) extended past two measurements. As on [page 8](08-three-plus-unmatched.qmd), each test asks one question first: **does the outcome differ anywhere among the visits (or groups)?** [Which visits differ?](#which-groups-differ) explains what to do next.

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice data. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

::: {.callout-warning}
## ⚠️ Watch out: these tests drop anyone with a missed visit
Repeated-measures ANOVA, the Friedman test and Cochran's Q need every patient measured at **every** visit. A patient who missed one visit is dropped completely, along with their other measurements. Below, 574 patients had a pre-op VR-12 score, but only 328 had all four, so the analysis loses 246 patients (43%). If the patients who miss visits differ from those who don't, the result is biased. [Mixed models](../beyond/16-mixed-models.qmd) use everyone's available data, and are usually the better choice for repeated PROMs.
:::

## Repeated-measures ANOVA {#repeated-measures-anova}

**The question:** Does patients' physical health (the VR-12 physical component score, PCS) change over the first year after surgery?

### When to use it

- A **measurement** taken **three or more times** on the same patients (or once on each member of a matched set).
- The changes between visits are roughly normal, or there are plenty of patients.
- **Sphericity:** the spread of the changes is similar for every pair of visits. Mauchly's test checks it; if it fails, the **Greenhouse-Geisser** correction adjusts the degrees of freedom. Both programs below report both.
- Only patients measured at **every** visit are included (see the warning above).
- If the outcome is skewed, bounded or ordinal → the [Friedman test](#friedman).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

pcs <- proms |>
  select(case_id, visit, vr12_pcs) |>
  group_by(case_id) |>
  filter(all(!is.na(vr12_pcs))) |>     # keep patients measured at all four visits
  ungroup() |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))   # in time order

n_distinct(pcs$case_id)                # patients with complete data

ggplot(pcs, aes(visit, vr12_pcs)) +
  geom_boxplot() +
  labs(x = "Visit", y = "VR-12 physical component score")

pcs |>
  group_by(visit) |>
  summarise(mean = mean(vr12_pcs), sd = sd(vr12_pcs))
```

## Python

```{python}
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt

proms = pd.read_csv("data/proms_long.csv")
visits = ["preop", "6wk", "3mo", "1yr"]   # in time order

pcs = proms[["case_id", "visit", "vr12_pcs"]]
complete = pcs.groupby("case_id")["vr12_pcs"].transform(lambda scores: scores.notna().all())
pcs = pcs[complete]                        # keep patients measured at all four visits

print(pcs["case_id"].nunique())            # patients with complete data

fig, ax = plt.subplots(figsize=(6, 3))
parts = ax.boxplot([pcs.loc[pcs["visit"] == v, "vr12_pcs"] for v in visits], tick_labels=visits)   # naming the result keeps it out of the output
ax.set_xlabel("Visit")
ax.set_ylabel("VR-12 physical component score")
plt.show()

print(pcs.groupby("visit")["vr12_pcs"].agg(["mean", "std"]).loc[visits])
```
:::

328 patients were measured at all four visits. Their mean PCS climbs at every visit, and the spreads stay similar.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
pcs_anova <- rstatix::anova_test(data = pcs, dv = vr12_pcs, wid = case_id, within = visit,
                                 effect.size = c("pes", "ges"))   # partial and generalized eta squared
pcs_anova
```

## Python

```{python}
pcs_anova = pg.rm_anova(data=pcs, dv="vr12_pcs", within="visit", subject="case_id",
                        correction=True, effsize="np2", detailed=True)   # np2 = partial eta squared
print(pcs_anova.T)    # .T turns the wide table on its side, so it fits
```
:::

```{python}
#| include: false
row = pcs_anova.iloc[0]
chk = {"f": float(row["F"]), "df_effect": float(row["DF"]), "df_error": float(pcs_anova.iloc[1]["DF"]),
       "pes": float(row["np2"]), "gg_eps": float(row["eps"]), "mauchly_w": float(row["W_spher"]),
       "mauchly_p": float(row["p_spher"])}
```

```{r}
#| include: false
pcs_aov <- summary(aov(vr12_pcs ~ visit + Error(case_id / visit), data = pcs))[["Error: case_id:visit"]][[1]]
pcs_pes <- effectsize::eta_squared(aov(vr12_pcs ~ visit + Error(case_id / visit), data = pcs),
                                   partial = TRUE, verbose = FALSE)
check_agree(list(f = pcs_aov["visit", "F value"], df_effect = pcs_aov["visit", "Df"],
                 df_error = pcs_aov["Residuals", "Df"], pes = pcs_pes$Eta2_partial), reticulate::py$chk[c("f", "df_effect", "df_error", "pes")])
check_agree(list(gg_eps = pcs_anova$`Sphericity Corrections`$GGe, mauchly_w = pcs_anova$`Mauchly's Test for Sphericity`$W,
                 mauchly_p = pcs_anova$`Mauchly's Test for Sphericity`$p),
            reticulate::py$chk[c("gg_eps", "mauchly_w", "mauchly_p")],
            tol = 1e-3)   # rstatix rounds these to 3 decimals before storing them
```

### Read the output

- **F = 317.1, with 3 and 981 degrees of freedom** (DFn/DFd in R, DF in Python): how much the visit means differ, compared with how much each patient's scores bounce around their own average. 3 = four visits minus one; 981 = 3 × (328 patients − 1).
- **p** (R prints `7.07e-144`; pingouin's table rounds it to `0.0` in the `p_unc` row): far below 0.001.
- **Mauchly's test, W = 0.982, p = 0.324:** no evidence that sphericity is violated, so the uncorrected result stands.
- **Sphericity corrections** (R) or **eps** and **p_GG_corr** (Python): the Greenhouse-Geisser epsilon is 0.988 (1 means perfect sphericity), and the corrected p-value is still far below 0.001.
- **pes = 0.492** (R) or **np2** (Python): partial eta squared, below.

### Effect size and 95% CI

**Partial eta squared (η²~p~)** is the share of the within-patient variation that the visits account for. As a rough guide, 0.01 is small, 0.06 medium and 0.14 large. **Generalized eta squared** (ges = 0.412 in R) also counts the differences *between* patients, which makes it comparable with designs that aren't repeated measures; report it when readers will compare studies of different designs.

::: {.panel-tabset group="language"}
## R

```{r}
pcs_model <- aov(vr12_pcs ~ visit + Error(case_id / visit), data = pcs)   # the same ANOVA in base R
effectsize::eta_squared(pcs_model, partial = TRUE)                         # with a 95% CI
```

## Python

```{python}
print(pcs_anova.loc[0, "np2"])    # pingouin doesn't compute a CI for it
```
:::

η²~p~ = 0.49: a very large effect. The visits account for about half of the variation in each patient's scores over the year.

### How to report it

> **Methods:** VR-12 PCS across the four visits was compared with one-way repeated-measures ANOVA in patients with all four measurements. Sphericity was assessed with Mauchly's test, with the Greenhouse-Geisser correction planned if it was violated. Partial eta squared (η²~p~) is reported as the effect size.
>
> **Results:** Of 574 patients with a pre-op PCS, 328 had all four measurements. Their mean PCS rose from 31.2 (SD 6.1) before surgery to 34.9 (SD 6.2) at 6 weeks, 41.0 (SD 6.2) at 3 months and 44.9 (SD 6.8) at 1 year (F(3, 981) = 317.1, p < 0.001; η²~p~ = 0.49, one-sided 95% CI 0.46 to 1.00). Sphericity was not violated (Mauchly's p = 0.324).

::: {.callout-warning}
## ⚠️ Watch out: a significant F doesn't say which visits differ
The ANOVA says PCS changed somewhere over the year. To say *when*, compare the visits with paired tests and a correction for multiple comparisons ([page 15](../beyond/15-post-hoc.qmd)). And remember who's missing: the 246 patients without complete data may have recovered differently.
:::

::: {.callout-tip}
## 🔀 R vs Python: which tools check sphericity
- **R:** base `aov(... + Error(case_id / visit))` gives the same F test but ignores sphericity; `rstatix::anova_test()` adds Mauchly's test and the corrections. rstatix rounds its numbers to 3 decimals.
- **Python:** pingouin's `rm_anova(correction=True)` reports Mauchly's test and the Greenhouse-Geisser correction. statsmodels' `AnovaRM` gives the F test only.
- **Effect sizes:** pingouin returns either partial (`effsize="np2"`) or generalized (`effsize="ng2"`) eta squared; rstatix returns both if asked.
:::

## Friedman test {#friedman}

**The question:** After knee replacement, does KOOS JR keep changing between 6 weeks, 3 months and 1 year?

### When to use it

- An outcome measured **three or more times** on the same patients, when it's **skewed**, **ordinal** or has a **ceiling or floor**. The 1-year KOOS JR has a ceiling ([page 3](../foundations/03-distributions.qmd#transform)).
- It ranks each patient's own scores (1st, 2nd, 3rd) and asks whether some visits tend to rank higher than others.
- Only patients measured at **every** visit are included.
- If the outcome is a roughly normal measurement → [repeated-measures ANOVA](#repeated-measures-anova).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

koos <- proms |>
  filter(instrument == "KOOS JR", visit %in% c("6wk", "3mo", "1yr")) |>
  select(case_id, visit, prom_score) |>
  group_by(case_id) |>
  filter(all(!is.na(prom_score))) |>     # keep patients measured at all three visits
  ungroup() |>
  mutate(visit = factor(visit, levels = c("6wk", "3mo", "1yr")))

n_distinct(koos$case_id)

ggplot(koos, aes(visit, prom_score)) +
  geom_boxplot() +
  labs(x = "Visit", y = "KOOS JR")

koos |>
  group_by(visit) |>
  summarise(median = median(prom_score), q1 = quantile(prom_score, 0.25), q3 = quantile(prom_score, 0.75))
```

## Python

```{python}
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt

proms = pd.read_csv("data/proms_long.csv")
visits = ["6wk", "3mo", "1yr"]

koos = proms[(proms["instrument"] == "KOOS JR") & proms["visit"].isin(visits)][["case_id", "visit", "prom_score"]]
complete = koos.groupby("case_id")["prom_score"].transform(lambda scores: scores.notna().all())
koos = koos[complete]                     # keep patients measured at all three visits

print(koos["case_id"].nunique())

fig, ax = plt.subplots(figsize=(6, 3))
parts = ax.boxplot([koos.loc[koos["visit"] == v, "prom_score"] for v in visits], tick_labels=visits)
ax.set_xlabel("Visit")
ax.set_ylabel("KOOS JR")
plt.show()

print(koos.groupby("visit")["prom_score"].describe()[["25%", "50%", "75%"]].loc[visits])
```
:::

205 TKA patients were measured at all three visits. Scores rise at each visit, and by 1 year they're crowding the ceiling of 100.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
koos_test <- friedman.test(prom_score ~ visit | case_id, data = koos)   # outcome ~ visit | patient
koos_test
```

## Python

```{python}
koos_test = pg.friedman(data=koos, dv="prom_score", within="visit", subject="case_id")
print(koos_test)
```
:::

```{python}
#| include: false
chk = {"chisq": float(koos_test["Q"].iloc[0]), "df": float(koos_test["ddof1"].iloc[0])}
```

```{r}
#| include: false
check_agree(list(chisq = unname(koos_test$statistic), df = unname(koos_test$parameter)), reticulate::py$chk)
```

### Read the output

- **Friedman chi-squared = 253.6** (R) or **Q** (Python): how consistently the visits rank in the same order across patients.
- **df = 2:** three visits minus one.
- **p < 0.001** (R prints "p < 2.2e-16").
- **W = 0.618** (Python): Kendall's W, below.

### Effect size and 95% CI

**Kendall's W** measures how consistently patients' scores rank the visits in the same order: 0 means no agreement at all, 1 means every patient's scores rank the three visits identically. As a rough guide, 0.1 is small, 0.3 moderate and 0.5 large.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
# kendalls_w() warns when a patient has the same score at two visits; the tie correction already handles that
set.seed(2026)   # its CI comes from a bootstrap (random resampling); a seed makes it repeatable
effectsize::kendalls_w(prom_score ~ visit | case_id, data = koos)
```

## Python

```{python}
print(koos_test["W"])
```
:::

```{python}
#| include: false
chk = {"w": float(koos_test["W"].iloc[0])}
```

```{r}
#| include: false
set.seed(2026)
koos_w <- suppressWarnings(effectsize::kendalls_w(prom_score ~ visit | case_id, data = koos))
check_agree(list(w = koos_w$Kendalls_W), reticulate::py$chk)
```

W = 0.62: a large effect. Most patients improved from each visit to the next. R's CI comes from a bootstrap, which is why the code sets a seed; pingouin doesn't compute one.

### How to report it

> **Methods:** Because KOOS JR scores showed a ceiling effect, scores at 6 weeks, 3 months and 1 year were compared with the Friedman test in patients with all three measurements, with Kendall's W as the effect size.
>
> **Results:** Among 205 patients with all three measurements, median KOOS JR rose from 62.6 (IQR 53.9 to 70.3) at 6 weeks to 73.1 (IQR 65.7 to 81.5) at 3 months and 85.7 (IQR 73.6 to 94.0) at 1 year (Friedman χ² = 253.6, df = 2, p < 0.001; Kendall's W = 0.62, one-sided 95% CI 0.55 to 1.00).

::: {.callout-warning}
## ⚠️ Watch out: the Friedman test ignores how big the changes are
It only uses each patient's ranking of the visits. A patient who gained 1 point and one who gained 30 count the same. Report the medians (or the changes) so readers can see the size of the improvement, and judge it against the MCID ([page 3](../foundations/03-distributions.qmd#effect-sizes)).
:::

::: {.callout-tip}
## 🔀 R vs Python: data formats
R's `friedman.test()` takes a formula, `outcome ~ visit | patient`, on long data. pingouin's `friedman()` also takes long data; scipy's `friedmanchisquare()` instead wants one column per visit in wide data. All three correct for tied scores within a patient, so they agree.
:::

## Cochran's Q test {#cochran-q}

**The question:** Does walking-aid use change over the first year after surgery?

### When to use it

- A **yes/no** outcome measured **three or more times** on the same patients (or once on each member of a matched set).
- It extends [McNemar's test](07-two-paired-groups.qmd#mcnemar) to more than two visits, and, like McNemar's, it only learns from patients whose answer changed.
- Only patients measured at **every** visit are included.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

aid <- proms |>
  select(case_id, visit, walking_aid) |>
  group_by(case_id) |>
  filter(all(!is.na(walking_aid))) |>    # keep patients measured at all four visits
  ungroup() |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))

aid |>
  group_by(visit) |>
  summarise(patients = n(), using_aid = sum(walking_aid), percent = 100 * mean(walking_aid))
```

## Python

```{python}
import pandas as pd
import pingouin as pg
from scipy import stats

proms = pd.read_csv("data/proms_long.csv")
visits = ["preop", "6wk", "3mo", "1yr"]

aid = proms[["case_id", "visit", "walking_aid"]]
complete = aid.groupby("case_id")["walking_aid"].transform(lambda answers: answers.notna().all())
aid = aid[complete]                     # keep patients measured at all four visits

print(aid.groupby("visit")["walking_aid"].agg(["count", "sum", "mean"]).loc[visits])
```
:::

328 patients answered at all four visits. A third used a walking aid before surgery, more than half at 6 weeks, and one in ten at 1 year.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
aid_test <- DescTools::CochranQTest(walking_aid ~ visit | case_id, data = aid)   # outcome ~ visit | patient
aid_test
```

## Python

```{python}
aid_test = pg.cochran(data=aid, dv="walking_aid", within="visit", subject="case_id")
print(aid_test)
```
:::

```{python}
#| include: false
chk = {"q": float(aid_test["Q"].iloc[0]), "df": float(aid_test["dof"].iloc[0])}
```

```{r}
#| include: false
check_agree(list(q = unname(aid_test$statistic), df = unname(aid_test$parameter)), reticulate::py$chk)
```

### Read the output

- **Q = 186.8, df = 3:** Cochran's Q statistic, with four visits minus one degrees of freedom.
- **p < 0.001** (R prints "p < 2.2e-16"): walking-aid use this different across visits would be very unlikely if it hadn't changed.

### Effect size and 95% CI

Cochran's Q has no standard single effect size. Describe the **proportion at each visit**, with its 95% CI (the Wilson interval from [page 4](04-describe-one-group.qmd#proportion)), and the changes between visits in percentage points.

::: {.panel-tabset group="language"}
## R

```{r}
aid_by_visit <- aid |> group_by(visit) |> summarise(using = sum(walking_aid), patients = n())
aid_ci <- sapply(aid_by_visit$using, function(k) prop.test(k, 328, correct = FALSE)$conf.int)

aid_by_visit |>
  mutate(percent = 100 * using / patients, ci_low = 100 * aid_ci[1, ], ci_high = 100 * aid_ci[2, ])
```

## Python

```{python}
counts = aid.groupby("visit")["walking_aid"].agg(["sum", "count"]).loc[visits]
cis = [stats.binomtest(int(k), int(n)).proportion_ci(method="wilson") for k, n in zip(counts["sum"], counts["count"])]

print(pd.DataFrame({"percent": 100 * counts["sum"] / counts["count"],
                    "ci_low": [100 * ci.low for ci in cis], "ci_high": [100 * ci.high for ci in cis]}))
```
:::

```{python}
#| include: false
chk = {f"low_{v}": float(ci.low) for v, ci in zip(visits, cis)} | {f"high_{v}": float(ci.high) for v, ci in zip(visits, cis)}
```

```{r}
#| include: false
visit_names <- as.character(aid_by_visit$visit)
check_agree(c(setNames(as.list(aid_ci[1, ]), paste0("low_", visit_names)),
              setNames(as.list(aid_ci[2, ]), paste0("high_", visit_names))), reticulate::py$chk)
```

Use rose by 24.4 percentage points from pre-op to 6 weeks, then fell well below its pre-op level by 1 year (24.4 points lower).

### How to report it

> **Methods:** Walking-aid use at the four visits was compared with Cochran's Q test in patients assessed at all four. Proportions are reported with Wilson 95% CIs.
>
> **Results:** Among 328 patients assessed at all four visits, walking-aid use rose from 34.8% (95% CI 29.8% to 40.1%) before surgery to 59.1% (95% CI 53.8% to 64.3%) at 6 weeks, then fell to 24.4% (95% CI 20.1% to 29.3%) at 3 months and 10.4% (95% CI 7.5% to 14.1%) at 1 year (Cochran's Q = 186.8, df = 3, p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: Q doesn't tell you the direction
Use went **up** and then **down**. Cochran's Q only says it wasn't the same at every visit. To say which changes are real, compare pairs of visits with McNemar's test and a correction for multiple comparisons ([page 15](../beyond/15-post-hoc.qmd)).
:::

::: {.callout-tip}
## 🔀 R vs Python: where to find Cochran's Q
Base R doesn't have Cochran's Q; `DescTools::CochranQTest()` (or `rstatix::cochran_qtest()`) does. In Python, pingouin's `cochran()` takes long data; statsmodels' `cochrans_q()` takes a wide array with one column per visit. All give the same Q.
:::

## Stratified Cox regression {#stratified-cox}

**The question:** In sets of three patients matched on procedure, age, sex, BMI and ASA class, does the risk of revision differ between implants A, B and C?

### When to use it

- The outcome is **time until an event**, and the patients come in **matched sets** of three or more.
- A Cox model **stratified** by matched set compares the implants only **within** sets, as on [page 7](07-two-paired-groups.qmd#stratified-cox), which used just the A and C patients from the same sets.
- With few events, expect wide CIs. [Page 14](../survival/14-cox-regression.qmd) covers Cox regression in full.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)

matched <- read_csv("data/matched_sets.csv", show_col_types = FALSE) |>
  mutate(revised = as.integer(event_status == 1))   # 1 = revised; deaths and censoring = 0

matched |> select(set_id, implant, age, sex, bmi, followup_years, revised) |> head(6)
matched |> group_by(implant) |> summarise(patients = n(), revisions = sum(revised))
```

## Python

```{python}
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

matched = pd.read_csv("data/matched_sets.csv")
matched["revised"] = (matched["event_status"] == 1).astype(int)   # 1 = revised; deaths and censoring = 0

print(matched[["set_id", "implant", "age", "sex", "bmi", "followup_years", "revised"]].head(6))
print(matched.groupby("implant")["revised"].agg(["count", "sum"]))
```
:::

52 matched sets of three: 5 revisions with implant A, 2 with B and 17 with C.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
set_cox <- coxph(Surv(followup_years, revised) ~ implant + strata(set_id), data = matched)
summary(set_cox)
```

## Python

```{python}
set_cox = CoxPHFitter().fit(
    matched[["followup_years", "revised", "implant", "set_id"]],
    duration_col="followup_years", event_col="revised",
    formula="implant", strata=["set_id"],    # one stratum per matched set
)
print(set_cox.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]])
print(set_cox.log_likelihood_ratio_test().test_statistic)   # overall test, all implants
```
:::

```{python}
#| include: false
rows = set_cox.summary
chk = {"hr_b": float(rows.loc["implant[T.B]", "exp(coef)"]), "hr_c": float(rows.loc["implant[T.C]", "exp(coef)"]),
       "low_c": float(rows.loc["implant[T.C]", "exp(coef) lower 95%"]),
       "high_c": float(rows.loc["implant[T.C]", "exp(coef) upper 95%"]),
       "lr": float(set_cox.log_likelihood_ratio_test().test_statistic)}
```

```{r}
#| include: false
set_hr <- summary(set_cox)$conf.int
check_agree(list(hr_b = set_hr["implantB", "exp(coef)"], hr_c = set_hr["implantC", "exp(coef)"],
                 low_c = set_hr["implantC", "lower .95"], high_c = set_hr["implantC", "upper .95"],
                 lr = unname(summary(set_cox)$logtest["test"])), reticulate::py$chk)
```

### Read the output

- **n = 156, number of events = 24:** 52 sets of three patients, 24 revisions.
- **exp(coef):** the hazard ratio of each implant against implant A, within matched sets. Implant B: 0.43; implant C: 3.91.
- **lower .95 / upper .95:** implant B's CI (0.08 to 2.25) is very wide and includes 1; implant C's (1.28 to 11.95) doesn't.
- **Likelihood ratio test = 13.5 on 2 df, p = 0.001:** the overall test that implant matters at all. Python prints it last.

### Effect size and 95% CI

The **hazard ratios** with their 95% CIs: within matched sets, implant C carried about four times the hazard of revision of implant A (3.91, 95% CI 1.28 to 11.95). The estimate for implant B (0.43, 95% CI 0.08 to 2.25) is too imprecise to interpret.

### How to report it

> **Methods:** Revision risk was compared between implants in matched sets using Cox regression stratified by set, with implant A as the reference.
>
> **Results:** In 52 sets of three patients matched on procedure, age, sex, BMI and ASA class, implant type was associated with revision (likelihood ratio test, χ² = 13.5, df = 2, p = 0.001). Compared with implant A, the hazard of revision was higher with implant C (hazard ratio 3.91, 95% CI 1.28 to 11.95); the estimate for implant B was imprecise (hazard ratio 0.43, 95% CI 0.08 to 2.25).

::: {.callout-warning}
## ⚠️ Watch out: only 24 events
A Cox model needs events, not just patients. With 24 revisions across three implants, the CIs are wide and the model can't support adjustment for anything else. [Page 14](../survival/14-cox-regression.qmd) covers how many events a model needs.
:::

::: {.callout-tip}
## 🔀 R vs Python: strata and convergence
As on [page 7](07-two-paired-groups.qmd#stratified-cox), R puts `strata(set_id)` in the formula while lifelines takes `strata=["set_id"]`. Here lifelines' default convergence matches R exactly; with page 7's pairs it stopped a little early and needed `fit_options={"precision": 1e-9}`. If the two programs disagree in the fourth decimal, tighten it.
:::

## Which visits differ? {#which-groups-differ}

Each test above answers "is there any difference among the visits (or implants)?". When the answer is yes, the next question is which pairs differ. Comparing every pair with an ordinary paired test inflates the chance of a false positive: four visits make six pairs.

| After | Use | Page |
|---|---|---|
| Repeated-measures ANOVA | Paired t tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
| Friedman | Pairwise Wilcoxon signed-rank (or Conover) tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
| Cochran's Q | Pairwise McNemar tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
| Stratified Cox | Hazard ratios against a chosen reference | [14](../survival/14-cox-regression.qmd) |

For repeated PROMs, a [mixed model](../beyond/16-mixed-models.qmd) answers both questions at once (does the score change, and at which visits?) while keeping patients who missed a visit.

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
pcs_by_visit <- pcs |> group_by(visit) |> summarise(mean = mean(vr12_pcs), sd = sd(vr12_pcs))
koos_quartiles <- koos |> group_by(visit) |>
  summarise(median = median(prom_score), q1 = quantile(prom_score, 0.25), q3 = quantile(prom_score, 0.75))
aid_percent <- 100 * aid_by_visit$using / aid_by_visit$patients
complete_cases <- function(data, value, visits) {   # long data, patients measured at every one of these visits
  data |> filter(visit %in% visits) |> select(case_id, visit, value = all_of(value)) |> group_by(case_id) |>
    filter(all(!is.na(value))) |> ungroup() |> mutate(visit = factor(visit, levels = visits)) |> rename(!!value := value)
}
ex_mcs <- complete_cases(proms, "vr12_mcs", c("preop", "6wk", "3mo", "1yr"))
ex_mcs_model <- aov(vr12_mcs ~ visit + Error(case_id / visit), data = ex_mcs)
ex_mcs_aov <- summary(ex_mcs_model)[["Error: case_id:visit"]][[1]]
ex_mcs_pes <- effectsize::eta_squared(ex_mcs_model, partial = TRUE, verbose = FALSE)$Eta2_partial
ex_mcs_rstatix <- rstatix::anova_test(data = ex_mcs, dv = vr12_mcs, wid = case_id, within = visit)
ex_hoos <- complete_cases(filter(proms, instrument == "HOOS JR"), "prom_score", c("6wk", "3mo", "1yr"))
ex_after <- complete_cases(proms, "walking_aid", c("6wk", "3mo", "1yr"))
stopifnot(
  sum(table(distinct(proms, case_id, patient_id)$patient_id) == 2) == 80,
  sum(proms$visit == "preop" & !is.na(proms$vr12_pcs)) == 574, n_distinct(pcs$case_id) == 328,
  574 - 328 == 246, round(100 * 246 / 574) == 43,
  round(pcs_by_visit$mean, 1) == c(31.2, 34.9, 41.0, 44.9), round(pcs_by_visit$sd, 1) == c(6.1, 6.2, 6.2, 6.8),
  round(pcs_aov["visit", "F value"], 1) == 317.1, pcs_aov["visit", "Df"] == 3, pcs_aov["Residuals", "Df"] == 981,
  3 * (328 - 1) == 981, pcs_anova$ANOVA$p == 7.07e-144,
  pcs_anova$`Mauchly's Test for Sphericity`$W == 0.982, pcs_anova$`Mauchly's Test for Sphericity`$p == 0.324,
  pcs_anova$`Sphericity Corrections`$GGe == 0.988, pcs_anova$`Sphericity Corrections`$`p[GG]` < 0.001,
  pcs_anova$ANOVA$pes == 0.492, pcs_anova$ANOVA$ges == 0.412,
  round(pcs_pes$Eta2_partial, 2) == 0.49, round(pcs_pes$CI_low, 2) == 0.46,
  n_distinct(koos$case_id) == 205,
  round(koos_quartiles$median, 1) == c(62.6, 73.1, 85.7),
  round(koos_quartiles$q1, 1) == c(53.9, 65.7, 73.6), round(koos_quartiles$q3, 1) == c(70.3, 81.5, 94.0),
  round(unname(koos_test$statistic), 1) == 253.6, unname(koos_test$parameter) == 2, koos_test$p.value < 0.001,
  round(koos_w$Kendalls_W, 3) == 0.618, round(koos_w$Kendalls_W, 2) == 0.62, round(koos_w$CI_low, 2) == 0.55,
  n_distinct(aid$case_id) == 328, aid_by_visit$patients == c(328, 328, 328, 328),
  round(aid_percent, 1) == c(34.8, 59.1, 24.4, 10.4),
  round(100 * aid_ci[1, ], 1) == c(29.8, 53.8, 20.1, 7.5), round(100 * aid_ci[2, ], 1) == c(40.1, 64.3, 29.3, 14.1),
  round(aid_percent[2] - aid_percent[1], 1) == 24.4, round(aid_percent[1] - aid_percent[4], 1) == 24.4,
  round(unname(aid_test$statistic), 1) == 186.8, unname(aid_test$parameter) == 3, aid_test$p.value < 0.001,
  nrow(matched) == 156, n_distinct(matched$set_id) == 52, sum(matched$revised) == 24,
  tapply(matched$revised, matched$implant, sum) == c(5, 2, 17),
  round(set_hr[, "exp(coef)"], 2) == c(0.43, 3.91),
  round(set_hr["implantB", c("lower .95", "upper .95")], 2) == c(0.08, 2.25),
  round(set_hr["implantC", c("lower .95", "upper .95")], 2) == c(1.28, 11.95),
  round(unname(summary(set_cox)$logtest["test"]), 1) == 13.5, round(summary(set_cox)$logtest["pvalue"], 3) == 0.001,
  choose(4, 2) == 6,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(ex_mcs_aov["visit", "F value"], 2) == 9.33, ex_mcs_aov["visit", "Df"] == 3, ex_mcs_aov["Residuals", "Df"] == 981,
  ex_mcs_aov["visit", "Pr(>F)"] < 0.001, round(ex_mcs_pes, 3) == 0.028,
  round(tapply(ex_mcs$vr12_mcs, ex_mcs$visit, mean)[c("preop", "1yr")], 1) == c(49.7, 53.3),
  ex_mcs_rstatix$`Mauchly's Test for Sphericity`$p == 0.814,
  n_distinct(ex_hoos$case_id) == 140, round(tapply(ex_hoos$prom_score, ex_hoos$visit, median), 1) == c(68.2, 79.8, 89.2),
  round(unname(friedman.test(prom_score ~ visit | case_id, data = ex_hoos)$statistic), 1) == 159.7,
  round(suppressWarnings(effectsize::kendalls_w(prom_score ~ visit | case_id, data = ex_hoos, ci = NULL))$Kendalls_W, 2) == 0.57,
  n_distinct(ex_after$case_id) == 345, tapply(ex_after$walking_aid, ex_after$visit, sum) == c(203, 87, 37),
  round(100 * tapply(ex_after$walking_aid, ex_after$visit, mean), 1) == c(58.8, 25.2, 10.7),
  round(100 * sapply(c(203, 87, 37), function(k) prop.test(k, 345, correct = FALSE)$conf.int), 1) == c(53.6, 63.9, 20.9, 30.1, 7.9, 14.4),
  round(unname(DescTools::CochranQTest(walking_aid ~ visit | case_id, data = ex_after)$statistic), 1) == 185.9
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Repeat the repeated-measures ANOVA for the VR-12 **mental** component score (`vr12_mcs`) across the four visits.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
mcs <- proms |>
  select(case_id, visit, vr12_mcs) |>
  group_by(case_id) |>
  filter(all(!is.na(vr12_mcs))) |>
  ungroup() |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))

rstatix::anova_test(data = mcs, dv = vr12_mcs, wid = case_id, within = visit, effect.size = "pes")
mcs |> group_by(visit) |> summarise(mean = mean(vr12_mcs), sd = sd(vr12_mcs))
```

## Python

```{python}
mcs = proms[["case_id", "visit", "vr12_mcs"]]
mcs = mcs[mcs.groupby("case_id")["vr12_mcs"].transform(lambda scores: scores.notna().all())]
print(pg.rm_anova(data=mcs, dv="vr12_mcs", within="visit", subject="case_id", correction=True, effsize="np2").T)
print(mcs.groupby("visit")["vr12_mcs"].agg(["mean", "std"]).loc[["preop", "6wk", "3mo", "1yr"]])
```
:::

The mental component also changed (F(3, 981) = 9.33, p < 0.001), but far less: from a mean of 49.7 before surgery to 53.3 at 1 year, with η²~p~ = 0.028, a small effect. Sphericity held (Mauchly's p = 0.814).
:::

**2.** A colleague wants to know whether **HOOS JR** (hip patients) keeps changing between 6 weeks, 3 months and 1 year. Which test would you use, and what do you find?

::: {.callout-tip collapse="true"}
## Solution
HOOS JR, like KOOS JR, has a ceiling at 1 year, and the same patients are measured three times: the **Friedman test**.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
hoos <- proms |>
  filter(instrument == "HOOS JR", visit %in% c("6wk", "3mo", "1yr")) |>
  select(case_id, visit, prom_score) |>
  group_by(case_id) |>
  filter(all(!is.na(prom_score))) |>
  ungroup() |>
  mutate(visit = factor(visit, levels = c("6wk", "3mo", "1yr")))

friedman.test(prom_score ~ visit | case_id, data = hoos)
set.seed(2026)
effectsize::kendalls_w(prom_score ~ visit | case_id, data = hoos)
hoos |> group_by(visit) |> summarise(median = median(prom_score))
```

## Python

```{python}
hoos = proms[(proms["instrument"] == "HOOS JR") & proms["visit"].isin(["6wk", "3mo", "1yr"])][["case_id", "visit", "prom_score"]]
hoos = hoos[hoos.groupby("case_id")["prom_score"].transform(lambda scores: scores.notna().all())]
print(pg.friedman(data=hoos, dv="prom_score", within="visit", subject="case_id"))
print(hoos.groupby("visit")["prom_score"].median())
```
:::

Among 140 hip patients with all three scores, median HOOS JR rose from 68.2 at 6 weeks to 79.8 at 3 months and 89.2 at 1 year (Friedman χ² = 159.7, df = 2, p < 0.001; Kendall's W = 0.57).
:::

**3.** Leaving out the pre-op visit, does walking-aid use change between 6 weeks, 3 months and 1 year? Run the test and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
after_surgery <- proms |>
  filter(visit %in% c("6wk", "3mo", "1yr")) |>
  select(case_id, visit, walking_aid) |>
  group_by(case_id) |>
  filter(all(!is.na(walking_aid))) |>
  ungroup() |>
  mutate(visit = factor(visit, levels = c("6wk", "3mo", "1yr")))

DescTools::CochranQTest(walking_aid ~ visit | case_id, data = after_surgery)
after_counts <- after_surgery |> group_by(visit) |> summarise(using = sum(walking_aid), patients = n())
after_counts
sapply(after_counts$using, function(k) prop.test(k, after_counts$patients[1], correct = FALSE)$conf.int)
```

## Python

```{python}
after = proms[proms["visit"].isin(["6wk", "3mo", "1yr"])][["case_id", "visit", "walking_aid"]]
after = after[after.groupby("case_id")["walking_aid"].transform(lambda answers: answers.notna().all())]
print(pg.cochran(data=after, dv="walking_aid", within="visit", subject="case_id"))
counts = after.groupby("visit")["walking_aid"].agg(["sum", "count"]).loc[["6wk", "3mo", "1yr"]]
print(counts)
print([stats.binomtest(int(k), int(n)).proportion_ci(method="wilson") for k, n in zip(counts["sum"], counts["count"])])
```
:::

"Among 345 patients assessed at all three post-operative visits, walking-aid use fell from 58.8% (95% CI 53.6% to 63.9%) at 6 weeks to 25.2% (95% CI 20.9% to 30.1%) at 3 months and 10.7% (95% CI 7.9% to 14.4%) at 1 year (Cochran's Q = 185.9, df = 2, p < 0.001)."

More patients are included here (345 vs 328) because patients who missed only the pre-op visit now count.
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/09-three-plus-matched.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `157 passed`.

- [ ] **Step 5: Prove the prose guard bites, then restore**

In the page's `# Prose guard` chunk, change `round(unname(aid_test$statistic), 1) == 186.8` to `== 186.9`, then run `quarto render catalog/09-three-plus-matched.qmd`.

Expected: the render FAILS with `round(unname(aid_test$statistic), 1) == 186.9 is not TRUE`. Undo the change, then run:

```bash
rm -rf catalog/09-three-plus-matched_files
quarto render catalog/09-three-plus-matched.qmd
uv run pytest tests/site -q
```

Expected: `157 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/09-three-plus-matched.qmd _freeze/catalog/09-three-plus-matched tests/site/test_catalog.py
git commit -m "Write page 9, three or more matched groups: repeated-measures ANOVA, Friedman, Cochran's Q, stratified Cox

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Record the conventions and run everything

**Files:**
- Modify: `CLAUDE.md`, `tests/python/test_repo_docs.py`

- [ ] **Step 1: Write the failing test**

In `tests/python/test_repo_docs.py`, replace

```python
                 'a ceiling of "p > 0.999"']:
```

with

```python
                 'a ceiling of "p > 0.999"', "Bootstrap CIs are seeded"]:
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `test_claude_md_states_the_golden_rules` FAILS on `Bootstrap CIs are seeded`.

- [ ] **Step 2: Update CLAUDE.md**

In `CLAUDE.md`'s golden rule 13, replace

```markdown
A section's first tabset loads its own packages and data, because readers jump straight to it from the decision table.
```

with

```markdown
A section's first tabset loads its own packages and data, and every name its Python uses is defined within the section, because readers jump straight to it from the decision table and copy only that section.
```

and after golden rule 14 add rule 15. Replace

```markdown
14. **Python survival uses lifelines on pandas 3.** lifelines declares `pandas<3`, but the pages are written for pandas 3 (page 1's tidying breaks on pandas 2), so `pyproject.toml` sets `override-dependencies = ["pandas>=3.0"]`. Every lifelines number on a page is checked against R's survival package by `check_agree()`. Remove the override once lifelines supports pandas 3.
```

with

```markdown
14. **Python survival uses lifelines on pandas 3.** lifelines declares `pandas<3`, but the pages are written for pandas 3 (page 1's tidying breaks on pandas 2), so `pyproject.toml` sets `override-dependencies = ["pandas>=3.0"]`. Every lifelines number on a page is checked against R's survival package by `check_agree()`. Remove the override once lifelines supports pandas 3.
15. **Bootstrap CIs are seeded.** effectsize computes some CIs by bootstrap (`rank_epsilon_squared()`, `kendalls_w()`), so their printed CI changes on every render. Call `set.seed(2026)` just before them in the same chunk, or pass `ci = NULL` where only the estimate is needed (prose guards). `tests/site/test_sources.py` enforces this.
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
- `quarto render` re-executes nothing
- site: `157 passed`
- lychee: `0 Errors`
- `git status` shows only `CLAUDE.md` and `tests/python/test_repo_docs.py`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md tests/python/test_repo_docs.py
git commit -m "CLAUDE.md: record Phase 3b conventions (seeded bootstrap CIs, self-contained Python sections)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
