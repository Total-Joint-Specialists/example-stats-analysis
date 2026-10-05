cohort <- read_tidy("cohort.csv")
proms  <- read_tidy("proms_long.csv")

wide <- function(col) {
  tidyr::pivot_wider(proms[, c("case_id", "visit", col)],
                     names_from = visit, values_from = dplyr::all_of(col))
}

test_that("one row per case x visit, for every cohort case", {
  expect_equal(nrow(dplyr::distinct(proms, case_id, visit)), nrow(proms))
  expect_equal(nrow(proms), 4 * nrow(cohort))
  expect_setequal(unique(proms$case_id), cohort$case_id)
  joined <- dplyr::left_join(proms, cohort[, c("case_id", "patient_id")],
                             by = "case_id", suffix = c("", "_cohort"))
  expect_equal(joined$patient_id, joined$patient_id_cohort)
})

test_that("no PROM visit is recorded after follow-up ended", {
  j <- dplyr::left_join(proms, cohort[, c("case_id", "followup_years")], by = "case_id")
  seen <- !is.na(j$visit_days)
  expect_true(all(j$visit_days[seen] <= j$followup_years[seen] * 365.25 + 4))
})

test_that("a missed visit has every measure missing", {
  missed <- is.na(proms$prom_score)
  expect_true(all(is.na(proms$visit_days[missed])))
  expect_true(all(is.na(proms$vr12_pcs[missed])))
  expect_true(all(is.na(proms$walking_aid[missed])))
})

test_that("visit missingness rises from about 10% to about 25%", {
  miss <- tapply(is.na(proms$prom_score), proms$visit, mean)
  expect_lt(miss[["preop"]], 0.06)
  expect_gt(miss[["6wk"]], 0.05)
  expect_lt(miss[["6wk"]], 0.15)
  expect_gt(miss[["1yr"]], 0.18)
  expect_lt(miss[["1yr"]], 0.32)
})

test_that("1-year PROMs show a ceiling effect", {
  yr1 <- proms$prom_score[proms$visit == "1yr"]
  expect_gte(mean(yr1 == 100, na.rm = TRUE), 0.15)
})

test_that("PROMs improve from pre-op to 1 year", {
  w <- wide("prom_score")
  expect_lt(stats::t.test(w$`1yr`, w$preop, paired = TRUE)$p.value, 0.001)
})

test_that("walking-aid use changes from pre-op to 6 weeks (McNemar)", {
  w <- wide("walking_aid")
  w <- w[!is.na(w$preop) & !is.na(w$`6wk`), ]
  expect_lt(stats::mcnemar.test(table(w$preop, w$`6wk`))$p.value, 0.05)
})

test_that("satisfaction tracks PROM improvement", {
  w <- wide("prom_score")
  at <- match(cohort$case_id, w$case_id)
  gain <- w$`1yr`[at] - w$preop[at]
  rho <- stats::cor(cohort$satisfaction_1yr, gain, method = "spearman",
                    use = "complete.obs")
  expect_gt(rho, 0.3)
})
