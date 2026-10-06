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
| `index.qmd` (welcome), `choose-a-test.qmd` (the decision table), `tests-a-z.qmd`, `getting-started/`, `foundations/`, `catalog/`, `survival/`, `beyond/`, `report/` | The site's pages |
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
