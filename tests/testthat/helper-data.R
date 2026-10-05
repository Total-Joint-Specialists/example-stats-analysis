# Shared helpers for the data tests. testthat runs with tests/testthat as the
# working directory, so paths go through test_path().
data_path <- function(...) testthat::test_path("..", "..", "data", ...)

read_tidy <- function(name) {
  readr::read_csv(data_path(name), show_col_types = FALSE, guess_max = 10000)
}
