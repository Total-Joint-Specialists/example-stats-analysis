# The committed CSVs must be exactly what the generator produces: no hand
# edits, and the seeds really do fix the output. (The .xlsx files embed
# timestamps, so they are checked by content tests instead.)

test_that("regenerating reproduces every committed CSV byte for byte", {
  gen_dir <- testthat::test_path("..", "..", "data-raw", "R")
  env <- new.env()
  for (f in list.files(gen_dir, pattern = "[.]R$", full.names = TRUE)) sys.source(f, envir = env)

  cohort <- env$make_cohort()
  proms  <- env$make_proms_long(cohort)
  items  <- env$make_survey_items(cohort, proms)
  fresh <- list(
    "cohort.csv"                                = cohort,
    "proms_long.csv"                            = proms,
    "matched_sets.csv"                          = env$make_matched_sets(cohort),
    "radiographic_reliability.csv"              = env$make_reliability(),
    "answer-keys/abstraction_workbook_tidy.csv" = env$make_abstraction_truth(cohort, proms),
    "answer-keys/survey_items_long.csv"         = items
  )
  out <- withr::local_tempdir()
  for (name in names(fresh)) {
    path <- file.path(out, basename(name))
    env$write_tidy(fresh[[name]], path)
    expect_identical(readLines(path), readLines(data_path(name)), label = name)
  }
  survey <- file.path(out, "messy_survey_export.csv")
  env$write_messy_survey(items, survey)
  expect_identical(readLines(survey), readLines(data_path("messy_survey_export.csv")),
                   label = "messy_survey_export.csv")

  books <- file.path(out, "codebooks")
  dir.create(books)
  env$write_codebooks(env$codebooks(), books)
  for (f in list.files(books)) {
    expect_identical(readLines(file.path(books, f)), readLines(data_path("codebooks", f)),
                     label = paste("codebook", f))
  }
})
