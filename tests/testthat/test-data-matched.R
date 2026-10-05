cohort  <- read_tidy("cohort.csv")
matched <- read_tidy("matched_sets.csv")

test_that("matched sets are true triplets of distinct patients", {
  expect_equal(anyDuplicated(matched$case_id), 0)
  expect_true(all(matched$case_id %in% cohort$case_id))
  s <- matched |>
    dplyr::mutate(patient_id = cohort$patient_id[match(case_id, cohort$case_id)]) |>
    dplyr::group_by(set_id) |>
    dplyr::summarise(n = dplyr::n(), imps = paste(sort(implant), collapse = ""),
                     procs = dplyr::n_distinct(procedure), sexes = dplyr::n_distinct(sex),
                     asas = dplyr::n_distinct(asa), age_rng = diff(range(age)),
                     bmi_rng = diff(range(bmi)), pats = dplyr::n_distinct(patient_id))
  expect_gte(nrow(s), 40)
  expect_true(all(s$n == 3 & s$imps == "ABC" & s$procs == 1 & s$sexes == 1 & s$asas == 1))
  expect_true(all(s$age_rng <= 6 & s$bmi_rng <= 6 & s$pats == 3))
})

test_that("matched rows copy their values from the cohort", {
  j <- dplyr::left_join(matched, cohort, by = "case_id", suffix = c("", "_cohort"))
  for (col in c("procedure", "implant", "age", "sex", "bmi", "asa",
                "followup_years", "event_status")) {
    expect_equal(j[[col]], j[[paste0(col, "_cohort")]], label = col)
  }
})
