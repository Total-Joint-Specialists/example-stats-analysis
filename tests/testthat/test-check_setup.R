root <- normalizePath(testthat::test_path("..", ".."))

test_that("check_setup.R passes in a working project", {
  out <- withr::with_dir(root, system2(file.path(R.home("bin"), "Rscript"),
                                      "getting-started/check_setup.R",
                                      stdout = TRUE, stderr = TRUE))
  expect_null(attr(out, "status"))
  expect_true(any(grepl("All good - you are ready.", out, fixed = TRUE)))
})
