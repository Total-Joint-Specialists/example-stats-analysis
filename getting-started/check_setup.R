# Checks that R is ready for the tutorials.
# Run from the repository folder:  Rscript getting-started/check_setup.R
# or, in Positron's R console:     source("getting-started/check_setup.R")

ok <- TRUE
report <- function(label, pass, fix) {
  cat(sprintf("%-40s %s\n", label, if (pass) "OK" else paste("PROBLEM -", fix)))
  if (!pass) ok <<- FALSE
}

report(sprintf("R version %s", getRversion()), getRversion() >= "4.4",
       "install R 4.4 or newer from https://cloud.r-project.org")
report("project packages switched on (renv)", nzchar(Sys.getenv("RENV_PROJECT")),
       "start R inside the example-stats-analysis folder")
for (pkg in c("knitr", "rmarkdown", "reticulate", "testthat", "tidyverse", "readxl",
             "tidyxl", "janitor", "gtsummary", "flextable", "smd", "effectsize",
             "DescTools", "survival", "ggsurvfit")) {
  report(paste("R package", pkg), requireNamespace(pkg, quietly = TRUE),
         "run renv::restore() in the R console")
}

report("practice data readable (data/cohort.csv)",
       file.exists("data/cohort.csv") && nrow(utils::read.csv("data/cohort.csv")) > 0,
       "run this from the example-stats-analysis folder")

cat(if (ok) "\nAll good - you are ready.\n" else "\nFix the problems above, then run this again.\n")
if (!interactive()) quit(status = if (ok) 0 else 1)
