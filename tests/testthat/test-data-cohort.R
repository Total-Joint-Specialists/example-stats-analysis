cohort <- read_tidy("cohort.csv")

skewness <- function(x) mean((x - mean(x))^3) / stats::sd(x)^3

test_that("one row per case, about 600 cases from about 520 patients", {
  expect_equal(anyDuplicated(cohort$case_id), 0)
  expect_gte(nrow(cohort), 550)
  expect_lte(nrow(cohort), 650)
  per_patient <- table(cohort$patient_id)
  expect_true(all(per_patient <= 2))
  expect_gte(sum(per_patient == 2), 60)
  expect_lte(sum(per_patient == 2), 100)
})

test_that("bilateral patients are internally consistent", {
  bil <- cohort |>
    dplyr::group_by(patient_id) |>
    dplyr::filter(dplyr::n() == 2)
  s <- bil |>
    dplyr::summarise(sides = paste(sort(side), collapse = ""),
                     sexes = dplyr::n_distinct(sex),
                     procs = dplyr::n_distinct(procedure), .groups = "drop")
  expect_true(all(s$sides == "LR"))
  expect_true(all(s$sexes == 1))
  expect_true(all(s$procs == 1))
  # A patient dies once: both cases imply the same death date (followup_years
  # is rounded to 0.01 y, about 4 days).
  deaths <- bil |>
    dplyr::filter(event_status == 2) |>
    dplyr::mutate(death = surgery_date + round(followup_years * 365.25)) |>
    dplyr::summarise(spread = as.numeric(diff(range(death))), .groups = "drop")
  expect_true(all(deaths$spread <= 4))
})

test_that("approach is recorded for THA only and revised matches event_status", {
  expect_true(all(is.na(cohort$approach[cohort$procedure == "TKA"])))
  expect_false(any(is.na(cohort$approach[cohort$procedure == "THA"])))
  expect_equal(cohort$revised, as.numeric(cohort$event_status == 1))
})

test_that("TKA patients have a higher BMI than THA patients", {
  tt <- stats::t.test(bmi ~ procedure, data = cohort)  # Welch
  expect_lt(tt$p.value, 0.01)
  m <- tapply(cohort$bmi, cohort$procedure, mean)
  expect_gt(m[["TKA"]] - m[["THA"]], 0.8)
})

test_that("sex is unrelated to 90-day readmission (a true null)", {
  expect_gt(stats::fisher.test(table(cohort$sex, cohort$readmit_90d))$p.value, 0.2)
})

test_that("length of stay is right-skewed with most stays 0-1 days", {
  expect_gt(skewness(cohort$los_days), 1.5)
  expect_gt(mean(cohort$los_days <= 1), 0.5)
})

test_that("BMI relates moderately to operative time; age only weakly", {
  r_bmi <- stats::cor(cohort$bmi, cohort$op_time_min)
  expect_gt(r_bmi, 0.3)
  expect_lt(r_bmi, 0.5)
  expect_lt(abs(stats::cor(cohort$age, cohort$op_time_min)), 0.2)
})

test_that("implant C has a higher revision hazard", {
  lr <- survival::survdiff(survival::Surv(followup_years, revised) ~ implant, data = cohort)
  expect_lt(1 - stats::pchisq(lr$chisq, df = 2), 0.05)
  fit <- survival::coxph(survival::Surv(followup_years, revised) ~ I(implant == "C"),
                         data = cohort)
  hr <- unname(exp(stats::coef(fit)))
  expect_gt(hr, 1.5)
  expect_lt(hr, 3.5)
})

test_that("deaths compete with revisions", {
  old <- cohort[cohort$age >= 75, ]
  expect_gte(sum(old$event_status == 2), sum(old$event_status == 1))
  km <- survival::survfit(survival::Surv(followup_years, revised) ~ 1, data = cohort)
  aj <- survival::survfit(survival::Surv(followup_years, factor(event_status, 0:2)) ~ 1,
                          data = cohort)
  one_minus_km <- 1 - summary(km, times = 10, extend = TRUE)$surv
  cif <- summary(aj, times = 10, extend = TRUE)$pstate[, 2]
  expect_gt(one_minus_km - cif, 0.005)
})

test_that("posterior THA approach violates proportional hazards", {
  tha <- cohort[cohort$procedure == "THA", ]
  fit <- survival::coxph(survival::Surv(followup_years, revised) ~ approach, data = tha)
  expect_lt(survival::cox.zph(fit)$table["approach", "p"], 0.05)
})

test_that("no 1-year satisfaction for cases whose follow-up ended before 1 year", {
  early <- cohort$followup_years < 1
  expect_gt(sum(early), 0)
  expect_true(all(is.na(cohort$satisfaction_1yr[early])))
})
