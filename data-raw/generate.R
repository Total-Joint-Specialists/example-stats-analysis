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

write_tidy(cohort,  "data/cohort.csv")
write_tidy(proms,   "data/proms_long.csv")
write_tidy(matched, "data/matched_sets.csv")
write_tidy(rel,     "data/radiographic_reliability.csv")

write_codebooks(codebooks()[c("cohort", "proms_long", "matched_sets",
                              "radiographic_reliability")], "data/codebooks")
message("Synthetic data written to data/")
