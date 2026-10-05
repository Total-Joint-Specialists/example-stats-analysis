source(testthat::test_path("..", "..", "R", "check_agree.R"))

test_that("matching results pass silently", {
  expect_invisible(check_agree(list(t = 2.41, p = 0.017), list(p = 0.017, t = 2.41)))
})

test_that("tiny numerical noise is tolerated, relative to magnitude", {
  expect_true(check_agree(list(p = 0.0170000001), list(p = 0.017)))
  expect_true(check_agree(list(stat = 12345.6), list(stat = 12345.6 * (1 + 1e-8))))
})

test_that("integers from Python count as numbers", {
  expect_true(check_agree(list(df = 598), list(df = 598L)))
})

test_that("a real disagreement stops with both values in the message", {
  expect_error(check_agree(list(p = 0.017), list(p = 0.021)),
               "disagree on 'p': R = 0.017, Python = 0.021")
})

test_that("different result names stop", {
  expect_error(check_agree(list(t = 1, p = 0.5), list(t = 1)),
               "R has \\[p, t\\] but Python has \\[t\\]")
})

test_that("missing or infinite values never pass", {
  expect_error(check_agree(list(p = NA_real_), list(p = NA_real_)), "not a finite number")
  expect_error(check_agree(list(p = NaN), list(p = 0.5)), "not a finite number")
  expect_error(check_agree(list(z = Inf), list(z = Inf)), "not a finite number")
})

test_that("non-numbers and vectors stop", {
  expect_error(check_agree(list(p = "0.017"), list(p = 0.017)), "single number")
  expect_error(check_agree(list(p = c(0.1, 0.2)), list(p = 0.1)), "single number")
  expect_error(check_agree(list(sig = TRUE), list(sig = TRUE)), "single number")
})

test_that("unnamed input stops", {
  expect_error(check_agree(list(0.017), list(0.017)), "named lists")
})
