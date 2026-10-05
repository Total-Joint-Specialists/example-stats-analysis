# Check that the synthetic data still teach what they are meant to.
# Run from the repo root:  Rscript data-raw/validate.R
testthat::test_dir("tests/testthat", filter = "data", stop_on_failure = TRUE)
