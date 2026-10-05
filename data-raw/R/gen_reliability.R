# Radiographic reliability: one row per knee x rater x session.
# Each knee has true MPTA/LDFA/HKA; every reading adds measurement error, and
# rater R2 reads HKA about 0.5 degrees high (a systematic bias for
# Bland-Altman to find). CPAK class is computed from each reading's own MPTA
# and LDFA, so class disagreements come from real measurement error.

cpak_class <- function(mpta, ldfa) {
  ahka <- mpta - ldfa
  jlo  <- mpta + ldfa
  col <- ifelse(ahka < -2, 1L, ifelse(ahka > 2, 3L, 2L))   # varus, neutral, valgus
  row <- ifelse(jlo < 177, 0L, ifelse(jlo > 183, 2L, 1L))  # apex distal, neutral, proximal
  as.character(utils::as.roman(row * 3L + col))
}

make_reliability <- function(seed = 20261018, n_knees = 60) {
  set.seed(seed)
  knees <- tibble::tibble(
    knee_id = sprintf("K%03d", seq_len(n_knees)),
    mpta    = stats::rnorm(n_knees, 87, 2.5),
    ldfa    = stats::rnorm(n_knees, 88, 2.2)
  )
  knees$hka <- 180 + (knees$mpta - knees$ldfa) + stats::rnorm(n_knees, 0, 1.5)

  reads <- tidyr::expand_grid(knees, rater = c("R1", "R2"), session = 1:2)
  m <- nrow(reads)
  mpta_deg <- round(reads$mpta + stats::rnorm(m, 0, 0.7), 1)
  ldfa_deg <- round(reads$ldfa + stats::rnorm(m, 0, 0.7), 1)
  tibble::tibble(
    knee_id    = reads$knee_id,
    rater      = reads$rater,
    session    = as.integer(reads$session),
    hka_deg    = round(reads$hka + 0.5 * (reads$rater == "R2") + stats::rnorm(m, 0, 1.2), 1),
    mpta_deg   = mpta_deg,
    ldfa_deg   = ldfa_deg,
    cpak_class = cpak_class(mpta_deg, ldfa_deg)
  )
}
