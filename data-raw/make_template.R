# Build templates/data-collection-template.xlsx: a starting point for a tidy
# chart-abstraction sheet. Run from the repo root:
#   Rscript data-raw/make_template.R

fields <- tibble::tribble(
  ~variable,      ~label,                          ~type,         ~units,  ~allowed,                         ~rule,
  "study_id",     "Study ID (never the MRN)",      "id",          "",      "e.g. C0001",                     "none",
  "surgery_date", "Date of surgery",               "date",        "",      "2000-01-01 to 2030-12-31",       "date",
  "procedure",    "Procedure",                     "categorical", "",      "THA, TKA, Not recorded",         "list",
  "side",         "Operative side",                "categorical", "",      "L, R, Not recorded",             "list",
  "age",          "Age at surgery",                "integer",     "years", "18 to 110",                      "whole",
  "sex",          "Sex",                           "categorical", "",      "Female, Male, Not recorded",     "list",
  "bmi",          "Body mass index",               "numeric",     "kg/m2", "10 to 80",                       "decimal",
  "asa",          "ASA class",                     "categorical", "",      "1, 2, 3, 4, Not recorded",       "list",
  "diabetes",     "Diabetes mellitus",             "categorical", "",      "Yes, No, Not recorded",          "list",
  "hypertension", "Hypertension",                  "categorical", "",      "Yes, No, Not recorded",          "list",
  "sleep_apnea",  "Obstructive sleep apnea",       "categorical", "",      "Yes, No, Not recorded",          "list",
  "los_days",     "Length of stay",                "integer",     "days",  "0 to 60",                        "whole",
  "revised",      "Revised during follow-up",      "categorical", "",      "Yes, No, Not recorded",          "list"
)

limits <- list(age = c(18, 110), bmi = c(10, 80), los_days = c(0, 60))
list_values <- function(allowed) paste0('"', gsub(", ", ",", allowed), '"')

wb <- openxlsx2::wb_workbook(creator = "TJS stats tutorials")

wb$add_worksheet("README")
readme <- c(
  "TJS data-collection template",
  "",
  "1. One row per procedure. One column per variable. One value per cell.",
  "2. Never type patient names or MRNs here. Use the study ID; keep the MRN-to-study-ID crosswalk in a separate, secured file.",
  "3. Pick categorical values from the dropdowns. Do not type variants (no 'F' vs 'female').",
  "4. Numbers only in number columns: 32.1, not '32.1 kg/m2'. Units are in the dictionary sheet.",
  "5. Dates as real dates (the cell checks the range).",
  "6. If a value is not in the chart: choose 'Not recorded' in dropdown columns, leave number and date cells blank.",
  "7. No colors, bold, or comments as data. If it matters, it gets a column.",
  "8. Do not merge cells, add title rows, or add totals rows.",
  "9. Add a variable? Add it to the dictionary sheet first, then the data sheet."
)
wb$add_data("README", readme, col_names = FALSE)

wb$add_worksheet("data")
wb$add_data("data", as.data.frame(t(fields$variable)), col_names = FALSE)
wb$freeze_pane("data", first_row = TRUE)
for (i in seq_len(nrow(fields))) {
  dims <- openxlsx2::wb_dims(rows = 2:1000, cols = i)
  f <- fields[i, ]
  if (f$rule == "list") {
    wb$add_data_validation("data", dims = dims, type = "list", value = list_values(f$allowed))
  } else if (f$rule %in% c("whole", "decimal")) {
    wb$add_data_validation("data", dims = dims, type = f$rule, operator = "between",
                           value = limits[[f$variable]])
  } else if (f$rule == "date") {
    wb$add_data_validation("data", dims = dims, type = "date", operator = "between",
                           value = as.Date(c("2000-01-01", "2030-12-31")))
  }
}

wb$add_worksheet("dictionary")
wb$add_data("dictionary", fields[, c("variable", "label", "type", "units", "allowed")])

wb$add_worksheet("missing_codes")
wb$add_data("missing_codes", tibble::tribble(
  ~situation,                                   ~what_to_enter,
  "Value not documented in the chart",          "Dropdown: 'Not recorded'. Number/date: leave blank",
  "Question does not apply (e.g. approach for TKA)", "Leave blank",
  "Not yet abstracted",                         "Leave the whole row unfinished; track progress outside the sheet"
))

dir.create("templates", showWarnings = FALSE)
wb$save("templates/data-collection-template.xlsx", overwrite = TRUE)
message("Wrote templates/data-collection-template.xlsx")
