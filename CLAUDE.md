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
9. **Never hand-edit `data/` or `templates/`.** Change `data-raw/` and run `just data`. Seeds and effect sizes are the default arguments of each `make_*()` function in `data-raw/R/`. Never loosen a test or change a seed or parameter just to make a test pass; if an effect weakens, strengthen it deliberately and record why.

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
