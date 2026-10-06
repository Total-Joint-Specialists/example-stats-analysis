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
  for (m in c("pandas", "numpy", "matplotlib", "scipy", "openpyxl", "tableone", "docx",
             "statsmodels", "pingouin", "lifelines")) {
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
