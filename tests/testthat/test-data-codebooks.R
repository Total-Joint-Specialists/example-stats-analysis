# Every tidy dataset and answer key has a codebook whose variables match the
# file's columns (same order) and whose allowed_values hold for every value.

dataset_path <- function(book) {
  if (file.exists(data_path(book))) data_path(book) else data_path("answer-keys", book)
}

values_allowed <- function(x, rule) {
  x <- x[!is.na(x)]
  if (is.na(rule) || rule == "") return(TRUE)
  if (grepl("..", rule, fixed = TRUE)) {
    lim <- as.numeric(strsplit(rule, "..", fixed = TRUE)[[1]])
    return(all(x >= lim[1] & x <= lim[2]))
  }
  all(as.character(x) %in% strsplit(rule, "|", fixed = TRUE)[[1]])
}

books <- list.files(data_path("codebooks"), pattern = "[.]csv$")

for (book in books) {
  test_that(paste("codebook agrees with", book), {
    cb <- readr::read_csv(data_path("codebooks", book), show_col_types = FALSE,
                          col_types = readr::cols(.default = "c"))
    df <- readr::read_csv(dataset_path(book), show_col_types = FALSE, guess_max = 10000)
    expect_equal(names(df), cb$variable)
    for (i in seq_len(nrow(cb))) {
      expect_true(values_allowed(df[[cb$variable[i]]], cb$allowed_values[i]),
                  label = paste(book, cb$variable[i], "within", cb$allowed_values[i]))
    }
  })
}

test_that("each tidy dataset and answer key has a codebook", {
  expect_setequal(books, c("cohort.csv", "proms_long.csv", "matched_sets.csv",
                           "radiographic_reliability.csv",
                           "abstraction_workbook_tidy.csv", "survey_items_long.csv"))
})

test_that("every codebook says the data are synthetic", {
  for (book in books) {
    cb <- readr::read_csv(data_path("codebooks", book), show_col_types = FALSE,
                          col_types = readr::cols(.default = "c"))
    expect_match(cb$notes[1], "^SYNTHETIC DATA - not real patients", label = book)
  }
})
