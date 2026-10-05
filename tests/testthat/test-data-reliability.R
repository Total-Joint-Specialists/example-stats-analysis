rel <- read_tidy("radiographic_reliability.csv")
session1 <- rel[rel$session == 1, ]

test_that("one row per knee x rater x session, 60 knees", {
  expect_equal(nrow(dplyr::distinct(rel, knee_id, rater, session)), nrow(rel))
  expect_equal(dplyr::n_distinct(rel$knee_id), 60)
  expect_equal(nrow(rel), 60 * 2 * 2)
})

test_that("CPAK class follows from each reading's own MPTA and LDFA", {
  ahka <- rel$mpta_deg - rel$ldfa_deg
  jlo  <- rel$mpta_deg + rel$ldfa_deg
  col <- ifelse(ahka < -2, 1L, ifelse(ahka > 2, 3L, 2L))
  row <- ifelse(jlo < 177, 0L, ifelse(jlo > 183, 2L, 1L))
  expect_equal(rel$cpak_class, as.character(utils::as.roman(row * 3L + col)))
})

test_that("raters agree well on HKA, with a small systematic bias", {
  hka <- tidyr::pivot_wider(session1[, c("knee_id", "rater", "hka_deg")],
                            names_from = rater, values_from = hka_deg)
  icc <- irr::icc(hka[, c("R1", "R2")], model = "twoway", type = "agreement",
                  unit = "single")$value
  expect_gt(icc, 0.80)
  expect_lt(icc, 0.95)
  bias <- mean(hka$R2 - hka$R1)
  expect_gt(bias, 0.3)
  expect_lt(bias, 0.7)
})

test_that("CPAK classification agreement is moderate to substantial", {
  cpak <- tidyr::pivot_wider(session1[, c("knee_id", "rater", "cpak_class")],
                             names_from = rater, values_from = cpak_class)
  k <- irr::kappa2(cpak[, c("R1", "R2")])$value
  expect_gt(k, 0.5)
  expect_lt(k, 0.85)
})
