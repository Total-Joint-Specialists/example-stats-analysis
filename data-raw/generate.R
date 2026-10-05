# Regenerate every synthetic dataset in data/.
# Run from the repo root:  Rscript data-raw/generate.R
# Then check it:            Rscript data-raw/validate.R

for (f in list.files("data-raw/R", pattern = "[.]R$", full.names = TRUE)) source(f)

dir.create("data/codebooks", recursive = TRUE, showWarnings = FALSE)
dir.create("data/answer-keys", recursive = TRUE, showWarnings = FALSE)

cohort  <- make_cohort()
proms   <- make_proms_long(cohort)
matched <- make_matched_sets(cohort)
rel     <- make_reliability()
truth   <- make_abstraction_truth(cohort, proms)
items   <- make_survey_items(cohort, proms)

write_tidy(cohort,  "data/cohort.csv")
write_tidy(proms,   "data/proms_long.csv")
write_tidy(matched, "data/matched_sets.csv")
write_tidy(rel,     "data/radiographic_reliability.csv")

write_messy_workbook(truth, "data/messy_abstraction_workbook.xlsx")
write_messy_survey(items, "data/messy_survey_export.csv")
write_tidy(truth, "data/answer-keys/abstraction_workbook_tidy.csv")
write_tidy(items, "data/answer-keys/survey_items_long.csv")

write_codebooks(codebooks(), "data/codebooks")
write_checksums("data")
message("Synthetic data written to data/")
