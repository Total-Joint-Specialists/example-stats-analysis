# Phase 4: Survival Analysis (Pages 13–14) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the two survival stubs with finished pages:
- `survival/13-kaplan-meier.qmd`: censoring, time zero and the event, the Kaplan-Meier curve with numbers at risk and a CI band, survivorship at 2, 5 and 10 years, median follow-up by reverse Kaplan-Meier, the log-rank test for two and for three or more groups, and competing risks (cumulative incidence, Gray's test)
- `survival/14-cox-regression.qmd`: the hazard ratio, choosing covariates and events per term, univariable to multivariable, checking straight-line effects, checking proportional hazards on the built-in violation, remedies (stratify, split time), stratified Cox for matched sets and bilateral patients, Fine-Gray regression (R only), and reporting

The catalog's forward links into these pages then point at the section each sentence promises.

**Architecture:**
- The same building blocks as Phases 2–3:
  - knitr-engine pages with R ⟷ Python tabsets
  - hidden `check_agree()` R ⟷ Python checks, a `# Prose guard` and a data-checksum stamp
  - exercise solutions that are executed chunks
- Spec §6 makes survival pages free-form: each topic in the spec's outline is an `##` section, with no fixed `###` anatomy. A new `tests/site/test_survival.py` checks:
  - the sections are present
  - code runs in both languages
  - the reporting conventions are followed
  - each page covers the content the spec requires
- The reporting-convention checks move from `test_catalog.py` into `sitelib.py`, so the catalog and survival tests share one definition.
- The source rules for executed solutions and prose guards now cover `survival/`. A new rule counts each survival page's R ⟷ Python checks.
- `just data` re-renders `survival/`.

**Tech Stack:**
- R: survival (Kaplan-Meier, log-rank, Aalen-Johansen, Cox, `cox.zph()`, `survSplit()`), ggsurvfit, splines, gtsummary
- R, new: tidycmprsk (Gray's test, Fine-Gray) and broom.helpers (needed by gtsummary's regression tables)
- Python: pandas 3; lifelines (`KaplanMeierFitter`, `CoxPHFitter`, `CoxTimeVaryingFitter`, log-rank tests); statsmodels (`CumIncidenceRight`, `lowess`); patsy (`cr()` splines); scipy
- Quarto 1.9.37

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`, especially:
- §4, pages 13 and 14: the topic lists these pages implement
- §3.2: the survival cells on rows 4, 6–9, 11 and 12, which link here
- §5.4: the built-in survival effects:
  - implant C's revision hazard
  - deaths competing with revisions
  - the posterior approach's early, non-proportional effect
- §6: page anatomy (free-form for survival pages) and §8: quality checks

## Global Constraints

- **`engine: knitr` per page.** Every page with code declares `engine: knitr` in its own front matter. Don't add `execute: message: false`: `_quarto.yml` already sets knitr's `opts_chunk: message: false` for every page.
- **Tabsets:** `::: {.panel-tabset group="language"}`, with `## R` first and `## Python` second. A method only R has (Gray's test, Fine-Gray) is a plain R chunk outside any tabset, and the page says so.
- **Hidden agreement checks:**
  - A hidden Python chunk sets `chk = {name: float(...)}`.
  - A hidden R chunk then calls `check_agree(list(name = <R value>), reticulate::py$chk)`.
  - Never pass DataFrames, sets or `pd.NA` through `reticulate::py`.
  - A looser `tol` always carries a comment saying why.
- **Quiet output:**
  - Chunks that call `library()` add `#| warning: false`. No page may show stderr output.
  - Never assign to `_` in a Python chunk.
  - Give a matplotlib return value that isn't a plot object a name (`legend = ax.legend()`).
  - Fit lifelines models in the same statement that creates them: a bare `model.fit(...)` prints the fitter object.
- **Prose guard:** one hidden R chunk headed `# Prose guard`, immediately before `## Exercises {#exercises}`. It `stopifnot()`s every quoted number, including the numbers in exercise solutions, and recomputes those itself because it runs before the solution chunks.
- **Data stamp:** each page has the `<!-- data-checksum: … -->` chunk.
- **Solutions:** exercise solutions are executed `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`, after the sentence "The solutions use the packages and data loaded in the sections above, so run the page from the top first." (page 14 says "packages, data and models made in").
- **Freeze:** render every changed page and commit its `_freeze/` directory. After a deliberately failed render, delete the leftover `<page>_files/` folder.
- **Reporting conventions:**
  - n (%); a 95% CI with every estimate
  - p to 3 decimals, with a floor of "p < 0.001" (R's `cox.zph()` prints 2 significant digits; quote 3 decimals)
  - a non-significant result or check is "imprecise" or "no clear evidence", never "similar", "held" or "not violated"
- **Survival tools:**
  - Every lifelines Cox fit passes `fit_options={"precision": 1e-12}`.
  - Python's cumulative incidence uses statsmodels' `CumIncidenceRight()`, with the log-log CI computed from its standard errors.
  - Gray's test and Fine-Gray regression are R only (tidycmprsk).
- **Branching:** work on branch `phase-4-survival`, in a worktree under `.worktrees/phase-4`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A cumulative incidence read at exactly 5 or 10 years in Python comes out wrong.**
   - lifelines' `AalenJohansenFitter` moves tied times by a small random amount. Two deaths at exactly 5.00 years moved just past 5, so it reported a 5-year death incidence of 13.6% against R's 14.2%.
   - Page 13 therefore uses statsmodels' `CumIncidenceRight()`. Its hidden check compares the 2-, 5- and 10-year incidences of revision and death, and the 10-year CI, at the default `tol = 1e-6`.
   - CLAUDE.md rule 17 (Task 5) records the choice.
2. **lifelines stops iterating early.**
   - At its default precision, the stratified model's implant B hazard ratio is 0.5425985; R's is 0.5425943.
   - Every Cox fit on page 14 passes `precision: 1e-12`. The Task 3 mutation step proves the hidden check notices when it's missing.
3. **"No clear evidence against proportional hazards" turns into "the assumption held".**
   - `tests/site/test_survival.py::test_reports_follow_the_reporting_conventions` (Tasks 2–3) runs the shared `NO_EVIDENCE_AS_NO_DIFFERENCE` pattern over every Methods/Results blockquote and exercise answer on pages 13–14.
   - It caught "gave a similar result" while prototyping.
4. **Bilateral patients counted as independent.**
   - Page 14's Methods promise robust standard errors.
   - Both the Results sentence and the hazard-ratio table use the clustered model (implant C 1.92 to 5.28, not the naive 5.29).
   - The hidden check compares the robust SEs, and the prose guard pins both CIs.
5. **A reader compares R's numbers at risk with lifelines' and finds they differ by one.**
   - R counts patients followed for at least t years; lifelines counts those followed for more than t.
   - Page 13 quotes R's counts, its hidden check counts with `>=` like R, and the 🔀 box explains the difference.

## Plan rulings (made while prototyping)

- **Examples:**
  - **Censoring:** six made-up patients, so the product-limit arithmetic can be followed by hand (survival 0.833, 0.625, 0.3125).
  - **Time zero:** four made-up patients with surgery, revision, death and last-visit dates. They show how `followup_years` and `event_status` are built, with "the first event wins".
  - **Kaplan-Meier and survivorship:** the whole cohort: 93.9%, 86.3% and 78.0% at 2, 5 and 10 years, with only 21 procedures at risk at 10 years.
  - **Log-rank, two groups:** anterior vs posterior total hips.
    - This is the built-in non-proportional effect: no clear evidence over the whole follow-up (p = 0.340), but the curves cross (6-month survivorship 88.7% vs 98.6%).
    - It sets up page 14's proportional-hazards section.
  - **Log-rank, three groups:** implant A, B and C (χ² = 33.5, df = 2), the same test page 8 prints.
  - **Competing risks:** the whole cohort; 1 − KM is 22.0% at 10 years against a cumulative incidence of 19.3%. Exercise 2 repeats it for patients aged 75 and over (16.5% vs 13.9% at 5 years).
  - **Gray's test:** by implant.
  - **Cox (page 14):** the implant model from page 8 and the adjusted model from page 12 (age, sex and BMI, chosen in advance), so the numbers match across pages. The proportional-hazards and remedy examples use surgical approach in total hips.
- **Python's cumulative incidence uses statsmodels, not lifelines:**
  - `CumIncidenceRight()` matches R's Aalen-Johansen estimates and standard errors exactly.
  - The Python code builds the log-log CI from those standard errors. That matches R's `survfit(conf.type = "log-log")` exactly.
  - R estimates the incidence with survival's `survfit()` on a three-level status, and uses tidycmprsk only for Gray's test and Fine-Gray. tidycmprsk's `cuminc()` gives the same estimates, but its variance formula gives slightly different CIs.
- **Linearity section added:** page 11 already promises that page 14 "shows how to check" the straight-line effect of age.
  - The check fits a natural cubic spline (`ns(age, df = 3)`) and runs a likelihood ratio test: χ² = 0.29, p = 0.864.
  - In Python, the spline columns come from patsy's `cr()` with R's knots and are passed to lifelines as ordinary columns. lifelines' own formula `cr()` fails to converge.
- **Proportional-hazards tests differ:**
  - R's `cox.zph()` computes the full score test; lifelines' `proportional_hazard_test()` uses Grambsch and Therneau's simpler original approximation (11.3 vs 11.2 for approach).
  - Per spec §8.2 the difference is documented in the 🔀 box, not checked.
  - The hidden check compares what both plots show instead: the scaled Schoenfeld residuals' mean, overall and in the first 6 months. lifelines leaves out the coefficient that R adds, so the Python code adds it back.
- **Residual plot:** Python uses a log time axis and LOWESS with `it=0`. Robust LOWESS treats one of the two residual clusters (±2) as outliers.
- **Robust standard errors:**
  - R and lifelines agree exactly when no follow-up times are tied (checked on jittered data with `timefix = FALSE`).
  - With ties, R applies Efron's tie correction inside the robust variance and lifelines doesn't, so the hidden check uses `tol = 1e-3` with a comment.
- **Time split:** lifelines' `CoxTimeVaryingFitter` on hand-built start/stop rows matches R's `survSplit()` model exactly with `precision: 1e-12`.
- **Bilateral patients:** spec §4 says "stratified Cox for matched sets and bilateral patients".
  - For bilateral patients, page 14 leads with robust standard errors clustered on patient, the usual choice. It presents stratifying by patient as an option that is rarely precise: only patients whose two joints differ in the predictor and who had a revision contribute (47 of the 80 bilateral patients have different implants on the two sides, and 20 had a revision).
  - Matched sets get the `strata(set_id)` explanation and links to the worked examples on pages 7 and 9, rather than a third copy of that code.
- **gtsummary regression tables** need broom.helpers. It's installed (with its dependency labelled) alongside tidycmprsk in Task 1.
- **Covariate hazard ratios:** page 14 warns that the covariates' own hazard ratios aren't findings, matching page 12's "exploratory" label on men's lower hazard.
- **Rounding:**
  - the crude median follow-up is 4.365 years, quoted as 4.4
  - the toy survival 0.3125 is quoted in full, because R prints 0.312
  - `cox.zph()` p-values are quoted to 3 decimals (0.359, 0.106)
- **Catalog links:** ten links on six catalog pages (4, 6, 8, 9, 11, 12) gain the anchor of the section their sentence promises. Generic "covers Cox regression in full" links stay as they are. Re-rendering page 6 also changes its jittered boxplot PNG, because `geom_jitter()` is random.
- **Not folded in:** the deferred minors from Phases 3b and 3c. The post-hoc sentence belongs to Phase 5's page 15.

## Reference results (prototype, 2026-10-06, R 4.6.0 / Python 3.13 / pandas 3.0.6 / lifelines 0.30.3 / statsmodels 0.15.0)

Both pages rendered with every hidden check passing. Full suite:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- pytest `tests/python`: 80 passed
- pytest `tests/site`: 246 passed
- lychee: 0 errors
- a full `quarto render` re-executes nothing

Mutation checks (each failed as it should):
- page 13 without `conf.type = "log-log"`: `disagree on 'low_2'`
- page 14's stratified model without `precision: 1e-12`: `disagree on 'hr_b'`
- page 13 without the Justfile line: `` `just data` must re-render: ['survival'] ``
- page 14 with "gave a similar result" in its Results: `test_reports_follow_the_reporting_conventions` fails

| Page | Numbers |
|---|---|
| 13 | survivorship 93.9% (91.6 to 95.6) at 2 years, 86.3% (82.8 to 89.2) at 5, 78.0% (72.5 to 82.6) at 10 with 21 at risk; median follow-up 5.62 years (IQR 3.52 to 7.93); approach log-rank χ² = 0.9, p = 0.340; implant log-rank χ² = 33.5, df = 2; cumulative incidence of revision 19.3% (15.3 to 23.7) at 10 years vs 1 − KM 22.0%; Gray's test χ² = 31.5 |
| 14 | implant C HR 3.07 (1.85 to 5.09), adjusted 3.19 (1.92 to 5.29; robust 1.92 to 5.28); age spline χ² = 0.29, p = 0.864; global `cox.zph()` p = 0.359; approach `cox.zph()` p < 0.001; posterior approach HR 8.47 (1.93 to 37.3) in the first 6 months, 0.43 (0.16 to 1.16) after; Fine-Gray SHR for implant C 3.09 (1.86 to 5.14), for age 1.07 (0.86 to 1.33) |

---

### Task 1: tidycmprsk, broom.helpers and the setup checks

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `getting-started/check_setup.R`, `tests/python/test_check_setup.py`

**Interfaces:**
- Produces: the R packages tidycmprsk (Gray's test on page 13, Fine-Gray on page 14) and broom.helpers (gtsummary's `tbl_regression()` and `tbl_uvregression()` on page 14).

- [ ] **Step 1: Create the worktree and build the current site**

```bash
git checkout main && git pull
git worktree add .worktrees/phase-4 -b phase-4-survival main
cd .worktrees/phase-4
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `216 passed`.

- [ ] **Step 2: Write the failing checks**

In `getting-started/check_setup.R`, replace

```r
"DescTools", "survival", "ggsurvfit", "rstatix")) {
```

with

```r
"DescTools", "survival", "ggsurvfit", "rstatix", "tidycmprsk",
             "broom.helpers")) {
```

In `tests/python/test_check_setup.py`, replace

```python
"effectsize", "DescTools", "survival", "ggsurvfit", "rstatix"]:
```

with

```python
"effectsize", "DescTools", "survival", "ggsurvfit", "rstatix", "tidycmprsk",
                "broom.helpers"]:
```

- [ ] **Step 3: Run them to verify they fail**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_setup")'`

Expected: "check_setup.R passes in a working project" FAILS. Running `Rscript getting-started/check_setup.R` reports `R package tidycmprsk PROBLEM` and `R package broom.helpers PROBLEM`.

- [ ] **Step 4: Install and lock the packages**

In `DESCRIPTION`, replace

```
Imports:
    DescTools,
```

with

```
Imports:
    broom.helpers,
    DescTools,
```

and replace

```
    tibble,
    tidyr,
```

with

```
    tibble,
    tidycmprsk,
    tidyr,
```

Run:

```bash
Rscript -e 'renv::install(c("tidycmprsk", "broom.helpers"), prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
python3 -c "import json; p = json.load(open('renv.lock'))['Packages']; print([k for k in ['broom.helpers', 'cmprsk', 'hardhat', 'labelled', 'sparsevctrs', 'tidycmprsk'] if k not in p])"
```

Expected: `[]`. The snapshot adds exactly six packages: broom.helpers, cmprsk, hardhat, labelled, sparsevctrs and tidycmprsk.

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
- site: `216 passed`

- [ ] **Step 6: Commit**

```bash
git add DESCRIPTION renv.lock getting-started/check_setup.R tests/python/test_check_setup.py
git commit -m "Add tidycmprsk (Gray's test, Fine-Gray) and broom.helpers (gtsummary regression tables) with their setup checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Page 13, Kaplan-Meier and the log-rank test

**Files:**
- Modify: `survival/13-kaplan-meier.qmd` (replace the stub)
- Create: `_freeze/survival/13-kaplan-meier/` (render output; commit it)
- Create: `tests/site/test_survival.py`
- Modify: `tests/site/sitelib.py`, `tests/site/test_catalog.py`, `tests/site/test_sources.py`, `Justfile`

**Interfaces:**
- Consumes:
  - Task 1's tidycmprsk (`cuminc()`, `glance()`)
  - `test_catalog.py`'s `text_of`, `section` and the two reporting tests (Phase 3c)
  - `test_sources.py`'s `written_pages()` and `hidden_chunks()`
  - `data/cohort.csv`
- Produces:
  - page 13 anchors `#censoring`, `#time-zero`, `#kaplan-meier`, `#survivorship`, `#follow-up`, `#log-rank`, `#competing-risks` and `#exercises`; page 14 and Task 4 link to `#competing-risks`, `#log-rank` and `#time-zero`
  - in `sitelib.py`: `text_of(element)`, `section(page, anchor)`, `NO_EVIDENCE_AS_NO_DIFFERENCE`, `EFFECT_SIZE` and `unreported(text) -> list`
  - in `test_survival.py`: `SECTIONS`, `KM` and `code_of(found)`
  - in `test_sources.py`: `test_survival_pages_check_r_against_python`

- [ ] **Step 1: Write the tests**

In `tests/site/sitelib.py`, replace the opening lines

```python
"""Shared constants and helpers for the built-site tests."""

from pathlib import Path
```

with

```python
"""Shared constants and helpers for the built-site tests."""

import re
from pathlib import Path
```

and append to the end of the file (after two blank lines):

```python
def text_of(element):
    """Text with smart quotes straightened and runs of whitespace collapsed."""
    return " ".join(element.get_text(" ").replace("’", "'").split())


def section(page, anchor):
    found = load(page).select_one(f"section#{anchor}")
    assert found is not None, f"{page} has no section #{anchor}"
    return found


# ---- reporting conventions (spec section 4, page 0.2) ------------------------

# A wide CI or a non-significant check is "no clear evidence of a difference", never "similar" or "held".
NO_EVIDENCE_AS_NO_DIFFERENCE = re.compile(
    r"\b(similar|no difference|held|not violated|(?:did not|does not|doesn't) improve)\b", re.IGNORECASE)
EFFECT_SIZE = re.compile(r"(ω²|ε²|η²( p)?|Kendall's W|Cramér's V|\br|ρ|φ) = [\d.]+|(odds|hazard) ratio [\d.]+")


def unreported(text):
    """The conventions a model Results sentence breaks: an effect size needs its CI,
    a mean its SD and a median its IQR."""
    problems = []
    if EFFECT_SIZE.search(text) and "CI" not in text:
        problems.append("effect size without a CI")
    if re.search(r"\bmeans? of [\d.]+", text) and "SD" not in text:
        problems.append("mean without an SD")
    if re.search(r"\bmedian\b[^.]*\d", text) and "IQR" not in text:
        problems.append("median without an IQR")
    return problems
```

In `tests/site/test_catalog.py`, the helpers and patterns now come from `sitelib.py`. Replace the import

```python
from sitelib import CELL_ANCHORS, ROOT, load
```

with

```python
from sitelib import CELL_ANCHORS, NO_EVIDENCE_AS_NO_DIFFERENCE, ROOT, load, section, text_of, unreported
```

delete these two functions and the two blank lines after them:

```python
def text_of(element):
    """Text with smart quotes straightened and runs of whitespace collapsed."""
    return " ".join(element.get_text(" ").replace("’", "'").split())


def section(page, anchor):
    found = load(page).select_one(f"section#{anchor}")
    assert found is not None, f"{page} has no section #{anchor}"
    return found
```

replace

```python
        found = re.findall(r"\b(similar|no difference|held|not violated|(?:did not|does not|doesn't) improve)\b", text, re.IGNORECASE)
```

with

```python
        found = NO_EVIDENCE_AS_NO_DIFFERENCE.findall(text)
```

and replace

```python
    for paragraph in section(page, "exercises").select("p"):
        text = text_of(paragraph)
        if re.search(r"(ω²|ε²|η²( p)?|Kendall's W|Cramér's V|\br|ρ|φ) = [\d.]+|(odds|hazard) ratio [\d.]+", text):
            assert "CI" in text, text
        if re.search(r"\bmeans? of [\d.]+", text):
            assert "SD" in text, text
        if re.search(r"\bmedian\b[^.]*\d", text):
            assert "IQR" in text, text
```

with

```python
    for paragraph in section(page, "exercises").select("p"):
        text = text_of(paragraph)
        assert unreported(text) == [], text
```

In `tests/site/test_sources.py`, replace

```python
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog"):
```

with

```python
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog", "survival"):
```

replace

```python
def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog"):
```

with

```python
def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog", "survival"):
```

and insert this test immediately above the line `# ---- each section's Python runs on its own -------------------------------`, followed by two blank lines:

```python
def test_survival_pages_check_r_against_python():
    """Free-form pages have no cell sections, so count the whole page's checks."""
    for name, text in written_pages("survival"):
        hidden = hidden_chunks(text)
        r_checks = sum(lang == "r" and "check_agree(" in code for lang, code in hidden)
        py_values = sum(lang == "python" and "chk = " in code for lang, code in hidden)
        assert r_checks >= 5 and r_checks == py_values, f"{name}: {r_checks} R checks, {py_values} Python chk"
```

Create `tests/site/test_survival.py`:

```python
"""Part 3 · Survival analysis: Kaplan-Meier and Cox regression in full (spec section 4, pages 13-14)."""

import pytest

from sitelib import NO_EVIDENCE_AS_NO_DIFFERENCE, ROOT, load, section, text_of, unreported

# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
}
KM = "survival/13-kaplan-meier.html"


def code_of(found):
    return " ".join(pre.get_text() for pre in found.select("pre"))


@pytest.mark.parametrize("page,sections", SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("section[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_page_runs_both_languages_and_is_frozen(site, page):
    ran = [tabset for tabset in load(page).select("div.panel-tabset")
           if all(pane.select(".cell-output, .cell-output-display") for pane in tabset.select("div.tab-pane"))]
    assert len(ran) >= 5, f"{page}: only {len(ran)} tabsets show output in both R and Python"
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in section(page, "exercises").select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    assert [out.get_text()[:80] for out in load(page).select(".cell-output-stderr")] == []


@pytest.mark.parametrize("page", SECTIONS)
def test_outputs_are_short_and_never_dump_objects(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text and "<matplotlib." not in text and "<lifelines." not in text, \
            f"{page}: object dumped: {text[:80]}"
        assert len(text.splitlines()) <= 40, f"{page}: {len(text.splitlines())}-line output"


@pytest.mark.parametrize("page", SECTIONS)
def test_reports_follow_the_reporting_conventions(site, page):
    """Methods and Results blockquotes and exercise answers: CIs with effect sizes, and no
    "similar" or "held" where the data only fail to show a difference."""
    quotes = [text_of(q) for q in load(page).select("blockquote")]
    assert any("Methods:" in q and "Results:" in q for q in quotes), f"{page}: no Methods and Results"
    answers = [text_of(p) for p in section(page, "exercises").select("p")]
    for text in quotes + answers:
        assert unreported(text) == [], text
        assert not NO_EVIDENCE_AS_NO_DIFFERENCE.findall(text), text


# ---- page 13: Kaplan-Meier and the log-rank test -----------------------------

def test_kaplan_meier_curves_show_numbers_at_risk_and_a_ci_band(site):
    found = section(KM, "kaplan-meier")
    code = code_of(found)
    assert "add_risktable(" in code and "add_confidence_interval()" in code and "add_at_risk_counts(" in code
    panes = found.select("div.panel-tabset div.tab-pane")
    assert len(panes) == 2 and all(pane.select("img") for pane in panes), "the curve is drawn in both languages"


def test_survivorship_is_reported_at_2_5_and_10_years_with_cis_and_numbers_at_risk(site):
    results = " ".join(text_of(q) for q in section(KM, "survivorship").select("blockquote"))
    for years in ["at 2 years", "at 5 years", "at 10 years"]:
        assert years in results, years
    assert results.count("95% CI") >= 3 and "remained at risk" in results


def test_median_follow_up_uses_reverse_kaplan_meier(site):
    found = section(KM, "follow-up")
    assert "reverse Kaplan-Meier" in " ".join(text_of(q) for q in found.select("blockquote"))
    assert "5.62 years" in text_of(found)


def test_log_rank_covers_two_groups_and_three_or_more(site):
    found = section(KM, "log-rank")
    outputs = " ".join(out.get_text() for out in found.select(".cell-output"))
    assert "on 1 degrees of freedom" in outputs and "on 2 degrees of freedom" in outputs
    assert "Mantel-Haenszel" in text_of(found)


def test_competing_risks_compare_the_cumulative_incidence_with_one_minus_km(site):
    text = text_of(section(KM, "competing-risks"))
    for phrase in ["Aalen-Johansen", "1 − Kaplan-Meier", "Gray's test", "Python has no mature implementation of Gray's test"]:
        assert phrase in text, phrase
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `9 failed, 219 passed`. All 9 failures are page-13 tests in `test_survival.py`; the no-warnings and short-outputs tests pass trivially on a stub. The refactored catalog tests and the new source rule pass. `written_pages()` skips stubs, so the source rule has nothing to check yet.

- [ ] **Step 3: Write the page**

Replace `survival/13-kaplan-meier.qmd` with:

````markdown
---
title: "13 · Kaplan-Meier & the log-rank test"
description: "Censoring, time zero, Kaplan-Meier curves with numbers at risk, survivorship at 2, 5 and 10 years, median follow-up, the log-rank test, and competing risks."
engine: knitr
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

"How long do the implants last?" is the central question of arthroplasty research, and it needs its own methods. Patients join the study over several years and are followed for different lengths of time, and most of them are never revised. **Survival analysis** uses every patient's follow-up for as long as it lasts.

Pages [4](../catalog/04-describe-one-group.qmd#kaplan-meier), [6](../catalog/06-two-unpaired-groups.qmd#log-rank) and [8](../catalog/08-three-plus-unmatched.qmd#cox) each showed one survival method in a few steps. This page covers the whole method:
- what censoring is
- how to set up the data
- how to read and report a Kaplan-Meier curve
- how long the patients were followed
- how to compare groups
- what to do when patients die before they can be revised

[Page 14](14-cox-regression.qmd) covers Cox regression.

::: {.callout-note}
## 💡 How this page works
Run the code blocks in order, from the top: later blocks use the packages and data loaded earlier.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 14](14-cox-regression.qmd#stratified-cox)) and say what you did.
:::

## What censoring means {#censoring}

Picture six patients, each followed from surgery until either a revision or the end of their follow-up:

| Patient | Years followed | Revised? |
|---|---|---|
| A | 1 | yes |
| B | 2 | no: the study closed |
| C | 3 | yes |
| D | 4 | no: moved away |
| E | 5 | yes |
| F | 6 | no: the study closed |

Patients B, D and F are **censored**. We know they went *at least* that long without a revision, but not what happened afterwards. Censoring isn't missing data: it's partial information, and survival methods use all of it.

Two simple summaries both get this wrong:
- **"3 of 6 (50%) were revised"** ignores time. Patient B was followed for only 2 years, so B's implant never had the chance to fail at 4 or 5 years.
- **Dropping the censored patients** ("3 of 3 were revised") throws away the years B, D and F spent without a revision.

The **Kaplan-Meier** method gets it right. It moves through time and recalculates at each revision, using only the patients still being followed (**at risk**) at that moment:

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)
library(ggsurvfit)

toy <- tibble(
  patient = c("A", "B", "C", "D", "E", "F"),
  years   = c(1, 2, 3, 4, 5, 6),
  revised = c(1, 0, 1, 0, 1, 0)        # 1 = revised, 0 = censored
)

toy_km <- survfit(Surv(years, revised) ~ 1, data = toy)
summary(toy_km)
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter

toy = pd.DataFrame({
    "patient": ["A", "B", "C", "D", "E", "F"],
    "years":   [1, 2, 3, 4, 5, 6],
    "revised": [1, 0, 1, 0, 1, 0],     # 1 = revised, 0 = censored
})

toy_km = KaplanMeierFitter().fit(toy["years"], event_observed=toy["revised"])
print(toy_km.event_table[["at_risk", "observed", "censored"]])   # observed = revisions
print(toy_km.survival_function_)
```
:::

```{python}
#| include: false
chk = {"surv_1": float(toy_km.survival_function_at_times(1).iloc[0]),
       "surv_3": float(toy_km.survival_function_at_times(3).iloc[0]),
       "surv_5": float(toy_km.survival_function_at_times(5).iloc[0])}
```

```{r}
#| include: false
toy_summary <- summary(toy_km, times = c(1, 3, 5))
check_agree(list(surv_1 = toy_summary$surv[1], surv_3 = toy_summary$surv[2], surv_5 = toy_summary$surv[3]),
            reticulate::py$chk)
```

Reading the output, one revision at a time:
- **Year 1:** 6 patients at risk, 1 revised. Survival = 5/6 = 0.833.
- **Year 2:** B is censored. Nothing happens to the curve, but the at-risk group shrinks to 4.
- **Year 3:** 4 at risk, 1 revised. Survival = 0.833 × 3/4 = 0.625.
- **Year 5:** 2 at risk (D was censored at year 4), 1 revised. Survival = 0.625 × 1/2 = 0.3125.

So the estimated chance of a revision by 5 years is 1 − 0.3125 = 69%, not 50%. Each censored patient counts fully while they're followed and then leaves the at-risk group.

::: {.callout-note collapse="true"}
## 🔍 Under the hood: the product-limit formula
At each time $t_i$ when at least one revision happens, with $n_i$ patients at risk and $d_i$ revisions, the chance of getting past $t_i$ unrevised is $1 - d_i/n_i$. Kaplan-Meier survival at time $t$ multiplies these together for every revision time up to $t$:

$$\hat S(t) = \prod_{t_i \le t} \left(1 - \frac{d_i}{n_i}\right)$$

This is why the method is also called the **product-limit** estimator. Censored patients appear only in the $n_i$ of the revision times before they leave.
:::

::: {.callout-warning}
## ⚠️ Watch out: censoring must be unrelated to the outcome
Kaplan-Meier assumes a censored patient has the same future risk as the patients still being followed. That's reasonable when follow-up ends because the study closed. It isn't when patients stop coming back *because* their hip hurts, or stay away because it's perfect. If many patients are lost to follow-up, say how many and why.
:::

## Time zero and the event {#time-zero}

Every survival analysis needs two definitions, fixed before you look at the results:

- **Time zero**, when the clock starts. For implant survival it's the **date of surgery**: every patient starts at the same clinical moment. Starting at the first clinic visit instead would ignore revisions that happened before that visit.
- **The event**, what stops the clock. Here it's **revision for any reason**: any reoperation that removes or exchanges a component. Other studies use aseptic revision, or any reoperation. Choose one in advance and define it in the Methods.

Real data rarely arrive as "years followed" and "revised: yes/no". You build those columns from dates. The practice cohort already has them: `followup_years` and `event_status`, where 0 means censored, 1 means revised and 2 means died without a revision. Here's how to make them from a table of dates, for four made-up patients:

::: {.panel-tabset group="language"}
## R

```{r}
dates <- tibble(
  patient       = c("P1", "P2", "P3", "P4"),
  surgery_date  = as.Date(c("2016-03-14", "2018-11-05", "2020-06-30", "2017-01-09")),
  revision_date = as.Date(c("2019-07-02", NA, NA, "2017-04-18")),
  death_date    = as.Date(c("2023-02-11", "2022-01-20", NA, NA)),
  last_seen     = as.Date(c("2022-10-03", "2021-12-02", "2025-11-17", "2024-08-15"))
)

follow_up <- dates |>
  mutate(
    # the first event wins: a revision, else a death, else censored at the last visit
    event_status = case_when(!is.na(revision_date) ~ 1,
                             !is.na(death_date)    ~ 2,
                             .default = 0),
    end_date = case_when(event_status == 1 ~ revision_date,
                         event_status == 2 ~ death_date,
                         .default = last_seen),
    followup_years = as.numeric(end_date - surgery_date) / 365.25
  )

follow_up |> select(patient, event_status, end_date, followup_years)
```

## Python

```{python}
dates = pd.DataFrame({
    "patient":       ["P1", "P2", "P3", "P4"],
    "surgery_date":  ["2016-03-14", "2018-11-05", "2020-06-30", "2017-01-09"],
    "revision_date": ["2019-07-02", None, None, "2017-04-18"],
    "death_date":    ["2023-02-11", "2022-01-20", None, None],
    "last_seen":     ["2022-10-03", "2021-12-02", "2025-11-17", "2024-08-15"],
})
for column in ["surgery_date", "revision_date", "death_date", "last_seen"]:
    dates[column] = pd.to_datetime(dates[column])

# the first event wins: a revision, else a death, else censored at the last visit
dates["event_status"] = np.select([dates["revision_date"].notna(), dates["death_date"].notna()],
                                  [1, 2], default=0)
dates["end_date"] = dates["revision_date"].fillna(dates["death_date"]).fillna(dates["last_seen"])
dates["followup_years"] = (dates["end_date"] - dates["surgery_date"]).dt.days / 365.25

print(dates[["patient", "event_status", "end_date", "followup_years"]])
```
:::

```{python}
#| include: false
chk = {"years_p1": float(dates["followup_years"].iloc[0]), "years_p2": float(dates["followup_years"].iloc[1]),
       "years_p3": float(dates["followup_years"].iloc[2]), "years_p4": float(dates["followup_years"].iloc[3]),
       "status_sum": float(dates["event_status"].sum())}
```

```{r}
#| include: false
check_agree(list(years_p1 = follow_up$followup_years[1], years_p2 = follow_up$followup_years[2],
                 years_p3 = follow_up$followup_years[3], years_p4 = follow_up$followup_years[4],
                 status_sum = sum(follow_up$event_status)),
            reticulate::py$chk)
```

- **P1** was revised in 2019 and died in 2023. The revision came first, so P1's follow-up ends at the revision, 3.30 years after surgery.
- **P2** died 3.21 years after surgery without a revision. Death ends the follow-up: P2 can never be revised. (The section on [competing risks](#competing-risks) explains why that matters.)
- **P3** was alive and unrevised at the last visit: censored at 5.38 years.
- **P4** was revised 99 days after surgery, at 0.27 years.

::: {.callout-warning}
## ⚠️ Watch out: follow-up ends at the last visit, not today
Don't set every unrevised patient's end date to the date you pulled the data. A patient last seen in 2021 might have been revised elsewhere since. Censor at the last date you *know* the implant was in place. And check that no event date comes before the surgery date: it's always a data-entry error.
:::

## The Kaplan-Meier curve {#kaplan-meier}

Now the practice cohort: 600 procedures, each followed from surgery to revision, death or the last visit.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4.5
cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

km <- survfit2(Surv(followup_years, revised) ~ 1, data = cohort,
               conf.type = "log-log")              # the CI method lifelines uses

km |>
  ggsurvfit() +
  add_confidence_interval() +
  add_censor_mark(size = 1, alpha = 0.4) +         # a tick for each censored patient
  add_risktable(times = c(0, 2, 4, 6, 8, 10)) +
  scale_ggsurvfit(x_scales = list(breaks = c(0, 2, 4, 6, 8, 10))) +
  labs(x = "Years since surgery", y = "Revision-free survival")
```

## Python

```{python}
from lifelines.plotting import add_at_risk_counts

cohort = pd.read_csv("data/cohort.csv")

km = KaplanMeierFitter(label="All procedures").fit(cohort["followup_years"], event_observed=cohort["revised"])

fig, ax = plt.subplots(figsize=(7, 4.5))
km.plot_survival_function(ax=ax, show_censors=True,                # a tick for each censored patient
                          censor_styles={"ms": 3, "alpha": 0.4}, legend=False)
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Revision-free survival")
add_at_risk_counts(km, ax=ax, xticks=[0, 2, 4, 6, 8, 10], rows_to_show=["At risk", "Events"])
plt.tight_layout()
plt.show()
```
:::

```{python}
#| include: false
chk = {"at_risk_4": float((cohort["followup_years"] >= 4).sum()),
       "at_risk_8": float((cohort["followup_years"] >= 8).sum()),
       "surv_4": float(km.survival_function_at_times(4).iloc[0]),
       "surv_8": float(km.survival_function_at_times(8).iloc[0])}
```

```{r}
#| include: false
km_4_8 <- summary(km, times = c(4, 8))
check_agree(list(at_risk_4 = km_4_8$n.risk[1], at_risk_8 = km_4_8$n.risk[2],
                 surv_4 = km_4_8$surv[1], surv_8 = km_4_8$surv[2]),
            reticulate::py$chk)
```

How to read it:
- **The steps:** the curve starts at 100% and drops at each revision. The drops get bigger later on, because each revision is then a bigger share of the fewer patients still at risk.
- **The ticks** mark censored patients. They don't move the curve; they leave the at-risk group.
- **The shaded band** is the 95% CI. It widens as patients leave.
- **The table below the plot** gives the number of patients still being followed (**at risk**) at each time, 600 at surgery, 332 at 4 years and 84 at 8 years, and the revisions so far. Always publish the numbers at risk with the curve: they tell the reader how much to trust each part of it.

::: {.callout-warning}
## ⚠️ Watch out: the tail of the curve
By 10 years only 21 procedures are still followed, so each late revision moves the curve a lot. Don't draw conclusions from the far right-hand end. A common rule of thumb is to stop drawing the curve once fewer than about 10% of patients (here, 60) remain at risk.
:::

::: {.callout-tip}
## 🔀 R vs Python: the confidence band
R's `survfit()` uses a "log" CI by default; lifelines uses "log-log". We set `conf.type = "log-log"` in R so the two match, as on [page 4](../catalog/04-describe-one-group.qmd#kaplan-meier). The numbers at risk can differ by one or two: R counts the patients followed for *at least* 4 years, lifelines those followed for *more than* 4 years, so a patient censored at exactly 4.00 years is in R's count only. lifelines' `add_at_risk_counts()` also adds a row of censored patients unless you choose rows with `rows_to_show`.
:::

## Survivorship at 2, 5 and 10 years {#survivorship}

Papers report the curve at fixed times: the **survivorship**, the percentage of implants still unrevised.

::: {.panel-tabset group="language"}
## R

```{r}
summary(km, times = c(2, 5, 10))
```

## Python

```{python}
for years in [2, 5, 10]:
    estimate = km.survival_function_at_times(years).iloc[0]
    ci = km.confidence_interval_survival_function_.loc[:years].iloc[-1]   # last step at or before that time
    at_risk = (cohort["followup_years"] >= years).sum()
    print(years, round(estimate, 3), ci.round(3).to_list(), at_risk)
```
:::

```{python}
#| include: false
chk = {}
for years in [2, 5, 10]:
    ci = km.confidence_interval_survival_function_.loc[:years].iloc[-1]
    chk[f"surv_{years}"] = float(km.survival_function_at_times(years).iloc[0])
    chk[f"low_{years}"] = float(ci.iloc[0])
    chk[f"high_{years}"] = float(ci.iloc[1])
```

```{r}
#| include: false
km_2_5_10 <- summary(km, times = c(2, 5, 10))
check_agree(list(surv_2 = km_2_5_10$surv[1], low_2 = km_2_5_10$lower[1], high_2 = km_2_5_10$upper[1],
                 surv_5 = km_2_5_10$surv[2], low_5 = km_2_5_10$lower[2], high_5 = km_2_5_10$upper[2],
                 surv_10 = km_2_5_10$surv[3], low_10 = km_2_5_10$lower[3], high_10 = km_2_5_10$upper[3]),
            reticulate::py$chk)
```

- **survival:** 0.939 at 2 years, 0.863 at 5 years and 0.780 at 10 years.
- **lower 95% CI / upper 95% CI:** the CI around each one. The 10-year CI (0.725 to 0.826) is the widest.
- **n.risk:** 496 procedures still followed at 2 years, 263 at 5 years and only 21 at 10 years.
- **n.event:** the revisions *since the previous time shown*, not the running total.

> **Methods:** Implant survivorship was estimated with the Kaplan-Meier method, with revision for any reason as the end point and the date of surgery as time zero. Patients were censored at death or at their last follow-up. Confidence intervals used the log-log transformation.
>
> **Results:** Survivorship free of revision was 93.9% (95% CI 91.6% to 95.6%) at 2 years, 86.3% (95% CI 82.8% to 89.2%) at 5 years and 78.0% (95% CI 72.5% to 82.6%) at 10 years, when 21 procedures remained at risk.

::: {.callout-warning}
## ⚠️ Watch out: "86% survival" needs its time point, CI and numbers at risk
A survivorship figure means nothing without the time it refers to. Give the 95% CI, and the number still at risk at the time you quote, so readers can see how much data the estimate rests on.
:::

## How long were patients followed? {#follow-up}

Every survival paper reports the **median follow-up**. The obvious way to calculate it is wrong:

::: {.panel-tabset group="language"}
## R

```{r}
median(cohort$followup_years)        # misleading: revisions and deaths cut follow-up short

# reverse Kaplan-Meier: treat "still followed at the end" as the event
reverse_km <- survfit(Surv(followup_years, event_status == 0) ~ 1, data = cohort)
quantile(reverse_km, probs = c(0.25, 0.5, 0.75), conf.int = FALSE)
```

## Python

```{python}
from lifelines.utils import qth_survival_times

print(cohort["followup_years"].median())   # misleading: revisions and deaths cut follow-up short

# reverse Kaplan-Meier: treat "still followed at the end" as the event
reverse_km = KaplanMeierFitter().fit(cohort["followup_years"],
                                     event_observed=(cohort["event_status"] == 0))
print(qth_survival_times([0.75, 0.5, 0.25], reverse_km.survival_function_))   # 25th, 50th, 75th percentiles
```
:::

```{python}
#| include: false
follow_up_quartiles = qth_survival_times([0.75, 0.5, 0.25], reverse_km.survival_function_).iloc[:, 0]
chk = {"crude": float(cohort["followup_years"].median()), "q1": float(follow_up_quartiles.iloc[0]),
       "median": float(follow_up_quartiles.iloc[1]), "q3": float(follow_up_quartiles.iloc[2])}
```

```{r}
#| include: false
follow_up_quartiles <- quantile(reverse_km, probs = c(0.25, 0.5, 0.75), conf.int = FALSE)
check_agree(list(crude = median(cohort$followup_years), q1 = follow_up_quartiles[[1]],
                 median = follow_up_quartiles[[2]], q3 = follow_up_quartiles[[3]]),
            reticulate::py$chk)
```

The plain median, 4.4 years, mixes two things: how long the study watched patients, and how soon they were revised or died. A patient revised at 1 year wasn't "followed for 1 year" in the sense readers care about. The study would have kept watching them.

The **reverse Kaplan-Meier** method answers the real question: how long would patients have been followed if nothing had happened to them? It swaps the roles: being censored at the end of follow-up becomes the "event", and revisions and deaths become the censored observations. The median follow-up is **5.62 years** (IQR 3.52 to 7.93).

> **Methods:** Median follow-up was estimated with the reverse Kaplan-Meier method.
>
> **Results:** The median follow-up was 5.62 years (IQR 3.52 to 7.93).

## Comparing groups: the log-rank test {#log-rank}

The **log-rank test** asks whether two or more survival curves differ. At every revision time it compares each group's observed revisions with the number expected if all groups had the same risk, then adds up the differences across the whole follow-up. It's the same test as the **Mantel-Haenszel** (or Mantel-Cox) test in the decision table.

**Two groups.** In total hips, does the surgical approach (anterior or posterior) affect revision?

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4.5
tha <- cohort |> filter(procedure == "THA")        # approach applies to hips only

survfit2(Surv(followup_years, revised) ~ approach, data = tha, conf.type = "log-log") |>
  ggsurvfit() +
  add_confidence_interval() +
  add_risktable() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Revision-free survival")

approach_logrank <- survdiff(Surv(followup_years, revised) ~ approach, data = tha)
approach_logrank
```

## Python

```{python}
from lifelines.statistics import logrank_test

tha = cohort[cohort["procedure"] == "THA"]                # approach applies to hips only
anterior = tha[tha["approach"] == "anterior"]
posterior = tha[tha["approach"] == "posterior"]

fig, ax = plt.subplots(figsize=(7, 4.5))
km_anterior = KaplanMeierFitter(label="anterior").fit(anterior["followup_years"], anterior["revised"])
km_posterior = KaplanMeierFitter(label="posterior").fit(posterior["followup_years"], posterior["revised"])
km_anterior.plot_survival_function(ax=ax)
km_posterior.plot_survival_function(ax=ax)
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Revision-free survival")
add_at_risk_counts(km_anterior, km_posterior, ax=ax, rows_to_show=["At risk", "Events"])
plt.tight_layout()
plt.show()

approach_logrank = logrank_test(anterior["followup_years"], posterior["followup_years"],
                                event_observed_A=anterior["revised"], event_observed_B=posterior["revised"])
print(approach_logrank.test_statistic, approach_logrank.p_value)
```
:::

```{python}
#| include: false
chk = {"chisq": float(approach_logrank.test_statistic), "p": float(approach_logrank.p_value)}
```

```{r}
#| include: false
check_agree(list(chisq = approach_logrank$chisq, p = approach_logrank$pvalue), reticulate::py$chk)
```

- **Observed / Expected:** the posterior hips had 19 revisions where 16.1 were expected; the anterior hips had 18 where 20.9 were expected.
- **Chisq = 0.9 on 1 degree of freedom, p = 0.340:** no clear evidence that the curves differ over the whole follow-up.

But look at the plot. The posterior curve drops sharply in the first months, then the two curves come together and cross. The early revisions are real: by 6 months, survivorship was 88.7% after the posterior approach and 98.6% after the anterior approach.

::: {.panel-tabset group="language"}
## R

```{r}
summary(survfit(Surv(followup_years, revised) ~ approach, data = tha, conf.type = "log-log"), times = 0.5)
```

## Python

```{python}
for curve in [km_anterior, km_posterior]:
    ci = curve.confidence_interval_survival_function_.loc[:0.5].iloc[-1]
    print(curve.label, round(curve.survival_function_at_times(0.5).iloc[0], 3), ci.round(3).to_list())
```
:::

```{python}
#| include: false
ci_anterior = km_anterior.confidence_interval_survival_function_.loc[:0.5].iloc[-1]
ci_posterior = km_posterior.confidence_interval_survival_function_.loc[:0.5].iloc[-1]
chk = {"surv_anterior": float(km_anterior.survival_function_at_times(0.5).iloc[0]),
       "low_anterior": float(ci_anterior.iloc[0]), "high_anterior": float(ci_anterior.iloc[1]),
       "surv_posterior": float(km_posterior.survival_function_at_times(0.5).iloc[0]),
       "low_posterior": float(ci_posterior.iloc[0]), "high_posterior": float(ci_posterior.iloc[1])}
```

```{r}
#| include: false
approach_6m <- summary(survfit(Surv(followup_years, revised) ~ approach, data = tha, conf.type = "log-log"), times = 0.5)
check_agree(list(surv_anterior = approach_6m$surv[1], low_anterior = approach_6m$lower[1],
                 high_anterior = approach_6m$upper[1], surv_posterior = approach_6m$surv[2],
                 low_posterior = approach_6m$lower[2], high_posterior = approach_6m$upper[2]),
            reticulate::py$chk)
```

The log-rank test adds up the differences over the whole follow-up. When one group does worse early and better later, the two parts cancel out, and the test misses a real difference. [Page 14](14-cox-regression.qmd#proportional-hazards) shows how to detect this and how to model it.

**Three or more groups.** The same test compares any number of groups. Does revision differ between implants A, B and C?

::: {.panel-tabset group="language"}
## R

```{r}
implant_logrank <- survdiff(Surv(followup_years, revised) ~ implant, data = cohort)
implant_logrank
```

## Python

```{python}
from lifelines.statistics import multivariate_logrank_test

implant_logrank = multivariate_logrank_test(cohort["followup_years"], cohort["implant"], cohort["revised"])
print(implant_logrank.test_statistic, implant_logrank.degrees_of_freedom, implant_logrank.p_value)
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

- **Observed / Expected:** implant C had 38 revisions where 16.9 were expected. Implants A (25 vs 34.0) and B (18 vs 30.0) had fewer than expected.
- **Chisq = 33.5 on 2 degrees of freedom, p < 0.001:** at least one implant's curve differs from the others. The test doesn't say which; [page 15](../beyond/15-post-hoc.qmd) covers comparing pairs of groups. [Page 8](../catalog/08-three-plus-unmatched.qmd#cox) gives each implant's hazard ratio.

> **Methods:** Revision-free survival was compared between groups with the log-rank test.
>
> **Results:** Revision-free survival differed between implants (log-rank χ² = 33.5, df = 2, p < 0.001). Over the whole follow-up there was no clear evidence of a difference between surgical approaches in total hip arthroplasty (log-rank χ² = 0.9, df = 1, p = 0.340), but the curves crossed: survivorship at 6 months was 88.7% (95% CI 81.7% to 93.2%) after the posterior approach and 98.6% (95% CI 94.5% to 99.6%) after the anterior approach.

::: {.callout-warning}
## ⚠️ Watch out: always plot the curves before you trust the test
The log-rank test is most powerful when one group's risk is a steady multiple of the other's over time. When the curves cross, as with the surgical approach here, a non-significant test can hide a real difference. And don't compare groups at one hand-picked time point to get a significant result: decide your time points before you look.
:::

::: {.callout-tip}
## 🔀 R vs Python: one function or two
R's `survdiff()` takes a formula and handles two groups or more. lifelines has `logrank_test()` for two groups, which takes each group's data separately, and `multivariate_logrank_test()` for any number, which takes a grouping column. They give identical results.
:::

## Competing risks: when patients die first {#competing-risks}

So far, patients who died were treated as censored. That assumes they would have gone on to be revised at the same rate as everyone else. They can't: a patient who has died can never be revised. Death is a **competing risk**.

With death treated as censored, 1 − Kaplan-Meier estimates the risk of revision in an imaginary world where nobody dies. In an older population, where many patients die during follow-up, it **overstates** the real proportion who will be revised. The **cumulative incidence function** (CIF), estimated with the **Aalen-Johansen** method, gives the real proportion: the chance of being revised by a given time, allowing for the chance of dying first.

The data need one status column with three values. In the cohort, `event_status` is 0 for censored, 1 for revised and 2 for died.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4.5
cohort <- cohort |>
  mutate(status = factor(event_status, levels = c(0, 1, 2),
                         labels = c("censored", "revision", "death")))   # censored must come first

# with a three-level status, survfit() estimates the cumulative incidences (Aalen-Johansen)
cif <- survfit2(Surv(followup_years, status) ~ 1, data = cohort, conf.type = "log-log")

cif |>
  ggcuminc(outcome = c("revision", "death")) +
  add_confidence_interval() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Cumulative incidence")

tidy_survfit(cif, times = c(2, 5, 10)) |>
  select(outcome, time, estimate, conf.low, conf.high)

1 - summary(km, times = c(2, 5, 10))$surv    # 1 − Kaplan-Meier, for comparison
```

## Python

```{python}
from scipy.stats import norm
from statsmodels.duration.survfunc import CumIncidenceRight

# event_status: 0 = censored, 1 = revision, 2 = death
cif = CumIncidenceRight(cohort["followup_years"], cohort["event_status"])
revision = pd.DataFrame({"cif": cif.cinc[0], "se": cif.cinc_se[0]}, index=cif.times)   # event type 1
death = pd.DataFrame({"cif": cif.cinc[1], "se": cif.cinc_se[1]}, index=cif.times)      # event type 2

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.step(revision.index, revision["cif"], where="post", label="revision")
ax.step(death.index, death["cif"], where="post", label="death")
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Cumulative incidence")
legend = ax.legend()
plt.tight_layout()
plt.show()

z = norm.ppf(0.975)
for years in [2, 5, 10]:
    row = revision.loc[:years].iloc[-1]                                  # last step at or before that time
    spread = np.exp(z * row["se"] / (row["cif"] * np.log(row["cif"])))   # the log-log CI, as in R
    print(years, round(row["cif"], 3), round(row["cif"] ** (1 / spread), 3), round(row["cif"] ** spread, 3),
          round(1 - km.survival_function_at_times(years).iloc[0], 3))
```
:::

```{python}
#| include: false
chk = {}
for years in [2, 5, 10]:
    chk[f"cif_{years}"] = float(revision.loc[:years].iloc[-1]["cif"])
    chk[f"death_{years}"] = float(death.loc[:years].iloc[-1]["cif"])
row_10 = revision.loc[:10].iloc[-1]
spread_10 = np.exp(z * row_10["se"] / (row_10["cif"] * np.log(row_10["cif"])))
chk["low_10"] = float(row_10["cif"] ** (1 / spread_10))
chk["high_10"] = float(row_10["cif"] ** spread_10)
```

```{r}
#| include: false
cif_table <- tidy_survfit(cif, times = c(2, 5, 10))
revision_rows <- cif_table |> filter(outcome == "revision")
death_rows <- cif_table |> filter(outcome == "death")
check_agree(list(cif_2 = revision_rows$estimate[1], cif_5 = revision_rows$estimate[2], cif_10 = revision_rows$estimate[3],
                 death_2 = death_rows$estimate[1], death_5 = death_rows$estimate[2], death_10 = death_rows$estimate[3],
                 low_10 = revision_rows$conf.low[3], high_10 = revision_rows$conf.high[3]),
            reticulate::py$chk)
```

Reading it:
- **The revision curve** is the cumulative incidence of revision: 5.9% at 2 years, 12.8% at 5 years and 19.3% at 10 years.
- **The death curve** rises faster: 24.0% of patients had died without a revision by 10 years.
- **1 − Kaplan-Meier** says 22.0% by 10 years. It overstates the real proportion revised by 2.7 percentage points, because it pretends the patients who died could still have been revised.

The gap grows with the number of deaths. It's small at 2 years, when few patients have died, and largest in older patients (see exercise 2).

**Comparing groups: Gray's test (R only).** Gray's test is the competing-risks counterpart of the log-rank test: it compares cumulative incidence curves between groups. The tidycmprsk package runs it:

```{r}
#| warning: false
library(tidycmprsk)

cif_by_implant <- cuminc(Surv(followup_years, status) ~ implant, data = cohort)
glance(cif_by_implant) |>
  select(outcome_1, statistic_1, p.value_1, outcome_2, statistic_2, p.value_2)
```

The cumulative incidence of revision differed between implants (Gray's test χ² = 31.5, df = 2, p < 0.001); there was no clear evidence that the cumulative incidence of death differed (χ² = 0.97, p = 0.616).

> **Methods:** The cumulative incidence of revision was estimated with the Aalen-Johansen method, treating death as a competing risk, and compared between implants with Gray's test.
>
> **Results:** The cumulative incidence of revision was 12.8% (95% CI 10.0% to 15.9%) at 5 years and 19.3% (95% CI 15.3% to 23.7%) at 10 years, when the cumulative incidence of death was 24.0%. It differed between implants (Gray's test χ² = 31.5, df = 2, p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: which number answers your question?
Both estimates are useful, but they answer different questions:
- **1 − Kaplan-Meier** answers "how well does the implant perform while patients are alive?" It's the usual measure for comparing implants, and registries report it.
- **The cumulative incidence** answers "what proportion of patients will actually be revised?" Use it to counsel patients or plan services, especially for older patients.

Say which one you report. Never call 1 − Kaplan-Meier "the proportion of patients revised" when many patients died.
:::

::: {.callout-tip}
## 🔀 R vs Python: which tools
- **The cumulative incidence:** R's `survfit()` estimates it whenever the status has more than two levels. In Python, use statsmodels' `CumIncidenceRight()`: it gives the estimates and their standard errors but no CI, so the code builds the same log-log CI as R. lifelines also has an `AalenJohansenFitter`, but it moves tied follow-up times by a small random amount, which can shift an estimate read at exactly 5 or 10 years, so we don't use it.
- **Gray's test:** Python has no mature implementation of Gray's test. Plot the curves in Python, but run the test in R. tidycmprsk's `cuminc()` also gives the cumulative incidences, with a slightly different CI method.
- **Fine-Gray regression** models the cumulative incidence with several predictors at once; it's R only too ([page 14](14-cox-regression.qmd#fine-gray)).
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
km_toy <- summary(toy_km, times = c(1, 3, 5))
approach_6m <- summary(survfit(Surv(followup_years, revised) ~ approach, data = tha, conf.type = "log-log"), times = 0.5)
one_minus_km <- 1 - summary(km, times = 10)$surv
gray <- glance(cif_by_implant)
old <- cohort |> filter(age >= 75)
old_cif <- tidy_survfit(survfit2(Surv(followup_years, status) ~ 1, data = old, conf.type = "log-log"), times = 5) |>
  filter(outcome == "revision")
procedure_5 <- summary(survfit(Surv(followup_years, revised) ~ procedure, data = cohort, conf.type = "log-log"), times = 5)
procedure_logrank <- survdiff(Surv(followup_years, revised) ~ procedure, data = cohort)
implant_cif_5 <- tidy_survfit(survfit2(Surv(followup_years, status) ~ implant, data = cohort, conf.type = "log-log"), times = 5) |>
  filter(outcome == "revision")
stopifnot(
  round(km_toy$surv, 4) == c(0.8333, 0.6250, 0.3125), round(100 * (1 - km_toy$surv[3])) == 69,
  sum(table(cohort$patient_id) == 2) == 80, nrow(cohort) == 600,
  round(follow_up$followup_years, 2) == c(3.30, 3.21, 5.38, 0.27),
  as.numeric(follow_up$end_date[4] - follow_up$surgery_date[4]) == 99,
  summary(km, times = c(0, 4, 8, 10))$n.risk == c(600, 332, 84, 21), 21 < 60,
  round(km_2_5_10$surv, 3) == c(0.939, 0.863, 0.780),
  round(km_2_5_10$lower[3], 3) == 0.725, round(km_2_5_10$upper[3], 3) == 0.826,
  km_2_5_10$n.risk == c(496, 263, 21),
  round(100 * km_2_5_10$lower, 1) == c(91.6, 82.8, 72.5), round(100 * km_2_5_10$upper, 1) == c(95.6, 89.2, 82.6),
  round(median(cohort$followup_years), 3) == 4.365,
  round(unname(follow_up_quartiles), 2) == c(3.52, 5.62, 7.93),
  approach_logrank$obs == c(18, 19), round(approach_logrank$exp, 1) == c(20.9, 16.1),
  round(approach_logrank$chisq, 1) == 0.9, round(approach_logrank$pvalue, 3) == 0.340,
  round(100 * approach_6m$surv, 1) == c(98.6, 88.7),
  round(100 * approach_6m$lower, 1) == c(94.5, 81.7), round(100 * approach_6m$upper, 1) == c(99.6, 93.2),
  implant_logrank$obs == c(25, 18, 38), round(implant_logrank$exp, 1) == c(34.0, 30.0, 16.9),
  round(implant_logrank$chisq, 1) == 33.5, implant_logrank$pvalue < 0.001,
  round(100 * revision_rows$estimate, 1) == c(5.9, 12.8, 19.3),
  round(100 * revision_rows$conf.low[2:3], 1) == c(10.0, 15.3), round(100 * revision_rows$conf.high[2:3], 1) == c(15.9, 23.7),
  round(100 * death_rows$estimate[3], 1) == 24.0,
  round(100 * one_minus_km, 1) == 22.0, round(100 * (one_minus_km - revision_rows$estimate[3]), 1) == 2.7,
  gray$outcome_1 == "revision", round(gray$statistic_1, 1) == 31.5, gray$df_1 == 2, gray$p.value_1 < 0.001,
  gray$outcome_2 == "death", round(gray$statistic_2, 2) == 0.97, round(gray$p.value_2, 3) == 0.616,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(100 * procedure_5$surv, 1) == c(86.9, 85.9),
  round(100 * procedure_5$lower, 1) == c(81.4, 80.9), round(100 * procedure_5$upper, 1) == c(90.8, 89.6),
  round(procedure_logrank$chisq, 2) == 0.01, round(procedure_logrank$pvalue, 3) == 0.937,
  nrow(old) == 100, sum(old$event_status == 1) == 13, sum(old$event_status == 2) == 41,
  round(100 * (1 - summary(survfit(Surv(followup_years, revised) ~ 1, data = old), times = 5)$surv), 1) == 16.5,
  round(100 * old_cif$estimate, 1) == 13.9, round(100 * old_cif$conf.low, 1) == 7.8, round(100 * old_cif$conf.high, 1) == 21.8,
  round(100 * implant_cif_5$estimate, 1) == c(9.7, 6.8, 27.3),
  round(100 * implant_cif_5$conf.low, 1) == c(6.2, 3.7, 19.5), round(100 * implant_cif_5$conf.high, 1) == c(14.1, 11.2, 35.6)
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Compare revision-free survival between total hips (THA) and total knees (TKA). Give each procedure's survivorship at 5 years with its 95% CI, and the log-rank test.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
summary(survfit(Surv(followup_years, revised) ~ procedure, data = cohort, conf.type = "log-log"), times = 5)
survdiff(Surv(followup_years, revised) ~ procedure, data = cohort)
```

## Python

```{python}
for procedure, group in cohort.groupby("procedure"):
    curve = KaplanMeierFitter().fit(group["followup_years"], group["revised"])
    ci = curve.confidence_interval_survival_function_.loc[:5].iloc[-1]
    print(procedure, round(curve.survival_function_at_times(5).iloc[0], 3), ci.round(3).to_list())

hips = cohort[cohort["procedure"] == "THA"]
knees = cohort[cohort["procedure"] == "TKA"]
procedure_logrank = logrank_test(hips["followup_years"], knees["followup_years"],
                                 event_observed_A=hips["revised"], event_observed_B=knees["revised"])
print(procedure_logrank.test_statistic, procedure_logrank.p_value)
```
:::

Survivorship free of revision at 5 years was 86.9% (95% CI 81.4% to 90.8%) after THA and 85.9% (95% CI 80.9% to 89.6%) after TKA. There was no clear evidence of a difference between the procedures (log-rank χ² = 0.01, df = 1, p = 0.937).
:::

**2.** A surgeon asks: "Of my patients aged 75 and over, what proportion will need a revision within 5 years?" Which estimate answers that question? Calculate it, and compare it with 1 − Kaplan-Meier.

::: {.callout-tip collapse="true"}
## Solution
The surgeon wants the real proportion of patients revised, and many patients over 75 die during follow-up. That's the **cumulative incidence**, with death as a competing risk.

::: {.panel-tabset group="language"}
## R

```{r}
old <- cohort |> filter(age >= 75)
count(old, status)

survfit2(Surv(followup_years, status) ~ 1, data = old, conf.type = "log-log") |>
  tidy_survfit(times = 5) |>
  select(outcome, estimate, conf.low, conf.high)
1 - summary(survfit(Surv(followup_years, revised) ~ 1, data = old), times = 5)$surv
```

## Python

```{python}
old = cohort[cohort["age"] >= 75]
print(old["event_status"].value_counts().sort_index())

old_cif = CumIncidenceRight(old["followup_years"], old["event_status"])
old_revision = pd.DataFrame({"cif": old_cif.cinc[0], "se": old_cif.cinc_se[0]}, index=old_cif.times)
row = old_revision.loc[:5].iloc[-1]
spread = np.exp(z * row["se"] / (row["cif"] * np.log(row["cif"])))
print(round(row["cif"], 3), round(row["cif"] ** (1 / spread), 3), round(row["cif"] ** spread, 3))

old_km = KaplanMeierFitter().fit(old["followup_years"], old["revised"])
print(1 - old_km.survival_function_at_times(5).iloc[0])
```
:::

Of the 100 procedures in patients aged 75 and over, 41 ended in death and only 13 in revision. The cumulative incidence of revision at 5 years was 13.9% (95% CI 7.8% to 21.8%). 1 − Kaplan-Meier gives 16.5%, overstating it by about a fifth.
:::

**3.** Estimate the cumulative incidence of revision at 5 years for each implant, with death as a competing risk, and write the Results sentence, including Gray's test.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
survfit2(Surv(followup_years, status) ~ implant, data = cohort, conf.type = "log-log") |>
  tidy_survfit(times = 5) |>
  filter(outcome == "revision") |>
  select(strata, estimate, conf.low, conf.high)
```

## Python

```{python}
for implant, group in cohort.groupby("implant"):
    implant_cif = CumIncidenceRight(group["followup_years"], group["event_status"])
    implant_revision = pd.DataFrame({"cif": implant_cif.cinc[0], "se": implant_cif.cinc_se[0]}, index=implant_cif.times)
    row = implant_revision.loc[:5].iloc[-1]
    spread = np.exp(z * row["se"] / (row["cif"] * np.log(row["cif"])))
    print(implant, round(row["cif"], 3), round(row["cif"] ** (1 / spread), 3), round(row["cif"] ** spread, 3))
```

Python has no Gray's test; take it from R.
:::

The cumulative incidence of revision at 5 years, with death as a competing risk, was 9.7% (95% CI 6.2% to 14.1%) with implant A, 6.8% (95% CI 3.7% to 11.2%) with implant B and 27.3% (95% CI 19.5% to 35.6%) with implant C (Gray's test χ² = 31.5, df = 2, p < 0.001).
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render survival/13-kaplan-meier.qmd
uv run pytest tests/site -q
```

Expected:
- The render completes.
- Then `1 failed, 227 passed`: `test_freshness.py::test_just_data_re_renders_the_pages_that_read_data` fails with `` `just data` must re-render: ['survival'] ``. Page 13 reads `data/`, so `just data` must re-render its folder.

- [ ] **Step 5: Re-render survival pages in `just data`**

In `Justfile`, replace

```
    # (Rendering a folder always re-runs its code.) Add survival, beyond, ... as they gain code.
    quarto render foundations
    quarto render catalog
```

with

```
    # (Rendering a folder always re-runs its code.) Add beyond, report, ... as they gain code.
    quarto render foundations
    quarto render catalog
    quarto render survival
```

Run: `uv run pytest tests/site -q`

Expected: `228 passed`.

- [ ] **Step 6: Prove the CI check bites, then restore**

In the `#kaplan-meier` section's R block, replace the two lines

```r
km <- survfit2(Surv(followup_years, revised) ~ 1, data = cohort,
               conf.type = "log-log")              # the CI method lifelines uses
```

with `km <- survfit2(Surv(followup_years, revised) ~ 1, data = cohort)`, then run `quarto render survival/13-kaplan-meier.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'low_2'`. R's default "log" CI differs from lifelines' log-log CI. Undo the change, then run:

```bash
rm -rf survival/13-kaplan-meier_files
quarto render survival/13-kaplan-meier.qmd
uv run pytest tests/site -q
```

Expected: `228 passed`.

- [ ] **Step 7: Commit**

```bash
git add survival/13-kaplan-meier.qmd _freeze/survival/13-kaplan-meier tests/site/sitelib.py tests/site/test_catalog.py \
        tests/site/test_sources.py tests/site/test_survival.py Justfile
git commit -m "Write page 13, Kaplan-Meier and the log-rank test: censoring, time zero, survivorship, follow-up, competing risks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Page 14, Cox proportional hazards regression

**Files:**
- Modify: `survival/14-cox-regression.qmd` (replace the stub)
- Create: `_freeze/survival/14-cox-regression/` (render output; commit it)
- Modify: `tests/site/test_survival.py`

**Interfaces:**
- Consumes:
  - Task 1's tidycmprsk (`crr()`) and broom.helpers
  - Task 2's `test_survival.py` (`SECTIONS`, `KM`, `code_of`) and `sitelib.py` helpers
  - page 13's anchors `#log-rank`, `#competing-risks` and `#time-zero`
  - pages 7 and 9's `#stratified-cox`, page 8's, 11's and 12's `#cox`, and page 12's `#multiple-nonlinear-regression`
  - `data/cohort.csv`
- Produces: page 14 anchors `#hazard-ratio`, `#choosing-covariates`, `#univariable-multivariable`, `#linearity`, `#proportional-hazards`, `#remedies`, `#stratified-cox`, `#fine-gray`, `#reporting` and `#exercises`. Page 13 links to `#proportional-hazards`, `#stratified-cox` and `#fine-gray`; Task 4 links to `#proportional-hazards`, `#choosing-covariates` and `#fine-gray`.

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_survival.py`, replace

```python
# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
}
KM = "survival/13-kaplan-meier.html"
```

with

```python
# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
    "survival/14-cox-regression.html": [
        "hazard-ratio", "choosing-covariates", "univariable-multivariable", "linearity",
        "proportional-hazards", "remedies", "stratified-cox", "fine-gray", "reporting", "exercises"],
}
KM = "survival/13-kaplan-meier.html"
COX = "survival/14-cox-regression.html"
```

and append to the end of the file (after two blank lines):

```python
# ---- page 14: Cox regression ---------------------------------------------------

def test_covariates_are_chosen_in_advance_with_enough_events(site):
    text = text_of(section(COX, "choosing-covariates"))
    assert "chosen before you look" in text and "10 events per term" in text


def test_proportional_hazards_are_checked_on_the_built_in_violation(site):
    found = section(COX, "proportional-hazards")
    assert "Schoenfeld" in text_of(found) and "cox.zph(" in code_of(found)
    plotted = [tabset for tabset in found.select("div.panel-tabset")
               if all(pane.select("img") for pane in tabset.select("div.tab-pane"))]
    assert plotted, "the residual plot is drawn in both languages"
    assert "approach" in code_of(plotted[0])


def test_remedies_cover_stratification_and_a_time_split(site):
    code = code_of(section(COX, "remedies"))
    for call in ["strata(approach)", 'strata=["approach"]', "survSplit(", "CoxTimeVaryingFitter("]:
        assert call in code, call


def test_stratified_cox_covers_matched_sets_and_bilateral_patients(site):
    found = section(COX, "stratified-cox")
    hrefs = [a["href"] for a in found.select("a[href]")]
    for target in ["07-two-paired-groups.html#stratified-cox", "09-three-plus-matched.html#stratified-cox"]:
        assert any(href.endswith(target) for href in hrefs), target
    code = code_of(found)
    assert "cluster = patient_id" in code and 'cluster_col="patient_id"' in code


def test_fine_gray_is_labeled_r_only(site):
    found = section(COX, "fine-gray")
    assert "(R only)" in found.select_one("h2").get_text()
    assert found.select("pre.r") and not found.select("pre.python")
    assert "subdistribution hazard ratio" in text_of(found)


def test_reporting_gives_univariable_and_multivariable_hazard_ratios(site):
    found = section(COX, "reporting")
    table = found.select_one("table")
    assert table is not None and "Univariable" in text_of(table) and "Multivariable" in text_of(table)
    assert "Univariable HR (95% CI)" in " ".join(out.get_text() for out in found.select(".cell-output"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `10 failed, 230 passed`. All 10 failures are page-14 tests; the no-warnings and short-outputs tests pass trivially on a stub.

- [ ] **Step 3: Write the page**

Replace `survival/14-cox-regression.qmd` with:

````markdown
---
title: "14 · Cox proportional hazards regression"
description: "Hazard ratios, choosing covariates, univariable and multivariable Cox models, checking straight-line effects and proportional hazards, remedies, stratified Cox for matched sets and bilateral patients, Fine-Gray regression, and reporting."
engine: knitr
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

[Page 13](13-kaplan-meier.qmd) compared survival curves. **Cox regression** goes further: it gives each group or predictor a **hazard ratio** with a 95% CI, and it can adjust for several predictors at once. Pages [8](../catalog/08-three-plus-unmatched.qmd#cox), [11](../catalog/11-predict-from-one.qmd#cox) and [12](../catalog/12-predict-from-several.qmd#cox) each fitted a Cox model in a few steps. This page covers the whole job:
- what a hazard ratio means
- how to choose covariates
- how to check the model's assumptions, and what to do when one fails
- how to handle matched sets and bilateral patients
- how to model competing risks
- how to report the result

::: {.callout-note}
## 💡 How this page works
Run the code blocks in order, from the top: later blocks use the packages, data and models made earlier.

Until the section on [bilateral patients](#stratified-cox), the examples use every case as if it were a separate patient, including the 80 patients who had both sides operated on.
:::

## The hazard ratio {#hazard-ratio}

The **hazard** is the rate of revision at a given moment among the implants still in place: the chance that an unrevised implant is revised in the next short interval. It can rise or fall over time. The **hazard ratio** (HR) divides one group's hazard by another's. A Cox model assumes that this ratio stays the same over the whole follow-up, even if the hazards themselves change: the hazards are **proportional**.

Here is the Cox model for implant alone, with implant A as the reference:

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)
library(ggsurvfit)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(age_10 = age / 10,                 # hazard ratios per 10 years of age
         bmi_5 = bmi / 5)                   # and per 5 kg/m² of BMI

implant_model <- coxph(Surv(followup_years, revised) ~ implant, data = cohort)
summary(implant_model)
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, KaplanMeierFitter

cohort = pd.read_csv("data/cohort.csv")
cohort["age_10"] = cohort["age"] / 10       # hazard ratios per 10 years of age
cohort["bmi_5"] = cohort["bmi"] / 5         # and per 5 kg/m² of BMI

implant_model = CoxPHFitter().fit(
    cohort[["followup_years", "revised", "implant"]],
    duration_col="followup_years", event_col="revised", formula="implant",
    fit_options={"precision": 1e-12},        # stop only when fully converged; see the R vs Python box
)
print(implant_model.summary[["coef", "exp(coef)", "se(coef)", "exp(coef) lower 95%",
                             "exp(coef) upper 95%", "z", "p"]].round(3))
print(implant_model.concordance_index_)                              # concordance
print(implant_model.log_likelihood_ratio_test().test_statistic)     # overall likelihood ratio test
```
:::

```{python}
#| include: false
rows = implant_model.summary
chk = {"hr_b": float(rows.loc["implant[T.B]", "exp(coef)"]), "hr_c": float(rows.loc["implant[T.C]", "exp(coef)"]),
       "low_c": float(rows.loc["implant[T.C]", "exp(coef) lower 95%"]),
       "high_c": float(rows.loc["implant[T.C]", "exp(coef) upper 95%"]),
       "p_c": float(rows.loc["implant[T.C]", "p"]),
       "lr": float(implant_model.log_likelihood_ratio_test().test_statistic),
       "concordance": float(implant_model.concordance_index_)}
```

```{r}
#| include: false
implant_hr <- summary(implant_model)$conf.int
check_agree(list(hr_b = implant_hr["implantB", "exp(coef)"], hr_c = implant_hr["implantC", "exp(coef)"],
                 low_c = implant_hr["implantC", "lower .95"], high_c = implant_hr["implantC", "upper .95"],
                 p_c = summary(implant_model)$coefficients["implantC", "Pr(>|z|)"],
                 lr = unname(summary(implant_model)$logtest["test"]),
                 concordance = unname(summary(implant_model)$concordance["C"])),
            reticulate::py$chk)
```

Reading the output, line by line:
- **n = 600, number of events = 81:** the procedures and the revisions. The revisions, not the procedures, set how much a Cox model can learn.
- **coef:** the log hazard ratio. Nobody reports it; it's what the model estimates.
- **exp(coef):** the **hazard ratio**. Implant C: 3.07. At any moment during follow-up, an unrevised implant C was revised at about three times the rate of an unrevised implant A. Implant B: 0.82.
- **se(coef), z, Pr(>|z|):** the standard error of the coefficient, and the Wald test of whether the hazard ratio differs from 1 (p < 0.001 for C, p = 0.514 for B).
- **lower .95 / upper .95:** the 95% CI of each hazard ratio: 1.85 to 5.09 for C, 0.45 to 1.50 for B.
- **Concordance = 0.659:** how often, in pairs of patients, the one revised sooner had the higher predicted risk. 0.5 is a coin toss and 1 is perfect.
- **Likelihood ratio, Wald and score tests:** three versions of the overall test that implant matters at all. With enough events they agree; the likelihood ratio test (27.6 on 2 df, p < 0.001) is the most reliable. Python prints the concordance and then this test under the table.

::: {.callout-tip}
## 🔀 R vs Python: convergence and the printout
Both programs handle tied revision times with Efron's method and use the first group alphabetically (A) as the reference. lifelines' default rule for when to stop iterating stops slightly early, so its hazard ratios can differ from R's in the fifth or sixth digit. Every Python model on this page tightens it with `fit_options={"precision": 1e-12}`. R's `summary()` prints the concordance and three overall tests; lifelines keeps them in `concordance_index_` and `log_likelihood_ratio_test()`. (lifelines' `print_summary()` shows everything at once, including the time the model was fitted.)
:::

::: {.callout-warning}
## ⚠️ Watch out: a hazard ratio isn't a risk ratio
"Three times the hazard" doesn't mean three times as many revisions by 5 years. By 5 years, 28.9% of implant C knees and hips had been revised (1 − Kaplan-Meier), against 10.1% of implant A: 2.85 times as many, not 3.07. The two ratios are close when revisions are rare and drift apart as they become common. Report the hazard ratio as a ratio of rates, and give the cumulative risks separately.
:::

::: {.panel-tabset group="language"}
## R

```{r}
km_by_implant <- survfit(Surv(followup_years, revised) ~ implant, data = cohort)
1 - summary(km_by_implant, times = 5)$surv    # revised by 5 years: A, B, C
```

## Python

```{python}
for implant, group in cohort.groupby("implant"):
    implant_km = KaplanMeierFitter().fit(group["followup_years"], group["revised"])
    print(implant, round(1 - implant_km.survival_function_at_times(5).iloc[0], 3))   # revised by 5 years
```
:::

```{python}
#| include: false
chk = {}
for implant, group in cohort.groupby("implant"):
    chk[f"risk_{implant}"] = float(1 - KaplanMeierFitter().fit(group["followup_years"], group["revised"]).survival_function_at_times(5).iloc[0])
```

```{r}
#| include: false
risk_5 <- 1 - summary(km_by_implant, times = 5)$surv
check_agree(list(risk_A = risk_5[1], risk_B = risk_5[2], risk_C = risk_5[3]), reticulate::py$chk)
```

## Choosing covariates {#choosing-covariates}

A study comparing implants has one question: does implant C carry a higher revision risk than implant A? The other predictors in the model are there to make that comparison fair. These **covariates** are chosen before you look at the results, for a reason you can write down:

- **Adjust for confounders:** factors that affect both which implant a patient gets and their risk of revision. Age, sex and BMI are the usual ones in arthroplasty: surgeons may choose implants differently for older, heavier or female patients, and these factors can change revision risk.
- **Don't adjust for what the implant causes.** A dislocation or a reoperation that follows the implant choice is part of the implant's effect, not a reason for it. Adjusting for it hides the effect you're trying to measure.
- **Don't choose covariates from the data.** Keeping only the predictors with p < 0.2 in univariable models, or letting a stepwise procedure pick them, makes p-values and CIs look more certain than they are and gives different answers in every sample.

**Events limit the model.** A Cox model needs about **10 events per term**, where a term is one coefficient: a two-level predictor like sex is one term, implant (B and C against A) is two, and a spline with 3 degrees of freedom is three. The practice cohort has 81 revisions, enough for about eight terms. Implant, age, sex and BMI use five, about 16 events per term. With fewer events, adjust for fewer things, and say so.

## From univariable to multivariable {#univariable-multivariable}

A **univariable** (or unadjusted) model has one predictor, like the implant model above. A **multivariable** (or adjusted) model has several; each hazard ratio is then that predictor's effect with the others held fixed.

::: {.panel-tabset group="language"}
## R

```{r}
adjusted_model <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + bmi_5, data = cohort)
summary(adjusted_model)$conf.int
```

## Python

```{python}
cox_data = cohort[["followup_years", "revised", "implant", "age_10", "sex", "bmi_5"]]
adjusted_model = CoxPHFitter().fit(cox_data, duration_col="followup_years", event_col="revised",
                                   formula="implant + age_10 + sex + bmi_5", fit_options={"precision": 1e-12})
print(adjusted_model.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

```{python}
#| include: false
rows = adjusted_model.summary
chk = {"hr_c": float(rows.loc["implant[T.C]", "exp(coef)"]),
       "low_c": float(rows.loc["implant[T.C]", "exp(coef) lower 95%"]),
       "high_c": float(rows.loc["implant[T.C]", "exp(coef) upper 95%"]),
       "hr_b": float(rows.loc["implant[T.B]", "exp(coef)"]), "hr_age": float(rows.loc["age_10", "exp(coef)"]),
       "hr_male": float(rows.loc["sex[T.Male]", "exp(coef)"]), "hr_bmi": float(rows.loc["bmi_5", "exp(coef)"])}
```

```{r}
#| include: false
adjusted_hr <- summary(adjusted_model)$conf.int
check_agree(list(hr_c = adjusted_hr["implantC", "exp(coef)"], low_c = adjusted_hr["implantC", "lower .95"],
                 high_c = adjusted_hr["implantC", "upper .95"], hr_b = adjusted_hr["implantB", "exp(coef)"],
                 hr_age = adjusted_hr["age_10", "exp(coef)"], hr_male = adjusted_hr["sexMale", "exp(coef)"],
                 hr_bmi = adjusted_hr["bmi_5", "exp(coef)"]),
            reticulate::py$chk)
```

Implant C's hazard ratio moved from 3.07 unadjusted to **3.19 adjusted** (95% CI 1.92 to 5.29). Age, sex and BMI don't explain the difference between the implants. When an adjusted estimate moves a lot, the covariates were confounding the unadjusted one; say so in the Discussion.

::: {.callout-warning}
## ⚠️ Watch out: the covariates' own hazard ratios aren't findings
The model also prints hazard ratios for age, sex and BMI. Men's hazard of revision was about half of women's (0.51, 95% CI 0.32 to 0.81). It's tempting to report that as a second result, but the model wasn't built to answer it: nobody chose covariates that would make the comparison of men and women fair. Report the covariates' estimates in the table, and describe any you discuss as exploratory, as [page 12](../catalog/12-predict-from-several.qmd#cox) does.
:::

## Is the effect a straight line? {#linearity}

A measured predictor like age enters the model as a straight line: each extra 10 years multiplies the hazard by the same amount, whether from 50 to 60 or from 75 to 85. To check, let the effect bend with a **natural cubic spline** ([page 12](../catalog/12-predict-from-several.qmd#multiple-nonlinear-regression) explains splines) and compare the two models with a likelihood ratio test:

::: {.panel-tabset group="language"}
## R

```{r}
library(splines)

age_spline_model <- coxph(Surv(followup_years, revised) ~ implant + ns(age, df = 3) + sex + bmi_5,
                          data = cohort)
anova(adjusted_model, age_spline_model)    # likelihood ratio test: does the bend help?
```

## Python

```{python}
import patsy
from scipy.stats import chi2

age_knots = list(cohort["age"].quantile([1/3, 2/3]))       # the same knots R's ns(df = 3) uses
age_low, age_high = cohort["age"].min(), cohort["age"].max()
age_spline = patsy.dmatrix("cr(age, knots=age_knots, lower_bound=age_low, upper_bound=age_high,"
                           " constraints='center') - 1", cohort, return_type="dataframe")
age_spline.columns = ["age_1", "age_2", "age_3"]           # three spline terms

spline_data = pd.concat([cox_data.drop(columns="age_10"), age_spline], axis=1)
age_spline_model = CoxPHFitter().fit(spline_data, duration_col="followup_years", event_col="revised",
                                     formula="implant + age_1 + age_2 + age_3 + sex + bmi_5",
                                     fit_options={"precision": 1e-12})

lr_stat = 2 * (age_spline_model.log_likelihood_ - adjusted_model.log_likelihood_)
print(lr_stat, chi2.sf(lr_stat, df=2))     # likelihood ratio test: 3 spline terms vs 1 straight line
```
:::

```{python}
#| include: false
chk = {"lr": float(lr_stat), "p": float(chi2.sf(lr_stat, df=2))}
```

```{r}
#| include: false
age_bend <- anova(adjusted_model, age_spline_model)
check_agree(list(lr = age_bend$Chisq[2], p = age_bend$`Pr(>|Chi|)`[2]), reticulate::py$chk)
```

The spline didn't clearly improve the fit (χ² = 0.29, df = 2, p = 0.864), so the straight line for age stands. Report the check in the Methods. (Exercise 2 checks BMI.)

## Checking proportional hazards {#proportional-hazards}

The Cox model assumes each hazard ratio stays the same over the whole follow-up. The standard check uses **Schoenfeld residuals**. At each revision, the model compares the revised patient's predictors with those of everyone still at risk. Rescaled and added to the model's coefficient, each residual estimates the log hazard ratio at that moment. If the hazard ratio is constant, these estimates scatter around a flat line; if they drift with time, the assumption fails.

**First, the adjusted model.**

::: {.panel-tabset group="language"}
## R

```{r}
cox.zph(adjusted_model)    # one test per predictor, and a global test
```

## Python

```{python}
from lifelines.statistics import proportional_hazard_test

ph_test = proportional_hazard_test(adjusted_model, cox_data, time_transform="km")
print(ph_test.summary[["test_statistic", "p"]])
```
:::

```{python}
#| include: false
chk = {"hr_age": float(adjusted_model.summary.loc["age_10", "exp(coef)"])}
```

```{r}
#| include: false
# The two proportional-hazards tests use different formulas (see the R vs Python box),
# so only the model they test is compared here.
check_agree(list(hr_age = adjusted_hr["age_10", "exp(coef)"]), reticulate::py$chk)
```

No predictor's hazard ratio clearly changed over time (global test p = 0.359; BMI had the smallest p-value, 0.106). That's no clear evidence against proportional hazards, which isn't the same as proof that they hold: with 81 revisions, the test can miss a modest change.

**Now a real violation.** The practice data have one built in: in total hips, the posterior approach has a much higher revision rate in the first months after surgery (early dislocation), and no higher rate after that. [Page 13](13-kaplan-meier.qmd#log-rank) showed the curves crossing.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4
tha <- cohort |> filter(procedure == "THA")
approach_model <- coxph(Surv(followup_years, revised) ~ approach, data = tha)
approach_zph <- cox.zph(approach_model)
approach_zph

plot(approach_zph, resid = TRUE, se = TRUE)          # the log hazard ratio over time
abline(h = coef(approach_model), lty = 2)            # the single hazard ratio the model assumes
```

## Python

```{python}
from statsmodels.nonparametric.smoothers_lowess import lowess

tha = cohort[cohort["procedure"] == "THA"]
tha_data = tha[["followup_years", "revised", "approach"]]
approach_model = CoxPHFitter().fit(tha_data, duration_col="followup_years", event_col="revised",
                                   formula="approach", fit_options={"precision": 1e-12})
print(proportional_hazard_test(approach_model, tha_data, time_transform="km").summary[["test_statistic", "p"]])

# scaled Schoenfeld residuals, one per revision; adding the coefficient gives the log hazard ratio over time
residuals = approach_model.compute_residuals(tha_data, kind="scaled_schoenfeld")
log_hr = residuals["approach[T.posterior]"] + approach_model.params_["approach[T.posterior]"]
years = tha_data.loc[log_hr.index, "followup_years"]

fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(years, log_hr, s=12)
trend = lowess(log_hr, np.log(years), frac=2/3, it=0)     # smooth trend; it=0 keeps every point's full weight
ax.plot(np.exp(trend[:, 0]), trend[:, 1])
ax.axhline(approach_model.params_["approach[T.posterior]"], linestyle="--")   # the single hazard ratio the model assumes
ax.set_xscale("log")                                       # spreads out the early revisions
ax.set_xticks([0.1, 0.5, 1, 2, 5], labels=["0.1", "0.5", "1", "2", "5"])
ax.set_xlabel("Years since surgery (log scale)")
ax.set_ylabel("Log hazard ratio, posterior vs anterior")
plt.tight_layout()
plt.show()
```
:::

```{python}
#| include: false
chk = {"hr": float(approach_model.summary.loc["approach[T.posterior]", "exp(coef)"]),
       "mean_log_hr": float(log_hr.mean()), "early_log_hr": float(log_hr[years <= 0.5].mean())}
```

```{r}
#| include: false
# zph$y holds the same scaled Schoenfeld residuals plus the coefficient, one per revision
check_agree(list(hr = unname(exp(coef(approach_model))), mean_log_hr = mean(approach_zph$y),
                 early_log_hr = mean(approach_zph$y[approach_zph$time <= 0.5])),
            reticulate::py$chk)
```

- **The test:** p < 0.001 (R's χ² = 11.3 on 1 df). The posterior approach's hazard ratio isn't constant.
- **The points:** one per revision. Points near +2 are posterior hips and points near −2 are anterior hips, so early on almost every point sits high.
- **The solid line** smooths the points into an estimate of the log hazard ratio at each time. It starts high in the first months, when posterior hips were revised far more often, then falls below the dashed line, which marks the model's single hazard ratio of 1.37 (log hazard ratio 0.31).

That single hazard ratio (1.37, 95% CI 0.72 to 2.61) averages a large early effect with a later one in the other direction. It describes no actual moment of follow-up, so don't report it.

::: {.callout-warning}
## ⚠️ Watch out: test and look
With many events, the test flags changes too small to matter; with few, it misses real ones. Always look at the plot too. And report a non-significant test as "no clear evidence that the hazard ratios changed over time", never as proof that the assumption holds.
:::

::: {.callout-tip}
## 🔀 R vs Python: two versions of the test
R's `cox.zph()` (survival 3.0 and later) computes the full score test, one per predictor, with implant's two terms tested together. lifelines' `proportional_hazard_test()` uses Grambsch and Therneau's simpler original approximation and tests every column separately (implant B and implant C each get their own line). The statistics differ slightly (11.3 in R, 11.2 in Python for the approach) and lead to the same conclusions here. lifelines' scaled Schoenfeld residuals leave out the coefficient that R adds, so the Python code adds it back. R's plot spaces the revisions evenly along the time axis (its "km" scale); the Python plot uses a log scale for the same reason: to keep the many early revisions from piling up at zero.
:::

## When hazards aren't proportional {#remedies}

There are two common fixes. Which one fits depends on whether you need the hazard ratio of the predictor that breaks the assumption.

**1. Stratify, when it's only an adjustment.** Suppose the question is implant, in total hips, and approach is just a covariate. A Cox model **stratified** by approach gives each approach its own baseline hazard, of any shape, and estimates the implant hazard ratios within approaches. Approach gets no hazard ratio of its own, so its non-proportional effect no longer matters.

::: {.panel-tabset group="language"}
## R

```{r}
stratified_model <- coxph(Surv(followup_years, revised) ~ implant + strata(approach), data = tha)
summary(stratified_model)$conf.int
```

## Python

```{python}
stratified_model = CoxPHFitter().fit(tha[["followup_years", "revised", "implant", "approach"]],
                                     duration_col="followup_years", event_col="revised", formula="implant",
                                     strata=["approach"], fit_options={"precision": 1e-12})
print(stratified_model.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

```{python}
#| include: false
rows = stratified_model.summary
chk = {"hr_b": float(rows.loc["implant[T.B]", "exp(coef)"]), "hr_c": float(rows.loc["implant[T.C]", "exp(coef)"]),
       "low_c": float(rows.loc["implant[T.C]", "exp(coef) lower 95%"]),
       "high_c": float(rows.loc["implant[T.C]", "exp(coef) upper 95%"])}
```

```{r}
#| include: false
stratified_hr <- summary(stratified_model)$conf.int
check_agree(list(hr_b = stratified_hr["implantB", "exp(coef)"], hr_c = stratified_hr["implantC", "exp(coef)"],
                 low_c = stratified_hr["implantC", "lower .95"], high_c = stratified_hr["implantC", "upper .95"]),
            reticulate::py$chk)
```

In total hips, with approach as a stratum, implant C's hazard ratio was 2.11 (95% CI 1.02 to 4.40) against implant A.

**2. Split the follow-up, when you need the effect.** If the approach *is* the question, give it one hazard ratio for the first 6 months and another for the time after. Each patient followed beyond 6 months gets two rows, one per period; the model then estimates the approach's effect separately in each:

::: {.panel-tabset group="language"}
## R

```{r}
# one row per patient per period: (0, 0.5] years and (0.5, end of follow-up]
tha_split <- survSplit(Surv(followup_years, revised) ~ ., data = tha, cut = 0.5, episode = "period") |>
  mutate(posterior_early = as.numeric(approach == "posterior" & period == 1),
         posterior_late  = as.numeric(approach == "posterior" & period == 2))

split_model <- coxph(Surv(tstart, followup_years, revised) ~ posterior_early + posterior_late,
                     data = tha_split)
summary(split_model)$conf.int
```

## Python

```{python}
from lifelines import CoxTimeVaryingFitter

hips = tha.reset_index(drop=True)
hips["id"] = hips.index                                   # one ID per hip, shared by its rows

early = hips.copy()                                       # row 1: surgery to 6 months
early["start"] = 0.0
early["stop"] = early["followup_years"].clip(upper=0.5)
early["event"] = ((early["followup_years"] <= 0.5) & (early["revised"] == 1)).astype(int)
early["period"] = 1

late = hips[hips["followup_years"] > 0.5].copy()          # row 2: 6 months onward, if followed that long
late["start"] = 0.5
late["stop"] = late["followup_years"]
late["event"] = late["revised"]
late["period"] = 2

tha_split = pd.concat([early, late])
tha_split["posterior_early"] = ((tha_split["approach"] == "posterior") & (tha_split["period"] == 1)).astype(int)
tha_split["posterior_late"] = ((tha_split["approach"] == "posterior") & (tha_split["period"] == 2)).astype(int)

split_model = CoxTimeVaryingFitter().fit(
    tha_split[["id", "start", "stop", "event", "posterior_early", "posterior_late"]],
    id_col="id", event_col="event", start_col="start", stop_col="stop", fit_options={"precision": 1e-12})
print(split_model.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

```{python}
#| include: false
rows = split_model.summary
chk = {"hr_early": float(rows.loc["posterior_early", "exp(coef)"]),
       "low_early": float(rows.loc["posterior_early", "exp(coef) lower 95%"]),
       "high_early": float(rows.loc["posterior_early", "exp(coef) upper 95%"]),
       "hr_late": float(rows.loc["posterior_late", "exp(coef)"]),
       "low_late": float(rows.loc["posterior_late", "exp(coef) lower 95%"]),
       "high_late": float(rows.loc["posterior_late", "exp(coef) upper 95%"])}
```

```{r}
#| include: false
split_hr <- summary(split_model)$conf.int
check_agree(list(hr_early = split_hr["posterior_early", "exp(coef)"], low_early = split_hr["posterior_early", "lower .95"],
                 high_early = split_hr["posterior_early", "upper .95"], hr_late = split_hr["posterior_late", "exp(coef)"],
                 low_late = split_hr["posterior_late", "lower .95"], high_late = split_hr["posterior_late", "upper .95"]),
            reticulate::py$chk)
```

In the first 6 months, the hazard of revision was 8.47 times higher after the posterior approach (95% CI 1.93 to 37.3). After 6 months the estimate was 0.43 (95% CI 0.16 to 1.16), which is imprecise. The CI for the early effect is wide because it rests on 16 early revisions.

Choose the cut point before you look, from clinical reasoning: here, the period of highest dislocation risk after hip replacement. Trying several cut points until one gives a striking result is data dredging. R can also let a hazard ratio change smoothly with time (the `tt()` argument of `coxph()`), which avoids choosing a cut point.

> **Methods:** Proportional hazards were checked with scaled Schoenfeld residuals. Because the effect of surgical approach changed over time, its hazard ratio was estimated separately for the first 6 months after surgery and thereafter.
>
> **Results:** The posterior approach was associated with a higher hazard of revision in the first 6 months (hazard ratio 8.47, 95% CI 1.93 to 37.3); after 6 months the estimate was imprecise (0.43, 95% CI 0.16 to 1.16).

## Stratified Cox: matched sets and bilateral patients {#stratified-cox}

A Cox model assumes every row is an independent patient. Two common designs break that.

**Matched sets.** When each implant C patient is matched with similar patients who got other implants, the matched patients belong together. A Cox model **stratified by matched set**, `strata(set_id)`, compares implants only within sets. The decision table calls this *conditional proportional hazards regression*. [Page 7](../catalog/07-two-paired-groups.qmd#stratified-cox) works through matched pairs and [page 9](../catalog/09-three-plus-matched.qmd#stratified-cox) matched sets of three.

**Bilateral patients.** 80 patients in the cohort had both sides replaced. Their two joints share the same patient's bone, activity and surgeon, so their outcomes aren't independent, and treating them as independent makes the CIs too narrow. There are three common choices:

- **Keep both joints and use robust standard errors** clustered on patient. The hazard ratios don't change; the CIs allow for the pairing. This is the usual choice.
- **Stratify by patient**, `strata(patient_id)`, to compare the two sides of each patient. Only patients whose two joints differ in the predictor, and who had a revision, contribute anything, so it's rarely precise enough.
- **Keep one joint per patient**, such as the first one operated on. Simple, but it throws away data.

::: {.panel-tabset group="language"}
## R

```{r}
clustered_model <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + bmi_5,
                         data = cohort, cluster = patient_id)    # robust SEs, clustered on patient
summary(clustered_model)$coefficients[, c("exp(coef)", "se(coef)", "robust se", "Pr(>|z|)")]
summary(clustered_model)$conf.int["implantC", ]
```

## Python

```{python}
clustered_model = CoxPHFitter().fit(
    cohort[["followup_years", "revised", "implant", "age_10", "sex", "bmi_5", "patient_id"]],
    duration_col="followup_years", event_col="revised", formula="implant + age_10 + sex + bmi_5",
    cluster_col="patient_id",                              # robust SEs, clustered on patient
    fit_options={"precision": 1e-12},
)
print(clustered_model.summary[["exp(coef)", "se(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

```{python}
#| include: false
rows = clustered_model.summary
chk = {"se_b": float(rows.loc["implant[T.B]", "se(coef)"]), "se_c": float(rows.loc["implant[T.C]", "se(coef)"]),
       "se_age": float(rows.loc["age_10", "se(coef)"]), "se_male": float(rows.loc["sex[T.Male]", "se(coef)"]),
       "se_bmi": float(rows.loc["bmi_5", "se(coef)"])}
```

```{r}
#| include: false
robust_se <- summary(clustered_model)$coefficients[, "robust se"]
# With tied follow-up times, R applies Efron's tie correction inside the robust variance and
# lifelines doesn't; the two agree exactly when no times are tied (checked while writing this page).
check_agree(list(se_b = robust_se[["implantB"]], se_c = robust_se[["implantC"]], se_age = robust_se[["age_10"]],
                 se_male = robust_se[["sexMale"]], se_bmi = robust_se[["bmi_5"]]),
            reticulate::py$chk, tol = 1e-3)
```

- **exp(coef):** unchanged: implant C's hazard ratio is still 3.19.
- **se(coef) / robust se:** R prints both; lifelines prints only the robust one when you cluster. Here they're almost the same (0.259 and 0.258 for implant C), so the CI barely moves (1.92 to 5.28). Only 20 of the 80 bilateral patients had a revision, so the pairing matters little in this cohort. It can matter much more in yours: check, and say in the Methods what you did.

::: {.callout-tip}
## 🔀 R vs Python: robust standard errors
Both programs compute the same robust ("sandwich") standard errors. When follow-up times are tied, R also applies Efron's tie correction inside the robust variance and lifelines doesn't, so the two differ in the fourth significant figure.
:::

## Competing risks regression: Fine-Gray (R only) {#fine-gray}

Every Cox model above treated death as censoring. That's a **cause-specific** Cox model: its hazard ratios describe the revision rate among patients still alive, which is the right question for whether an implant performs worse. But as [page 13](13-kaplan-meier.qmd#competing-risks) showed, deaths also stop revisions from ever happening. For "which patients will actually be revised?" use the **Fine-Gray** model, which models the cumulative incidence of revision directly. Its effect sizes are **subdistribution hazard ratios** (SHR).

Fine-Gray regression has no mature Python implementation, so this section is R only. tidycmprsk's `crr()` takes the same three-level status as page 13's cumulative incidence:

```{r}
#| warning: false
library(tidycmprsk)

cohort <- cohort |>
  mutate(status = factor(event_status, levels = c(0, 1, 2),
                         labels = c("censored", "revision", "death")))   # censored must come first

fine_gray <- crr(Surv(followup_years, status) ~ implant + age_10 + sex + bmi_5,
                 data = cohort, failcode = "revision")
fine_gray
```

Compare it with the cause-specific model:
- **Implant C:** SHR 3.09 (95% CI 1.86 to 5.14), close to the cause-specific HR of 3.19. Death doesn't depend on the implant, so allowing for it changes little.
- **Age:** SHR 1.07 per 10 years (95% CI 0.86 to 1.33), against a cause-specific HR of 1.22. Older patients may be revised at a somewhat higher rate while alive, but more of them die before they can be revised, so age barely changes how many are actually revised.

Report the cause-specific model to compare implants, and the Fine-Gray model when the question is how many patients will be revised. Many papers report both, and say which is which.

::: {.callout-warning}
## ⚠️ Watch out: a subdistribution hazard ratio isn't a hazard ratio
The SHR has no simple meaning as a rate: patients who have died stay in its "at risk" group. Read it only as "higher or lower cumulative incidence", and call it a subdistribution hazard ratio in the text and tables.
:::

## Reporting a Cox model {#reporting}

Most papers present Cox models as a table: one row per predictor, with the univariable and the multivariable hazard ratios side by side. The multivariable column here comes from the model with robust standard errors ([above](#stratified-cox)), so its CIs allow for the bilateral patients.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(gtsummary)

hr_labels <- list(implant ~ "Implant", age_10 ~ "Age (per 10 years)", sex ~ "Sex",
                  bmi_5 ~ "BMI (per 5 kg/m²)")

univariable_table <- cohort |>
  select(followup_years, revised, implant, age_10, sex, bmi_5) |>
  tbl_uvregression(method = coxph, y = Surv(followup_years, revised), exponentiate = TRUE,
                   label = hr_labels, pvalue_fun = label_style_pvalue(digits = 3))
multivariable_table <- clustered_model |>                   # robust SEs, for the bilateral patients
  tbl_regression(exponentiate = TRUE, label = hr_labels, pvalue_fun = label_style_pvalue(digits = 3))

tbl_merge(list(univariable_table, multivariable_table),
          tab_spanner = c("**Univariable**", "**Multivariable**"))
```

## Python

```{python}
def hr_with_ci(model):
    """Each term's hazard ratio and 95% CI as text, like '3.19 (1.92 to 5.29)'."""
    rows = model.summary
    return (rows["exp(coef)"].map("{:.2f}".format) + " (" + rows["exp(coef) lower 95%"].map("{:.2f}".format)
            + " to " + rows["exp(coef) upper 95%"].map("{:.2f}".format) + ")")

univariable = []
for term in ["implant", "age_10", "sex", "bmi_5"]:
    one_predictor = CoxPHFitter().fit(cox_data[["followup_years", "revised", term]], duration_col="followup_years",
                                      event_col="revised", formula=term, fit_options={"precision": 1e-12})
    univariable.append(hr_with_ci(one_predictor))

hr_table = pd.DataFrame({"Univariable HR (95% CI)": pd.concat(univariable),
                         "Multivariable HR (95% CI)": hr_with_ci(clustered_model)})   # robust SEs, for the bilateral patients
print(hr_table)
```
:::

```{python}
#| include: false
def univariable_hr(term, row):
    model = CoxPHFitter().fit(cox_data[["followup_years", "revised", term]], duration_col="followup_years",
                              event_col="revised", formula=term, fit_options={"precision": 1e-12})
    return float(model.summary.loc[row, "exp(coef)"])
chk = {"uni_age": univariable_hr("age_10", "age_10"), "uni_male": univariable_hr("sex", "sex[T.Male]"),
       "uni_bmi": univariable_hr("bmi_5", "bmi_5")}
```

```{r}
#| include: false
uni_hr <- function(term) exp(coef(coxph(reformulate(term, "Surv(followup_years, revised)"), data = cohort)))
check_agree(list(uni_age = unname(uni_hr("age_10")), uni_male = unname(uni_hr("sex")), uni_bmi = unname(uni_hr("bmi_5"))),
            reticulate::py$chk)
```

> **Methods:** The association between implant and revision for any reason was estimated with Cox proportional hazards regression, with time from surgery as the time scale and implant A as the reference. Age, sex and body mass index were chosen in advance as covariates. Age entered the model as a linear term after a natural cubic spline showed no clear evidence of non-linearity. Proportional hazards were checked with scaled Schoenfeld residuals. Robust standard errors accounted for patients who had both sides replaced. A Fine-Gray model, treating death as a competing risk, was fitted as a sensitivity analysis.
>
> **Results:** During follow-up, 81 of 600 procedures were revised. After adjustment for age, sex and body mass index, implant C was associated with a higher hazard of revision than implant A (hazard ratio 3.19, 95% CI 1.92 to 5.28), while the estimate for implant B was imprecise (0.83, 95% CI 0.45 to 1.52). There was no clear evidence that any hazard ratio changed over time (global test p = 0.359). With death treated as a competing risk, the subdistribution hazard ratio for implant C was 3.09 (95% CI 1.86 to 5.14).

Before you submit, check that the paper states:
- the number of patients, procedures and events
- time zero and the event definition ([page 13](13-kaplan-meier.qmd#time-zero))
- which covariates were adjusted for, and why
- how continuous predictors were modeled, and how proportional hazards were checked
- how bilateral patients and deaths were handled

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
implant_summary <- summary(implant_model)
adjusted_zph <- cox.zph(adjusted_model)
clustered_ci <- summary(clustered_model)$conf.int
fg <- fine_gray$tidy
fg_hr <- function(term) round(exp(fg$estimate[fg$term == term]), 2)
fg_ci <- function(term) round(exp(c(fg$conf.low[fg$term == term], fg$conf.high[fg$term == term])), 2)
bilateral <- cohort |> group_by(patient_id) |> filter(n() == 2) |> ungroup()
asa_model <- coxph(Surv(followup_years, revised) ~ asa, data = cohort)
bmi_spline_model <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + ns(bmi, df = 3), data = cohort)
bmi_bend <- anova(adjusted_model, bmi_spline_model)
procedure_model <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + bmi_5 + strata(procedure), data = cohort)
stopifnot(
  implant_summary$n == 600, implant_summary$nevent == 81, sum(table(cohort$patient_id) == 2) == 80,
  round(implant_hr[, "exp(coef)"], 2) == c(0.82, 3.07),
  round(implant_hr["implantC", c("lower .95", "upper .95")], 2) == c(1.85, 5.09),
  round(implant_hr["implantB", c("lower .95", "upper .95")], 2) == c(0.45, 1.50),
  implant_summary$coefficients["implantC", "Pr(>|z|)"] < 0.001,
  round(implant_summary$coefficients["implantB", "Pr(>|z|)"], 3) == 0.514,
  round(implant_summary$concordance[["C"]], 3) == 0.659,
  round(implant_summary$logtest[["test"]], 1) == 27.6, implant_summary$logtest[["pvalue"]] < 0.001,
  round(100 * risk_5, 1) == c(10.1, 7.6, 28.9), round(risk_5[3] / risk_5[1], 2) == 2.85,
  round(81 / 10) == 8, round(81 / 5) == 16,
  round(adjusted_hr["implantC", c("exp(coef)", "lower .95", "upper .95")], 2) == c(3.19, 1.92, 5.29),
  round(adjusted_hr["sexMale", c("exp(coef)", "lower .95", "upper .95")], 2) == c(0.51, 0.32, 0.81),
  round(adjusted_hr["implantB", c("exp(coef)", "lower .95", "upper .95")], 2) == c(0.83, 0.45, 1.52),
  round(age_bend$Chisq[2], 2) == 0.29, age_bend$Df[2] == 2, round(age_bend$`Pr(>|Chi|)`[2], 3) == 0.864,
  round(adjusted_zph$table["GLOBAL", "p"], 3) == 0.359,
  rownames(adjusted_zph$table)[which.min(adjusted_zph$table[, "p"])] == "bmi_5",
  round(adjusted_zph$table["bmi_5", "p"], 3) == 0.106,
  approach_zph$table["approach", "p"] < 0.001, round(approach_zph$table["approach", "chisq"], 1) == 11.3,
  round(reticulate::py_eval("float(proportional_hazard_test(approach_model, tha_data, time_transform='km').summary['test_statistic'].iloc[0])"), 1) == 11.2,
  round(exp(coef(approach_model)), 2) == 1.37, round(exp(confint(approach_model)), 2) == c(0.72, 2.61),
  round(stratified_hr["implantC", c("exp(coef)", "lower .95", "upper .95")], 2) == c(2.11, 1.02, 4.40),
  round(split_hr["posterior_early", c("exp(coef)", "lower .95")], 2) == c(8.47, 1.93),
  round(split_hr["posterior_early", "upper .95"], 1) == 37.3,
  round(split_hr["posterior_late", c("exp(coef)", "lower .95", "upper .95")], 2) == c(0.43, 0.16, 1.16),
  sum(tha$revised == 1 & tha$followup_years <= 0.5) == 16,
  round(clustered_ci["implantC", c("exp(coef)", "lower .95", "upper .95")], 2) == c(3.19, 1.92, 5.28),
  round(summary(clustered_model)$coefficients["implantC", c("se(coef)", "robust se")], 3) == c(0.259, 0.258),
  n_distinct(bilateral$patient_id) == 80, n_distinct(bilateral$patient_id[bilateral$revised == 1]) == 20,
  fg_hr("implantC") == 3.09, fg_ci("implantC") == c(1.86, 5.14),
  fg_hr("age_10") == 1.07, fg_ci("age_10") == c(0.86, 1.33),
  round(adjusted_hr["age_10", "exp(coef)"], 2) == 1.22,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(summary(asa_model)$conf.int[, c("exp(coef)", "lower .95", "upper .95")], 2) == c(1.38, 0.99, 1.93),
  round(summary(asa_model)$coefficients[, "Pr(>|z|)"], 3) == 0.060,
  round(bmi_bend$Chisq[2], 2) == 2.64, round(bmi_bend$`Pr(>|Chi|)`[2], 3) == 0.267,
  round(summary(procedure_model)$conf.int["implantC", c("exp(coef)", "lower .95", "upper .95")], 2) == c(3.16, 1.90, 5.24)
)
```

## Exercises {#exercises}

The solutions use the packages, data and models made in the sections above, so run the page from the top first.

**1.** Fit a univariable Cox model for ASA class (as a number, 1 to 4) and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
asa_model <- coxph(Surv(followup_years, revised) ~ asa, data = cohort)
summary(asa_model)$conf.int
summary(asa_model)$coefficients[, "Pr(>|z|)"]
```

## Python

```{python}
asa_model = CoxPHFitter().fit(cohort[["followup_years", "revised", "asa"]], duration_col="followup_years",
                              event_col="revised", fit_options={"precision": 1e-12})
print(asa_model.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]])
```
:::

Each one-class increase in ASA class was associated with a hazard ratio for revision of 1.38 (95% CI 0.99 to 1.93, p = 0.060). The estimate is imprecise: the data are compatible with no association and with a near doubling of the hazard per class.
:::

**2.** Check whether BMI's effect in the adjusted model is a straight line, using a natural cubic spline with 3 degrees of freedom.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
bmi_spline_model <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + ns(bmi, df = 3),
                          data = cohort)
anova(adjusted_model, bmi_spline_model)
```

## Python

```{python}
bmi_knots = list(cohort["bmi"].quantile([1/3, 2/3]))
bmi_low, bmi_high = cohort["bmi"].min(), cohort["bmi"].max()
bmi_spline = patsy.dmatrix("cr(bmi, knots=bmi_knots, lower_bound=bmi_low, upper_bound=bmi_high,"
                           " constraints='center') - 1", cohort, return_type="dataframe")
bmi_spline.columns = ["bmi_1", "bmi_2", "bmi_3"]

bmi_data = pd.concat([cox_data.drop(columns="bmi_5"), bmi_spline], axis=1)
bmi_spline_model = CoxPHFitter().fit(bmi_data, duration_col="followup_years", event_col="revised",
                                     formula="implant + age_10 + sex + bmi_1 + bmi_2 + bmi_3",
                                     fit_options={"precision": 1e-12})
bmi_lr = 2 * (bmi_spline_model.log_likelihood_ - adjusted_model.log_likelihood_)
print(bmi_lr, chi2.sf(bmi_lr, df=2))
```
:::

There was no clear evidence that BMI's effect bends (likelihood ratio χ² = 2.64, df = 2, p = 0.267), so the straight line stands.
:::

**3.** Total hips and total knees may have different baseline revision rates. Refit the adjusted model stratified by procedure. Does implant C's hazard ratio change? Write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
procedure_model <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + bmi_5 + strata(procedure),
                         data = cohort)
summary(procedure_model)$conf.int["implantC", ]
```

## Python

```{python}
procedure_model = CoxPHFitter().fit(cohort[["followup_years", "revised", "implant", "age_10", "sex", "bmi_5", "procedure"]],
                                    duration_col="followup_years", event_col="revised",
                                    formula="implant + age_10 + sex + bmi_5", strata=["procedure"],
                                    fit_options={"precision": 1e-12})
print(procedure_model.summary.loc["implant[T.C]", ["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

Barely. In a Cox model stratified by procedure and adjusted for age, sex and BMI, implant C was associated with a higher hazard of revision than implant A (hazard ratio 3.16, 95% CI 1.90 to 5.24), close to the unstratified estimate of 3.19.
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render survival/14-cox-regression.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `240 passed`. Page 13's links to `#proportional-hazards`, `#stratified-cox` and `#fine-gray` now resolve.

- [ ] **Step 5: Prove the convergence check bites, then restore**

In the `#remedies` section's first Python block, change `strata=["approach"], fit_options={"precision": 1e-12})` to `strata=["approach"])`, then run `quarto render survival/14-cox-regression.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'hr_b'` (R 0.5425943, Python 0.5425985). Undo the change, then run:

```bash
rm -rf survival/14-cox-regression_files
quarto render survival/14-cox-regression.qmd
uv run pytest tests/site -q
```

Expected: `240 passed`.

- [ ] **Step 6: Commit**

```bash
git add survival/14-cox-regression.qmd _freeze/survival/14-cox-regression tests/site/test_survival.py
git commit -m "Write page 14, Cox regression: hazard ratios, covariates, linearity, proportional hazards, remedies, bilateral patients, Fine-Gray, reporting

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Catalog links land on the section they promise

**Files:**
- Modify: `catalog/04-describe-one-group.qmd`, `catalog/06-two-unpaired-groups.qmd`, `catalog/08-three-plus-unmatched.qmd`, `catalog/09-three-plus-matched.qmd`, `catalog/11-predict-from-one.qmd`, `catalog/12-predict-from-several.qmd`
- Modify: `_freeze/` for those six pages (re-render; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes: page 13's `#competing-risks`; page 14's `#proportional-hazards`, `#choosing-covariates` and `#fine-gray`; `test_catalog.py`'s `SURVIVAL_LINKS`
- Produces: `SECTION_LINKS` and `test_links_into_the_survival_pages_land_on_the_section_they_promise`

- [ ] **Step 1: Write the failing test**

In `tests/site/test_catalog.py`, a link with an anchor still counts as a link to its page. Replace

```python
    hrefs = [a["href"] for a in section(page, anchor).select("a[href]")]
    assert any(href.endswith(target) for href in hrefs)
```

with

```python
    hrefs = [a["href"].split("#")[0] for a in section(page, anchor).select("a[href]")]
    assert any(href.endswith(target) for href in hrefs)
```

and append to the end of the file (after two blank lines):

```python
# ---- links into the survival pages ----------------------------------------------

# Where a sentence promises one topic ("page 13 covers competing risks"), its link
# lands on that section of pages 13-14, not the top of the page.
SECTION_LINKS = {
    "catalog/04-describe-one-group.html": ["survival/13-kaplan-meier.html#competing-risks"],
    "catalog/06-two-unpaired-groups.html": ["survival/14-cox-regression.html#proportional-hazards",
                                            "survival/13-kaplan-meier.html#competing-risks"],
    "catalog/08-three-plus-unmatched.html": ["survival/14-cox-regression.html#proportional-hazards",
                                             "survival/13-kaplan-meier.html#competing-risks"],
    "catalog/09-three-plus-matched.html": ["survival/14-cox-regression.html#choosing-covariates"],
    "catalog/11-predict-from-one.html": ["survival/13-kaplan-meier.html#competing-risks",
                                         "survival/14-cox-regression.html#fine-gray"],
    "catalog/12-predict-from-several.html": ["survival/14-cox-regression.html#proportional-hazards"],
}


@pytest.mark.parametrize("page,targets", SECTION_LINKS.items())
def test_links_into_the_survival_pages_land_on_the_section_they_promise(site, page, targets):
    hrefs = {a["href"].removeprefix("../") for a in load(page).select("main a[href]")}
    assert [target for target in targets if target not in hrefs] == []
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/site -q`

Expected: `6 failed, 240 passed`, one failure per catalog page in `SECTION_LINKS`.

- [ ] **Step 3: Add the anchors**

In `catalog/04-describe-one-group.qmd`, replace

```markdown
[Page 13](../survival/13-kaplan-meier.qmd) shows the competing-risks method that fixes this.
```

with

```markdown
[Page 13](../survival/13-kaplan-meier.qmd#competing-risks) shows the competing-risks method that fixes this.
```

In `catalog/06-two-unpaired-groups.qmd`, replace

```markdown
If the curves cross, see [page 14](../survival/14-cox-regression.qmd).
```

with

```markdown
If the curves cross, see [page 14](../survival/14-cox-regression.qmd#proportional-hazards).
```

In `catalog/06-two-unpaired-groups.qmd`, replace

```markdown
[page 13](../survival/13-kaplan-meier.qmd) covers competing risks.
```

with

```markdown
[page 13](../survival/13-kaplan-meier.qmd#competing-risks) covers competing risks.
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
[Page 14](../survival/14-cox-regression.qmd) shows how to check that and covers Cox regression in full.
```

with

```markdown
[Page 14](../survival/14-cox-regression.qmd#proportional-hazards) shows how to check that and covers Cox regression in full.
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
[page 13](../survival/13-kaplan-meier.qmd) covers competing risks.
```

with

```markdown
[page 13](../survival/13-kaplan-meier.qmd#competing-risks) covers competing risks.
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
[Page 14](../survival/14-cox-regression.qmd) covers how many events a model needs.
```

with

```markdown
[Page 14](../survival/14-cox-regression.qmd#choosing-covariates) covers how many events a model needs.
```

In `catalog/11-predict-from-one.qmd`, replace

```markdown
use the cumulative incidence ([page 13](../survival/13-kaplan-meier.qmd)) or a Fine-Gray model ([page 14](../survival/14-cox-regression.qmd)).
```

with

```markdown
use the cumulative incidence ([page 13](../survival/13-kaplan-meier.qmd#competing-risks)) or a Fine-Gray model ([page 14](../survival/14-cox-regression.qmd#fine-gray)).
```

In `catalog/12-predict-from-several.qmd`, replace

```markdown
[Page 14](../survival/14-cox-regression.qmd) shows how to check it and covers Cox regression in full.
```

with

```markdown
[Page 14](../survival/14-cox-regression.qmd#proportional-hazards) shows how to check it and covers Cox regression in full.
```

In `catalog/12-predict-from-several.qmd`, replace

```markdown
before trusting any of them ([page 14](../survival/14-cox-regression.qmd)).
```

with

```markdown
before trusting any of them ([page 14](../survival/14-cox-regression.qmd#proportional-hazards)).
```

- [ ] **Step 4: Render the six pages and run the tests**

Run:

```bash
for page in 04-describe-one-group 06-two-unpaired-groups 08-three-plus-unmatched \
            09-three-plus-matched 11-predict-from-one 12-predict-from-several; do
  quarto render catalog/$page.qmd
done
uv run pytest tests/site -q
lychee --offline --include-fragments --no-progress _site
git status --short _freeze
```

Expected:
- `246 passed`
- lychee `0 Errors`: every new anchor exists
- `git status` lists the six pages' `execute-results/html.json` and page 6's `figure-html/unnamed-chunk-13-1.png`. The jittered boxplot is random, so its PNG changes on every render. The JSON diffs change only the links, the freeze hashes and pages 11–12's statsmodels "Time:" stamps.

- [ ] **Step 5: Commit**

```bash
git add catalog/04-describe-one-group.qmd catalog/06-two-unpaired-groups.qmd catalog/08-three-plus-unmatched.qmd \
        catalog/09-three-plus-matched.qmd catalog/11-predict-from-one.qmd catalog/12-predict-from-several.qmd \
        _freeze/catalog tests/site/test_catalog.py
git commit -m "Catalog links into pages 13-14 land on the section they promise

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Record the survival-tools convention and run everything

**Files:**
- Modify: `CLAUDE.md`, `tests/python/test_repo_docs.py`

- [ ] **Step 1: Write the failing test**

In `tests/python/test_repo_docs.py`, replace

```python
                 "Regression CIs"]:
```

with

```python
                 "Regression CIs", "CumIncidenceRight"]:
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `test_claude_md_states_the_golden_rules` FAILS on `CumIncidenceRight`.

- [ ] **Step 2: Update CLAUDE.md**

After golden rule 16,

```markdown
16. **Regression CIs.** R's `confint()` profiles the likelihood of `glm()` and `nls()` fits; statsmodels and scipy give Wald CIs (estimate ± z or t × standard error). Pages quote R's profile CI and give Python's in the 🔀 box. The hidden check compares estimates and standard errors (and, for `glm()`, the Wald CI from `confint.default()`) with `tol = 1e-4` and a comment, because the two sides stop iterating, or approximate derivatives, slightly differently.
```

add rule 17:

```markdown
17. **Survival tools.** lifelines stops iterating slightly early, so every Cox fit passes `fit_options={"precision": 1e-9}` or tighter (stratified and start-stop fits need `1e-12`) and the 🔀 box says so. For cumulative incidence, use statsmodels' `CumIncidenceRight()`, not lifelines' `AalenJohansenFitter`, which moves tied times by a random amount. Gray's test and Fine-Gray regression exist only in R (tidycmprsk); the page says so.
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
- site: `246 passed`
- lychee: `0 Errors`
- `git status` shows only `CLAUDE.md` and `tests/python/test_repo_docs.py`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md tests/python/test_repo_docs.py
git commit -m "CLAUDE.md: record Phase 4 convention (survival tools in Python and R)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
