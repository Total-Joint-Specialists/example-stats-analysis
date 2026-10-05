# PROMs in long format: one row per case x visit (preop, 6wk, 3mo, 1yr).
# A missed visit keeps its row with every measure NA, so "expected but not
# completed" stays visible. No visit is recorded after follow-up ended.

make_proms_long <- function(cohort, seed = 20261008) {
  set.seed(seed)
  visits <- tibble::tibble(
    visit     = c("preop", "6wk", "3mo", "1yr"),
    nominal   = c(-14L, 42L, 90L, 365L),
    jitter    = c(13L, 7L, 14L, 30L),
    p_missing = c(0.03, 0.10, 0.15, 0.16),
    gain_tha  = c(0, 22, 34, 44),
    gain_tka  = c(0, 12, 24, 34),
    rec_frac  = c(0, 0.5, 0.8, 1),
    pcs_gain  = c(0, 4, 10, 14),
    aid_prob  = c(0.35, 0.60, 0.25, 0.10)
  )
  n <- nrow(cohort)
  case_base <- tibble::tibble(
    case_id    = cohort$case_id,
    patient_id = cohort$patient_id,
    procedure  = cohort$procedure,
    age        = cohort$age,
    recovery   = cohort$.recovery,
    fu_days    = cohort$followup_years * 365.25,
    pre_mean   = ifelse(cohort$procedure == "THA", 46, 50) - 0.15 * (cohort$bmi - 30),
    pre_dev    = stats::rnorm(n, 0, 12)
  )

  grid <- tidyr::expand_grid(case_base, visits)
  m <- nrow(grid)
  is_pre <- grid$visit == "preop"
  gain <- ifelse(grid$procedure == "THA", grid$gain_tha, grid$gain_tka)

  score <- ifelse(
    is_pre,
    grid$pre_mean + grid$pre_dev,
    grid$pre_mean + gain + 0.5 * grid$pre_dev +
      10 * grid$recovery * grid$rec_frac + stats::rnorm(m, 0, 8))
  pcs <- 31 + grid$pcs_gain + 0.15 * (score - grid$pre_mean - gain) + stats::rnorm(m, 0, 6)
  mcs <- 50 + c(preop = 0, `6wk` = 1, `3mo` = 2, `1yr` = 3)[grid$visit] +
    stats::rnorm(m, 0, 9)
  aid <- stats::rbinom(m, 1, stats::plogis(
    stats::qlogis(grid$aid_prob) + 0.05 * (grid$age - 66) -
      0.3 * grid$recovery * (!is_pre)))
  visit_days <- grid$nominal + sample(-1:1, m, TRUE) *
    as.integer(round(stats::runif(m, 0, grid$jitter)))

  missed <- stats::runif(m) < grid$p_missing | visit_days > grid$fu_days

  out <- tibble::tibble(
    case_id     = grid$case_id,
    patient_id  = grid$patient_id,
    visit       = grid$visit,
    visit_days  = as.integer(visit_days),
    instrument  = ifelse(grid$procedure == "THA", "HOOS JR", "KOOS JR"),
    prom_score  = round(clamp(score, 0, 100), 1),
    vr12_pcs    = round(clamp(pcs, 0, 100), 1),
    vr12_mcs    = round(clamp(mcs, 0, 100), 1),
    walking_aid = as.integer(aid)
  )
  measures <- c("visit_days", "prom_score", "vr12_pcs", "vr12_mcs", "walking_aid")
  out[missed, measures] <- NA
  out
}
