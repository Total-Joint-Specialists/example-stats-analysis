# Messy abstraction workbook, derived from a known truth table.
#
# make_abstraction_truth() picks 60 cases per site and assembles the values a
# chart abstractor would have recorded, including some missing values. Columns
# starting with "." (fake name and MRN) exist only to be written into the
# workbook; they are not part of the answer key.
#
# write_messy_workbook() renders that truth the way real abstraction sheets
# look: banner rows, merged headers, inconsistent formats, five missing codes,
# color-as-data, duplicate rows, and a totals row.

make_abstraction_truth <- function(cohort, proms, seed = 20261011) {
  set.seed(seed)
  pick <- cohort |>
    dplyr::group_by(site) |>
    dplyr::slice_sample(n = 60) |>
    dplyr::ungroup()
  prom_at <- function(v) {
    proms |>
      dplyr::filter(visit == v) |>
      dplyr::select(case_id, visit_days, prom_score)
  }
  pre <- prom_at("preop")
  yr1 <- prom_at("1yr")
  n <- nrow(pick)
  words <- c("ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF",
             "HOTEL", "INDIA", "JULIET", "KILO", "LIMA")

  truth <- pick |>
    dplyr::left_join(pre, by = "case_id") |>
    dplyr::rename(pre_days = visit_days, prom_preop = prom_score) |>
    dplyr::left_join(yr1, by = "case_id") |>
    dplyr::rename(yr1_days = visit_days, prom_1yr = prom_score) |>
    dplyr::transmute(
      .name = sprintf("TESTPATIENT, %s-%03d", sample(words, n, TRUE), seq_len(n)),
      .mrn  = sprintf("SYN-%06d", sample(100000:999999, n)),
      .rev_date = dplyr::if_else(revised == 1,
                                 surgery_date + round(followup_years * 365.25),
                                 as.Date(NA)),
      case_id, site, surgery_date, age, sex, bmi, asa, diabetes, hypertension,
      sleep_apnea, procedure, side, los_days, revised,
      prom_preop_date = surgery_date + pre_days,
      prom_preop,
      prom_1yr_date = surgery_date + yr1_days,
      prom_1yr) |>
    dplyr::arrange(site, case_id)

  # Values the abstractor could not find in the chart.
  truth$bmi[stats::runif(n) < 0.04] <- NA
  truth$asa[stats::runif(n) < 0.03] <- NA
  truth$los_days[stats::runif(n) < 0.03] <- NA
  truth
}

missing_code <- function(k, numeric = FALSE) {
  codes <- c("N/A", "unk", "-", "")
  if (numeric) codes <- c(codes, "999")
  sample(codes, k, replace = TRUE)
}

fmt_date_text <- function(d) {
  style <- sample(c("mdy", "iso", "long"), length(d), TRUE)
  month <- as.integer(format(d, "%m"))
  day   <- as.integer(format(d, "%d"))
  # month.name is always English; format("%B") would follow the computer's locale.
  ifelse(style == "mdy",
         sprintf("%d/%d/%s", month, day, format(d, "%y")),
         ifelse(style == "iso", format(d, "%Y-%m-%d"),
                sprintf("%s %d %s", month.name[month], day, format(d, "%Y"))))
}

# A cell is either a real Excel date, a number, or text. Encode each cell as a
# one-element list so a single column can mix types.
cell_date <- function(d) {
  lapply(seq_along(d), function(i) {
    if (is.na(d[i])) return(missing_code(1))
    if (stats::runif(1) < 0.4) d[i] else fmt_date_text(d[i])
  })
}

cell_number <- function(x, text_fmt = NULL, p_text = 0, numeric_missing = TRUE) {
  lapply(seq_along(x), function(i) {
    if (is.na(x[i])) return(missing_code(1, numeric = numeric_missing))
    if (!is.null(text_fmt) && stats::runif(1) < p_text) sprintf(text_fmt(), x[i]) else x[i]
  })
}

render_sheet_values <- function(t) {
  n <- nrow(t)
  sex_txt <- ifelse(t$sex == "Female",
                    sample(c("F", "Female", "f", "female"), n, TRUE),
                    sample(c("M", "Male", "male"), n, TRUE))
  asa_txt <- lapply(t$asa, function(a) {
    if (is.na(a)) return(missing_code(1, numeric = TRUE))
    switch(sample(c("num", "roman", "prefix"), 1, prob = c(0.6, 0.25, 0.15)),
           num = a,
           roman = as.character(utils::as.roman(a)),
           prefix = paste("ASA", a))
  })
  comorb <- vapply(seq_len(n), function(i) {
    toks <- c(if (t$diabetes[i] == 1) "DM", if (t$hypertension[i] == 1) "HTN",
              if (t$sleep_apnea[i] == 1) "OSA",
              if (stats::runif(1) < 0.1) sample(c("GERD", "hypothyroid", "OA hands"), 1))
    if (length(toks) == 0) return(sample(c("None", "none", "Nil"), 1))
    toks <- sample(toks)
    if (stats::runif(1) < 0.2) toks <- tolower(toks)
    paste(toks, collapse = sample(c(", ", "; ", " and ", ","), 1))
  }, character(1))
  side_txt <- ifelse(t$side == "L", sample(c("L", "Left"), n, TRUE),
                     sample(c("R", "Right"), n, TRUE))
  proc_txt <- ifelse(t$procedure == "TKA", sample(c("TKA", "Total knee"), n, TRUE),
                     sample(c("THA", "Total hip"), n, TRUE))
  procedure <- ifelse(stats::runif(n) < 0.6, paste(side_txt, proc_txt),
                      sprintf("%s (%s)", proc_txt, side_txt))
  los <- lapply(t$los_days, function(x) {
    if (is.na(x)) return(missing_code(1, numeric = TRUE))
    if (x == 0 && stats::runif(1) < 0.5) return("0 (same day)")
    if (stats::runif(1) < 0.15) return(if (x == 1) "1 day" else sprintf("%d days", x))
    x
  })
  rev_year <- format(t$.rev_date, "%Y")   # the cohort's own revision date
  notes <- ifelse(t$revised == 1 & stats::runif(n) < 0.5,
                  sprintf("revised %s for %s", rev_year,
                          sample(c("instability", "loosening", "infection"), n, TRUE)),
                  sample(c("", "", "", "pt moved out of state", "check chart",
                           "PROM by phone"), n, TRUE))

  list(
    "Pt Name"       = as.list(t$.name),
    "MRN"           = as.list(t$.mrn),
    "Study ID"      = as.list(t$case_id),
    "DOS"           = cell_date(t$surgery_date),
    "Age"           = cell_number(t$age, function() "%d yo", 0.15),
    "Sex"           = as.list(sex_txt),
    "BMI"           = cell_number(t$bmi, function() sample(c("%.1f kg/m2", "BMI %.1f"), 1), 0.3),
    "ASA"           = asa_txt,
    "Comorbidities" = as.list(comorb),
    "Procedure"     = as.list(procedure),
    "LOS"           = los,
    "Date"          = cell_date(t$prom_preop_date),
    "Score"         = cell_number(t$prom_preop),
    "Date "         = cell_date(t$prom_1yr_date),
    "Score "        = cell_number(t$prom_1yr),
    "Notes"         = as.list(notes)
  )
}

write_one_sheet <- function(wb, sheet, t, extra_mua = FALSE) {
  wb$add_worksheet(sheet)
  vals <- render_sheet_values(t)
  if (extra_mua) {
    mua <- as.list(sample(c("Y", "N", "", "N"), nrow(t), TRUE))
    at <- which(names(vals) == "LOS")
    vals <- c(vals[1:at], list(MUA = mua), vals[(at + 1):length(vals)])
  }
  headers <- trimws(names(vals))
  if (extra_mua) headers[headers == "Study ID"] <- "Study ID "  # trailing space, as in real tabs
  ncols <- length(headers)
  id_col <- which(trimws(headers) == "Study ID")

  # ~2% exact duplicates: repeat two rows a few rows before the end.
  order <- seq_len(nrow(t))
  order <- append(order, sample(order, 2), after = length(order) - 5)

  wb$add_data(sheet, sprintf("TJS Outcomes Abstraction - %s (SYNTHETIC DATA - NOT REAL PATIENTS)", sheet),
              start_row = 1, start_col = 1)
  wb$merge_cells(sheet, dims = openxlsx2::wb_dims(rows = 1, cols = 1:ncols))
  wb$add_data(sheet, "Abstractor: RA | Last updated: 1/15/2026 | DO NOT SORT",
              start_row = 2, start_col = 1)
  wb$merge_cells(sheet, dims = openxlsx2::wb_dims(rows = 2, cols = 1:ncols))

  first_date <- which(headers == "Date")[1]
  group_spans <- list(
    Patient       = 1:3,
    Surgery       = 4:(first_date - 1),
    `Pre-op PROM` = first_date:(first_date + 1),
    `1-yr PROM`   = (first_date + 2):(first_date + 3))
  for (g in names(group_spans)) {
    wb$add_data(sheet, g, start_row = 3, start_col = min(group_spans[[g]]))
    wb$merge_cells(sheet, dims = openxlsx2::wb_dims(rows = 3, cols = group_spans[[g]]))
  }
  wb$add_data(sheet, as.data.frame(t(headers)), start_row = 4, col_names = FALSE)

  for (r in seq_along(order)) {
    i <- order[r]
    row <- 4 + r
    for (j in seq_len(ncols)) {
      v <- vals[[j]][[i]]
      if (identical(v, "")) next
      wb$add_data(sheet, v, start_row = row, start_col = j, col_names = FALSE)
    }
    if (t$revised[i] == 1) {
      wb$add_fill(sheet, dims = openxlsx2::wb_dims(rows = row, cols = id_col),
                  color = openxlsx2::wb_color(hex = "FFFF9999"))
    }
  }
  total_row <- 4 + length(order) + 1
  wb$add_data(sheet, "TOTAL", start_row = total_row, start_col = 1)
  wb$add_data(sheet, sprintf("n = %d", nrow(t)), start_row = total_row, start_col = id_col)
  wb$add_data(sheet, sprintf("Mean %.1f", mean(t$bmi, na.rm = TRUE)),
              start_row = total_row, start_col = which(headers == "BMI"))
  invisible(wb)
}

write_messy_workbook <- function(truth, path, seed = 20261012) {
  set.seed(seed)
  wb <- openxlsx2::wb_workbook(creator = "TJS synthetic data generator")
  write_one_sheet(wb, "Site A", dplyr::filter(truth, site == "Site A"))
  write_one_sheet(wb, "Site B", dplyr::filter(truth, site == "Site B"), extra_mua = TRUE)
  wb$save(path, overwrite = TRUE)
  invisible(path)
}
