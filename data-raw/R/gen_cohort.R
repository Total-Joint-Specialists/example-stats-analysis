# Synthetic cohort: one row per primary THA/TKA.
#
# Columns whose names start with "." are latent helpers that other generators
# use (for example .recovery drives PROM gains). write_tidy() drops them.

clamp <- function(x, lo, hi) pmin(pmax(x, lo), hi)

# Draw a time from a piecewise-constant hazard: `rate_early` until `cut`
# years, then `rate_late`. Inverse-CDF method on a unit exponential.
rpiecewise <- function(rate_early, rate_late, cut) {
  e <- stats::rexp(length(rate_early))
  ifelse(e < rate_early * cut,
         e / rate_early,
         cut + (e - rate_early * cut) / rate_late)
}

# Draw a time from a Gompertz hazard h(t) = a * exp(b * t).
rgompertz_time <- function(a, b) {
  e <- stats::rexp(length(a))
  log1p(e * b / a) / b
}

make_cohort <- function(seed = 20261007, hr_c = 2.5, base_rate = 0.015,
                        early_mult = 10, early_cut = 0.5) {
  set.seed(seed)
  n_pat     <- 520
  n_bilat   <- 85
  admin_end <- as.Date("2025-12-31")

  patients <- tibble::tibble(
    patient_id   = sprintf("P%04d", seq_len(n_pat)),
    sex          = sample(c("Female", "Male"), n_pat, TRUE, prob = c(0.58, 0.42)),
    procedure    = sample(c("TKA", "THA"), n_pat, TRUE, prob = c(0.55, 0.45)),
    site         = sample(c("Site A", "Site B"), n_pat, TRUE),
    smoker       = sample(c("never", "former", "current"), n_pat, TRUE,
                          prob = c(0.55, 0.35, 0.10)),
    age1         = round(clamp(stats::rnorm(n_pat, 66, 9), 40, 85)),
    bmi_base     = stats::rnorm(n_pat, 29.6, 5.5),
    date1        = as.Date("2015-01-01") +
                   sample(0:(365 * 9), n_pat, replace = TRUE),
    gap_days     = sample(90:540, n_pat, replace = TRUE),
    wants_second = seq_len(n_pat) %in% sample(n_pat, n_bilat),
    rec_pat      = stats::rnorm(n_pat)
  )
  patients$bmi_base <- clamp(patients$bmi_base + 1.6 * (patients$procedure == "TKA"),
                             18, 55)
  patients$diabetes <- stats::rbinom(n_pat, 1, stats::plogis(
    -2.2 + 0.08 * (patients$bmi_base - 30) + 0.02 * (patients$age1 - 66)))
  patients$hypertension <- stats::rbinom(n_pat, 1, stats::plogis(
    0.1 + 0.05 * (patients$age1 - 66) + 0.06 * (patients$bmi_base - 30)))
  patients$sleep_apnea <- stats::rbinom(n_pat, 1, stats::plogis(
    -2.0 + 0.12 * (patients$bmi_base - 30) + 0.5 * (patients$sex == "Male")))

  # Patient-level follow-up end: death (Gompertz in age), loss to follow-up
  # (3%/yr), or administrative end of data.
  t_death <- rgompertz_time(0.008 * exp(0.1 * (patients$age1 - 66)), 0.1)
  t_ltfu  <- stats::rexp(n_pat, 0.03)
  patients$death_date <- patients$date1 + round(t_death * 365.25)
  patients$ltfu_date  <- patients$date1 + round(t_ltfu * 365.25)
  patients$end_date   <- pmin(patients$death_date, patients$ltfu_date, admin_end)
  patients$died       <- patients$death_date <= pmin(patients$ltfu_date, admin_end)

  first <- patients |>
    dplyr::mutate(case_no = 1L, surgery_date = date1,
                  side = sample(c("L", "R"), n_pat, TRUE))
  second <- patients |>
    dplyr::mutate(surgery_date = date1 + gap_days) |>
    dplyr::filter(wants_second,
                  surgery_date < end_date,
                  surgery_date <= as.Date("2024-12-31")) |>
    dplyr::mutate(case_no = 2L)
  second$side <- ifelse(first$side[match(second$patient_id, first$patient_id)] == "L",
                        "R", "L")

  cases <- dplyr::bind_rows(first, second) |>
    dplyr::arrange(surgery_date, patient_id) |>
    dplyr::mutate(case_id = sprintf("C%04d", dplyr::row_number()))
  n <- nrow(cases)

  cases$age <- cases$age1 + floor(as.numeric(cases$surgery_date - cases$date1) / 365.25)
  cases$bmi <- round(clamp(cases$bmi_base + ifelse(cases$case_no == 2,
                                                   stats::rnorm(n, 0, 0.8), 0),
                           18, 55), 1)

  asa_latent <- 0.04 * (cases$age - 66) + 0.08 * (cases$bmi - 30) +
    0.6 * cases$diabetes + 0.3 * cases$hypertension + stats::rnorm(n)
  cases$asa <- as.integer(cut(asa_latent,
                              stats::quantile(asa_latent, c(0, 0.06, 0.56, 0.97, 1)),
                              include.lowest = TRUE))
  cases$cci <- stats::rpois(n, exp(-0.5 + 0.04 * (cases$age - 66) +
                                   0.5 * cases$diabetes + 0.25 * (cases$asa - 2)))

  cases$surgeon    <- sample(c("S1", "S2", "S3"), n, TRUE, prob = c(0.40, 0.35, 0.25))
  cases$anesthesia <- sample(c("spinal", "general"), n, TRUE, prob = c(0.75, 0.25))
  cases$approach   <- ifelse(cases$procedure == "THA",
                             sample(c("anterior", "posterior"), n, TRUE,
                                    prob = c(0.55, 0.45)),
                             NA_character_)
  cases$implant    <- sample(c("A", "B", "C"), n, TRUE, prob = c(0.40, 0.35, 0.25))

  cases$op_time_min <- as.integer(pmax(45, round(
    80 + 1.3 * (cases$bmi - 30) + 0.2 * (cases$age - 66) +
      6 * (cases$procedure == "TKA") + stats::rnorm(n, 0, 14))))
  cases$los_days <- stats::rnbinom(n, size = 1.2, mu = exp(
    -0.25 + 0.25 * (cases$asa - 2) + 0.02 * (cases$age - 66)))
  cases$discharge <- ifelse(stats::rbinom(n, 1, stats::plogis(
    -3.4 + 0.08 * (cases$age - 66) + 0.4 * (cases$asa - 2))) == 1,
    "facility", "home")
  # Readmission deliberately does not depend on sex (a true null result).
  cases$readmit_90d <- stats::rbinom(n, 1, stats::plogis(
    -3.2 + 0.03 * (cases$age - 66) + 0.3 * (cases$asa - 2)))
  cases$complication_90d <- stats::rbinom(n, 1, stats::plogis(
    -2.6 + 0.04 * (cases$age - 66) + 0.35 * (cases$asa - 2) + 0.05 * (cases$bmi - 30)))

  cases$.recovery <- 0.7 * cases$rec_pat + 0.7 * stats::rnorm(n)
  sat_latent <- cases$.recovery + stats::rnorm(n, 0, 0.6)
  cases$satisfaction_1yr <- as.integer(cut(
    sat_latent, stats::quantile(sat_latent, c(0, 0.03, 0.08, 0.18, 0.50, 1)),
    include.lowest = TRUE))
  cases$satisfaction_1yr[stats::runif(n) < 0.08] <- NA_integer_

  # Revision: implant C multiplies the hazard by `hr_c`. Posterior THA
  # multiplies it by `early_mult` for the first `early_cut` years only (early
  # instability), which violates proportional hazards on purpose. Rates are
  # inflated for teaching so the survival pages have enough events.
  hr_implant <- c(A = 1, B = 1, C = hr_c)[cases$implant]
  rate_late  <- base_rate * hr_implant * exp(0.02 * (cases$bmi - 30))
  mult       <- ifelse(!is.na(cases$approach) & cases$approach == "posterior", early_mult, 1)
  t_rev      <- rpiecewise(rate_late * mult, rate_late, cut = early_cut)
  rev_date   <- cases$surgery_date + round(t_rev * 365.25)

  revised_first <- rev_date < cases$end_date
  stop_date     <- dplyr::if_else(revised_first, rev_date, cases$end_date)
  cases$event_status <- dplyr::case_when(
    revised_first ~ 1L,
    cases$died & cases$end_date == cases$death_date ~ 2L,
    TRUE ~ 0L)
  cases$revised <- as.integer(cases$event_status == 1L)
  cases$followup_years <- round(pmax(as.numeric(stop_date - cases$surgery_date) / 365.25,
                                     0.01), 2)

  # A 1-year satisfaction score needs a joint that was still followed at 1 year.
  cases$satisfaction_1yr[cases$followup_years < 1] <- NA_integer_

  cases |>
    dplyr::select(case_id, patient_id, site, surgeon, procedure, side, surgery_date,
                  age, sex, bmi, asa, diabetes, hypertension, sleep_apnea, smoker, cci,
                  anesthesia, approach, implant, op_time_min, los_days, discharge,
                  readmit_90d, complication_90d, satisfaction_1yr,
                  followup_years, event_status, revised, .recovery)
}
