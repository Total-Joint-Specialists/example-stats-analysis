test_that("the survey export has a metadata row and reshapes exactly to its answer key", {
  path <- data_path("messy_survey_export.csv")
  lines <- readLines(path, n = 2)
  expect_match(lines[2], "^Response ID,Study ID,Instrument,")
  wide <- readr::read_csv(path, skip = 2, col_names = strsplit(lines[1], ",")[[1]],
                          col_types = readr::cols(.default = "c"))
  expect_equal(nrow(wide), 150)
  long <- wide |>
    tidyr::pivot_longer(-c(ResponseId, case_id, instrument),
                        names_to = c("inst", "item", "visit"),
                        names_pattern = "(KOOS|HOOS)_Q(\\d)_(.*)",
                        values_to = "response") |>
    dplyr::filter(substr(instrument, 1, 4) == inst) |>
    dplyr::mutate(item = as.integer(item), response = as.integer(response),
                  visit_order = match(visit, c("preop", "6wk", "3mo", "1yr"))) |>
    dplyr::arrange(case_id, visit_order, item) |>
    dplyr::select(case_id, instrument, visit, item, response)
  expected <- read_tidy("answer-keys/survey_items_long.csv")
  expect_equal(as.data.frame(long), as.data.frame(expected), ignore_attr = TRUE)
})
