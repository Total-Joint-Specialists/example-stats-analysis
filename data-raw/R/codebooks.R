# Codebooks: one per published tidy dataset.
# allowed_values grammar (checked by tests/testthat/test-data-codebooks.R):
#   "a|b|c"  -> value must be one of the listed strings
#   "lo..hi" -> numeric value must lie in [lo, hi]
#   ""       -> not checked (IDs, dates, free text)
# Missing values are always blank cells and are never checked.

cb <- function(...) {
  tibble::tribble(~variable, ~label, ~type, ~units, ~allowed_values, ~notes, ...)
}

codebooks <- function() {
  list(
    cohort = cb(
      "case_id", "Procedure (case) ID", "id", "", "", "One row per case",
      "patient_id", "Patient ID", "id", "", "", "Bilateral patients have two cases",
      "site", "Surgery site", "categorical", "", "Site A|Site B", "",
      "surgeon", "Surgeon", "categorical", "", "S1|S2|S3", "",
      "procedure", "Procedure", "categorical", "", "THA|TKA", "",
      "side", "Operative side", "categorical", "", "L|R", "",
      "surgery_date", "Date of surgery (synthetic)", "date", "", "", "Time zero for survival",
      "age", "Age at surgery", "integer", "years", "40..89", "",
      "sex", "Sex", "categorical", "", "Female|Male", "",
      "bmi", "Body mass index", "numeric", "kg/m2", "18..55", "",
      "asa", "ASA physical status class", "integer", "", "1|2|3|4", "Ordinal",
      "diabetes", "Diabetes mellitus", "binary", "", "0|1", "1 = yes",
      "hypertension", "Hypertension", "binary", "", "0|1", "1 = yes",
      "sleep_apnea", "Obstructive sleep apnea", "binary", "", "0|1", "1 = yes",
      "smoker", "Smoking status", "categorical", "", "never|former|current", "",
      "cci", "Charlson comorbidity index", "integer", "points", "0..15", "",
      "anesthesia", "Primary anesthesia", "categorical", "", "spinal|general", "",
      "approach", "Surgical approach (THA only)", "categorical", "", "anterior|posterior", "Blank for TKA",
      "implant", "Implant design", "categorical", "", "A|B|C", "",
      "op_time_min", "Operative time", "integer", "minutes", "45..200", "",
      "los_days", "Length of stay", "integer", "days", "0..30", "0 = same-day discharge",
      "discharge", "Discharge destination", "categorical", "", "home|facility", "",
      "readmit_90d", "Readmitted within 90 days", "binary", "", "0|1", "1 = yes",
      "complication_90d", "Any complication within 90 days", "binary", "", "0|1", "1 = yes",
      "satisfaction_1yr", "Satisfaction at 1 year", "integer", "", "1|2|3|4|5", "Likert: 1 = very dissatisfied, 5 = very satisfied; blank = no response",
      "followup_years", "Follow-up from surgery to event or censoring", "numeric", "years", "0.01..11.5", "",
      "event_status", "Status at end of follow-up", "integer", "", "0|1|2", "0 = censored, 1 = revision, 2 = death. Revision rates are inflated for teaching",
      "revised", "Revised during follow-up", "binary", "", "0|1", "1 = yes; equals event_status == 1"
    ),
    proms_long = cb(
      "case_id", "Procedure (case) ID", "id", "", "", "Links to cohort.csv",
      "patient_id", "Patient ID", "id", "", "", "",
      "visit", "Scheduled visit", "categorical", "", "preop|6wk|3mo|1yr", "",
      "visit_days", "Days from surgery to the visit", "integer", "days", "-30..400", "Negative = before surgery; blank = visit missed",
      "instrument", "PROM instrument", "categorical", "", "HOOS JR|KOOS JR", "HOOS JR for THA, KOOS JR for TKA",
      "prom_score", "HOOS JR / KOOS JR interval score", "numeric", "points", "0..100", "100 = best",
      "vr12_pcs", "VR-12 physical component score", "numeric", "points", "0..100", "",
      "vr12_mcs", "VR-12 mental component score", "numeric", "points", "0..100", "",
      "walking_aid", "Uses a walking aid", "binary", "", "0|1", "1 = yes"
    ),
    matched_sets = cb(
      "set_id", "Matched set ID", "id", "", "", "One case per implant design in each set",
      "case_id", "Procedure (case) ID", "id", "", "", "Links to cohort.csv",
      "procedure", "Procedure", "categorical", "", "THA|TKA", "Matched exactly",
      "implant", "Implant design", "categorical", "", "A|B|C", "",
      "age", "Age at surgery", "integer", "years", "40..89", "Matched within 3 years",
      "sex", "Sex", "categorical", "", "Female|Male", "Matched exactly",
      "bmi", "Body mass index", "numeric", "kg/m2", "18..55", "Matched within 3 units",
      "asa", "ASA class", "integer", "", "1|2|3|4", "Matched exactly",
      "followup_years", "Follow-up", "numeric", "years", "0.01..11.5", "",
      "event_status", "Status at end of follow-up", "integer", "", "0|1|2", "0 = censored, 1 = revision, 2 = death"
    ),
    radiographic_reliability = cb(
      "knee_id", "Knee ID", "id", "", "", "",
      "rater", "Rater", "categorical", "", "R1|R2", "",
      "session", "Reading session", "integer", "", "1|2", "Sessions at least 2 weeks apart",
      "hka_deg", "Hip-knee-ankle angle", "numeric", "degrees", "165..195", "180 = neutral; < 180 = varus",
      "mpta_deg", "Medial proximal tibial angle", "numeric", "degrees", "78..96", "",
      "ldfa_deg", "Lateral distal femoral angle", "numeric", "degrees", "80..97", "",
      "cpak_class", "CPAK class", "categorical", "", "I|II|III|IV|V|VI|VII|VIII|IX", "From this reading's MPTA and LDFA"
    ),
    abstraction_workbook_tidy = cb(
      "case_id", "Study ID", "id", "", "", "Name and MRN are dropped during tidying",
      "site", "Surgery site", "categorical", "", "Site A|Site B", "From the sheet name",
      "surgery_date", "Date of surgery", "date", "", "", "",
      "age", "Age at surgery", "integer", "years", "40..89", "",
      "sex", "Sex", "categorical", "", "Female|Male", "",
      "bmi", "Body mass index", "numeric", "kg/m2", "18..55", "",
      "asa", "ASA class", "integer", "", "1|2|3|4", "",
      "diabetes", "Diabetes (DM)", "binary", "", "0|1", "From the comorbidity list",
      "hypertension", "Hypertension (HTN)", "binary", "", "0|1", "From the comorbidity list",
      "sleep_apnea", "Sleep apnea (OSA)", "binary", "", "0|1", "From the comorbidity list",
      "procedure", "Procedure", "categorical", "", "THA|TKA", "Split from the Procedure cell",
      "side", "Operative side", "categorical", "", "L|R", "Split from the Procedure cell",
      "los_days", "Length of stay", "integer", "days", "0..30", "",
      "revised", "Revised", "binary", "", "0|1", "Red fill on the Study ID cell",
      "prom_preop_date", "Pre-op PROM date", "date", "", "", "",
      "prom_preop", "Pre-op PROM score", "numeric", "points", "0..100", "",
      "prom_1yr_date", "1-year PROM date", "date", "", "", "",
      "prom_1yr", "1-year PROM score", "numeric", "points", "0..100", ""
    ),
    survey_items_long = cb(
      "case_id", "Study ID", "id", "", "", "",
      "instrument", "PROM instrument", "categorical", "", "HOOS JR|KOOS JR", "",
      "visit", "Visit", "categorical", "", "preop|6wk|3mo|1yr", "",
      "item", "Item number", "integer", "", "1..7", "KOOS JR has 7 items, HOOS JR 6",
      "response", "Item response", "integer", "", "0|1|2|3|4", "0 = none ... 4 = extreme; blank = not answered"
    )
  )
}

write_codebooks <- function(books, dir) {
  for (nm in names(books)) {
    readr::write_csv(books[[nm]], file.path(dir, paste0(nm, ".csv")), na = "")
  }
  invisible(dir)
}
