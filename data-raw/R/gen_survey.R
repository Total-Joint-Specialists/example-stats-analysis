# Survey-platform export of KOOS JR / HOOS JR item responses.
#
# make_survey_items() is the tidy truth: one row per case x visit x item of the
# case's own instrument, response 0 (none) to 4 (extreme), NA if missing.
# Responses track that visit's prom_score so the data look plausible; turning
# items into the 0-100 interval score is deliberately not part of the lesson.
#
# write_messy_survey() writes the wide export: one column per item per visit
# for both instruments, plus a metadata row of question labels under the header.

survey_visits <- c("preop", "6wk", "3mo", "1yr")
survey_items <- list(
  `KOOS JR` = c("Stiffness on waking", "Pain twisting or pivoting",
                "Pain straightening knee", "Pain on stairs", "Pain standing upright",
                "Rising from sitting", "Bending to the floor"),
  `HOOS JR` = c("Pain on stairs", "Pain on uneven ground", "Rising from sitting",
                "Bending to the floor", "Lying in bed", "Sitting")
)

make_survey_items <- function(cohort, proms, seed = 20261013) {
  set.seed(seed)
  picked <- sort(sample(cohort$case_id, 150))
  base <- proms |>
    dplyr::filter(case_id %in% picked) |>
    dplyr::select(case_id, instrument, visit, prom_score)
  rows <- base |>
    dplyr::mutate(n_items = lengths(survey_items[instrument])) |>
    tidyr::uncount(n_items, .id = "item")
  m <- nrow(rows)
  resp <- round(4 * (1 - rows$prom_score / 100) + stats::rnorm(m, 0, 0.6))
  resp <- as.integer(clamp(resp, 0, 4))
  resp[stats::runif(m) < 0.03] <- NA_integer_
  rows |>
    dplyr::mutate(item = as.integer(item), response = resp,
                  visit = factor(visit, levels = survey_visits)) |>
    dplyr::arrange(case_id, visit, item) |>
    dplyr::mutate(visit = as.character(visit)) |>
    dplyr::select(case_id, instrument, visit, item, response)
}

survey_column_name <- function(instrument, item, visit) {
  sprintf("%s_Q%d_%s", ifelse(instrument == "KOOS JR", "KOOS", "HOOS"), item, visit)
}

write_messy_survey <- function(items, path, seed = 20261014) {
  set.seed(seed)
  cols <- unlist(lapply(names(survey_items), function(ins) {
    unlist(lapply(survey_visits, function(v) {
      survey_column_name(ins, seq_along(survey_items[[ins]]), v)
    }))
  }))
  labels <- unlist(lapply(names(survey_items), function(ins) {
    unlist(lapply(survey_visits, function(v) {
      sprintf("%s - %s - %s", ins, survey_items[[ins]], v)
    }))
  }))

  wide <- items |>
    dplyr::mutate(col = survey_column_name(instrument, item, visit)) |>
    dplyr::select(case_id, instrument, col, response) |>
    tidyr::pivot_wider(names_from = col, values_from = response)
  for (cname in setdiff(cols, names(wide))) wide[[cname]] <- NA_integer_
  wide <- wide[, c("case_id", "instrument", cols)]
  ids <- vapply(seq_len(nrow(wide)), function(i) {
    paste0("R_", paste(sample(c(letters, LETTERS, 0:9), 15, TRUE), collapse = ""))
  }, character(1))
  wide <- tibble::add_column(wide, ResponseId = ids, .before = 1)

  header <- paste(names(wide), collapse = ",")
  meta <- paste(c("Response ID", "Study ID", "Instrument", labels), collapse = ",")
  body <- readr::format_csv(wide, na = "", col_names = FALSE)
  writeLines(c(header, meta, sub("\n$", "", body)), path)
  invisible(path)
}
