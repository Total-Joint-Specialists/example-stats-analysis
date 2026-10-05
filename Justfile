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
