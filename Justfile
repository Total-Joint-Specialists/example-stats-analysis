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

# Regenerate the synthetic data and template, then check them in both languages
data:
    Rscript data-raw/generate.R
    Rscript data-raw/make_template.R
    Rscript data-raw/validate.R
    uv run pytest tests/python -q
    # Freeze only notices .qmd changes, so re-render every folder whose pages read data/.
    # (Rendering a folder always re-runs its code.) Add beyond, report, ... as they gain code.
    quarto render foundations
    quarto render catalog
    quarto render survival
