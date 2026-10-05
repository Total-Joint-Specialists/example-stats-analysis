test_that("no real-looking identifiers in any CSV", {
  files <- list.files(data_path(), pattern = "[.]csv$", recursive = TRUE, full.names = TRUE)
  expect_gt(length(files), 0)
  txt <- unlist(lapply(files, readLines))
  expect_false(any(grepl("\\b\\d{3}-\\d{2}-\\d{4}\\b", txt)))  # SSN-shaped
  expect_false(any(grepl("@", txt, fixed = TRUE)))             # e-mail addresses
  expect_false(any(grepl("\\b\\d{7,}\\b", txt)))               # MRN-shaped digit runs
})
