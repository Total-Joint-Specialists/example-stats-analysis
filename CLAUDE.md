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
8. **Reporting conventions** (spec section 4, page 0.2): mean (SD) or median (IQR); n (%); p to 3 decimals with a floor of "p < 0.001" and a ceiling of "p > 0.999"; a 95% CI with every estimate.
9. **Never hand-edit `data/` or `templates/`.** Change `data-raw/` and run `just data`. Seeds and effect sizes are the default arguments of each `make_*()` function in `data-raw/R/`. Never loosen a test or change a seed or parameter just to make a test pass; if an effect weakens, strengthen it deliberately and record why.
10. **Quiet pages.** `_quarto.yml` hides messages on every page through knitr's own default (`knitr: opts_chunk: message: false`). Quarto silently ignores `message` under a page's `execute:` key, so don't put it there. Chunks that call `library()` add `#| warning: false`. A site test fails on any stderr output. Don't attach packages that mask base functions (janitor masks `chisq.test()`/`fisher.test()`); call them as `pkg::fun()`. In Python chunks, never assign to `_` (as in `_ = ax.hist(...)`): reticulate reads `_` to decide what to print, and once `_` holds a plot object every later Python output on the page silently disappears. Bare matplotlib calls print nothing; give any other result you want to hide a name (`qq = stats.probplot(...)`). `tests/site/test_sources.py` enforces this.
11. **Prose guards.** Each page ends, just before Exercises, with a hidden R chunk headed `# Prose guard` that `stopifnot()`s every number quoted in the text, reading displayed values from the library objects where it can. Freeze only notices `.qmd` changes, not data changes, so: `just data` re-renders every folder whose pages read `data/`, and each such page stamps `<!-- data-checksum: … -->` (a visible-to-nobody chunk) that `tests/site/test_freshness.py` compares with `data/CHECKSUMS.md5`. Stale pages fail the site tests, locally and in CI.
12. **Exercise solutions are executed chunks** (`{r}` / `{python}`) inside the collapsed Solution callout, so they can't rot.
13. **Catalog sections follow spec §6.** Each decision-table section opens with a `**The question:**` line, then these `###` steps in order: When to use it, Look at the data first, Run it, Read the output, Effect size and 95% CI (not on page 4, where the estimate is the result), How to report it (a Methods and a Results blockquote). Each section also has a ⚠️ box. A section's first tabset loads its own packages and data, and every name its Python uses is defined within the section, because readers jump straight to it from the decision table and copy only that section. Catalog pages set `toc-depth: 2`. `tests/site/test_catalog.py` and `tests/site/test_sources.py` enforce this.
14. **Python survival uses lifelines on pandas 3.** lifelines declares `pandas<3`, but the pages are written for pandas 3 (page 1's tidying breaks on pandas 2), so `pyproject.toml` sets `override-dependencies = ["pandas>=3.0"]`. Every lifelines number on a page is checked against R's survival package by `check_agree()`. Remove the override once lifelines supports pandas 3.
15. **Bootstrap CIs are seeded.** effectsize computes some CIs by bootstrap (`rank_epsilon_squared()`, `kendalls_w()`), so their printed CI changes on every render. Call `set.seed(2026)` just before them in the same chunk, or pass `ci = NULL` where only the estimate is needed (prose guards). `tests/site/test_sources.py` enforces this.
16. **Regression CIs.** R's `confint()` profiles the likelihood of `glm()` and `nls()` fits; statsmodels and scipy give Wald CIs (estimate ± z or t × standard error). Pages quote R's profile CI and give Python's in the 🔀 box. The hidden check compares estimates and standard errors (and, for `glm()`, the Wald CI from `confint.default()`) with `tol = 1e-4` and a comment, because the two sides stop iterating, or approximate derivatives, slightly differently.
17. **Survival tools.** lifelines stops iterating slightly early, so every Cox fit passes `fit_options={"precision": 1e-9}` or tighter (stratified and start-stop fits need `1e-12`) and the 🔀 box says so. For cumulative incidence, use statsmodels' `CumIncidenceRight()`, not lifelines' `AalenJohansenFitter`, which moves tied times by a random amount. Gray's test and Fine-Gray regression exist only in R (tidycmprsk); the page says so.
18. **Mixed models.** Pages fit `lmer()` (from lmerTest) and statsmodels' `mixedlm(...).fit(reml=True)`, both by REML. The estimates agree to about 1e-6, but the standard errors differ in the fourth significant figure: lme4 holds the variance components at their estimates, statsmodels uses the whole likelihood's Hessian. So hidden checks on standard errors, estimated marginal means and Wald statistics use `tol = 1e-3` with a comment. `emmeans()` passes `lmer.df = "satterthwaite"`; Python computes marginal means from the fixed effects with z intervals, and the 🔀 box says so.
19. **Multiple comparisons.** Pairwise follow-ups adjust with Holm unless the method adjusts itself (Tukey, Games-Howell); unadjusted pairwise p-values appear only to show what adjusting does. A significant overall test isn't required first (page 15, `#overall-test-first`), and planned comparisons are named in the Methods.

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
