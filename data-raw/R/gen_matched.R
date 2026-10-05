# Matched triplets: one case per implant design (A, B, C), matched exactly on
# procedure, sex and ASA, and within 3 years of age and 3 BMI units.
# Deterministic greedy matching: each implant-C case, in case_id order, takes
# the nearest unused A and B case. One case per patient (the first surgery)
# is eligible, so sets never share a patient.

make_matched_sets <- function(cohort) {
  pool <- cohort |>
    dplyr::group_by(patient_id) |>
    dplyr::slice_min(surgery_date, n = 1, with_ties = FALSE) |>
    dplyr::ungroup()
  anchors <- pool |> dplyr::filter(implant == "C") |> dplyr::arrange(case_id)
  used <- character()
  sets <- list()

  nearest <- function(x, imp) {
    cand <- pool |>
      dplyr::filter(implant == imp, procedure == x$procedure, sex == x$sex,
                    asa == x$asa, abs(age - x$age) <= 3, abs(bmi - x$bmi) <= 3,
                    !case_id %in% used)
    if (nrow(cand) == 0) return(NULL)
    cand |>
      dplyr::mutate(dist = abs(age - x$age) / 3 + abs(bmi - x$bmi) / 3) |>
      dplyr::arrange(dist, case_id) |>
      dplyr::slice(1) |>
      dplyr::select(-dist)
  }

  for (i in seq_len(nrow(anchors))) {
    x <- anchors[i, ]
    a <- nearest(x, "A")
    if (is.null(a)) next
    used <- c(used, a$case_id)
    b <- nearest(x, "B")
    if (is.null(b)) {
      used <- setdiff(used, a$case_id)
      next
    }
    used <- c(used, x$case_id, b$case_id)
    sets[[length(sets) + 1]] <- dplyr::bind_rows(x, a, b) |>
      dplyr::mutate(set_id = sprintf("M%03d", length(sets) + 1))
  }

  dplyr::bind_rows(sets) |>
    dplyr::select(set_id, case_id, procedure, implant, age, sex, bmi, asa,
                  followup_years, event_status)
}
