# Phase 5: Beyond the Table (Pages 15–17) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three "beyond the table" stubs with finished pages, and settle two questions earlier phases left open:
- `beyond/15-post-hoc.qmd`: why many tests mislead, adjusting p-values, and the follow-up tests for every overall test on pages 8, 9 and 13. That covers Tukey and Games-Howell, Dunn, pairwise Fisher, paired t, pairwise Wilcoxon and Conover, pairwise McNemar, and pairwise log-rank, along with whether a significant overall test must come first, and planned vs exploratory comparisons.
- `beyond/16-mixed-models.qmd`: why repeated-measures ANOVA drops patients, random intercepts, estimated marginal means, time as categories or a curve, group × time, bilateral patients, and reporting.
- `beyond/17-agreement.qmd`: reliability vs agreement, choosing the ICC form, inter- and intra-rater designs, Bland-Altman limits, kappa and weighted kappa, and reporting.
- **Carryover 1 (from Phase 4):** page 13 promises that page 15 covers comparing pairs of survival curves. Page 15's `#after-log-rank` section does, and page 13's link now lands on it.
- **Carryover 2 (from Phase 3b):** page 8 says "only run post-hoc tests when the overall test is significant". Page 15's `#overall-test-first` settles the question: adjusted methods don't need the gate. Page 8's sentence is rewritten to match.

**Architecture:**
- The same building blocks as Phases 2–4:
  - knitr-engine pages with R ⟷ Python tabsets
  - hidden `check_agree()` R ⟷ Python checks, a `# Prose guard` and a data-checksum stamp
  - exercise solutions that are executed chunks
- Every hidden check compares the objects the visible code printed, never a recomputation.
- The pages are free-form (spec §6), like pages 13–14. The tests every free-form page shares move from `test_survival.py` into `tests/site/test_free_form.py`. That file is driven by `FREE_FORM_SECTIONS` in `sitelib.py`, which each task extends. `tests/site/test_beyond.py` holds the page-specific tests.
- Links on pages 3, 7, 8, 9, 11, 12 and 13 that point at pages 15–17 gain the anchor of the section their sentence promises.
- `just data` re-renders `beyond/`.

**Tech Stack:**
- R: rstatix (Games-Howell, Dunn, pairwise Fisher, paired t and Wilcoxon), survival, irr (ICC), DescTools (kappa)
- R, new: PMCMRplus (Conover after Friedman), lme4 and lmerTest (mixed models), emmeans (estimated marginal means)
- Python: statsmodels (`pairwise_tukeyhsd`, `multipletests`, `mcnemar`, `mixedlm`, `cohens_kappa`), pingouin (`pairwise_gameshowell`, `pairwise_tests`, `intraclass_corr`), scipy, lifelines (`pairwise_logrank_test`), patsy
- Python, new: scikit-posthocs (Dunn, Conover)
- Quarto 1.9.37

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`, especially:
- §4, pages 15, 16 and 17: the topic lists these pages implement
- §5.4: the built-in effects (the rater-2 bias, the ICC and kappa ranges, PROM improvement)
- §6: page anatomy (free-form for these pages)
- §7.3: the packages (lme4, lmerTest, emmeans, irr, DescTools, rstatix, PMCMRplus; pingouin, scikit-posthocs, statsmodels)
- §8: quality checks

## Global Constraints

- **`engine: knitr` per page.** Every page with code declares `engine: knitr` in its own front matter. Don't add `execute: message: false`; `_quarto.yml` already hides messages.
- **Tabsets:** `::: {.panel-tabset group="language"}`, with `## R` first and `## Python` second.
- **Hidden agreement checks:**
  - A hidden Python chunk sets `chk = {name: float(...)}`.
  - A hidden R chunk then calls `check_agree(list(name = <R value>), reticulate::py$chk)`.
  - Both sides read the objects the visible code made, never a fresh call.
  - Never pass DataFrames, sets or `pd.NA` through `reticulate::py`.
  - A looser `tol` always carries a comment saying why.
  - Compare test statistics as well as p-values: `check_agree()` compares values below 1 on an absolute scale, so a check on p < 1e-10 alone proves nothing.
- **Quiet output:**
  - Chunks that call `library()` add `#| warning: false`. No page may show stderr output.
  - Call rstatix, PMCMRplus, irr and DescTools as `pkg::fun()`.
  - Never assign to `_` in a Python chunk.
  - Print numbers, not objects. Write `test.statistic, test.pvalue`, not a results object, and no `np.float64(...)` wrappers.
- **Prose guard:** one hidden R chunk headed `# Prose guard`, immediately before `## Exercises {#exercises}`, that `stopifnot()`s every quoted number, including the exercise answers.
- **Data stamp:** each page has the `<!-- data-checksum: … -->` chunk.
- **Solutions:** exercise solutions are executed `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`.
- **Freeze:** render every changed page and commit its `_freeze/` directory. After a deliberately failed render, delete the leftover `<page>_files/` folder.
- **Reporting conventions:**
  - mean (SD) or median (IQR); n (%); a 95% CI with every estimate
  - p to 3 decimals, with a floor of "p < 0.001"
  - "no clear evidence" or "imprecise", never "similar", "held" or "the same"
- **Multiple comparisons:**
  - Pairwise follow-ups adjust with Holm unless the method adjusts itself (Tukey, Games-Howell).
  - Unadjusted pairwise p-values appear only to show what adjusting does.
- **Mixed models:** both languages fit by REML. Hidden checks on standard errors, marginal means and Wald statistics use `tol = 1e-3`, with the comment explaining why.
- **Branching:** work on branch `phase-5-beyond`, in a worktree under `.worktrees/phase-5`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A reader takes "only after a significant overall test" as a rule, or runs unadjusted pairwise tests.**
   - Page 15's `#overall-test-first` explains where the rule came from (Fisher's least significant difference) and why adjusted methods don't need it.
   - It also shows the two kinds of test disagreeing on real data: complications by ASA class, overall p = 0.016, with no pair below 0.05 after Holm.
   - Page 8's sentence is rewritten to match. `test_beyond.py::test_post_hoc_tests_are_no_longer_gated_on_the_overall_test` (Task 5) pins it.
2. **Mixed-model standard errors that don't quite match.**
   - lme4 holds the variance components fixed when it computes standard errors; statsmodels uses the Hessian of the whole likelihood. They differ in the fourth significant figure. This was verified by reproducing lme4's values by hand.
   - The checks use `tol = 1e-3` with that comment.
   - The Task 3 mutation (Python fitted by ML instead of REML) proves they still catch a real difference: `disagree on 'se_1yr'`.
3. **Complete-case results read as unbiased.**
   - Page 16 explains missing completely at random, missing at random, and missing not at random.
   - It says that the complete-knee means match the mixed model here only because the synthetic cohort's visits were missed completely at random.
4. **Weighted kappa on categories in the wrong order.**
   - `irr::kappa2(weight = "equal")` turns factors into text and sorts them alphabetically, so it gives 0.63 instead of 0.73 for varus/neutral/valgus.
   - Page 17 uses DescTools on a table in the real order, and warns about the trap.
   - The prose guard pins both numbers.
5. **A hidden check that recomputes its value instead of reading what the page printed.**
   - Prototyping found page 17's ICC check passing even when the visible code asked for a different ICC.
   - Every check on pages 15–17 now reads the visible objects. One mutation per page proves it: `pool.sd` (Task 2), REML (Task 3), the ICC type (Task 4).

## Plan rulings (made while prototyping)

- **Page 15's examples continue the pages that send readers there:**
  - age by ASA class (page 8's ANOVA): Tukey and Games-Howell
  - length of stay by ASA class: Dunn. Page 8's own Kruskal-Wallis example has no difference to follow up.
  - complications by ASA class (page 8's exercise 3): pairwise Fisher
  - VR-12 PCS, KOOS JR and walking aids (page 9): paired t, Wilcoxon or Conover, McNemar
  - implants (page 13): pairwise log-rank and a Cox model with B as the reference
- **The adjustment demo uses Welch t tests.** R's `pairwise.t.test()` pools the SD across all four groups by default, which Python can't reproduce, so the page passes `pool.sd = FALSE`. The Task 2 mutation shows the default fails the check.
- **Conventions carried over:**
  - Wilcoxon signed-rank tests use `exact = FALSE, correct = FALSE`, and McNemar's test keeps R's continuity correction, as on page 7.
  - R has no pairwise log-rank function in the project's packages, so the page loops over the pairs and names survminer's `pairwise_survdiff()`.
- **Settling the overall-test question:**
  - Tukey, Games-Howell, Dunn and Holm-adjusted tests control the family-wise error rate on their own. The "significant overall test first" gate belongs to Fisher's LSD.
  - The page's advice is to decide the comparisons in advance and use an adjusted method; the overall test is optional.
- **Page 16 uses KOOS JR in knees, not VR-12 PCS:**
  - The synthetic PCS scores barely cluster within patients (random-intercept SD 1.2 against a residual SD of 6.2). KOOS JR clusters realistically (8.8 against 8.6, so about half the variance is between knees).
  - Hips (HOOS JR) aren't mixed in, because the instruments differ.
  - The group × time example (sex) is an honest null, p = 0.100.
  - VR-12 PCS appears in exercise 2, for comparison with page 9.
- **Time as a curve:** the natural spline over days invents a peak of about 89 points at 8 months, where no knee was measured. The page keeps it as the reason categories suit fixed visits.
- **Bilateral knees:** the nested model `(1 | patient_id/case_id)` is singular on these data (patient-level variance about 0, and lme4 warns), so page 16 describes it without fitting it, as spec §4 allows ("mentioned with a pointer").
- **emmeans:**
  - Contrasts against pre-op use `adjust = "none"`, because they are the planned comparisons; emmeans otherwise applies a Dunnett adjustment to their CIs.
  - Python computes marginal means from the fixed effects through patsy's `model_spec` with z intervals. R uses Satterthwaite t intervals; the 🔀 box says so.
- **Page 17:**
  - The ICC is ICC(A,1): two-way random, absolute agreement, single rater. pingouin rounds its CI to 2 decimals, so the checks round R's bounds to match and the pages quote 2 decimals.
  - The limits of agreement use Bland and Altman's approximate SE, √(3s²/n), with a t quantile.
  - Weighted kappa is shown on the ordered arithmetic-HKA axis of CPAK (varus, neutral, valgus), because CPAK class itself has no order.
  - DescTools and statsmodels give identical kappas and CIs.
- **Harness:** the shared free-form tests move from `test_survival.py` into `test_free_form.py` unchanged, so the survival tests keep their count (252 at the start).
- **Packages:**
  - R gains lmerTest, emmeans and PMCMRplus, plus seven dependencies (estimability, multcompView, gmp, Rmpfr, SuppDists, kSamples, BWStest). lme4 was already locked as a dependency and is now declared.
  - Python gains scikit-posthocs.
  - All install as prebuilt binaries.
- **Links:** 18 links on 7 pages gain section anchors. None of those pages has random figures, so their re-renders change only text.
- **Not folded in:** Phase 4's other deferred minors.

## Reference results (prototype, 2026-10-06, R 4.6.0 / Python 3.13 / pandas 3.0.6 / statsmodels 0.15.0 / pingouin 0.7.0 / scikit-posthocs 0.17.0)

All three pages rendered with every hidden check passing. Full suite:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- pytest `tests/python`: 81 passed
- pytest `tests/site`: 307 passed
- lychee: 0 errors
- a full `quarto render` re-executes nothing

Mutation checks (each failed as it should):
- page 15 with R's default pooled SD: `disagree on 'raw_12'`
- page 16's Python model fitted by ML: `disagree on 'se_1yr'`
- page 17's visible ICC switched to consistency: `disagree on 'icc'`
- page 15 without the Justfile line: `` `just data` must re-render: ['beyond'] ``

| Page | Numbers |
|---|---|
| 15 | ASA 1 vs 2 age: p = 0.022 unadjusted, 0.132 Bonferroni, 0.044 Holm, 0.026 BH; Tukey ASA 2 vs 1 3.6 years (−0.4 to 7.7), p = 0.096; Dunn LOS ASA 3 vs 4 p = 0.061; complications by ASA overall Fisher p = 0.016, smallest Holm p 0.058; implant A vs B log-rank p = 0.520; C vs B HR 3.75 (2.14 to 6.58) |
| 16 | 330 knees, 192 complete (138 dropped, 42%); random-intercept SD 8.8, residual 8.6; KOOS JR 50.0 (48.6 to 51.3) pre-op to 83.9 (82.5 to 85.3) at 1 year, change 33.9 (32.5 to 35.3); visit × sex F(3, 832) = 2.09, p = 0.100 |
| 17 | inter-rater ICC(A,1) 0.889 (0.82 to 0.93); intra-rater 0.915 (0.86 to 0.95); bias 0.50° (0.08° to 0.93°), limits −2.74° to 3.74°; CPAK κ = 0.58 (0.44 to 0.73); weighted κ (aHKA group) 0.73 (0.58 to 0.87) |

---

### Task 1: Packages for post-hoc tests and mixed models

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `pyproject.toml`, `uv.lock`, `getting-started/check_setup.R`, `getting-started/check_setup.py`, `tests/python/test_check_setup.py`

**Interfaces:**
- Produces: the R packages lme4, lmerTest, emmeans and PMCMRplus, and the Python package scikit-posthocs (imported as `scikit_posthocs`), which pages 15 and 16 use.

- [ ] **Step 1: Create the worktree and build the current site**

```bash
git checkout main && git pull
git worktree add .worktrees/phase-5 -b phase-5-beyond main
cd .worktrees/phase-5
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `252 passed`.

- [ ] **Step 2: Write the failing checks**

In `getting-started/check_setup.R`, replace

```r
"rstatix", "tidycmprsk",
             "broom.helpers")) {
```

with

```r
"rstatix", "tidycmprsk",
             "broom.helpers", "lme4", "lmerTest", "emmeans", "PMCMRplus")) {
```

In `getting-started/check_setup.py`, replace

```python
             "statsmodels", "pingouin", "lifelines"]:
```

with

```python
             "statsmodels", "pingouin", "lifelines", "scikit_posthocs"]:
```

In `tests/python/test_check_setup.py`, replace

```python
"rstatix", "tidycmprsk",
                "broom.helpers"]:
        assert f'"{pkg}"' in script, pkg
```

with

```python
"rstatix", "tidycmprsk",
                "broom.helpers", "lme4", "lmerTest", "emmeans", "PMCMRplus"]:
        assert f'"{pkg}"' in script, pkg


def test_python_check_covers_the_packages_the_pages_import():
    script = SCRIPT.read_text(encoding="utf-8")
    for name in ["pandas", "numpy", "matplotlib", "scipy", "statsmodels", "pingouin", "lifelines", "scikit_posthocs"]:
        assert f'"{name}"' in script, name
```

- [ ] **Step 3: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_setup")'
uv run pytest tests/python/test_check_setup.py -q
```

Expected:
- R: "check_setup.R passes in a working project" FAILS. `Rscript getting-started/check_setup.R` reports `R package lmerTest PROBLEM`, `R package emmeans PROBLEM` and `R package PMCMRplus PROBLEM`.
- Python: `1 failed, 4 passed`. `test_passes_inside_the_project_environment` fails because `check_setup.py` reports `Python package scikit_posthocs PROBLEM`.

- [ ] **Step 4: Install and lock the packages**

In `DESCRIPTION`, replace

```
    effectsize,
```

with

```
    effectsize,
    emmeans,
```

replace

```
    knitr,
```

with

```
    knitr,
    lme4,
    lmerTest,
```

and replace

```
    openxlsx2,
```

with

```
    openxlsx2,
    PMCMRplus,
```

Run:

```bash
Rscript -e 'renv::install(c("lmerTest", "emmeans", "PMCMRplus"), prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
python3 -c "import json; p = json.load(open('renv.lock'))['Packages']; print([k for k in ['lme4', 'lmerTest', 'emmeans', 'estimability', 'multcompView', 'PMCMRplus', 'gmp', 'Rmpfr', 'SuppDists', 'kSamples', 'BWStest'] if k not in p])"
uv add scikit-posthocs
grep -n "scikit-posthocs" pyproject.toml
```

Expected:
- `[]`. The snapshot adds ten packages: lmerTest, emmeans, estimability, multcompView, PMCMRplus, gmp, Rmpfr, SuppDists, kSamples and BWStest. lme4 was already in the lockfile.
- `pyproject.toml` gains `"scikit-posthocs>=0.17.0",` between python-docx and scipy.

- [ ] **Step 5: Run all the tests**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
uv run pytest tests/site -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- Python: `81 passed`
- site: `252 passed`

- [ ] **Step 6: Commit**

```bash
git add DESCRIPTION renv.lock pyproject.toml uv.lock getting-started/check_setup.R getting-started/check_setup.py \
        tests/python/test_check_setup.py
git commit -m "Add lmerTest, emmeans, PMCMRplus and scikit-posthocs (mixed models, post-hoc tests) with their setup checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Page 15, post-hoc tests and multiple comparisons

**Files:**
- Modify: `beyond/15-post-hoc.qmd` (replace the stub)
- Create: `_freeze/beyond/15-post-hoc/` (render output; commit it)
- Create: `tests/site/test_free_form.py`, `tests/site/test_beyond.py`
- Modify: `tests/site/sitelib.py`, `tests/site/test_survival.py`, `tests/site/test_sources.py`, `Justfile`

**Interfaces:**
- Consumes:
  - Task 1's PMCMRplus and scikit-posthocs
  - Phase 4's `test_survival.py` (generic tests, `KM`, `COX`) and `sitelib.py` (`load`, `section`, `text_of`, `unreported`, `NO_EVIDENCE_AS_NO_DIFFERENCE`)
  - `data/cohort.csv`, `data/proms_long.csv`
- Produces:
  - page 15 anchors `#why-adjust`, `#adjusting-p-values`, `#after-anova`, `#after-kruskal-wallis`, `#after-chi-square`, `#after-repeated-measures-anova`, `#after-friedman`, `#after-cochran-q`, `#after-log-rank`, `#overall-test-first`, `#planned-comparisons` and `#exercises`
  - in `sitelib.py`: `FREE_FORM_SECTIONS` (a dict of page → section anchors) and `code_of(found) -> str`
  - `tests/site/test_free_form.py`, driven by `FREE_FORM_SECTIONS`
  - `tests/site/test_beyond.py` with `POST_HOC`
  - in `test_sources.py`: `test_free_form_pages_check_r_against_python`

- [ ] **Step 1: Write the tests**

In `tests/site/sitelib.py`, insert this block immediately above the line `def load(page: str) -> BeautifulSoup:`, followed by two blank lines:

```python
# Free-form pages (spec section 6): one ## section per topic in the spec's outline.
# Each phase adds its pages as they're written; tests/site/test_free_form.py checks them all.
FREE_FORM_SECTIONS = {
    "survival/13-kaplan-meier.html": [
        "censoring", "time-zero", "kaplan-meier", "survivorship", "follow-up", "log-rank",
        "competing-risks", "exercises"],
    "survival/14-cox-regression.html": [
        "hazard-ratio", "choosing-covariates", "univariable-multivariable", "linearity",
        "proportional-hazards", "remedies", "stratified-cox", "fine-gray", "reporting", "exercises"],
    "beyond/15-post-hoc.html": [
        "why-adjust", "adjusting-p-values", "after-anova", "after-kruskal-wallis", "after-chi-square",
        "after-repeated-measures-anova", "after-friedman", "after-cochran-q", "after-log-rank",
        "overall-test-first", "planned-comparisons", "exercises"],
}
```

and after the end of the `section()` function,

```python
    assert found is not None, f"{page} has no section #{anchor}"
    return found
```

add (after two blank lines):

```python
def code_of(found):
    """The code shown in a page element, as one string."""
    return " ".join(pre.get_text() for pre in found.select("pre"))
```

Create `tests/site/test_free_form.py`. It holds the tests every free-form page shares, moved unchanged from `test_survival.py`:

```python
"""Free-form pages (spec section 6): the survival and "beyond the table" pages, which have no fixed
section anatomy. Every page in FREE_FORM_SECTIONS gets these checks."""

import pytest

from sitelib import FREE_FORM_SECTIONS, NO_EVIDENCE_AS_NO_DIFFERENCE, ROOT, load, section, text_of, unreported


@pytest.mark.parametrize("page,sections", FREE_FORM_SECTIONS.items())
def test_page_is_written_with_all_its_sections(site, page, sections):
    soup = load(page)
    assert soup.select_one(".coming-soon") is None, f"{page} is still a stub"
    ids = {el["id"] for el in soup.select("section[id]")}
    assert [s for s in sections if s not in ids] == []


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_page_runs_both_languages_and_is_frozen(site, page):
    ran = [tabset for tabset in load(page).select("div.panel-tabset")
           if all(pane.select(".cell-output, .cell-output-display") for pane in tabset.select("div.tab-pane"))]
    assert len(ran) >= 5, f"{page}: only {len(ran)} tabsets show output in both R and Python"
    assert (ROOT / "_freeze" / page.removesuffix(".html")).is_dir()


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_page_ends_with_at_least_three_solved_exercises(site, page):
    headers = [h.get_text(strip=True) for h in section(page, "exercises").select("div.callout .callout-header")]
    assert sum(h.endswith("Solution") for h in headers) >= 3


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_page_shows_no_warnings_or_package_messages(site, page):
    assert [out.get_text()[:80] for out in load(page).select(".cell-output-stderr")] == []


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_outputs_are_short_and_never_dump_objects(site, page):
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert "array(" not in text and "<matplotlib." not in text and "<lifelines." not in text, \
            f"{page}: object dumped: {text[:80]}"
        assert len(text.splitlines()) <= 40, f"{page}: {len(text.splitlines())}-line output"


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_reports_follow_the_reporting_conventions(site, page):
    """Methods and Results blockquotes and exercise answers: CIs with effect sizes, and no
    "similar" or "held" where the data only fail to show a difference."""
    quotes = [text_of(q) for q in load(page).select("blockquote")]
    assert any("Methods:" in q and "Results:" in q for q in quotes), f"{page}: no Methods and Results"
    answers = [text_of(p) for p in section(page, "exercises").select("p")]
    for text in quotes + answers:
        assert unreported(text) == [], text
        assert not NO_EVIDENCE_AS_NO_DIFFERENCE.findall(text), text


@pytest.mark.parametrize("page", FREE_FORM_SECTIONS)
def test_printed_tables_show_every_column(site, page):
    """pandas swaps columns that don't fit for "..."; print wide tables with .to_string()."""
    for out in load(page).select(".cell-output"):
        text = out.get_text()
        assert " ... " not in text and "rows x" not in text, f"{page}: {text[:120]}"
```

Replace `tests/site/test_survival.py` with what remains: its page-specific tests.

```python
"""Part 3 · Survival analysis: Kaplan-Meier and Cox regression in full (spec section 4, pages 13-14).
tests/site/test_free_form.py checks what every free-form page shares."""

from sitelib import code_of, load, section, text_of

KM = "survival/13-kaplan-meier.html"
COX = "survival/14-cox-regression.html"


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


# ---- final review fixes ------------------------------------------------------

def test_reported_models_all_allow_for_bilateral_patients(site):
    """The Methods promise robust standard errors, so both columns of the table use them."""
    found = section(COX, "reporting")
    table = text_of(found.select_one("table"))
    assert "1.87, 5.04" in table and "1.92, 5.28" in table   # implant C, univariable and multivariable, clustered
    printed = " ".join(out.get_text() for out in found.select(".cell-output"))
    assert "3.07 (1.87 to 5.04)" in printed and "3.19 (1.92 to 5.28)" in printed
    methods = next(text_of(q) for q in found.select("blockquote") if "Methods:" in text_of(q))
    assert "In the Cox models, robust standard errors" in methods


def test_imprecise_estimates_are_not_described_as_effects(site):
    """Explanatory prose follows the same rule as the Results: no clear evidence isn't evidence of none."""
    for page, phrase in [(KM, "does worse early and better later"), (KM, "but the curves crossed"),
                         (COX, "Death doesn't depend on the implant"), (COX, "age barely changes"),
                         (COX, "a later one in the other direction")]:
        assert phrase not in text_of(load(page)), f"{page}: {phrase!r}"


def test_a_moving_hazard_ratio_is_not_proof_of_confounding(site):
    """Hazard ratios shift when a strong predictor is added, even without confounding."""
    text = text_of(section(COX, "univariable-multivariable"))
    assert "the covariates were confounding the unadjusted one" not in text
    assert "even without confounding" in text


def test_results_give_every_estimate_its_ci_and_every_count_its_percentage(site):
    km_results = " ".join(text_of(q) for q in section(KM, "competing-risks").select("blockquote"))
    assert "24.0% (95% CI 19.3% to 29.0%)" in km_results
    cox_results = " ".join(text_of(q) for q in section(COX, "reporting").select("blockquote"))
    assert "81 of 600 procedures (13.5%)" in cox_results
```

Create `tests/site/test_beyond.py`:

```python
"""Part 4 · Beyond the table: post-hoc tests, mixed models, agreement (spec section 4, pages 15-17).
tests/site/test_free_form.py checks what every free-form page shares."""

import pytest

from sitelib import code_of, load, section, text_of

POST_HOC = "beyond/15-post-hoc.html"


# ---- page 15: post-hoc tests and multiple comparisons ----------------------------

def test_adjustments_are_compared_side_by_side(site):
    found = section(POST_HOC, "adjusting-p-values")
    text = text_of(found)
    for name in ["Bonferroni", "Holm", "Benjamini-Hochberg", "false discovery rate", "family-wise"]:
        assert name in text or name in text_of(section(POST_HOC, "why-adjust")), name
    outputs = [out.get_text() for out in found.select(".cell-output")]
    assert sum(all(column in out for column in ["bonferroni", "holm", "bh"]) for out in outputs) == 2   # R and Python


# Spec section 4, page 15, plus the follow-ups pages 9 and 13 promise.
FOLLOW_UPS = {
    "after-anova": ["TukeyHSD(", "pairwise_tukeyhsd(", "games_howell_test(", "pairwise_gameshowell("],
    "after-kruskal-wallis": ["dunn_test(", "posthoc_dunn("],
    "after-chi-square": ["pairwise_fisher_test(", "fisher_exact("],
    "after-repeated-measures-anova": ["pairwise_t_test(", "pairwise_tests("],
    "after-friedman": ["pairwise_wilcox_test(", "frdAllPairsConoverTest(", "wilcoxon(", "posthoc_conover_friedman("],
    "after-cochran-q": ["mcnemar.test(", "mcnemar("],
    "after-log-rank": ["survdiff(", "pairwise_logrank_test("],
}


@pytest.mark.parametrize("anchor,calls", FOLLOW_UPS.items())
def test_each_overall_test_has_its_follow_up_in_both_languages(site, anchor, calls):
    found = section(POST_HOC, anchor)
    code = code_of(found)
    assert [call for call in calls if call not in code] == []
    assert "holm" in code.lower() or anchor == "after-anova"     # Tukey and Games-Howell adjust themselves


def test_the_overall_test_is_not_a_gate(site):
    """Settles the Phase 3b question: adjusted post-hoc methods don't need a significant overall test first."""
    text = text_of(section(POST_HOC, "overall-test-first"))
    assert "Fisher's least significant difference" in text and "don't need the gate" in text
    assert "p = 0.016" in text                       # the significant-overall, no-significant-pair example


def test_planned_and_exploratory_comparisons_are_distinguished(site):
    text = text_of(section(POST_HOC, "planned-comparisons"))
    assert "pre-specified" in text and "exploratory" in text
```

In `tests/site/test_sources.py`, replace

```python
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog", "survival"):
```

with

```python
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog", "survival", "beyond"):
```

replace

```python
def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog", "survival"):
```

with

```python
def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog", "survival", "beyond"):
```

and replace

```python
def test_survival_pages_check_r_against_python():
    """Free-form pages have no cell sections, so count the whole page's checks."""
    for name, text in written_pages("survival"):
```

with

```python
def test_free_form_pages_check_r_against_python():
    """Free-form pages have no cell sections, so count the whole page's checks."""
    for name, text in written_pages("survival", "beyond"):
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `14 failed, 255 passed`:
- 4 in `test_free_form.py`, page 15's written, runs-both-languages, exercises and reporting tests. Its no-warnings, short-outputs and printed-tables tests pass trivially on a stub.
- all 10 page-15 tests in `test_beyond.py`.

The moved survival tests still pass.

- [ ] **Step 3: Write the page**

Replace `beyond/15-post-hoc.qmd` with:

````markdown
---
title: "15 · Post-hoc tests & multiple comparisons"
description: "Which groups differ after ANOVA, Kruskal-Wallis, chi-square, repeated-measures tests or a log-rank test, and how to keep false positives in check."
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

A test for three or more groups asks one question: "is there any difference among them?". When the answer is yes, the next question is which groups differ from which. Answering it means running several tests at once, and every extra test is another chance of a false positive. This page shows how to compare groups in pairs while keeping that chance under control. Each "After …" section picks up an example from [page 8](../catalog/08-three-plus-unmatched.qmd), [page 9](../catalog/09-three-plus-matched.qmd) or [page 13](../survival/13-kaplan-meier.qmd).

::: {.callout-note}
## 💡 How this page works
Run the code blocks in order, from the top: later blocks use the packages and data loaded in the first one.

As on the pages these examples come from, the code uses every case, including the 80 patients who had both sides operated on.
:::

## Why many tests mislead {#why-adjust}

A test at the 5% level has a 5% chance of a false positive when there is truly no difference. Run several tests and those chances add up. The chance of **at least one** false positive across a set of tests is the **family-wise error rate**. For independent tests at the 5% level it's 1 − 0.95^k^, where k is the number of tests:

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)
proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

tests <- c(1, 3, 6, 10, 20)
tibble(tests, chance_of_a_false_positive = round(1 - 0.95^tests, 2))
```

## Python

```{python}
import itertools
import numpy as np
import pandas as pd
import pingouin as pg
import scikit_posthocs as sp
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.contingency_tables import mcnemar
from lifelines import CoxPHFitter
from lifelines.statistics import pairwise_logrank_test

cohort = pd.read_csv("data/cohort.csv")
proms = pd.read_csv("data/proms_long.csv")

tests = np.array([1, 3, 6, 10, 20])
print(pd.DataFrame({"tests": tests, "chance_of_a_false_positive": (1 - 0.95**tests).round(2)}))
```
:::

```{python}
#| include: false
chk = {"six": float(1 - 0.95**6), "twenty": float(1 - 0.95**20)}
```

```{r}
#| include: false
check_agree(list(six = 1 - 0.95^6, twenty = 1 - 0.95^20), reticulate::py$chk)
```

Four groups make six pairs. Six independent tests at the 5% level give a 26% chance of at least one false alarm, even when nothing is going on; twenty tests give 64%. Comparing pairs therefore needs an **adjustment**: a stricter rule that keeps the chance of any false positive across the whole set of comparisons at 5%.

::: {.callout-note}
## 💡 In plain language
Buy one lottery ticket and you'll almost certainly lose. Buy twenty and your chance of winning something goes up. Each p-value below 0.05 is a small "win", and with enough tests one will turn up by luck alone. Adjusting the p-values makes each win harder to get, so the overall chance stays where you set it.
:::

## Adjusting p-values: Bonferroni, Holm and Benjamini-Hochberg {#adjusting-p-values}

[Page 8](../catalog/08-three-plus-unmatched.qmd#one-way-anova) found that age differs across the four ASA classes. Here are the six pairwise comparisons, each a Welch t test, with the p-values left as they are (**unadjusted**) and then adjusted three ways:

::: {.panel-tabset group="language"}
## R

```{r}
age_pairs <- pairwise.t.test(cohort$age, cohort$asa, pool.sd = FALSE,      # Welch t tests
                             p.adjust.method = "none")
unadjusted <- age_pairs$p.value[lower.tri(age_pairs$p.value, diag = TRUE)]  # the six p-values, in pair order

adjusted <- tibble(pair = c("1 vs 2", "1 vs 3", "1 vs 4", "2 vs 3", "2 vs 4", "3 vs 4"),
                   unadjusted,
                   bonferroni = p.adjust(unadjusted, method = "bonferroni"),
                   holm = p.adjust(unadjusted, method = "holm"),
                   bh = p.adjust(unadjusted, method = "BH"))
adjusted |> mutate(across(-pair, \(p) round(p, 4)))
```

## Python

```{python}
asa_pairs = list(itertools.combinations([1, 2, 3, 4], 2))
unadjusted = [stats.ttest_ind(cohort.loc[cohort["asa"] == a, "age"], cohort.loc[cohort["asa"] == b, "age"],
                              equal_var=False).pvalue                    # Welch t tests
              for a, b in asa_pairs]

adjusted = pd.DataFrame({
    "pair": [f"{a} vs {b}" for a, b in asa_pairs],
    "unadjusted": unadjusted,
    "bonferroni": multipletests(unadjusted, method="bonferroni")[1],
    "holm": multipletests(unadjusted, method="holm")[1],
    "bh": multipletests(unadjusted, method="fdr_bh")[1],
})
print(adjusted.round(4))
```
:::

```{python}
#| include: false
chk = {"raw_12": float(unadjusted[0]), "raw_34": float(unadjusted[5]),
       "bonferroni_12": float(adjusted["bonferroni"].iloc[0]), "holm_12": float(adjusted["holm"].iloc[0]),
       "bh_12": float(adjusted["bh"].iloc[0]), "bh_34": float(adjusted["bh"].iloc[5])}
```

```{r}
#| include: false
check_agree(list(raw_12 = adjusted$unadjusted[1], raw_34 = adjusted$unadjusted[6],
                 bonferroni_12 = adjusted$bonferroni[1], holm_12 = adjusted$holm[1],
                 bh_12 = adjusted$bh[1], bh_34 = adjusted$bh[6]),
            reticulate::py$chk)
```

Follow the ASA 1 vs ASA 2 comparison across the row:
- **Unadjusted, p = 0.022:** "significant" on its own, but it's one of six tests.
- **Bonferroni, p = 0.132:** multiplies every p-value by the number of tests (here 6). Simple, but the strictest: it often throws away real differences.
- **Holm, p = 0.044:** a step-down version of Bonferroni. It multiplies the smallest p-value by 6, the next smallest by 5, and so on. It controls the family-wise error rate just as well as Bonferroni and is never less powerful, so **use Holm rather than Bonferroni**.
- **Benjamini-Hochberg (BH), p = 0.026:** controls something different, the **false discovery rate**: the expected share of false positives among the results you call significant. It's the most lenient of the three. It suits screening many outcomes for leads, not confirming a claim.

::: {.callout-warning}
## ⚠️ Watch out: decide the adjustment before you see the p-values
Picking whichever adjustment keeps your favourite result significant is p-hacking. Choose in advance: Holm (or a method built for the test, like Tukey's below) for comparisons you'll report as findings, Benjamini-Hochberg only for exploratory screening. Say in the Methods which you used and how many comparisons it covered.
:::

## After ANOVA: Tukey's HSD and Games-Howell {#after-anova}

After a one-way ANOVA, **Tukey's honestly significant difference** (HSD) compares every pair of group means. It adjusts for all the pairs at once, and gives each difference a CI that's adjusted too. It assumes the groups have similar spreads, like the ANOVA. When they don't (the largest SD is more than about twice the smallest), use **Games-Howell**, the Welch version of Tukey's test.

::: {.panel-tabset group="language"}
## R

```{r}
age_anova <- aov(age ~ factor(asa), data = cohort)
age_tukey <- TukeyHSD(age_anova)                          # diff, adjusted 95% CI, adjusted p
age_tukey

games_howell <- rstatix::games_howell_test(cohort |> mutate(asa = factor(asa)), age ~ asa)
games_howell |> select(group1, group2, estimate, conf.low, conf.high, p.adj)
```

## Python

```{python}
age_tukey = pairwise_tukeyhsd(cohort["age"], cohort["asa"])
print(age_tukey.summary())

games_howell = pg.pairwise_gameshowell(data=cohort, dv="age", between="asa")
print(games_howell[["A", "B", "diff", "se", "pval"]].round(4))
```
:::

```{python}
#| include: false
chk = {"diff_12": float(age_tukey.meandiffs[0]), "low_12": float(age_tukey.confint[0][0]),
       "high_12": float(age_tukey.confint[0][1]), "p_12": float(age_tukey.pvalues[0]), "p_34": float(age_tukey.pvalues[5]),
       "gh_12": float(games_howell["pval"].iloc[0]), "gh_34": float(games_howell["pval"].iloc[5])}
```

```{r}
#| include: false
tukey <- age_tukey$`factor(asa)`
check_agree(list(diff_12 = tukey["2-1", "diff"], low_12 = tukey["2-1", "lwr"], high_12 = tukey["2-1", "upr"],
                 p_12 = tukey["2-1", "p adj"], p_34 = tukey["4-3", "p adj"],
                 gh_12 = games_howell$p.adj[1], gh_34 = games_howell$p.adj[6]),
            reticulate::py$chk)
```

- **diff / meandiff:** the difference in mean age between two ASA classes, in years.
- **lwr, upr / lower, upper:** the 95% CI of that difference, adjusted for all six comparisons.
- **p adj / p-adj:** the adjusted p-value.

Four of the six pairs differ clearly (p < 0.001 or, for ASA 2 vs 4 in the Games-Howell test, p = 0.001). Two don't: ASA 2 patients were 3.6 years older than ASA 1 patients (95% CI −0.4 to 7.7, p = 0.096), and ASA 4 patients 5.3 years older than ASA 3 patients (95% CI −0.3 to 10.9, p = 0.072). Both CIs include 0, and both comparisons involve one of the two small classes. The SDs are similar (8.7 to 9.3 years), so Games-Howell reaches the same conclusions.

> **Methods:** Age was compared across ASA classes with one-way ANOVA, followed by Tukey's honestly significant difference test for pairwise comparisons.
>
> **Results:** Mean age differed across ASA classes (F(3, 596) = 23.9, p < 0.001). In pairwise comparisons, ASA 3 patients were 5.0 years older than ASA 2 patients (95% CI 3.0 to 6.9, p < 0.001); the differences between ASA 1 and 2 (3.6 years, 95% CI −0.4 to 7.7, p = 0.096) and between ASA 3 and 4 (5.3 years, 95% CI −0.3 to 10.9, p = 0.072) were imprecise.

::: {.callout-tip}
## 🔀 R vs Python: Tukey and Games-Howell
R's `TukeyHSD()` and statsmodels' `pairwise_tukeyhsd()` give identical results; R writes the pairs as "2-1" (second group minus first), statsmodels as group1, group2 with meandiff = group2 − group1. For Games-Howell, R needs the rstatix package; in Python, pingouin's `pairwise_gameshowell()` reports `diff` as A − B, so its signs are the reverse of R's estimates. The p-values agree.
:::

## After Kruskal-Wallis: Dunn's test {#after-kruskal-wallis}

**Dunn's test** follows a Kruskal-Wallis test. It compares the groups' mean ranks from the Kruskal-Wallis ranking, so it measures every pair on the same scale. Use it with Holm's adjustment. Running separate Mann-Whitney tests instead re-ranks the data for each pair and needs an adjustment of its own.

Length of stay (LOS) is skewed (most patients go home on day 0 or 1), so it belongs in the rank column. Does it differ across ASA classes?

::: {.panel-tabset group="language"}
## R

```{r}
cohort |>
  group_by(asa) |>
  summarise(n = n(), median = median(los_days),
            q1 = quantile(los_days, 0.25), q3 = quantile(los_days, 0.75))

los_kw <- kruskal.test(los_days ~ factor(asa), data = cohort)
los_kw
dunn <- rstatix::dunn_test(cohort, los_days ~ asa, p.adjust.method = "holm")
dunn |> select(group1, group2, statistic, p, p.adj)
```

## Python

```{python}
print(cohort.groupby("asa")["los_days"].describe()[["count", "25%", "50%", "75%"]])

los_kw = stats.kruskal(*[group["los_days"] for _, group in cohort.groupby("asa")])
print(los_kw.statistic, los_kw.pvalue)
dunn = sp.posthoc_dunn(cohort, val_col="los_days", group_col="asa", p_adjust="holm")
print(dunn.round(4))                                           # adjusted p-values
```
:::

```{python}
#| include: false
chk = {"h": float(los_kw.statistic), "p_12": float(dunn.loc[1, 2]), "p_23": float(dunn.loc[2, 3]),
       "p_24": float(dunn.loc[2, 4]), "p_34": float(dunn.loc[3, 4])}
```

```{r}
#| include: false
check_agree(list(h = unname(los_kw$statistic), p_12 = dunn$p.adj[1], p_23 = dunn$p.adj[4],
                 p_24 = dunn$p.adj[5], p_34 = dunn$p.adj[6]),
            reticulate::py$chk)
```

- **Kruskal-Wallis H = 24.3, df = 3, p < 0.001:** LOS differs somewhere across the classes.
- **Dunn's test:** ASA 1 differs from every other class (adjusted p = 0.011 against ASA 2, p < 0.001 against ASAs 3 and 4), and ASA 2 differs from ASAs 3 (p = 0.047) and 4 (p = 0.022). There was no clear evidence of a difference between ASA 3 and 4 (p = 0.061).
- **The statistic** in R's output is a z score: positive means the second group's ranks are higher (longer stays).

> **Results:** Length of stay rose with ASA class, from a median of 0 days (IQR 0 to 0) in ASA 1 to 1 day (IQR 0.25 to 3.5) in ASA 4 (Kruskal-Wallis H = 24.3, df = 3, p < 0.001). In Dunn's tests with Holm's adjustment, ASA 1 differed from every other class (p ≤ 0.011); the difference between ASA 3 and 4 was imprecise (p = 0.061).

::: {.callout-tip}
## 🔀 R vs Python: Dunn's test
Both correct the z scores for tied ranks, which matter here because many patients share a LOS of 0 or 1 day, and both give the same adjusted p-values. R's rstatix returns one row per pair; scikit-posthocs' `posthoc_dunn()` returns a square table of p-values with the groups on both sides.
:::

## After chi-square: pairwise Fisher's exact tests {#after-chi-square}

After a chi-square (or Fisher) test on a table with three or more groups, compare the groups two at a time with **Fisher's exact test**, then adjust with Holm. [Page 8's exercise 3](../catalog/08-three-plus-unmatched.qmd#exercises) found that 90-day complications differ across ASA classes:

::: {.panel-tabset group="language"}
## R

```{r}
complications <- table(asa = cohort$asa, complication = cohort$complication_90d)
complications
fisher_overall <- fisher.test(complications)      # overall: expected counts are too small for chi-square
fisher_overall

pairwise_fisher <- rstatix::pairwise_fisher_test(complications, p.adjust.method = "holm")
pairwise_fisher
```

## Python

```{python}
complications = pd.crosstab(cohort["asa"], cohort["complication_90d"])
print(complications)

fisher_p = []
for a, b in asa_pairs:
    two_classes = complications.loc[[a, b]]                     # a 2 x 2 table for this pair
    fisher_p.append(stats.fisher_exact(two_classes).pvalue)
fisher_holm = multipletests(fisher_p, method="holm")[1]
print(pd.DataFrame({"pair": [f"{a} vs {b}" for a, b in asa_pairs], "p": fisher_p, "p_holm": fisher_holm}).round(4))
```
:::

```{python}
#| include: false
chk = {"p_14": float(fisher_p[2]), "holm_14": float(fisher_holm[2]), "holm_24": float(fisher_holm[4]),
       "holm_12": float(fisher_holm[0])}
```

```{r}
#| include: false
check_agree(list(p_14 = pairwise_fisher$p[3], holm_14 = pairwise_fisher$p.adj[3], holm_24 = pairwise_fisher$p.adj[5],
                 holm_12 = pairwise_fisher$p.adj[1]),
            reticulate::py$chk)
```

The overall Fisher test says the complication rate differs across ASA classes (p = 0.016). But no single pair differs clearly after Holm's adjustment: the closest is ASA 1 vs ASA 4 (0 of 36 vs 4 of 18 patients; p = 0.010 unadjusted, 0.058 adjusted). [A later section](#overall-test-first) explains why that can happen.

## After repeated-measures ANOVA: paired t tests {#after-repeated-measures-anova}

[Page 9](../catalog/09-three-plus-matched.qmd#repeated-measures-anova) found that the VR-12 physical component score (PCS) changed over the first year, in 328 patients measured at all four visits. To say *when* it changed, compare every pair of visits with a **paired t test** and adjust with Holm:

::: {.panel-tabset group="language"}
## R

```{r}
pcs <- proms |>
  select(case_id, visit, vr12_pcs) |>
  group_by(case_id) |>
  filter(all(!is.na(vr12_pcs))) |>                  # patients measured at all four visits
  ungroup() |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr"))) |>
  arrange(case_id, visit)                           # paired tests match rows by position

pcs_pairs <- rstatix::pairwise_t_test(pcs, vr12_pcs ~ visit, paired = TRUE, p.adjust.method = "holm")
pcs_pairs |> select(group1, group2, n1, statistic, df, p.adj)
```

## Python

```{python}
pcs = proms[["case_id", "visit", "vr12_pcs"]]
pcs = pcs[pcs.groupby("case_id")["vr12_pcs"].transform(lambda scores: scores.notna().all())]

pcs_pairs = pg.pairwise_tests(data=pcs, dv="vr12_pcs", within="visit", subject="case_id", padjust="holm")
print(pcs_pairs[["A", "B", "T", "dof", "p_corr"]])
```
:::

```{python}
#| include: false
def paired_t(a, b):
    row = pcs_pairs[((pcs_pairs["A"] == a) & (pcs_pairs["B"] == b)) | ((pcs_pairs["A"] == b) & (pcs_pairs["B"] == a))]
    return float(abs(row["T"].iloc[0]))
chk = {"t_pre_6wk": paired_t("preop", "6wk"), "t_3mo_1yr": paired_t("3mo", "1yr"), "t_pre_1yr": paired_t("preop", "1yr")}
```

```{r}
#| include: false
check_agree(list(t_pre_6wk = abs(pcs_pairs$statistic[1]), t_3mo_1yr = abs(pcs_pairs$statistic[6]),
                 t_pre_1yr = abs(pcs_pairs$statistic[3])),
            reticulate::py$chk)
```

Every pair of visits differs (all adjusted p < 0.001): PCS improved between each visit and the next, from pre-op to 6 weeks (t = 8.0) through to 3 months and 1 year (t = 7.6 for the last step). With 328 patients and changes this large, the adjustment changes nothing. It matters most when results sit near p = 0.05.

::: {.callout-tip}
## 🔀 R vs Python: which way round
pingouin sorts the visits alphabetically and subtracts the second from the first, so its t statistics are negative where R's are positive, or the other way round. Compare their sizes. rstatix needs the rows in the same patient order within every visit, so sort by patient first.
:::

## After Friedman: pairwise Wilcoxon or Conover tests {#after-friedman}

After a Friedman test, compare pairs of visits with **Wilcoxon signed-rank tests** and Holm's adjustment, or with **Conover's test**, which reuses the Friedman ranks (as Dunn's test does after Kruskal-Wallis) and is often more powerful. [Page 9](../catalog/09-three-plus-matched.qmd#friedman) found that KOOS JR changed between 6 weeks, 3 months and 1 year in 205 knees:

::: {.panel-tabset group="language"}
## R

```{r}
koos <- proms |>
  filter(instrument == "KOOS JR", visit != "preop") |>
  select(case_id, visit, prom_score) |>
  group_by(case_id) |>
  filter(n() == 3, all(!is.na(prom_score))) |>         # knees scored at all three visits
  ungroup() |>
  mutate(visit = factor(visit, levels = c("6wk", "3mo", "1yr"))) |>
  arrange(case_id, visit)

koos_pairs <- rstatix::pairwise_wilcox_test(koos, prom_score ~ visit, paired = TRUE, exact = FALSE, correct = FALSE,
                                            p.adjust.method = "holm")
koos_pairs |> select(group1, group2, statistic, p, p.adj)

koos_conover <- PMCMRplus::frdAllPairsConoverTest(y = koos$prom_score, groups = koos$visit, blocks = koos$case_id,
                                                  p.adjust.method = "holm")
koos_conover
```

## Python

```{python}
koos = proms[(proms["instrument"] == "KOOS JR") & (proms["visit"] != "preop")]
koos_wide = koos.pivot(index="case_id", columns="visit", values="prom_score")[["6wk", "3mo", "1yr"]].dropna()
print(len(koos_wide))                                    # knees scored at all three visits

wilcoxon = {}
for a, b in [("6wk", "3mo"), ("6wk", "1yr"), ("3mo", "1yr")]:
    wilcoxon[(a, b)] = stats.wilcoxon(koos_wide[a], koos_wide[b], method="approx", correction=False)
    print(a, b, wilcoxon[(a, b)].statistic)
print(multipletests([test.pvalue for test in wilcoxon.values()], method="holm")[1])

koos_conover = sp.posthoc_conover_friedman(koos_wide, p_adjust="holm")
print(koos_conover)
```
:::

```{python}
#| include: false
chk = {"v_6wk_3mo": float(wilcoxon[("6wk", "3mo")].statistic), "v_3mo_1yr": float(wilcoxon[("3mo", "1yr")].statistic),
       "n": float(len(koos_wide))}
```

```{r}
#| include: false
check_agree(list(v_6wk_3mo = koos_pairs$statistic[1], v_3mo_1yr = koos_pairs$statistic[3],
                 n = n_distinct(koos$case_id)),
            reticulate::py$chk)
```

All three pairs differ (adjusted p < 0.001 with either method): KOOS JR rose between 6 weeks and 3 months and again between 3 months and 1 year.

::: {.callout-tip}
## 🔀 R vs Python: the statistic
R's `wilcox.test()` reports V, the sum of the positive ranks; scipy reports the smaller of the two rank sums. Here both are the same number, because the later visit scores higher for most knees. Conover's test needs the PMCMRplus package in R and scikit-posthocs in Python; they give the same p-values.
:::

## After Cochran's Q: pairwise McNemar tests {#after-cochran-q}

After Cochran's Q, compare pairs of visits with **McNemar's test** and adjust with Holm. [Page 9](../catalog/09-three-plus-matched.qmd#cochran-q) found that walking-aid use changed over the year in 328 patients assessed at all four visits:

::: {.panel-tabset group="language"}
## R

```{r}
aid <- proms |>
  select(case_id, visit, walking_aid) |>
  group_by(case_id) |>
  filter(all(!is.na(walking_aid))) |>               # patients assessed at all four visits
  ungroup() |>
  pivot_wider(names_from = visit, values_from = walking_aid)

visit_pairs <- combn(c("preop", "6wk", "3mo", "1yr"), 2)    # six pairs, one per column
mcnemar_p <- apply(visit_pairs, 2, function(pair) {
  mcnemar.test(table(factor(aid[[pair[1]]], levels = 0:1), factor(aid[[pair[2]]], levels = 0:1)))$p.value
})
mcnemar_results <- tibble(first = visit_pairs[1, ], second = visit_pairs[2, ],
                          p = mcnemar_p, p_holm = p.adjust(mcnemar_p, method = "holm"))
mcnemar_results
```

## Python

```{python}
aid = proms.pivot(index="case_id", columns="visit", values="walking_aid").dropna()   # assessed at all four visits

mcnemar_p = []
visit_pairs = list(itertools.combinations(["preop", "6wk", "3mo", "1yr"], 2))
for first, second in visit_pairs:
    pair_table = pd.crosstab(aid[first], aid[second]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    mcnemar_p.append(mcnemar(pair_table, exact=False, correction=True).pvalue)   # as R's mcnemar.test()
mcnemar_holm = multipletests(mcnemar_p, method="holm")[1]
print(pd.DataFrame({"pair": visit_pairs, "p": mcnemar_p, "p_holm": mcnemar_holm}))
```
:::

```{python}
#| include: false
chk = {"p_pre_3mo": float(mcnemar_p[1]), "holm_pre_3mo": float(mcnemar_holm[1]), "n": float(len(aid))}
```

```{r}
#| include: false
check_agree(list(p_pre_3mo = mcnemar_results$p[2], holm_pre_3mo = mcnemar_results$p_holm[2], n = nrow(aid)),
            reticulate::py$chk)
```

Every pair of visits differs after adjustment. Use rose from pre-op to 6 weeks and fell at each visit after that; by 3 months it was already below its pre-op level (adjusted p = 0.005), and by 1 year lower still.

## After a log-rank test: pairwise survival comparisons {#after-log-rank}

[Page 13](../survival/13-kaplan-meier.qmd#log-rank) found that revision-free survival differs across implants A, B and C. To say which implants differ, run the **log-rank test for each pair** and adjust with Holm. A Cox model gives the matching effect sizes: refit it with a different reference group to get the hazard ratio for any pair.

::: {.panel-tabset group="language"}
## R

```{r}
implant_pairs <- combn(c("A", "B", "C"), 2)
logrank <- apply(implant_pairs, 2, function(pair) {
  two_implants <- cohort |> filter(implant %in% pair)
  test <- survdiff(Surv(followup_years, revised) ~ implant, data = two_implants)
  c(chisq = test$chisq, p = test$pvalue)
})
logrank_results <- tibble(first = implant_pairs[1, ], second = implant_pairs[2, ], chisq = logrank["chisq", ],
                          p = logrank["p", ], p_holm = p.adjust(logrank["p", ], method = "holm"))
logrank_results

# hazard ratios against implant B instead of A
cohort <- cohort |> mutate(implant_vs_b = relevel(factor(implant), ref = "B"))
implant_vs_b_model <- coxph(Surv(followup_years, revised) ~ implant_vs_b, data = cohort)
summary(implant_vs_b_model)$conf.int
```

## Python

```{python}
pairwise_logrank = pairwise_logrank_test(cohort["followup_years"], cohort["implant"], cohort["revised"])
logrank_p = pairwise_logrank.summary["p"]
logrank_holm = multipletests(logrank_p, method="holm")[1]
print(pd.DataFrame({"chisq": pairwise_logrank.summary["test_statistic"], "p": logrank_p, "p_holm": logrank_holm}))

# hazard ratios against implant B instead of A: the first category is the reference
cohort["implant_vs_b"] = pd.Categorical(cohort["implant"], categories=["B", "A", "C"])
implant_vs_b = CoxPHFitter().fit(cohort[["followup_years", "revised", "implant_vs_b"]],
                                 duration_col="followup_years", event_col="revised", formula="implant_vs_b",
                                 fit_options={"precision": 1e-12})
print(implant_vs_b.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%"]])
```
:::

```{python}
#| include: false
hr_rows = implant_vs_b.summary
chk = {"p_ab": float(logrank_p.iloc[0]), "holm_ab": float(logrank_holm[0]), "chisq_bc": float(pairwise_logrank.summary["test_statistic"].iloc[2]),
       "hr_cb": float(hr_rows.loc["implant_vs_b[T.C]", "exp(coef)"]),
       "low_cb": float(hr_rows.loc["implant_vs_b[T.C]", "exp(coef) lower 95%"]),
       "high_cb": float(hr_rows.loc["implant_vs_b[T.C]", "exp(coef) upper 95%"])}
```

```{r}
#| include: false
implant_vs_b_hr <- summary(implant_vs_b_model)$conf.int
check_agree(list(p_ab = logrank_results$p[1], holm_ab = logrank_results$p_holm[1], chisq_bc = logrank_results$chisq[3],
                 hr_cb = implant_vs_b_hr["implant_vs_bC", "exp(coef)"], low_cb = implant_vs_b_hr["implant_vs_bC", "lower .95"],
                 high_cb = implant_vs_b_hr["implant_vs_bC", "upper .95"]),
            reticulate::py$chk)
```

Implant C differs from both A and B (adjusted p < 0.001 for each). There was no clear evidence of a difference between A and B (p = 0.520). Against implant B, implant C's hazard ratio was 3.75 (95% CI 2.14 to 6.58); against implant A it was 3.07 ([page 8](../catalog/08-three-plus-unmatched.qmd#cox)).

> **Results:** Revision-free survival differed across implants (log-rank χ² = 33.5, df = 2, p < 0.001). In pairwise log-rank tests with Holm's adjustment, implant C differed from implant A and from implant B (both p < 0.001), with no clear evidence of a difference between A and B (p = 0.520).

::: {.callout-tip}
## 🔀 R vs Python: pairwise log-rank tests
lifelines has `pairwise_logrank_test()`, which runs every pair at once and leaves the adjustment to you. R's survival package has no pairwise function, so the R code loops over the pairs; the survminer package's `pairwise_survdiff()` does the same in one call. To change the reference group, R uses `relevel()`; lifelines uses the first category of a pandas `Categorical`.
:::

## Do you need a significant overall test first? {#overall-test-first}

A common rule says: only run post-hoc tests if the overall test (the ANOVA, Kruskal-Wallis or chi-square) is significant. It comes from **Fisher's least significant difference** method, which runs unadjusted pairwise tests and relies on the overall test as a gate. That gate only fully protects you with three groups.

The tests on this page don't need the gate. Tukey's HSD, Games-Howell, Dunn's test and any Holm-adjusted set of pairwise tests control the family-wise error rate on their own. Requiring a significant overall test first just makes them stricter than they need to be.

The two kinds of test can also disagree, and that's not a contradiction:
- **A significant overall test with no significant pair**, as with complications by ASA class above (overall p = 0.016; no pair below 0.05 after adjustment). The overall test pools the evidence from all four classes, while each pair uses only two of them, and the ASA 1 and ASA 4 groups are small. Report it as it is: complication rates differed across ASA classes overall, but no single pair of classes differed clearly.
- **A significant pair with no significant overall test.** This can happen when one pair differs and the others don't, diluting the overall test.

What to do:
1. **Decide before you look at the data** which comparisons you'll make: every pair, or a few planned ones.
2. **If your question is about pairs, go straight to an adjusted pairwise method.** The overall test is optional; report it if your readers expect it.
3. **Never run unadjusted pairwise tests**, whatever the overall test says.
4. **Say what you did** in the Methods.

## Planned comparisons and how to report them {#planned-comparisons}

Not every comparison is a fishing trip. A study comparing a new implant with the standard one has one **pre-specified** comparison, named in the protocol before any data were collected. It needs no adjustment, because it isn't one of many. If you planned three comparisons, adjust for three, not for every possible pair.

Everything else is **exploratory**: comparisons chosen after seeing the data, or a scan across many outcomes. Adjust for every comparison you looked at, not only the ones you report, and label the results exploratory: they suggest questions for the next study, not conclusions.

> **Methods:** Pairwise comparisons after the omnibus tests used Tukey's honestly significant difference test (after ANOVA), Dunn's test (after Kruskal-Wallis) and Fisher's exact tests (after chi-square), with Holm's adjustment for multiple comparisons where the method did not adjust itself. All pairwise comparisons were exploratory.
>
> **Results:** Mean age differed across ASA classes (F(3, 596) = 23.9, p < 0.001); ASA 3 patients were 5.0 years older than ASA 2 patients (95% CI 3.0 to 6.9, p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: report every comparison you ran
Running ten comparisons and reporting the two significant ones hides how many chances you had. Give the number of comparisons and the adjustment in the Methods, and put the full set of pairwise results in a table or supplement.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
asa_sd <- tapply(cohort$age, cohort$asa, sd)
los_q <- cohort |> group_by(asa) |> summarise(median = median(los_days), q1 = quantile(los_days, 0.25), q3 = quantile(los_days, 0.75))
age_f <- summary(age_anova)[[1]]
tukey_bmi <- TukeyHSD(aov(bmi ~ factor(asa), data = cohort))$`factor(asa)`
sex_vars <- c("diabetes", "hypertension", "sleep_apnea", "readmit_90d", "complication_90d")
sex_p <- c(sapply(sex_vars, function(v) fisher.test(table(cohort$sex, cohort[[v]]))$p.value),
           facility = fisher.test(table(cohort$sex, cohort$discharge))$p.value)
aid3 <- proms |> filter(visit != "preop") |> select(case_id, visit, walking_aid) |> group_by(case_id) |>
  filter(all(!is.na(walking_aid))) |> ungroup() |> pivot_wider(names_from = visit, values_from = walking_aid)
aid3_p <- sapply(list(c("6wk", "3mo"), c("6wk", "1yr"), c("3mo", "1yr")),
                 function(pair) mcnemar.test(table(factor(aid3[[pair[1]]], 0:1), factor(aid3[[pair[2]]], 0:1)))$p.value)
stopifnot(
  round(1 - 0.95^c(6, 20), 2) == c(0.26, 0.64), sum(table(cohort$patient_id) == 2) == 80,
  round(unadjusted[1], 3) == 0.022, round(p.adjust(unadjusted, "bonferroni")[1], 3) == 0.132,
  round(p.adjust(unadjusted, "holm")[1], 3) == 0.044, round(p.adjust(unadjusted, "BH")[1], 3) == 0.026,
  round(range(asa_sd), 1) == c(8.7, 9.3),
  round(tukey["2-1", c("diff", "lwr", "upr")], 1) == c(3.6, -0.4, 7.7), round(tukey["2-1", "p adj"], 3) == 0.096,
  round(tukey["4-3", c("diff", "lwr", "upr")], 1) == c(5.3, -0.3, 10.9), round(tukey["4-3", "p adj"], 3) == 0.072,
  round(tukey["3-2", c("diff", "lwr", "upr")], 1) == c(5.0, 3.0, 6.9), tukey["3-2", "p adj"] < 0.001,
  sum(tukey[, "p adj"] < 0.001) == 4, round(games_howell$p.adj[5], 3) == 0.001,
  all(games_howell$p.adj[c(2, 3, 4)] < 0.001), round(games_howell$p.adj[c(1, 6)], 3) == c(0.097, 0.122),
  round(age_f[1, "F value"], 1) == 23.9, age_f[1, "Df"] == 3, age_f[2, "Df"] == 596,
  round(unname(los_kw$statistic), 1) == 24.3, los_kw$p.value < 0.001,
  round(dunn$p.adj, 3) == c(0.011, 0, 0, 0.047, 0.022, 0.061), round(max(dunn$p.adj[1:3]), 3) == 0.011,
  los_q$median == c(0, 0, 1, 1), los_q$q1[c(1, 4)] == c(0, 0.25), los_q$q3[c(1, 4)] == c(0, 3.5),
  round(fisher_overall$p.value, 3) == 0.016, min(pairwise_fisher$p.adj) > 0.05,
  complications["1", "1"] == 0, sum(complications["1", ]) == 36, complications["4", "1"] == 4, sum(complications["4", ]) == 18,
  round(pairwise_fisher$p[3], 3) == 0.010, round(pairwise_fisher$p.adj[3], 3) == 0.058,
  n_distinct(pcs$case_id) == 328, all(pcs_pairs$p.adj < 0.001),
  round(abs(pcs_pairs$statistic[c(1, 6)]), 1) == c(8.0, 7.6),
  n_distinct(koos$case_id) == 205, all(koos_pairs$p.adj < 0.001),
  nrow(aid) == 328, round(mcnemar_results$p_holm[2], 3) == 0.005, all(mcnemar_results$p_holm[-2] < 0.001),
  colMeans(aid[, c("preop", "3mo", "1yr")]) |> (\(x) x[2] < x[1] && x[3] < x[2])(),
  all(logrank_results$p_holm[2:3] < 0.001), round(logrank_results$p[1], 3) == 0.520,
  round(implant_vs_b_hr["implant_vs_bC", c("exp(coef)", "lower .95", "upper .95")], 2) == c(3.75, 2.14, 6.58),
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  all(tukey_bmi[, "p adj"] < 0.01), round(tukey_bmi["2-1", c("diff", "lwr", "upr")], 1) == c(2.9, 0.6, 5.2),
  round(tukey_bmi["4-3", c("diff", "lwr", "upr")], 1) == c(4.1, 0.9, 7.2),
  round(tukey_bmi["2-1", "p adj"], 3) == 0.007, round(tukey_bmi["4-3", "p adj"], 3) == 0.006,
  names(which(p.adjust(sex_p, "holm") < 0.05)) == "sleep_apnea", round(sex_p[["hypertension"]], 3) == 0.135,
  all(p.adjust(sex_p, "BH")[names(sex_p) != "sleep_apnea"] > 0.4),
  nrow(aid3) == 345, all(p.adjust(aid3_p, "holm") < 0.001),
  round(100 * colMeans(aid3[, c("6wk", "3mo", "1yr")]), 1) == c(58.8, 25.2, 10.7)
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** [Page 8's exercise 1](../catalog/08-three-plus-unmatched.qmd#exercises) found that BMI differs across ASA classes. Which pairs of classes differ? Use Tukey's HSD.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
TukeyHSD(aov(bmi ~ factor(asa), data = cohort))
```

## Python

```{python}
print(pairwise_tukeyhsd(cohort["bmi"], cohort["asa"]).summary())
```
:::

Every pair differs (all adjusted p < 0.01): mean BMI rises with each step in ASA class. The smallest steps were from ASA 1 to 2 (2.9 kg/m², 95% CI 0.6 to 5.2, p = 0.007) and from ASA 3 to 4 (4.1 kg/m², 95% CI 0.9 to 7.2, p = 0.006).
:::

**2.** A colleague compares men and women on six yes/no characteristics (diabetes, hypertension, sleep apnea, readmission, complications and discharge to a facility) with Fisher's exact test. Which adjustment fits, and which differences survive it?

::: {.callout-tip collapse="true"}
## Solution
This is a screen across several outcomes with no single planned comparison, so the results are exploratory. Holm's adjustment protects against any false positive; Benjamini-Hochberg is acceptable for a screen, as long as the results are labeled exploratory.

::: {.panel-tabset group="language"}
## R

```{r}
yes_no <- cohort |> mutate(facility = as.integer(discharge == "facility"))
characteristics <- c("diabetes", "hypertension", "sleep_apnea", "readmit_90d", "complication_90d", "facility")
by_sex_p <- sapply(characteristics, function(v) fisher.test(table(yes_no$sex, yes_no[[v]]))$p.value)
round(cbind(unadjusted = by_sex_p, holm = p.adjust(by_sex_p, "holm"), bh = p.adjust(by_sex_p, "BH")), 4)
```

## Python

```{python}
cohort["facility"] = (cohort["discharge"] == "facility").astype(int)
characteristics = ["diabetes", "hypertension", "sleep_apnea", "readmit_90d", "complication_90d", "facility"]
by_sex_p = [stats.fisher_exact(pd.crosstab(cohort["sex"], cohort[v])).pvalue for v in characteristics]
print(pd.DataFrame({"unadjusted": by_sex_p, "holm": multipletests(by_sex_p, method="holm")[1],
                    "bh": multipletests(by_sex_p, method="fdr_bh")[1]}, index=characteristics).round(4))
```
:::

Only sleep apnea differs between men and women after either adjustment (adjusted p < 0.001). Hypertension's unadjusted p = 0.135 was never close, and every other characteristic's Benjamini-Hochberg p-value is above 0.4.
:::

**3.** Leaving out the pre-op visit, which pairs of visits differ in walking-aid use (6 weeks, 3 months, 1 year)? Write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
later <- proms |>
  filter(visit != "preop") |>
  select(case_id, visit, walking_aid) |>
  group_by(case_id) |>
  filter(all(!is.na(walking_aid))) |>
  ungroup() |>
  pivot_wider(names_from = visit, values_from = walking_aid)
nrow(later)
colMeans(later[, c("6wk", "3mo", "1yr")])

later_pairs <- combn(c("6wk", "3mo", "1yr"), 2)
later_p <- apply(later_pairs, 2, function(pair) {
  mcnemar.test(table(factor(later[[pair[1]]], levels = 0:1), factor(later[[pair[2]]], levels = 0:1)))$p.value
})
p.adjust(later_p, method = "holm")
```

## Python

```{python}
later = proms[proms["visit"] != "preop"].pivot(index="case_id", columns="visit", values="walking_aid").dropna()
print(len(later), later[["6wk", "3mo", "1yr"]].mean().round(3).to_list())

later_p = []
for first, second in itertools.combinations(["6wk", "3mo", "1yr"], 2):
    pair_table = pd.crosstab(later[first], later[second]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    later_p.append(mcnemar(pair_table, exact=False, correction=True).pvalue)
print(multipletests(later_p, method="holm")[1])
```
:::

Among 345 patients assessed at all three visits, walking-aid use fell from 58.8% at 6 weeks to 25.2% at 3 months and 10.7% at 1 year; every pair of visits differed in McNemar tests with Holm's adjustment (all p < 0.001).
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render beyond/15-post-hoc.qmd
uv run pytest tests/site -q
```

Expected:
- The render completes.
- Then `1 failed, 268 passed`: `test_freshness.py::test_just_data_re_renders_the_pages_that_read_data` fails with `` `just data` must re-render: ['beyond'] ``.

- [ ] **Step 5: Re-render `beyond/` in `just data`**

In `Justfile`, replace

```
    # (Rendering a folder always re-runs its code.) Add beyond, report, ... as they gain code.
    quarto render foundations
    quarto render catalog
    quarto render survival
```

with

```
    # (Rendering a folder always re-runs its code.) Add report when it gains code.
    quarto render foundations
    quarto render catalog
    quarto render survival
    quarto render beyond
```

Run: `uv run pytest tests/site -q`

Expected: `269 passed`.

- [ ] **Step 6: Prove the check reads the visible code, then restore**

In the `#adjusting-p-values` section's R block, delete `pool.sd = FALSE,      # Welch t tests` from the `pairwise.t.test()` call, leaving `age_pairs <- pairwise.t.test(cohort$age, cohort$asa,`. Then run `quarto render beyond/15-post-hoc.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'raw_12'`. R's default pools the SD across all four classes, and scipy can't. Undo the change, then run:

```bash
rm -rf beyond/15-post-hoc_files
quarto render beyond/15-post-hoc.qmd
uv run pytest tests/site -q
```

Expected: `269 passed`.

- [ ] **Step 7: Commit**

```bash
git add beyond/15-post-hoc.qmd _freeze/beyond/15-post-hoc tests/site/sitelib.py tests/site/test_free_form.py \
        tests/site/test_survival.py tests/site/test_beyond.py tests/site/test_sources.py Justfile
git commit -m "Write page 15, post-hoc tests and multiple comparisons, incl. pairwise survival tests and the overall-test question; shared free-form page tests

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Page 16, mixed models for repeated PROMs

**Files:**
- Modify: `beyond/16-mixed-models.qmd` (replace the stub)
- Create: `_freeze/beyond/16-mixed-models/` (render output; commit it)
- Modify: `tests/site/sitelib.py`, `tests/site/test_beyond.py`

**Interfaces:**
- Consumes:
  - Task 1's lme4, lmerTest and emmeans
  - Task 2's `FREE_FORM_SECTIONS`, `code_of` and `test_beyond.py`
  - links to page 9's `#repeated-measures-anova`, page 12's `#multiple-nonlinear-regression`, page 3's `#paired`, page 14's `#stratified-cox` and page 17's `#icc` (written in Task 4; lychee runs in Task 5)
  - `data/proms_long.csv`, `data/cohort.csv`
- Produces: page 16 anchors `#why-mixed-models`, `#random-intercept`, `#estimated-marginal-means`, `#time`, `#group-by-time`, `#bilateral`, `#reporting` and `#exercises`.

- [ ] **Step 1: Write the failing tests**

In `tests/site/sitelib.py`'s `FREE_FORM_SECTIONS`, after the last line of the page 15 entry,

```python
        "overall-test-first", "planned-comparisons", "exercises"],
```

add

```python
    "beyond/16-mixed-models.html": [
        "why-mixed-models", "random-intercept", "estimated-marginal-means", "time", "group-by-time",
        "bilateral", "reporting", "exercises"],
```

In `tests/site/test_beyond.py`, replace

```python
POST_HOC = "beyond/15-post-hoc.html"
```

with

```python
POST_HOC = "beyond/15-post-hoc.html"
MIXED = "beyond/16-mixed-models.html"
```

and append to the end of the file (after two blank lines):

```python
# ---- page 16: mixed models ---------------------------------------------------------

def test_mixed_model_page_counts_what_repeated_measures_anova_drops(site):
    text = text_of(section(MIXED, "why-mixed-models"))
    assert "192 knees" in text and "138 knees (42%)" in text
    for kind in ["Missing completely at random", "Missing at random", "Missing not at random"]:
        assert kind in text, kind


def test_random_intercept_and_marginal_means_in_both_languages(site):
    code = code_of(section(MIXED, "random-intercept")) + code_of(section(MIXED, "estimated-marginal-means"))
    for call in ["lmer(", "(1 | case_id)", "mixedlm(", "emmeans(", "marginal_means("]:
        assert call in code, call
    assert "Satterthwaite" in text_of(section(MIXED, "random-intercept"))


def test_time_is_shown_as_categories_and_as_a_curve(site):
    code = code_of(section(MIXED, "time"))
    assert "ns(visit_days" in code and "cr(visit_days" in code


def test_group_by_time_tests_the_interaction(site):
    text = text_of(section(MIXED, "group-by-time"))
    assert "visit:sex" in text and "p = 0.100" in text and "no clear evidence" in text


def test_bilateral_patients_get_a_nested_model_and_a_pointer(site):
    found = section(MIXED, "bilateral")
    assert "(1 | patient_id/case_id)" in text_of(found)
    assert any(a["href"].endswith("survival/14-cox-regression.html#stratified-cox") for a in found.select("a[href]"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `9 failed, 272 passed`: 4 page-16 tests in `test_free_form.py` and the 5 in `test_beyond.py`.

- [ ] **Step 3: Write the page**

Replace `beyond/16-mixed-models.qmd` with:

````markdown
---
title: "16 · Mixed models for repeated PROMs"
description: "PROMs at several visits, including patients who missed some: random intercepts, time as categories or a curve, group × time, and estimated marginal means."
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

PROMs are collected at several visits, and patients miss some of them. [Page 9](../catalog/09-three-plus-matched.qmd#repeated-measures-anova) analyzed repeated scores with repeated-measures ANOVA, which only uses patients measured at every visit. A **linear mixed model** uses every score from every patient, and answers the questions a PROM study usually asks: how much do patients improve, by when, and does recovery differ between groups?

The examples use KOOS JR, the knee score, in the 330 total knee replacements. Hips answer a different questionnaire (HOOS JR), and a point on one isn't guaranteed to equal a point on the other, so the two aren't mixed in one model.

::: {.callout-note}
## 💡 How this page works
Run the code blocks in order, from the top: later blocks use the packages, data and models made earlier.

Each knee is treated as its own patient until the section on [bilateral patients](#bilateral).
:::

## Why not repeated-measures ANOVA? {#why-mixed-models}

Count how many of the four visits each knee has a score for:

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(lmerTest)        # lme4's lmer(), plus p-values for its fixed effects
library(emmeans)         # estimated marginal means
library(splines)         # natural cubic splines, for time as a curve

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)
cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

knees <- proms |>
  filter(instrument == "KOOS JR", !is.na(prom_score)) |>          # every knee score that exists
  left_join(select(cohort, case_id, sex, age), by = "case_id") |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))

knees |>
  count(case_id, name = "visits") |>            # scores per knee
  count(visits, name = "knees")                 # knees with 1, 2, 3 or 4 scores
```

## Python

```{python}
import numpy as np
import pandas as pd
import patsy
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

proms = pd.read_csv("data/proms_long.csv")
cohort = pd.read_csv("data/cohort.csv")

knees = proms[(proms["instrument"] == "KOOS JR") & proms["prom_score"].notna()]    # every knee score that exists
knees = knees.merge(cohort[["case_id", "sex", "age"]], on="case_id")
visits = ["preop", "6wk", "3mo", "1yr"]
knees["visit"] = pd.Categorical(knees["visit"], categories=visits)               # pre-op first: the reference

print(knees.groupby("case_id").size().value_counts().sort_index())   # knees with 1, 2, 3 or 4 scores
```
:::

```{python}
#| include: false
per_knee = knees.groupby("case_id").size()
chk = {"knees": float(per_knee.size), "complete": float((per_knee == 4).sum()), "scores": float(len(knees))}
```

```{r}
#| include: false
per_knee <- count(knees, case_id)
check_agree(list(knees = nrow(per_knee), complete = sum(per_knee$n == 4), scores = nrow(knees)), reticulate::py$chk)
```

All 330 knees have at least one score, 1146 scores in all, but only 192 knees have all four. Repeated-measures ANOVA would drop the other 138 knees (42%) together with every score they did give. A mixed model keeps all 1146 scores.

Dropping patients isn't only wasteful. It can bias the result, and that depends on why scores are missing:
- **Missing completely at random:** a missed visit has nothing to do with the patient's recovery (the clinic rescheduled, the patient moved). Both methods are unbiased; the mixed model is more precise because it uses more data.
- **Missing at random:** missing depends on things you measured, such as an earlier score. A patient who scored badly at 6 weeks is less likely to return at 3 months. Repeated-measures ANOVA is then biased, because the patients it keeps recovered better; a mixed model is still unbiased, because it uses the earlier scores to fill the picture in.
- **Missing not at random:** missing depends on the score that wasn't collected (patients stay away *because* their knee is worse that week). Nothing fixes this from the data alone. Say so as a limitation.

## A random intercept for each knee {#random-intercept}

Scores from the same knee are related: a knee that starts low tends to stay lower than average. A mixed model handles this with a **random intercept**: each knee gets its own baseline level, shifted up or down from the average. The **fixed effects** (here, the visits) describe the average patient; the random intercepts describe how much knees differ from that average.

::: {.panel-tabset group="language"}
## R

```{r}
knee_model <- lmer(prom_score ~ visit + (1 | case_id), data = knees)   # (1 | case_id): an intercept per knee
print(summary(knee_model), correlation = FALSE)
```

## Python

```{python}
knee_model = smf.mixedlm("prom_score ~ visit", knees, groups="case_id").fit(reml=True)   # groups: an intercept per knee
print(knee_model.summary())
```
:::

```{python}
#| include: false
fixed = knee_model.fe_params
chk = {"intercept": float(fixed["Intercept"]), "visit_6wk": float(fixed["visit[T.6wk]"]), "visit_1yr": float(fixed["visit[T.1yr]"]),
       "se_1yr": float(knee_model.bse_fe["visit[T.1yr]"]), "sd_knee": float(np.sqrt(knee_model.cov_re.iloc[0, 0])),
       "sd_residual": float(np.sqrt(knee_model.scale))}
```

```{r}
#| include: false
knee_sd <- as.data.frame(VarCorr(knee_model))$sdcor
# The estimates agree to about 1e-6. The standard errors differ in the fourth significant figure:
# lme4 computes them with the variances held fixed, statsmodels from the whole likelihood's
# Hessian (checked by hand while writing this page). See the R vs Python box.
check_agree(list(intercept = fixef(knee_model)[["(Intercept)"]], visit_6wk = fixef(knee_model)[["visit6wk"]],
                 visit_1yr = fixef(knee_model)[["visit1yr"]], se_1yr = sqrt(diag(vcov(knee_model)))[4],
                 sd_knee = knee_sd[1], sd_residual = knee_sd[2]),
            reticulate::py$chk, tol = 1e-3)
```

Reading the output:
- **Fixed effects:** the average KOOS JR was 50.0 before surgery (the intercept), and higher by 12.5 points at 6 weeks, 24.2 at 3 months and 33.9 at 1 year. Each visit's coefficient is its difference from pre-op.
- **Random effects:** knees' own baseline levels vary around the average with an SD of 8.8 points (R's "case_id (Intercept)" row; Python's "case_id Var" row gives the variance, 8.8² = 78.1). The scores also vary from visit to visit within a knee with a residual SD of 8.6 points.
- **How much of the variation is between knees:** 78.1 / (78.1 + 73.5) = 0.52, the intraclass correlation ([page 17](17-agreement.qmd#icc) uses the same idea for raters). About half of the spread in scores comes from knees differing from each other; that's why the scores can't be treated as independent.
- **REML:** both programs fit the model by restricted maximum likelihood, the standard choice for estimating it.

::: {.callout-tip}
## 🔀 R vs Python: degrees of freedom
The estimates agree. The standard errors agree to three or four significant figures: lme4 computes them with the knee and residual variances held at their estimates, statsmodels from the curvature of the whole likelihood. The p-values and CIs differ a little more. lmerTest gives each fixed effect a t test with **Satterthwaite** degrees of freedom, an approximation to how much information the estimate rests on. statsmodels uses a z test, as if the degrees of freedom were infinite. With 330 knees the difference is in the third decimal place; with a small study, trust R's.
:::

## Estimated marginal means {#estimated-marginal-means}

Report the model's estimate at each visit, with its 95% CI. These are the **estimated marginal means** (EMMs): the average score the model expects at each visit, using every knee, including those with missed visits.

::: {.panel-tabset group="language"}
## R

```{r}
knee_means <- emmeans(knee_model, ~ visit, lmer.df = "satterthwaite")
knee_means
# each visit minus pre-op; adjust = "none" because these are the planned comparisons (page 15)
confint(contrast(knee_means, method = "trt.vs.ctrl", adjust = "none"))
```

## Python

```{python}
def marginal_means(model, grid):
    """The model's average score for each row of grid (fixed effects only), with its standard error and 95% CI."""
    X = patsy.build_design_matrices([model.model.data.model_spec], grid, return_type="dataframe")[0]
    beta = model.fe_params
    cov = model.cov_params().loc[beta.index, beta.index]
    means = grid.copy()
    means["emmean"] = X @ beta
    means["se"] = np.sqrt(np.diag(X @ cov @ X.T))
    means["lower"] = means["emmean"] - 1.96 * means["se"]
    means["upper"] = means["emmean"] + 1.96 * means["se"]
    return means

visit_grid = pd.DataFrame({"visit": pd.Categorical(visits, categories=visits)})
print(marginal_means(knee_model, visit_grid).round(2))
print(knee_model.conf_int().loc[["visit[T.6wk]", "visit[T.3mo]", "visit[T.1yr]"]])   # each visit minus pre-op
```
:::

```{python}
#| include: false
knee_means = marginal_means(knee_model, visit_grid)
chk = {"emm_pre": float(knee_means["emmean"].iloc[0]), "emm_1yr": float(knee_means["emmean"].iloc[3]),
       "se_pre": float(knee_means["se"].iloc[0]), "se_1yr": float(knee_means["se"].iloc[3])}
```

```{r}
#| include: false
knee_emm <- summary(knee_means)
# standard errors computed two ways, as in the check above
check_agree(list(emm_pre = knee_emm$emmean[1], emm_1yr = knee_emm$emmean[4], se_pre = knee_emm$SE[1], se_1yr = knee_emm$SE[4]),
            reticulate::py$chk, tol = 1e-3)
```

- **emmean, lower.CL / upper.CL:** KOOS JR averaged 50.0 (95% CI 48.6 to 51.3) before surgery, 62.5 at 6 weeks, 74.2 at 3 months and 83.9 (95% CI 82.5 to 85.3) at 1 year.
- **The contrasts:** the improvement from pre-op, with its CI: 33.9 points by 1 year (95% CI 32.5 to 35.3).

The 192 knees with all four scores average 49.2 before surgery and 84.0 at 1 year. That's close to the mixed model, as expected here: in this synthetic cohort, visits were missed completely at random. With real patients you can't count on that, and the mixed model's answer, which uses all 330 knees, is the one to report.

## Time: categories or a curve? {#time}

So far each visit has its own mean: **time as categories**. That fits when everyone is seen at the same few scheduled visits, and it makes no assumption about the shape of recovery. The alternative is **time as a number**, days since surgery, with a curve. That suits many or irregular visits, but the curve's shape must be right. Recovery isn't a straight line, so use a natural cubic spline ([page 12](../catalog/12-predict-from-several.qmd#multiple-nonlinear-regression) explains splines):

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 3.5
curve_model <- lmer(prom_score ~ ns(visit_days, df = 3) + (1 | case_id), data = knees)

days <- tibble(visit_days = c(-14, 42, 90, 365))           # the scheduled visit days
on_days <- predict(curve_model, newdata = days, re.form = NA)   # re.form = NA: the average knee
on_days

curve <- tibble(visit_days = -27:395)
curve$prom_score <- predict(curve_model, newdata = curve, re.form = NA)
ggplot(curve, aes(visit_days, prom_score)) +
  geom_line() +
  geom_point(data = summary(knee_means) |> mutate(visit_days = c(-14, 42, 90, 365)), aes(y = emmean)) +
  labs(x = "Days since surgery", y = "KOOS JR")
```

## Python

```{python}
day_knots = list(knees["visit_days"].quantile([1/3, 2/3]))     # the same knots R's ns(df = 3) uses
day_low, day_high = knees["visit_days"].min(), knees["visit_days"].max()
curve_model = smf.mixedlm("prom_score ~ cr(visit_days, knots=day_knots, lower_bound=day_low, upper_bound=day_high,"
                          " constraints='center')", knees, groups="case_id").fit(reml=True)

days = pd.DataFrame({"visit_days": [-14, 42, 90, 365]})        # the scheduled visit days
on_days = curve_model.predict(days)                            # the average knee
print(on_days.round(2))

curve = pd.DataFrame({"visit_days": np.arange(-27, 396)})
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(curve["visit_days"], curve_model.predict(curve))
ax.scatter(days["visit_days"], marginal_means(knee_model, visit_grid)["emmean"])
ax.set_xlabel("Days since surgery")
ax.set_ylabel("KOOS JR")
plt.tight_layout()
plt.show()
```
:::

```{python}
#| include: false
chk = {"day_42": float(on_days.iloc[1]), "day_365": float(on_days.iloc[3])}
```

```{r}
#| include: false
# the two optimizers stop at slightly different points
check_agree(list(day_42 = on_days[[2]], day_365 = on_days[[4]]), reticulate::py$chk, tol = 1e-4)
```

The curve passes close to the visit means (the points): 62.7 at 6 weeks and 84.1 at 1 year, against 62.5 and 83.9. But look between 3 months and 1 year. No knee was scored there, and the curve invents a peak of about 89 points at around 8 months, then falls. With a few fixed visits, a curve has nothing to follow between them. Categories are simpler, make no such claims, and are what the rest of this page uses.

::: {.callout-warning}
## ⚠️ Watch out: a straight line for time
`prom_score ~ visit_days` would force recovery to be a straight line: as steep between 3 months and 1 year as in the first 6 weeks. Always plot the visit means first. If you use time as a number, let it bend.
:::

## Does recovery differ between groups? {#group-by-time}

To ask whether men and women recover differently, add sex and its **interaction** with visit. The interaction lets each sex have its own pattern of change. Its test asks whether the patterns differ, which is the question; the main effect of sex alone only compares the average levels.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 3.5
sex_model <- lmer(prom_score ~ visit * sex + (1 | case_id), data = knees)
sex_anova <- anova(sex_model)                           # F tests, Satterthwaite degrees of freedom
sex_anova

sex_means <- emmeans(sex_model, ~ visit | sex, lmer.df = "satterthwaite")
sex_means
emmip(sex_model, sex ~ visit, CIs = TRUE) +            # the two recovery patterns, with 95% CIs
  labs(x = "Visit", y = "KOOS JR")
```

## Python

```{python}
sex_model = smf.mixedlm("prom_score ~ visit * sex", knees, groups="case_id").fit(reml=True)

interaction = [name for name in sex_model.fe_params.index if ":" in name]     # the three visit x sex terms
sex_wald = sex_model.wald_test(" = 0, ".join(interaction) + " = 0", scalar=True)   # do the patterns differ?
print(sex_wald.statistic, sex_wald.pvalue)                                          # chi-square on 3 df, p-value

sex_grid = pd.DataFrame([(visit, sex) for sex in ["Female", "Male"] for visit in visits], columns=["visit", "sex"])
sex_grid["visit"] = pd.Categorical(sex_grid["visit"], categories=visits)
sex_means = marginal_means(sex_model, sex_grid)
print(sex_means.round(2))

fig, ax = plt.subplots(figsize=(7, 3.5))
for sex, rows in sex_means.groupby("sex"):
    ax.errorbar(rows["visit"].astype(str), rows["emmean"], yerr=1.96 * rows["se"], marker="o", capsize=3, label=sex)
ax.set_xlabel("Visit")
ax.set_ylabel("KOOS JR")
legend = ax.legend()
plt.tight_layout()
plt.show()
```
:::

```{python}
#| include: false
chk = {"wald_per_df": float(sex_wald.statistic) / 3, "emm_male_6wk": float(sex_means["emmean"].iloc[5]),
       "emm_female_1yr": float(sex_means["emmean"].iloc[3])}
```

```{r}
#| include: false
sex_emm <- summary(sex_means)
# R's F is the same Wald statistic divided by its 3 degrees of freedom; it inherits the
# standard-error difference explained in the check after the first model
check_agree(list(wald_per_df = sex_anova["visit:sex", "F value"], emm_male_6wk = sex_emm$emmean[6],
                 emm_female_1yr = sex_emm$emmean[4]),
            reticulate::py$chk, tol = 1e-3)
```

- **visit:sex, F = 2.09 on 3 and 832 df, p = 0.100:** no clear evidence that recovery differs between men and women. Python's Wald test gives the undivided statistic, 6.26 on 3 degrees of freedom, with a chi-square p-value of 0.099.
- **The EMMs** show why: the two patterns cross back and forth by a point or two. Men were 2.8 points ahead at 6 weeks (63.9 vs 61.2), women 0.9 points ahead at 3 months, and they were within about a point of each other at 1 year (84.4 vs 83.4).

::: {.callout-warning}
## ⚠️ Watch out: a non-significant interaction isn't "the same recovery"
p = 0.100 means the data can't show a difference in recovery between the sexes; it doesn't show the recoveries are the same. Report the EMMs with their CIs so readers can see how big a difference the data still allow.
:::

## Bilateral patients {#bilateral}

46 of the knee patients had both knees replaced, so 92 of the 330 knees come in pairs. The two knees share the same person, so their scores may be related beyond what each knee's own intercept captures. The standard fix is a second random intercept, for the patient, with knees **nested** in patients: in lme4, `(1 | patient_id/case_id)`; in statsmodels, `groups="patient_id"` with a variance component for `case_id`.

In this cohort the patient-level intercept comes out at almost exactly zero (lme4 warns that the fit is "singular"), so the simpler model above is enough. In your data, fit the nested model and report it unless it is singular. [Page 3](../foundations/03-distributions.qmd#paired) explains why bilateral patients need care, and [page 14](../survival/14-cox-regression.qmd#stratified-cox) shows the survival-analysis version.

## How to report it {#reporting}

> **Methods:** KOOS JR scores before surgery and at 6 weeks, 3 months and 1 year were analyzed with a linear mixed model, with visit as a categorical fixed effect and a random intercept for each knee, fitted by restricted maximum likelihood. All available scores were used, including those from knees that missed a visit. Differences between men and women in the pattern of recovery were tested with a visit × sex interaction (Satterthwaite degrees of freedom). Estimated marginal means are reported with 95% CIs.
>
> **Results:** Of 330 knees, 192 (58.2%) had all four scores; all 1146 scores were analyzed. The estimated mean KOOS JR rose from 50.0 (95% CI 48.6 to 51.3) before surgery to 83.9 (95% CI 82.5 to 85.3) at 1 year, an improvement of 33.9 points (95% CI 32.5 to 35.3). There was no clear evidence that the pattern of recovery differed between men and women (interaction F(3, 832) = 2.09, p = 0.100).

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
knee_vc <- as.data.frame(VarCorr(knee_model))
knee_change <- summary(confint(contrast(knee_means, method = "trt.vs.ctrl", adjust = "none")))
complete_means <- knees |> group_by(case_id) |> filter(n() == 4) |> ungroup() |> group_by(visit) |> summarise(mean = mean(prom_score))
bilateral_knees <- knees |> distinct(patient_id, case_id) |> count(patient_id) |> filter(n == 2)
hips <- proms |> filter(instrument == "HOOS JR", !is.na(prom_score)) |> mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))
hip_emm <- summary(emmeans(lmer(prom_score ~ visit + (1 | case_id), data = hips), ~ visit, lmer.df = "satterthwaite"))
pcs_all <- proms |> filter(!is.na(vr12_pcs)) |> mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))
pcs_emm <- summary(emmeans(lmer(vr12_pcs ~ visit + (1 | case_id), data = pcs_all), ~ visit, lmer.df = "satterthwaite"))
age_knees <- knees |> mutate(age_group = cut(age, c(0, 64, 74, Inf), labels = c("under 65", "65 to 74", "75 and over")))
age_anova <- anova(lmer(prom_score ~ visit * age_group + (1 | case_id), data = age_knees))
stopifnot(
  nrow(per_knee) == 330, sum(per_knee$n == 4) == 192, nrow(knees) == 1146, 330 - 192 == 138,
  round(100 * 138 / 330) == 42, round(100 * 192 / 330, 1) == 58.2,
  round(fixef(knee_model)[2:4], 1) == c(12.5, 24.2, 33.9), round(fixef(knee_model)[[1]], 1) == 50.0,
  round(knee_vc$sdcor, 1) == c(8.8, 8.6), round(knee_vc$vcov, 1) == c(78.1, 73.5),
  round(knee_vc$vcov[1] / sum(knee_vc$vcov), 2) == 0.52,
  round(knee_emm$emmean, 1) == c(50.0, 62.5, 74.2, 83.9),
  round(c(knee_emm$lower.CL[1], knee_emm$upper.CL[1], knee_emm$lower.CL[4], knee_emm$upper.CL[4]), 1) == c(48.6, 51.3, 82.5, 85.3),
  round(c(knee_change$estimate[3], knee_change$lower.CL[3], knee_change$upper.CL[3]), 1) == c(33.9, 32.5, 35.3),
  round(complete_means$mean[c(1, 4)], 1) == c(49.2, 84.0),
  round(on_days[c(2, 4)], 1) == c(62.7, 84.1),
  round(max(curve$prom_score)) == 89, curve$visit_days[which.max(curve$prom_score)] %/% 30 == 8,
  round(sex_anova["visit:sex", "F value"], 2) == 2.09, round(sex_anova["visit:sex", "DenDF"]) == 832,
  round(sex_anova["visit:sex", "Pr(>F)"], 3) == 0.100,
  round(reticulate::py_eval("float(sex_wald.statistic)"), 2) == 6.26, round(reticulate::py_eval("float(sex_wald.pvalue)"), 3) == 0.099,
  round(sex_emm$emmean[c(6, 2)], 1) == c(63.9, 61.2), round(sex_emm$emmean[6] - sex_emm$emmean[2], 1) == 2.8,
  round(sex_emm$emmean[3] - sex_emm$emmean[7], 1) == 0.9, round(sex_emm$emmean[c(8, 4)], 1) == c(84.4, 83.4),
  nrow(bilateral_knees) == 46,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  n_distinct(hips$case_id) == 270, nrow(hips) == 906, sum(table(hips$case_id) == 4) == 136,
  round(hip_emm$emmean, 1) == c(45.5, 68.6, 80.1, 88.2),
  round(c(hip_emm$lower.CL[4], hip_emm$upper.CL[4]), 1) == c(86.7, 89.7),
  n_distinct(pcs_all$case_id) == 600, nrow(pcs_all) == 2052,
  round(pcs_emm$emmean, 1) == c(31.2, 35.3, 41.0, 44.9),
  round(age_anova["visit:age_group", "F value"], 2) == 1.00, round(age_anova["visit:age_group", "Pr(>F)"], 3) == 0.422,
  round(age_anova["visit:age_group", "NumDF"]) == 6
)
```

## Exercises {#exercises}

The solutions use the packages, data and functions loaded in the sections above, so run the page from the top first.

**1.** Fit the same random-intercept model to HOOS JR in the total hip replacements and report the estimated mean at each visit.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
hips <- proms |>
  filter(instrument == "HOOS JR", !is.na(prom_score)) |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))
c(hips = n_distinct(hips$case_id), scores = nrow(hips), complete = sum(table(hips$case_id) == 4))

hip_model <- lmer(prom_score ~ visit + (1 | case_id), data = hips)
emmeans(hip_model, ~ visit, lmer.df = "satterthwaite")
```

## Python

```{python}
hips = proms[(proms["instrument"] == "HOOS JR") & proms["prom_score"].notna()].copy()
hips["visit"] = pd.Categorical(hips["visit"], categories=visits)
print(hips["case_id"].nunique(), len(hips), (hips.groupby("case_id").size() == 4).sum())

hip_model = smf.mixedlm("prom_score ~ visit", hips, groups="case_id").fit(reml=True)
print(marginal_means(hip_model, visit_grid).round(2))
```
:::

Of 270 hips, 136 had all four scores; all 906 scores were used. The estimated mean HOOS JR rose from 45.5 before surgery to 68.6 at 6 weeks, 80.1 at 3 months and 88.2 (95% CI 86.7 to 89.7) at 1 year.
:::

**2.** [Page 9](../catalog/09-three-plus-matched.qmd#repeated-measures-anova) analyzed the VR-12 physical component score (PCS) with repeated-measures ANOVA in the 328 patients measured at all four visits. Fit a mixed model with every PCS score instead. How many patients does it use, and do the visit means change?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
pcs_all <- proms |>
  filter(!is.na(vr12_pcs)) |>
  mutate(visit = factor(visit, levels = c("preop", "6wk", "3mo", "1yr")))
c(patients = n_distinct(pcs_all$case_id), scores = nrow(pcs_all))

pcs_model <- lmer(vr12_pcs ~ visit + (1 | case_id), data = pcs_all)
emmeans(pcs_model, ~ visit, lmer.df = "satterthwaite")
```

## Python

```{python}
pcs_all = proms[proms["vr12_pcs"].notna()].copy()
pcs_all["visit"] = pd.Categorical(pcs_all["visit"], categories=visits)
print(pcs_all["case_id"].nunique(), len(pcs_all))

pcs_model = smf.mixedlm("vr12_pcs ~ visit", pcs_all, groups="case_id").fit(reml=True)
print(marginal_means(pcs_model, visit_grid).round(2))
```
:::

The mixed model uses all 600 patients (2052 scores) instead of 328. Its visit means, 31.2, 35.3, 41.0 and 44.9, are almost the same as page 9's complete-patient means (31.2, 34.9, 41.0 and 44.9): in this synthetic cohort visits were missed completely at random, so dropping patients cost precision rather than accuracy.
:::

**3.** Does knee recovery differ by age group (under 65, 65 to 74, 75 and over)? Fit the visit × age group model and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
age_knees <- knees |>
  mutate(age_group = cut(age, c(0, 64, 74, Inf), labels = c("under 65", "65 to 74", "75 and over")))
age_model <- lmer(prom_score ~ visit * age_group + (1 | case_id), data = age_knees)
anova(age_model)
```

## Python

```{python}
age_knees = knees.copy()
age_knees["age_group"] = pd.cut(age_knees["age"], [0, 64, 74, 200], labels=["under 65", "65 to 74", "75 and over"])
age_model = smf.mixedlm("prom_score ~ visit * age_group", age_knees, groups="case_id").fit(reml=True)
age_terms = [name for name in age_model.fe_params.index if ":" in name]     # the six visit x age group terms
age_wald = age_model.wald_test(" = 0, ".join(age_terms) + " = 0", scalar=True)
print(age_wald.statistic, age_wald.pvalue)                                          # chi-square on 6 df, p-value
```
:::

There was no clear evidence that the pattern of recovery in KOOS JR differed between age groups (visit × age group interaction F(6, 831) = 1.00, p = 0.422).
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render beyond/16-mixed-models.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `281 passed`.

- [ ] **Step 5: Prove the standard-error check bites, then restore**

In the `#random-intercept` section's Python block, change `.fit(reml=True)` to `.fit(reml=False)` in the `knee_model = ...` line, then run `quarto render beyond/16-mixed-models.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'se_1yr'` (R 0.73351, Python 0.73226). Maximum likelihood shrinks the variances, a 0.2% change that the `tol = 1e-3` check still catches. Undo the change, then run:

```bash
rm -rf beyond/16-mixed-models_files
quarto render beyond/16-mixed-models.qmd
uv run pytest tests/site -q
```

Expected: `281 passed`.

- [ ] **Step 6: Commit**

```bash
git add beyond/16-mixed-models.qmd _freeze/beyond/16-mixed-models tests/site/sitelib.py tests/site/test_beyond.py
git commit -m "Write page 16, mixed models for repeated PROMs: random intercepts, marginal means, time, group x time, bilateral patients

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Page 17, agreement and reliability

**Files:**
- Modify: `beyond/17-agreement.qmd` (replace the stub)
- Create: `_freeze/beyond/17-agreement/` (render output; commit it)
- Modify: `tests/site/sitelib.py`, `tests/site/test_beyond.py`

**Interfaces:**
- Consumes:
  - Task 2's `FREE_FORM_SECTIONS`, `code_of` and `test_beyond.py`
  - irr and DescTools (already installed)
  - page 7's `#exercises`
  - `data/radiographic_reliability.csv`
- Produces: page 17 anchors `#reliability-vs-agreement`, `#icc`, `#inter-intra-rater`, `#bland-altman`, `#kappa`, `#reporting` and `#exercises`. Page 16 links to `#icc`, and Task 5 links to `#bland-altman`.

- [ ] **Step 1: Write the failing tests**

In `tests/site/sitelib.py`'s `FREE_FORM_SECTIONS`, after the last line of the page 16 entry,

```python
        "bilateral", "reporting", "exercises"],
```

add

```python
    "beyond/17-agreement.html": [
        "reliability-vs-agreement", "icc", "inter-intra-rater", "bland-altman", "kappa", "reporting",
        "exercises"],
```

In `tests/site/test_beyond.py`, replace the line `MIXED = "beyond/16-mixed-models.html"` with

```python
MIXED = "beyond/16-mixed-models.html"
AGREEMENT = "beyond/17-agreement.html"
```

and append to the end of the file (after two blank lines):

```python
# ---- page 17: agreement and reliability ----------------------------------------------

def test_icc_form_is_named_and_interpreted_with_koo_and_li(site):
    text = text_of(section(AGREEMENT, "icc"))
    for phrase in ["two-way random", "absolute agreement", "single", "Koo and Li", "ICC(A,1)"]:
        assert phrase in text, phrase


def test_inter_and_intra_rater_reliability_are_both_measured(site):
    assert "inter-rater" in text_of(section(AGREEMENT, "icc"))
    text = text_of(section(AGREEMENT, "inter-intra-rater"))
    assert "intra-rater" in text.lower() and "0.915" in text


def test_bland_altman_plot_and_limits_in_both_languages(site):
    found = section(AGREEMENT, "bland-altman")
    plotted = [tabset for tabset in found.select("div.panel-tabset")
               if all(pane.select("img") for pane in tabset.select("div.tab-pane"))]
    assert plotted, "the Bland-Altman plot is drawn in both languages"
    assert "limits of agreement" in text_of(found).lower() and "−2.74° to 3.74°" in text_of(found)


def test_kappa_and_weighted_kappa_with_ordered_categories(site):
    found = section(AGREEMENT, "kappa")
    code = code_of(found)
    assert "CohenKappa(" in code and "cohens_kappa(" in code and "Equal-Spacing" in code and 'wt="linear"' in code
    assert "alphabetically" in text_of(found)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `8 failed, 284 passed`: 4 page-17 tests in `test_free_form.py` and the 4 in `test_beyond.py`.

- [ ] **Step 3: Write the page**

Replace `beyond/17-agreement.qmd` with:

````markdown
---
title: "17 · Agreement & reliability"
description: "ICC, Bland-Altman limits of agreement, and kappa for radiographic measurements: how well two raters, or one rater on two days, agree."
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

Before a measurement goes into a study, someone should ask: if it were measured again, would you get the same answer? Alignment angles on long-leg radiographs are a good example. Two surgeons can place the same landmarks a little differently, and one surgeon can place them differently on another day. This page shows how to measure that, using the practice data's reliability study: 60 knees, each measured by two raters (R1 and R2), twice, at least two weeks apart.

::: {.callout-note}
## 💡 How this page works
Run the code blocks in order, from the top: later blocks use the packages and data loaded in the first one.
:::

## Reliability or agreement? {#reliability-vs-agreement}

The two words are often used as if they meant the same thing. They don't:
- **Reliability** asks whether a measurement can tell patients apart: are the real differences between knees large compared with the disagreement between readings? It's measured with the **intraclass correlation coefficient** (ICC), a number from 0 to 1. Because it compares the disagreement with how much the knees differ, the same raters look more reliable in a cohort with a wider range of deformities.
- **Agreement** asks how close two readings are, in the measurement's own units. If rater 2 reads 3° higher than rater 1 for some knees, that's poor agreement, however reliable the ranking. It's measured with the **Bland-Altman limits of agreement**, in degrees.

Report both. A clinician deciding whether a knee is in varus needs to know the agreement in degrees, not only that the ICC was 0.9.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

readings <- read_csv("data/radiographic_reliability.csv", show_col_types = FALSE)
readings |> head(4)
readings |> count(rater, session)                      # 60 knees in every rater x session
```

## Python

```{python}
import numpy as np
import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.inter_rater import cohens_kappa

readings = pd.read_csv("data/radiographic_reliability.csv")
print(readings.head(4))
print(readings.groupby(["rater", "session"]).size())     # 60 knees in every rater x session
```
:::

```{python}
#| include: false
chk = {"knees": float(readings["knee_id"].nunique()), "rows": float(len(readings))}
```

```{r}
#| include: false
check_agree(list(knees = n_distinct(readings$knee_id), rows = nrow(readings)), reticulate::py$chk)
```

The data are long: one row per knee, rater and session, with the hip-knee-ankle angle (HKA, 180° is neutral, below 180° is varus), the medial proximal tibial angle (MPTA), the lateral distal femoral angle (LDFA) and the CPAK class those angles give.

## The intraclass correlation coefficient {#icc}

There are several ICCs, and the right one depends on the design. Three choices define it (Koo & Li, 2016):
- **Model:** are the raters a random sample of the raters who might use this measurement (**two-way random**), or the only raters you care about (**two-way mixed**)? For a measurement other surgeons will use, choose random.
- **Type:** should a rater who always reads higher count against the measurement (**absolute agreement**) or not (**consistency**)? For angles that feed clinical decisions, it should: choose absolute agreement.
- **Unit:** will the study use one rater's reading (**single**) or the average of several (**average**)? Usually single.

For inter-rater reliability of HKA, that gives a two-way random, absolute-agreement, single-rater ICC, written ICC(A,1) (or ICC(2,1) in Shrout and Fleiss's older naming). Using each rater's first-session readings:

::: {.panel-tabset group="language"}
## R

```{r}
inter_hka <- readings |>
  filter(session == 1) |>
  select(knee_id, rater, hka_deg) |>
  pivot_wider(names_from = rater, values_from = hka_deg)     # one column per rater

inter_icc <- irr::icc(inter_hka[, c("R1", "R2")], model = "twoway", type = "agreement", unit = "single")
inter_icc
```

## Python

```{python}
first_session = readings[readings["session"] == 1]
inter_icc = pg.intraclass_corr(data=first_session, targets="knee_id", raters="rater", ratings="hka_deg")
print(inter_icc[["Type", "ICC", "CI95"]])     # ICC(A,1): two-way random, absolute agreement, single rater
```
:::

```{python}
#| include: false
row = inter_icc.set_index("Type").loc["ICC(A,1)"]
chk = {"icc": float(row["ICC"]), "low": float(row["CI95"][0]), "high": float(row["CI95"][1])}
```

```{r}
#| include: false
# pingouin rounds its CI to 2 decimals, so R's bounds are rounded to match
check_agree(list(icc = inter_icc$value, low = round(inter_icc$lbound, 2), high = round(inter_icc$ubound, 2)),
            reticulate::py$chk)
```

- **ICC(A,1) = 0.889** (Python's `ICC(A,1)` row; R prints 0.889).
- **95% CI 0.82 to 0.93.** Koo and Li's guide: below 0.5 poor, 0.5 to 0.75 moderate, 0.75 to 0.9 good, above 0.9 excellent. Judge by the CI, not the point estimate: this one runs from good to excellent.
- **The F test** (R) tests whether the ICC is above 0. It nearly always is, so it's rarely worth reporting.

::: {.callout-warning}
## ⚠️ Watch out: always say which ICC
The same data give a different ICC for every model, type and unit: here 0.889 for absolute agreement and 0.896 for consistency, and 0.94 for the average of the two raters. "ICC = 0.94" with no form named can't be interpreted. Write the form out in the Methods.
:::

::: {.callout-tip}
## 🔀 R vs Python: one ICC or all of them
R's `irr::icc()` computes the one ICC you ask for. pingouin's `intraclass_corr()` computes all six forms at once; pick the row. It labels them two ways: `ICC(A,1)` in McGraw and Wong's naming, which matches R's arguments, or `ICC2` in older pingouin versions. pingouin rounds the CI to 2 decimals.
:::

## Inter-rater and intra-rater reliability {#inter-intra-rater}

The ICC above is **inter-rater** reliability: two raters, same films. **Intra-rater** (test-retest) reliability uses one rater reading the same films twice, far enough apart that they don't remember their first answers. The same ICC form applies, with the two sessions in place of the two raters:

::: {.panel-tabset group="language"}
## R

```{r}
intra_hka <- readings |>
  filter(rater == "R1") |>
  select(knee_id, session, hka_deg) |>
  pivot_wider(names_from = session, values_from = hka_deg, names_prefix = "session_")

intra_icc <- irr::icc(intra_hka[, c("session_1", "session_2")], model = "twoway", type = "agreement", unit = "single")
intra_icc
```

## Python

```{python}
rater_1 = readings[readings["rater"] == "R1"]
intra_icc = pg.intraclass_corr(data=rater_1, targets="knee_id", raters="session", ratings="hka_deg")
print(intra_icc.set_index("Type").loc["ICC(A,1)", ["ICC", "CI95"]])
```
:::

```{python}
#| include: false
row = intra_icc.set_index("Type").loc["ICC(A,1)"]
chk = {"icc": float(row["ICC"]), "low": float(row["CI95"][0]), "high": float(row["CI95"][1])}
```

```{r}
#| include: false
# pingouin rounds its CI to 2 decimals
check_agree(list(icc = intra_icc$value, low = round(intra_icc$lbound, 2), high = round(intra_icc$ubound, 2)),
            reticulate::py$chk)
```

Rater 1 agreed with themselves a little better than with rater 2: intra-rater ICC(A,1) = 0.915 (95% CI 0.86 to 0.95), excellent at its point estimate and good to excellent across its CI.

## Bland-Altman: how far apart are the readings? {#bland-altman}

The ICC is a ratio and has no units. To see how far apart two readings can be, in degrees, plot the **difference** between them against their **mean**, one point per knee. Then add three lines:
- **The bias:** the mean difference, showing whether one rater reads systematically higher.
- **The 95% limits of agreement:** bias ± 1.96 × SD of the differences. For 95% of knees, rater 2's reading will fall between these limits relative to rater 1's.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 4
inter_hka <- inter_hka |> mutate(difference = R2 - R1, mean = (R1 + R2) / 2)

n_knees <- nrow(inter_hka)
bias <- mean(inter_hka$difference)
sd_diff <- sd(inter_hka$difference)
limits <- bias + c(-1.96, 1.96) * sd_diff
se_limit <- sqrt(3 * sd_diff^2 / n_knees)                      # Bland and Altman's SE for each limit
limit_cis <- rbind(lower = limits[1] + c(-1, 1) * qt(0.975, n_knees - 1) * se_limit,
                   upper = limits[2] + c(-1, 1) * qt(0.975, n_knees - 1) * se_limit)

c(bias = bias, bias_ci = t.test(inter_hka$difference)$conf.int, sd = sd_diff, limits = limits)
limit_cis

ggplot(inter_hka, aes(mean, difference)) +
  geom_point() +
  geom_hline(yintercept = bias) +
  geom_hline(yintercept = limits, linetype = "dashed") +
  labs(x = "Mean of the two readings (°)", y = "Rater 2 − rater 1 (°)")
```

## Python

```{python}
inter = first_session.pivot(index="knee_id", columns="rater", values="hka_deg")
difference = inter["R2"] - inter["R1"]
mean = (inter["R1"] + inter["R2"]) / 2

n_knees = len(difference)
bias = difference.mean()
sd_diff = difference.std()                                     # pandas uses n - 1, like R
limits = bias + np.array([-1.96, 1.96]) * sd_diff
se_limit = np.sqrt(3 * sd_diff**2 / n_knees)                   # Bland and Altman's SE for each limit
t_crit = stats.t.ppf(0.975, n_knees - 1)
bias_ci = stats.ttest_1samp(difference, 0).confidence_interval()
print(round(bias, 3), round(float(bias_ci.low), 3), round(float(bias_ci.high), 3), round(sd_diff, 3), limits.round(3))
print((limits - t_crit * se_limit).round(3), (limits + t_crit * se_limit).round(3))   # CI of each limit: lower ends, upper ends

fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(mean, difference)
ax.axhline(bias)
for limit in limits:
    ax.axhline(limit, linestyle="--")
ax.set_xlabel("Mean of the two readings (°)")
ax.set_ylabel("Rater 2 − rater 1 (°)")
plt.tight_layout()
plt.show()
```
:::

```{python}
#| include: false
chk = {"bias": float(bias), "bias_low": float(bias_ci.low), "sd": float(sd_diff), "limit_low": float(limits[0]),
       "limit_high": float(limits[1]), "limit_high_ci_high": float(limits[1] + t_crit * se_limit)}
```

```{r}
#| include: false
check_agree(list(bias = bias, bias_low = t.test(inter_hka$difference)$conf.int[1], sd = sd_diff, limit_low = limits[1],
                 limit_high = limits[2], limit_high_ci_high = limit_cis["upper", 2]),
            reticulate::py$chk)
```

- **Bias = 0.50°** (95% CI 0.08° to 0.93°): rater 2 reads half a degree higher than rater 1 on average, the same difference [page 7's exercise 2](../catalog/07-two-paired-groups.qmd#exercises) found with a paired t test.
- **Limits of agreement, −2.74° to 3.74°:** for 95% of knees, rater 2's reading will be between 2.7° below and 3.7° above rater 1's.
- **The CIs of the limits** (−3.48° to −2.00° and 3.00° to 4.48°) show how precisely 60 knees pin the limits down.
- **The plot:** the points scatter evenly around the bias line, with no trend up or down as the mean angle changes. A trend would mean the raters disagree more for some knees (more varus, say) than others, and a single pair of limits wouldn't describe them.

Whether limits of ±3.7° are good enough is a clinical question, not a statistical one. If a 3° difference moves a knee from "neutral" to "varus" in your study, it matters. Decide the acceptable limits **before** you run the reliability study, and compare the limits (and their CIs) with them.

## Kappa for categories {#kappa}

For a category, like CPAK class, use **Cohen's kappa**: the agreement between two raters beyond what chance alone would produce. Kappa is 1 for perfect agreement and 0 for agreement no better than chance.

::: {.panel-tabset group="language"}
## R

```{r}
cpak_levels <- c("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")
cpak <- readings |>
  filter(session == 1) |>
  select(knee_id, rater, cpak_class) |>
  pivot_wider(names_from = rater, values_from = cpak_class) |>
  mutate(R1 = factor(R1, levels = cpak_levels), R2 = factor(R2, levels = cpak_levels))

mean(cpak$R1 == cpak$R2)                                     # simple percentage agreement
cpak_kappa <- DescTools::CohenKappa(cpak$R1, cpak$R2, conf.level = 0.95)
cpak_kappa
```

## Python

```{python}
cpak_levels = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
cpak = first_session.pivot(index="knee_id", columns="rater", values="cpak_class")
print((cpak["R1"] == cpak["R2"]).mean())                       # simple percentage agreement

cpak_table = pd.crosstab(pd.Categorical(cpak["R1"], categories=cpak_levels),
                         pd.Categorical(cpak["R2"], categories=cpak_levels), dropna=False)
cpak_kappa = cohens_kappa(cpak_table.to_numpy())
print(cpak_kappa.kappa, cpak_kappa.kappa_low, cpak_kappa.kappa_upp)
```
:::

```{python}
#| include: false
chk = {"agreement": float((cpak["R1"] == cpak["R2"]).mean()), "kappa": float(cpak_kappa.kappa),
       "low": float(cpak_kappa.kappa_low), "high": float(cpak_kappa.kappa_upp)}
```

```{r}
#| include: false
check_agree(list(agreement = mean(cpak$R1 == cpak$R2), kappa = cpak_kappa[["kappa"]], low = cpak_kappa[["lwr.ci"]],
                 high = cpak_kappa[["upr.ci"]]),
            reticulate::py$chk)
```

The raters gave the same CPAK class to 40 of the 60 knees (66.7%), but some of that would happen by chance. Kappa = 0.58 (95% CI 0.44 to 0.73): moderate agreement on Landis and Koch's scale (0.41 to 0.60 moderate, 0.61 to 0.80 substantial, above 0.80 almost perfect).

**Weighted kappa for ordered categories.** Plain kappa treats every disagreement as equally bad. When the categories have an order, a near miss should count less than a big miss. CPAK class has no single order (it's a 3 × 3 grid of two angles), but each axis does. The arithmetic HKA group goes varus, neutral, valgus. A **weighted kappa** gives a disagreement between varus and neutral half the penalty of one between varus and valgus (linear weights):

::: {.panel-tabset group="language"}
## R

```{r}
hka_group <- function(cpak_class) {
  # CPAK classes I-III, IV-VI and VII-IX each run varus, neutral, valgus
  factor(c("varus", "neutral", "valgus")[(as.integer(cpak_class) - 1) %% 3 + 1],
         levels = c("varus", "neutral", "valgus"))                # in order
}
hka_table <- table(R1 = hka_group(cpak$R1), R2 = hka_group(cpak$R2))
hka_table
unweighted_kappa <- DescTools::CohenKappa(hka_table, conf.level = 0.95)                            # unweighted
weighted_kappa <- DescTools::CohenKappa(hka_table, weights = "Equal-Spacing", conf.level = 0.95)   # linear weights
rbind(unweighted = unweighted_kappa, weighted = weighted_kappa)
```

## Python

```{python}
hka_group = {cls: ["varus", "neutral", "valgus"][i % 3] for i, cls in enumerate(cpak_levels)}   # I-III, IV-VI, VII-IX
order = ["varus", "neutral", "valgus"]
hka_table = pd.crosstab(pd.Categorical(cpak["R1"].map(hka_group), categories=order),
                        pd.Categorical(cpak["R2"].map(hka_group), categories=order), dropna=False)
print(hka_table)

unweighted = cohens_kappa(hka_table.to_numpy())
weighted = cohens_kappa(hka_table.to_numpy(), wt="linear")     # linear weights
print(unweighted.kappa, weighted.kappa, weighted.kappa_low, weighted.kappa_upp)
```
:::

```{python}
#| include: false
chk = {"unweighted": float(unweighted.kappa), "weighted": float(weighted.kappa),
       "low": float(weighted.kappa_low), "high": float(weighted.kappa_upp)}
```

```{r}
#| include: false
check_agree(list(unweighted = unweighted_kappa[["kappa"]], weighted = weighted_kappa[["kappa"]],
                 low = weighted_kappa[["lwr.ci"]], high = weighted_kappa[["upr.ci"]]),
            reticulate::py$chk)
```

The raters agreed on the HKA group for 48 of 60 knees, and every disagreement was a near miss: no knee was called varus by one rater and valgus by the other. Unweighted kappa is 0.68; the weighted kappa, which gives near misses partial credit, is 0.73 (95% CI 0.58 to 0.87), substantial agreement.

::: {.callout-warning}
## ⚠️ Watch out: weighted kappa needs the categories in order
The weights depend on the order of the categories. Put them in their real order (varus, neutral, valgus) yourself. Some functions sort categories alphabetically, which would put "neutral" before "valgus" before "varus" and weight the wrong disagreements: `irr::kappa2(weight = "equal")` does, and gives 0.63 here instead of 0.73. Never use weighted kappa for categories with no order, like CPAK class itself.
:::

::: {.callout-tip}
## 🔀 R vs Python: kappa and its CI
DescTools' `CohenKappa()` and statsmodels' `cohens_kappa()` give the same kappa and the same CI. DescTools calls linear weights "Equal-Spacing" and quadratic weights "Fleiss-Cohen"; statsmodels uses `wt="linear"` and `wt="quadratic"`. scikit-learn's `cohen_kappa_score()` gives the kappa but no CI.
:::

## How to report it {#reporting}

> **Methods:** Two raters measured the hip-knee-ankle angle, MPTA and LDFA on 60 long-leg radiographs, twice, at least 2 weeks apart. Inter- and intra-rater reliability were assessed with two-way random-effects, absolute-agreement, single-rater intraclass correlation coefficients (ICC(A,1)) and interpreted according to Koo and Li. Agreement was assessed with Bland-Altman 95% limits of agreement. Agreement on CPAK class was assessed with Cohen's kappa, and on the ordered arithmetic HKA group with linearly weighted kappa.
>
> **Results:** Inter-rater reliability of the hip-knee-ankle angle was good to excellent (ICC 0.89, 95% CI 0.82 to 0.93), and intra-rater reliability excellent at its point estimate (ICC 0.91, 95% CI 0.86 to 0.95). Rater 2 measured 0.50° higher than rater 1 on average (95% CI 0.08° to 0.93°), with 95% limits of agreement from −2.74° to 3.74°. Agreement on CPAK class was moderate (κ = 0.58, 95% CI 0.44 to 0.73), and on the arithmetic HKA group substantial (weighted κ = 0.73, 95% CI 0.58 to 0.87).

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
inter_c <- irr::icc(inter_hka[, c("R1", "R2")], model = "twoway", type = "consistency", unit = "single")
inter_k <- irr::icc(inter_hka[, c("R1", "R2")], model = "twoway", type = "agreement", unit = "average")
irr_weighted <- irr::kappa2(data.frame(hka_group(cpak$R1), hka_group(cpak$R2)), weight = "equal")
mpta <- readings |> filter(session == 1) |> select(knee_id, rater, mpta_deg) |> pivot_wider(names_from = rater, values_from = mpta_deg)
mpta_icc <- irr::icc(mpta[, c("R1", "R2")], model = "twoway", type = "agreement", unit = "single")
retest <- intra_hka$session_2 - intra_hka$session_1
retest_limits <- mean(retest) + c(-1.96, 1.96) * sd(retest)
shifted <- inter_hka |> mutate(R2_shifted = R2 + 5)
shifted_icc <- irr::icc(shifted[, c("R1", "R2_shifted")], model = "twoway", type = "agreement", unit = "single")
pearson <- cor.test(inter_hka$R1, inter_hka$R2)
stopifnot(
  n_distinct(readings$knee_id) == 60, nrow(readings) == 240,
  round(inter_icc$value, 3) == 0.889, round(c(inter_icc$lbound, inter_icc$ubound), 2) == c(0.82, 0.93),
  round(inter_c$value, 3) == 0.896, round(inter_k$value, 2) == 0.94,
  round(intra_icc$value, 3) == 0.915, round(intra_icc$value, 2) == 0.91, round(c(intra_icc$lbound, intra_icc$ubound), 2) == c(0.86, 0.95),
  round(c(bias, t.test(inter_hka$difference)$conf.int), 2) == c(0.50, 0.08, 0.93),
  round(limits, 2) == c(-2.74, 3.74), round(limits, 1) == c(-2.7, 3.7),
  round(c(limit_cis["lower", ], limit_cis["upper", ]), 2) == c(-3.48, -2.00, 3.00, 4.48),
  cor.test(inter_hka$difference, inter_hka$mean)$p.value > 0.5,
  sum(cpak$R1 == cpak$R2) == 40, round(100 * mean(cpak$R1 == cpak$R2), 1) == 66.7,
  round(cpak_kappa[c("kappa", "lwr.ci", "upr.ci")], 2) == c(0.58, 0.44, 0.73),
  sum(diag(hka_table)) == 48, hka_table["varus", "valgus"] == 0, hka_table["valgus", "varus"] == 0,
  round(unweighted_kappa[["kappa"]], 2) == 0.68,
  round(weighted_kappa[c("kappa", "lwr.ci", "upr.ci")], 2) == c(0.73, 0.58, 0.87),
  round(irr_weighted$value, 2) == 0.63,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(mpta_icc$value, 2) == 0.93, round(c(mpta_icc$lbound, mpta_icc$ubound), 2) == c(0.89, 0.96),
  round(c(mean(retest), t.test(retest)$conf.int), 2) == c(-0.26, -0.65, 0.12),
  round(retest_limits, 2) == c(-3.20, 2.67),
  round(c(pearson$estimate, pearson$conf.int), 2) == c(0.90, 0.83, 0.94),
  round(cor(shifted$R1, shifted$R2_shifted), 2) == 0.90,
  round(shifted_icc$value, 2) == 0.42, round(c(shifted_icc$lbound, shifted_icc$ubound), 2) == c(-0.04, 0.78)
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Calculate the inter-rater ICC for the MPTA, using each rater's first-session readings, and describe it with Koo and Li's guide.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
mpta <- readings |>
  filter(session == 1) |>
  select(knee_id, rater, mpta_deg) |>
  pivot_wider(names_from = rater, values_from = mpta_deg)
irr::icc(mpta[, c("R1", "R2")], model = "twoway", type = "agreement", unit = "single")
```

## Python

```{python}
mpta_icc = pg.intraclass_corr(data=first_session, targets="knee_id", raters="rater", ratings="mpta_deg")
print(mpta_icc.set_index("Type").loc["ICC(A,1)", ["ICC", "CI95"]])
```
:::

Inter-rater reliability of the MPTA was excellent at its point estimate (ICC(A,1) = 0.93, 95% CI 0.89 to 0.96); the CI runs from good to excellent.
:::

**2.** Using rater 1's two sessions, calculate the Bland-Altman bias and 95% limits of agreement for HKA, and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
retest <- intra_hka$session_2 - intra_hka$session_1
c(bias = mean(retest), t.test(retest)$conf.int, limits = mean(retest) + c(-1.96, 1.96) * sd(retest))
```

## Python

```{python}
sessions = rater_1.pivot(index="knee_id", columns="session", values="hka_deg")
retest = sessions[2] - sessions[1]
retest_ci = stats.ttest_1samp(retest, 0).confidence_interval()
print(retest.mean(), retest_ci.low, retest_ci.high, retest.mean() + np.array([-1.96, 1.96]) * retest.std())
```
:::

Rater 1's second readings were 0.26° lower than the first on average (95% CI −0.65° to 0.12°), with 95% limits of agreement from −3.20° to 2.67°.
:::

**3.** A colleague reports that the two raters' HKA readings correlate well (Pearson's r = 0.90, 95% CI 0.83 to 0.94) as evidence that they agree. What's wrong with that? Show it by adding 5° to every one of rater 2's readings and recalculating r and the ICC.

::: {.callout-tip collapse="true"}
## Solution
Correlation measures whether two readings rise and fall together, not whether they're equal. A rater who reads every knee 5° too high correlates perfectly well with an accurate one.

::: {.panel-tabset group="language"}
## R

```{r}
cor.test(inter_hka$R1, inter_hka$R2)

shifted <- inter_hka |> mutate(R2_shifted = R2 + 5)
cor(shifted$R1, shifted$R2_shifted)
irr::icc(shifted[, c("R1", "R2_shifted")], model = "twoway", type = "agreement", unit = "single")
```

## Python

```{python}
pearson = stats.pearsonr(inter["R1"], inter["R2"])
pearson_ci = pearson.confidence_interval()
print(round(pearson.statistic, 3), round(float(pearson_ci.low), 3), round(float(pearson_ci.high), 3))

shifted = first_session.copy()
shifted.loc[shifted["rater"] == "R2", "hka_deg"] += 5
shifted_wide = shifted.pivot(index="knee_id", columns="rater", values="hka_deg")
print(stats.pearsonr(shifted_wide["R1"], shifted_wide["R2"]).statistic)
shifted_icc = pg.intraclass_corr(data=shifted, targets="knee_id", raters="rater", ratings="hka_deg")
print(shifted_icc.set_index("Type").loc["ICC(A,1)", ["ICC", "CI95"]])
```
:::

Pearson's r is 0.90 (95% CI 0.83 to 0.94) before and after the shift: it can't see a systematic difference. The absolute-agreement ICC drops from 0.89 to 0.42 (95% CI −0.04 to 0.78), because a 5° disagreement on every knee is poor agreement. Report the ICC and the Bland-Altman limits, not r.
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render beyond/17-agreement.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `292 passed`.

- [ ] **Step 5: Prove the ICC check reads the visible code, then restore**

In the `#icc` section's R block, change `type = "agreement"` to `type = "consistency"` in the `inter_icc <- irr::icc(...)` line, then run `quarto render beyond/17-agreement.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'icc'` (R 0.8964, Python 0.8894). Undo the change, then run:

```bash
rm -rf beyond/17-agreement_files
quarto render beyond/17-agreement.qmd
uv run pytest tests/site -q
```

Expected: `292 passed`.

- [ ] **Step 6: Commit**

```bash
git add beyond/17-agreement.qmd _freeze/beyond/17-agreement tests/site/sitelib.py tests/site/test_beyond.py
git commit -m "Write page 17, agreement and reliability: ICC forms, inter- and intra-rater, Bland-Altman, kappa and weighted kappa

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Links land on the section they promise; settle the overall-test sentence

**Files:**
- Modify: `foundations/03-distributions.qmd`, `catalog/07-two-paired-groups.qmd`, `catalog/08-three-plus-unmatched.qmd`, `catalog/09-three-plus-matched.qmd`, `catalog/11-predict-from-one.qmd`, `catalog/12-predict-from-several.qmd`, `survival/13-kaplan-meier.qmd`
- Modify: `_freeze/` for those seven pages (re-render; commit it)
- Modify: `tests/site/test_catalog.py`, `tests/site/test_beyond.py`

**Interfaces:**
- Consumes: pages 15–17's anchors (Tasks 2–4); `test_catalog.py`'s three link checks into pages 15 and 16
- Produces: `SECTION_LINKS` and three tests in `test_beyond.py`

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, a link with an anchor still counts as a link to its page. Replace

```python
    hrefs = [a["href"] for a in section(page, "which-groups-differ").select("a[href]")]
```

with

```python
    hrefs = [a["href"].split("#")[0] for a in section(page, "which-groups-differ").select("a[href]")]
```

and replace both occurrences of

```python
    assert any(a["href"].endswith("beyond/16-mixed-models.html") for a in warnings[0].select("a[href]"))
```

with

```python
    assert any(a["href"].split("#")[0].endswith("beyond/16-mixed-models.html") for a in warnings[0].select("a[href]"))
```

Append to the end of `tests/site/test_beyond.py` (after two blank lines):

```python
# ---- links into pages 15-17 ----------------------------------------------------------

# Where a sentence promises one topic ("compare the visits with paired tests ... page 15"),
# its link lands on that section, not the top of the page.
SECTION_LINKS = {
    "foundations/03-distributions.html": ["beyond/16-mixed-models.html#bilateral"],
    "catalog/07-two-paired-groups.html": ["beyond/16-mixed-models.html#why-mixed-models",
                                          "beyond/17-agreement.html#bland-altman"],
    "catalog/08-three-plus-unmatched.html": ["beyond/15-post-hoc.html#after-anova", "beyond/15-post-hoc.html#after-kruskal-wallis",
                                             "beyond/15-post-hoc.html#after-chi-square", "beyond/15-post-hoc.html#overall-test-first"],
    "catalog/09-three-plus-matched.html": ["beyond/15-post-hoc.html#after-repeated-measures-anova",
                                           "beyond/15-post-hoc.html#after-friedman", "beyond/15-post-hoc.html#after-cochran-q",
                                           "beyond/16-mixed-models.html#why-mixed-models"],
    "catalog/11-predict-from-one.html": ["beyond/16-mixed-models.html#random-intercept"],
    "catalog/12-predict-from-several.html": ["beyond/16-mixed-models.html#random-intercept"],
    "survival/13-kaplan-meier.html": ["beyond/15-post-hoc.html#after-log-rank"],
}


def beyond_links(page):
    return [a["href"].replace("../", "") for a in load(page).select("main a[href]") if "beyond/1" in a["href"]]


@pytest.mark.parametrize("page,targets", SECTION_LINKS.items())
def test_links_into_pages_15_to_17_land_on_the_section_they_promise(site, page, targets):
    assert [target for target in targets if target not in beyond_links(page)] == []


@pytest.mark.parametrize("page", SECTION_LINKS)
def test_no_link_into_pages_15_to_17_stops_at_the_top_of_the_page(site, page):
    assert [href for href in beyond_links(page) if "#" not in href] == []


def test_post_hoc_tests_are_no_longer_gated_on_the_overall_test(site):
    """Phase 3b's deferred question, settled on page 15: adjusted post-hoc tests don't need a significant overall test."""
    found = section("catalog/08-three-plus-unmatched.html", "which-groups-differ")
    assert "Only run post-hoc tests when the overall test is significant" not in text_of(found)
    assert any(a["href"].endswith("beyond/15-post-hoc.html#overall-test-first") for a in found.select("a[href]"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `15 failed, 292 passed`:
- 7 `test_links_into_pages_15_to_17_land_on_the_section_they_promise`
- 7 `test_no_link_into_pages_15_to_17_stops_at_the_top_of_the_page`
- `test_post_hoc_tests_are_no_longer_gated_on_the_overall_test`

The three edited catalog tests still pass.

- [ ] **Step 3: Add the anchors and rewrite page 8's sentence**

In `foundations/03-distributions.qmd`, replace

```markdown
use methods built for clustered data, such as [mixed models](../beyond/16-mixed-models.qmd).
```

with

```markdown
use methods built for clustered data, such as [mixed models](../beyond/16-mixed-models.qmd#bilateral).
```

In `catalog/07-two-paired-groups.qmd`, replace

```markdown
[Mixed models](../beyond/16-mixed-models.qmd) can use everyone's data
```

with

```markdown
[Mixed models](../beyond/16-mixed-models.qmd#why-mixed-models) can use everyone's data
```

In `catalog/07-two-paired-groups.qmd`, replace

```markdown
[page 17](../beyond/17-agreement.qmd) shows how to judge agreement
```

with

```markdown
[page 17](../beyond/17-agreement.qmd#bland-altman) shows how to judge agreement
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
Use a post-hoc test ([page 15](../beyond/15-post-hoc.qmd)).
```

with

```markdown
Use a post-hoc test ([page 15](../beyond/15-post-hoc.qmd#after-anova)).
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
| One-way ANOVA | Tukey's HSD (Games-Howell if the spreads differ) | [15](../beyond/15-post-hoc.qmd) |
```

with

```markdown
| One-way ANOVA | Tukey's HSD (Games-Howell if the spreads differ) | [15](../beyond/15-post-hoc.qmd#after-anova) |
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
| Kruskal-Wallis | Dunn's test with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
```

with

```markdown
| Kruskal-Wallis | Dunn's test with Holm's adjustment | [15](../beyond/15-post-hoc.qmd#after-kruskal-wallis) |
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
| Chi-square | Pairwise Fisher or chi-square tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
```

with

```markdown
| Chi-square | Pairwise Fisher or chi-square tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd#after-chi-square) |
```

In `catalog/08-three-plus-unmatched.qmd`, replace

```markdown
Only run post-hoc tests when the overall test is significant, or when you planned specific comparisons before seeing the data; say which in your Methods.
```

with

```markdown
Tukey's HSD, Dunn's test and Holm-adjusted pairwise tests control false positives on their own, so they don't need a significant overall test first. Decide before you see the data which comparisons you'll make, and say so in your Methods ([page 15](../beyond/15-post-hoc.qmd#overall-test-first)).
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
[Mixed models](../beyond/16-mixed-models.qmd) use everyone's available data
```

with

```markdown
[Mixed models](../beyond/16-mixed-models.qmd#why-mixed-models) use everyone's available data
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
a correction for multiple comparisons ([page 15](../beyond/15-post-hoc.qmd)). And remember
```

with

```markdown
a correction for multiple comparisons ([page 15](../beyond/15-post-hoc.qmd#after-repeated-measures-anova)). And remember
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
compare pairs of visits with McNemar's test and a correction for multiple comparisons ([page 15](../beyond/15-post-hoc.qmd)).
```

with

```markdown
compare pairs of visits with McNemar's test and a correction for multiple comparisons ([page 15](../beyond/15-post-hoc.qmd#after-cochran-q)).
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
| Repeated-measures ANOVA | Paired t tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
```

with

```markdown
| Repeated-measures ANOVA | Paired t tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd#after-repeated-measures-anova) |
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
| Friedman | Pairwise Wilcoxon signed-rank (or Conover) tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
```

with

```markdown
| Friedman | Pairwise Wilcoxon signed-rank (or Conover) tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd#after-friedman) |
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
| Cochran's Q | Pairwise McNemar tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd) |
```

with

```markdown
| Cochran's Q | Pairwise McNemar tests with Holm's adjustment | [15](../beyond/15-post-hoc.qmd#after-cochran-q) |
```

In `catalog/09-three-plus-matched.qmd`, replace

```markdown
For repeated PROMs, a [mixed model](../beyond/16-mixed-models.qmd) answers both questions
```

with

```markdown
For repeated PROMs, a [mixed model](../beyond/16-mixed-models.qmd#why-mixed-models) answers both questions
```

In `catalog/11-predict-from-one.qmd`, replace

```markdown
A mixed model ([page 16](../beyond/16-mixed-models.qmd)) accounts for this.
```

with

```markdown
A mixed model ([page 16](../beyond/16-mixed-models.qmd#random-intercept)) accounts for this.
```

In `catalog/12-predict-from-several.qmd`, replace

```markdown
A mixed model ([page 16](../beyond/16-mixed-models.qmd)) handles that.
```

with

```markdown
A mixed model ([page 16](../beyond/16-mixed-models.qmd#random-intercept)) handles that.
```

In `survival/13-kaplan-meier.qmd`, replace

```markdown
[page 15](../beyond/15-post-hoc.qmd) covers comparing pairs of groups.
```

with

```markdown
[page 15](../beyond/15-post-hoc.qmd#after-log-rank) covers comparing pairs of groups.
```

- [ ] **Step 4: Render the seven pages and run the tests**

Run:

```bash
for page in catalog/07-two-paired-groups catalog/08-three-plus-unmatched catalog/09-three-plus-matched catalog/11-predict-from-one catalog/12-predict-from-several foundations/03-distributions survival/13-kaplan-meier; do
  quarto render $page.qmd
done
uv run pytest tests/site -q
lychee --offline --include-fragments --no-progress _site
git status --short _freeze
```

Expected:
- `307 passed`
- lychee `0 Errors`: every new anchor exists, including page 16's link to page 17's `#icc`
- `git status` lists the seven pages' `execute-results/html.json` files and nothing else. The diffs change the links, page 8's sentence, the freeze hashes and pages 11–12's statsmodels "Time:" stamps.

- [ ] **Step 5: Commit**

```bash
git add catalog/07-two-paired-groups.qmd catalog/08-three-plus-unmatched.qmd catalog/09-three-plus-matched.qmd catalog/11-predict-from-one.qmd catalog/12-predict-from-several.qmd foundations/03-distributions.qmd survival/13-kaplan-meier.qmd \
        _freeze/foundations _freeze/catalog _freeze/survival tests/site/test_catalog.py tests/site/test_beyond.py
git commit -m "Links into pages 15-17 land on the section they promise; page 8 no longer gates post-hoc tests on the overall test

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Record the Phase 5 conventions and run everything

**Files:**
- Modify: `CLAUDE.md`, `tests/python/test_repo_docs.py`

- [ ] **Step 1: Write the failing test**

In `tests/python/test_repo_docs.py`, replace

```python
                 "Regression CIs", "CumIncidenceRight"]:
```

with

```python
                 "Regression CIs", "CumIncidenceRight", "Mixed models", "Multiple comparisons"]:
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `test_claude_md_states_the_golden_rules` FAILS on `Mixed models`.

- [ ] **Step 2: Update CLAUDE.md**

After golden rule 17,

```markdown
17. **Survival tools.** lifelines stops iterating slightly early, so every Cox fit passes `fit_options={"precision": 1e-9}` or tighter (stratified and start-stop fits need `1e-12`) and the 🔀 box says so. For cumulative incidence, use statsmodels' `CumIncidenceRight()`, not lifelines' `AalenJohansenFitter`, which moves tied times by a random amount. Gray's test and Fine-Gray regression exist only in R (tidycmprsk); the page says so.
```

add rules 18 and 19:

```markdown
18. **Mixed models.** Pages fit `lmer()` (from lmerTest) and statsmodels' `mixedlm(...).fit(reml=True)`, both by REML. The estimates agree to about 1e-6, but the standard errors differ in the fourth significant figure: lme4 holds the variance components at their estimates, statsmodels uses the whole likelihood's Hessian. So hidden checks on standard errors, estimated marginal means and Wald statistics use `tol = 1e-3` with a comment. `emmeans()` passes `lmer.df = "satterthwaite"`; Python computes marginal means from the fixed effects with z intervals, and the 🔀 box says so.
19. **Multiple comparisons.** Pairwise follow-ups adjust with Holm unless the method adjusts itself (Tukey, Games-Howell); unadjusted pairwise p-values appear only to show what adjusting does. A significant overall test isn't required first (page 15, `#overall-test-first`), and planned comparisons are named in the Methods.
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
- Python: `81 passed`
- `quarto render` re-executes nothing
- site: `307 passed`
- lychee: `0 Errors`
- `git status` shows only `CLAUDE.md` and `tests/python/test_repo_docs.py`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md tests/python/test_repo_docs.py
git commit -m "CLAUDE.md: record Phase 5 conventions (mixed-model checks, multiple comparisons)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
