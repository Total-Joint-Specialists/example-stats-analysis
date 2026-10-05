# Regenerate every synthetic dataset in data/.
# Run from the repo root:  Rscript data-raw/generate.R
# Then check it:            Rscript data-raw/validate.R

for (f in list.files("data-raw/R", pattern = "[.]R$", full.names = TRUE)) source(f)

dir.create("data/codebooks", recursive = TRUE, showWarnings = FALSE)
dir.create("data/answer-keys", recursive = TRUE, showWarnings = FALSE)

cohort <- make_cohort()
write_tidy(cohort, "data/cohort.csv")

write_codebooks(codebooks()["cohort"], "data/codebooks")
message("Synthetic data written to data/")
