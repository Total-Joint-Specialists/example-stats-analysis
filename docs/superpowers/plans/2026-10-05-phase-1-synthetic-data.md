# Phase 1: Synthetic Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate every synthetic dataset the tutorials use, plus the messy files, their answer keys, codebooks and the data-collection template. The data come from seeded R code, and test suites in both languages prove that each file still teaches its built-in lesson.

**Architecture:**
- One R generator (`data-raw/generate.R`, which sources `data-raw/R/*.R`) builds the tidy truth first: the cohort, then PROMs, matched sets and reliability readings.
- It then derives the messy workbook and survey export *from* that truth, and writes the truth out as answer keys.
- Every output is committed under `data/` (and `templates/`).
- testthat suites check structure, codebooks, built-in effects and byte-for-byte reproducibility. pytest suites check that Python reads every file the same way.

**Tech Stack:**
- R 4.6: dplyr, tidyr, tibble, readr, readxl, openxlsx2, survival, irr, testthat, withr (renv)
- Python 3.13: pandas, openpyxl, pytest (uv)

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md` (sections 5 and 8)
**Depends on:** Phase 0 merged to `main` (`docs/superpowers/plans/2026-10-05-phase-0-site-scaffold.md`)

## Global Constraints

- **Synthetic only, public repo.** Fake names match `TESTPATIENT, <WORD>-<###>` and fake MRNs match `SYN-<6 digits>`. Nothing in `data/` may look like a real identifier.
- **Seeds are fixed and were chosen in prototyping** so every assertion passes:

  | Generator | Seed |
  |---|---|
  | cohort | 20261007 |
  | proms | 20261008 |
  | abstraction truth | 20261011 |
  | workbook writer | 20261012 |
  | survey items | 20261013 |
  | survey writer | 20261014 |
  | reliability | 20261018 |

  **Never change a seed or a parameter to make a test pass.** If an effect test fails, stop and report the failing assertion and its observed value.
- **Never hand-edit anything in `data/`.** Change `data-raw/` and regenerate.
- **CSV format:** written only through `write_tidy()`. Missing values are blank cells (`na = ""`), dates are ISO, and `.`-prefixed helper columns are dropped.
- **Excel files:** written with **openxlsx2**, never `openxlsx`. openxlsx 4.2.9 writes a dangling drawing reference that Python's openpyxl cannot open (verified).
- **Generator code style:** `pkg::fun()` calls, no `library()`, native pipe `|>`.
- **Codebook `allowed_values` grammar:** `a|b|c` (set), `lo..hi` (inclusive numeric range), or blank (not checked).
- **Branching:** work on branch `phase-1-synthetic-data`, created from `main` after Phase 0 is merged.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **R writes missing values as the text `NA`.** That's readr's default. Python and Excel users would then see the string "NA" instead of a missing value. Test: `tests/python/test_data_files.py::test_missing_values_are_blank_cells` (Task 1). Verified in prototyping: it fails when `na = "NA"`.
2. **The messy workbook won't open in Python.** That was the openxlsx bug. Test: `tests/python/test_messy_files.py::test_workbook_opens_and_red_fill_marks_exactly_the_revisions` (Task 5).
3. **Someone hand-edits a CSV, or package updates silently change the generated data.** Test: `tests/testthat/test-data-reproducible.R` (Task 8).
4. **A PROM visit is recorded after the patient was revised, died or was lost to follow-up, or a missed visit keeps some values.** Tests: `tests/testthat/test-data-proms.R` (Task 2).
5. **The answer key leaks fake names or MRNs, or drifts from the cohort it came from.** Test: `tests/testthat/test-data-workbook.R` (Task 5).

## Reference numbers from the prototype

Regenerating on the maintainer's Mac (R 4.6.0) produced the following. Use them to confirm your run matches.

| Output | Value |
|---|---|
| `data/cohort.csv` | 604 rows; 520 patients, 84 of them bilateral; `event_status` 0/1/2 = 501/67/36; md5 `676d190d1d2bbea0387ce6ed3f2ba7de` |
| `data/proms_long.csv` | 2,416 rows |
| `data/matched_sets.csv` | 177 rows in 59 sets |
| `data/radiographic_reliability.csv` | 240 rows |
| `data/answer-keys/abstraction_workbook_tidy.csv` | 120 rows, 15 of them revised |
| `data/answer-keys/survey_items_long.csv` | 3,956 rows |
| `data/messy_survey_export.csv` | 152 lines (header, metadata row, 150 responses) |

If the cohort md5 differs but **every** test passes, note it in your task report and continue. If any effect test fails, stop and report (see Global Constraints).

---

### Task 1: Data dependencies, cohort generator, codebooks, validation runner

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `pyproject.toml`, `uv.lock`
- Create: `data-raw/R/gen_cohort.R`, `data-raw/R/write_tidy.R`, `data-raw/R/codebooks.R`, `data-raw/generate.R`, `data-raw/validate.R`
- Create (generated): `data/cohort.csv`, `data/codebooks/cohort.csv`
- Test: `tests/testthat/helper-data.R`, `tests/testthat/test-data-cohort.R`, `tests/testthat/test-data-codebooks.R`, `tests/python/test_data_files.py`

**Interfaces:**
- Produces:
  - `clamp(x, lo, hi)`, `rpiecewise(rate_early, rate_late, cut)`, `rgompertz_time(a, b)`
  - `make_cohort(seed = 20261007, hr_c = 2.5, base_rate = 0.015, early_mult = 10, early_cut = 0.5)`. It returns a tibble with columns `case_id, patient_id, site, surgeon, procedure, side, surgery_date, age, sex, bmi, asa, diabetes, hypertension, sleep_apnea, smoker, cci, anesthesia, approach, implant, op_time_min, los_days, discharge, readmit_90d, complication_90d, satisfaction_1yr, followup_years, event_status, revised, .recovery`. The `.recovery` column is a latent helper.
  - `write_tidy(df, path)`
  - `codebooks()`: a named list of 6 tibbles named `cohort, proms_long, matched_sets, radiographic_reliability, abstraction_workbook_tidy, survey_items_long`
  - `write_codebooks(books, dir)`
  - Test helpers `data_path(...)` and `read_tidy(name)`

- [ ] **Step 1: Create the branch**

```bash
git checkout main && git pull && git checkout -b phase-1-synthetic-data
```

- [ ] **Step 2: Add the R and Python dependencies**

Replace the `Imports:` block of `DESCRIPTION` with:

```
Imports:
    dplyr,
    irr,
    knitr,
    openxlsx2,
    readr,
    readxl,
    reticulate,
    rmarkdown,
    survival,
    testthat,
    tibble,
    tidyr,
    withr
```

Run:

```bash
Rscript -e 'renv::install(c("dplyr", "irr", "openxlsx2", "readr", "readxl", "survival", "tibble", "tidyr"), prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
uv add openpyxl
```

Expected:
- `renv.lock` now lists `openxlsx2`, `irr` and `survival`
- `pyproject.toml` lists `openpyxl` under `dependencies`

- [ ] **Step 3: Write the failing tests**

`tests/testthat/helper-data.R`:

```r
# Shared helpers for the data tests. testthat runs with tests/testthat as the
# working directory, so paths go through test_path().
data_path <- function(...) testthat::test_path("..", "..", "data", ...)

read_tidy <- function(name) {
  readr::read_csv(data_path(name), show_col_types = FALSE, guess_max = 10000)
}
```

`tests/testthat/test-data-cohort.R`:

```r
cohort <- read_tidy("cohort.csv")

skewness <- function(x) mean((x - mean(x))^3) / stats::sd(x)^3

test_that("one row per case, about 600 cases from about 520 patients", {
  expect_equal(anyDuplicated(cohort$case_id), 0)
  expect_gte(nrow(cohort), 550)
  expect_lte(nrow(cohort), 650)
  per_patient <- table(cohort$patient_id)
  expect_true(all(per_patient <= 2))
  expect_gte(sum(per_patient == 2), 60)
  expect_lte(sum(per_patient == 2), 100)
})

test_that("bilateral patients are internally consistent", {
  bil <- cohort |>
    dplyr::group_by(patient_id) |>
    dplyr::filter(dplyr::n() == 2)
  s <- bil |>
    dplyr::summarise(sides = paste(sort(side), collapse = ""),
                     sexes = dplyr::n_distinct(sex),
                     procs = dplyr::n_distinct(procedure), .groups = "drop")
  expect_true(all(s$sides == "LR"))
  expect_true(all(s$sexes == 1))
  expect_true(all(s$procs == 1))
  # A patient dies once: both cases imply the same death date (followup_years
  # is rounded to 0.01 y, about 4 days).
  deaths <- bil |>
    dplyr::filter(event_status == 2) |>
    dplyr::mutate(death = surgery_date + round(followup_years * 365.25)) |>
    dplyr::summarise(spread = as.numeric(diff(range(death))), .groups = "drop")
  expect_true(all(deaths$spread <= 4))
})

test_that("approach is recorded for THA only and revised matches event_status", {
  expect_true(all(is.na(cohort$approach[cohort$procedure == "TKA"])))
  expect_false(any(is.na(cohort$approach[cohort$procedure == "THA"])))
  expect_equal(cohort$revised, as.numeric(cohort$event_status == 1))
})

test_that("TKA patients have a higher BMI than THA patients", {
  tt <- stats::t.test(bmi ~ procedure, data = cohort)  # Welch
  expect_lt(tt$p.value, 0.01)
  m <- tapply(cohort$bmi, cohort$procedure, mean)
  expect_gt(m[["TKA"]] - m[["THA"]], 0.8)
})

test_that("sex is unrelated to 90-day readmission (a true null)", {
  expect_gt(stats::fisher.test(table(cohort$sex, cohort$readmit_90d))$p.value, 0.2)
})

test_that("length of stay is right-skewed with most stays 0-1 days", {
  expect_gt(skewness(cohort$los_days), 1.5)
  expect_gt(mean(cohort$los_days <= 1), 0.5)
})

test_that("BMI relates moderately to operative time; age only weakly", {
  r_bmi <- stats::cor(cohort$bmi, cohort$op_time_min)
  expect_gt(r_bmi, 0.3)
  expect_lt(r_bmi, 0.5)
  expect_lt(abs(stats::cor(cohort$age, cohort$op_time_min)), 0.2)
})

test_that("implant C has a higher revision hazard", {
  lr <- survival::survdiff(survival::Surv(followup_years, revised) ~ implant, data = cohort)
  expect_lt(1 - stats::pchisq(lr$chisq, df = 2), 0.05)
  fit <- survival::coxph(survival::Surv(followup_years, revised) ~ I(implant == "C"),
                         data = cohort)
  hr <- unname(exp(stats::coef(fit)))
  expect_gt(hr, 1.5)
  expect_lt(hr, 3.5)
})

test_that("deaths compete with revisions", {
  old <- cohort[cohort$age >= 75, ]
  expect_gte(sum(old$event_status == 2), sum(old$event_status == 1))
  km <- survival::survfit(survival::Surv(followup_years, revised) ~ 1, data = cohort)
  aj <- survival::survfit(survival::Surv(followup_years, factor(event_status, 0:2)) ~ 1,
                          data = cohort)
  one_minus_km <- 1 - summary(km, times = 10, extend = TRUE)$surv
  cif <- summary(aj, times = 10, extend = TRUE)$pstate[, 2]
  expect_gt(one_minus_km - cif, 0.005)
})

test_that("posterior THA approach violates proportional hazards", {
  tha <- cohort[cohort$procedure == "THA", ]
  fit <- survival::coxph(survival::Surv(followup_years, revised) ~ approach, data = tha)
  expect_lt(survival::cox.zph(fit)$table["approach", "p"], 0.05)
})
```

`tests/testthat/test-data-codebooks.R`. This is the loop part only; Task 8 appends the completeness test.

```r
# Every tidy dataset and answer key has a codebook whose variables match the
# file's columns (same order) and whose allowed_values hold for every value.

dataset_path <- function(book) {
  if (file.exists(data_path(book))) data_path(book) else data_path("answer-keys", book)
}

values_allowed <- function(x, rule) {
  x <- x[!is.na(x)]
  if (is.na(rule) || rule == "") return(TRUE)
  if (grepl("..", rule, fixed = TRUE)) {
    lim <- as.numeric(strsplit(rule, "..", fixed = TRUE)[[1]])
    return(all(x >= lim[1] & x <= lim[2]))
  }
  all(as.character(x) %in% strsplit(rule, "|", fixed = TRUE)[[1]])
}

books <- list.files(data_path("codebooks"), pattern = "[.]csv$")

for (book in books) {
  test_that(paste("codebook agrees with", book), {
    cb <- readr::read_csv(data_path("codebooks", book), show_col_types = FALSE,
                          col_types = readr::cols(.default = "c"))
    df <- readr::read_csv(dataset_path(book), show_col_types = FALSE, guess_max = 10000)
    expect_equal(names(df), cb$variable)
    for (i in seq_len(nrow(cb))) {
      expect_true(values_allowed(df[[cb$variable[i]]], cb$allowed_values[i]),
                  label = paste(book, cb$variable[i], "within", cb$allowed_values[i]))
    }
  })
}
```

`tests/python/test_data_files.py`:

```python
"""Python-side checks on the tidy CSVs: every file opens in pandas, matches its
codebook, and stores missing values as blank cells (never the text "NA")."""

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CODEBOOKS = sorted((DATA / "codebooks").glob("*.csv"))


def dataset_for(codebook: Path) -> Path:
    direct = DATA / codebook.name
    return direct if direct.exists() else DATA / "answer-keys" / codebook.name


@pytest.mark.parametrize("codebook", CODEBOOKS, ids=lambda p: p.name)
def test_columns_match_codebook(codebook):
    df = pd.read_csv(dataset_for(codebook))
    assert list(df.columns) == list(pd.read_csv(codebook)["variable"])


@pytest.mark.parametrize("codebook", CODEBOOKS, ids=lambda p: p.name)
def test_missing_values_are_blank_cells(codebook):
    df = pd.read_csv(dataset_for(codebook), keep_default_na=False, na_values=[""])
    text = df.select_dtypes(include=["object", "string"])
    for token in ["NA", "N/A", "NaN", "null", "None"]:
        assert not (text == token).any().any(), f"{codebook.name} contains the text {token!r}"


def test_cohort_dates_parse():
    cohort = pd.read_csv(DATA / "cohort.csv", parse_dates=["surgery_date"])
    assert len(cohort) > 0
    assert cohort["surgery_date"].dt.year.between(2015, 2025).all()
```

- [ ] **Step 4: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "data")'
uv run pytest tests/python/test_data_files.py -q
```

Expected:
- R: errors with `'.../data/cohort.csv' does not exist`
- Python: `test_cohort_dates_parse` FAILS with `FileNotFoundError`; the parametrized tests are skipped (empty parameter set)

- [ ] **Step 5: Write the generator code**

`data-raw/R/gen_cohort.R`:

```r
# Synthetic cohort: one row per primary THA/TKA.
#
# Columns whose names start with "." are latent helpers that other generators
# use (for example .recovery drives PROM gains). write_tidy() drops them.

clamp <- function(x, lo, hi) pmin(pmax(x, lo), hi)

# Draw a time from a piecewise-constant hazard: `rate_early` until `cut`
# years, then `rate_late`. Inverse-CDF method on a unit exponential.
rpiecewise <- function(rate_early, rate_late, cut) {
  e <- stats::rexp(length(rate_early))
  ifelse(e < rate_early * cut,
         e / rate_early,
         cut + (e - rate_early * cut) / rate_late)
}

# Draw a time from a Gompertz hazard h(t) = a * exp(b * t).
rgompertz_time <- function(a, b) {
  e <- stats::rexp(length(a))
  log1p(e * b / a) / b
}

make_cohort <- function(seed = 20261007, hr_c = 2.5, base_rate = 0.015,
                        early_mult = 10, early_cut = 0.5) {
  set.seed(seed)
  n_pat     <- 520
  n_bilat   <- 85
  admin_end <- as.Date("2025-12-31")

  patients <- tibble::tibble(
    patient_id   = sprintf("P%04d", seq_len(n_pat)),
    sex          = sample(c("Female", "Male"), n_pat, TRUE, prob = c(0.58, 0.42)),
    procedure    = sample(c("TKA", "THA"), n_pat, TRUE, prob = c(0.55, 0.45)),
    site         = sample(c("Site A", "Site B"), n_pat, TRUE),
    smoker       = sample(c("never", "former", "current"), n_pat, TRUE,
                          prob = c(0.55, 0.35, 0.10)),
    age1         = round(clamp(stats::rnorm(n_pat, 66, 9), 40, 85)),
    bmi_base     = stats::rnorm(n_pat, 29.6, 5.5),
    date1        = as.Date("2015-01-01") +
                   sample(0:(365 * 9), n_pat, replace = TRUE),
    gap_days     = sample(90:540, n_pat, replace = TRUE),
    wants_second = seq_len(n_pat) %in% sample(n_pat, n_bilat),
    rec_pat      = stats::rnorm(n_pat)
  )
  patients$bmi_base <- clamp(patients$bmi_base + 1.6 * (patients$procedure == "TKA"),
                             18, 55)
  patients$diabetes <- stats::rbinom(n_pat, 1, stats::plogis(
    -2.2 + 0.08 * (patients$bmi_base - 30) + 0.02 * (patients$age1 - 66)))
  patients$hypertension <- stats::rbinom(n_pat, 1, stats::plogis(
    0.1 + 0.05 * (patients$age1 - 66) + 0.06 * (patients$bmi_base - 30)))
  patients$sleep_apnea <- stats::rbinom(n_pat, 1, stats::plogis(
    -2.0 + 0.12 * (patients$bmi_base - 30) + 0.5 * (patients$sex == "Male")))

  # Patient-level follow-up end: death (Gompertz in age), loss to follow-up
  # (3%/yr), or administrative end of data.
  t_death <- rgompertz_time(0.008 * exp(0.1 * (patients$age1 - 66)), 0.1)
  t_ltfu  <- stats::rexp(n_pat, 0.03)
  patients$death_date <- patients$date1 + round(t_death * 365.25)
  patients$ltfu_date  <- patients$date1 + round(t_ltfu * 365.25)
  patients$end_date   <- pmin(patients$death_date, patients$ltfu_date, admin_end)
  patients$died       <- patients$death_date <= pmin(patients$ltfu_date, admin_end)

  first <- patients |>
    dplyr::mutate(case_no = 1L, surgery_date = date1,
                  side = sample(c("L", "R"), n_pat, TRUE))
  second <- patients |>
    dplyr::mutate(surgery_date = date1 + gap_days) |>
    dplyr::filter(wants_second,
                  surgery_date < end_date,
                  surgery_date <= as.Date("2024-12-31")) |>
    dplyr::mutate(case_no = 2L)
  second$side <- ifelse(first$side[match(second$patient_id, first$patient_id)] == "L",
                        "R", "L")

  cases <- dplyr::bind_rows(first, second) |>
    dplyr::arrange(surgery_date, patient_id) |>
    dplyr::mutate(case_id = sprintf("C%04d", dplyr::row_number()))
  n <- nrow(cases)

  cases$age <- cases$age1 + floor(as.numeric(cases$surgery_date - cases$date1) / 365.25)
  cases$bmi <- round(clamp(cases$bmi_base + ifelse(cases$case_no == 2,
                                                   stats::rnorm(n, 0, 0.8), 0),
                           18, 55), 1)

  asa_latent <- 0.04 * (cases$age - 66) + 0.08 * (cases$bmi - 30) +
    0.6 * cases$diabetes + 0.3 * cases$hypertension + stats::rnorm(n)
  cases$asa <- as.integer(cut(asa_latent,
                              stats::quantile(asa_latent, c(0, 0.06, 0.56, 0.97, 1)),
                              include.lowest = TRUE))
  cases$cci <- stats::rpois(n, exp(-0.5 + 0.04 * (cases$age - 66) +
                                   0.5 * cases$diabetes + 0.25 * (cases$asa - 2)))

  cases$surgeon    <- sample(c("S1", "S2", "S3"), n, TRUE, prob = c(0.40, 0.35, 0.25))
  cases$anesthesia <- sample(c("spinal", "general"), n, TRUE, prob = c(0.75, 0.25))
  cases$approach   <- ifelse(cases$procedure == "THA",
                             sample(c("anterior", "posterior"), n, TRUE,
                                    prob = c(0.55, 0.45)),
                             NA_character_)
  cases$implant    <- sample(c("A", "B", "C"), n, TRUE, prob = c(0.40, 0.35, 0.25))

  cases$op_time_min <- as.integer(pmax(45, round(
    80 + 1.3 * (cases$bmi - 30) + 0.2 * (cases$age - 66) +
      6 * (cases$procedure == "TKA") + stats::rnorm(n, 0, 14))))
  cases$los_days <- stats::rnbinom(n, size = 1.2, mu = exp(
    -0.25 + 0.25 * (cases$asa - 2) + 0.02 * (cases$age - 66)))
  cases$discharge <- ifelse(stats::rbinom(n, 1, stats::plogis(
    -3.4 + 0.08 * (cases$age - 66) + 0.4 * (cases$asa - 2))) == 1,
    "facility", "home")
  # Readmission deliberately does not depend on sex (a true null result).
  cases$readmit_90d <- stats::rbinom(n, 1, stats::plogis(
    -3.2 + 0.03 * (cases$age - 66) + 0.3 * (cases$asa - 2)))
  cases$complication_90d <- stats::rbinom(n, 1, stats::plogis(
    -2.6 + 0.04 * (cases$age - 66) + 0.35 * (cases$asa - 2) + 0.05 * (cases$bmi - 30)))

  cases$.recovery <- 0.7 * cases$rec_pat + 0.7 * stats::rnorm(n)
  sat_latent <- cases$.recovery + stats::rnorm(n, 0, 0.6)
  cases$satisfaction_1yr <- as.integer(cut(
    sat_latent, stats::quantile(sat_latent, c(0, 0.03, 0.08, 0.18, 0.50, 1)),
    include.lowest = TRUE))
  cases$satisfaction_1yr[stats::runif(n) < 0.08] <- NA_integer_

  # Revision: implant C multiplies the hazard by `hr_c`. Posterior THA
  # multiplies it by `early_mult` for the first `early_cut` years only (early
  # instability), which violates proportional hazards on purpose. Rates are
  # inflated for teaching so the survival pages have enough events.
  hr_implant <- c(A = 1, B = 1, C = hr_c)[cases$implant]
  rate_late  <- base_rate * hr_implant * exp(0.02 * (cases$bmi - 30))
  mult       <- ifelse(!is.na(cases$approach) & cases$approach == "posterior", early_mult, 1)
  t_rev      <- rpiecewise(rate_late * mult, rate_late, cut = early_cut)
  rev_date   <- cases$surgery_date + round(t_rev * 365.25)

  revised_first <- rev_date < cases$end_date
  stop_date     <- dplyr::if_else(revised_first, rev_date, cases$end_date)
  cases$event_status <- dplyr::case_when(
    revised_first ~ 1L,
    cases$died & cases$end_date == cases$death_date ~ 2L,
    TRUE ~ 0L)
  cases$revised <- as.integer(cases$event_status == 1L)
  cases$followup_years <- round(pmax(as.numeric(stop_date - cases$surgery_date) / 365.25,
                                     0.01), 2)

  cases |>
    dplyr::select(case_id, patient_id, site, surgeon, procedure, side, surgery_date,
                  age, sex, bmi, asa, diabetes, hypertension, sleep_apnea, smoker, cci,
                  anesthesia, approach, implant, op_time_min, los_days, discharge,
                  readmit_90d, complication_90d, satisfaction_1yr,
                  followup_years, event_status, revised, .recovery)
}
```

`data-raw/R/write_tidy.R`:

```r
# Write a tidy dataset: drop latent "."-prefixed helper columns, ISO dates,
# missing values as blank cells (read as missing by both readr and pandas).
write_tidy <- function(df, path) {
  df <- dplyr::select(df, !dplyr::starts_with("."))
  readr::write_csv(df, path, na = "")
  invisible(path)
}
```

`data-raw/R/codebooks.R`. This is complete; it defines all six codebooks now, and `generate.R` writes only the ones whose data exist so far.

```r
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
```

`data-raw/generate.R` (Task 1 version):

```r
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
```

`data-raw/validate.R`:

```r
# Check that the synthetic data still teach what they are meant to.
# Run from the repo root:  Rscript data-raw/validate.R
testthat::test_dir("tests/testthat", filter = "data", stop_on_failure = TRUE)
```

- [ ] **Step 6: Generate, and compare with the reference numbers**

Run:

```bash
Rscript data-raw/generate.R
Rscript -e 'd <- read.csv("data/cohort.csv"); cat(nrow(d), length(unique(d$patient_id)), sum(table(d$patient_id) == 2), table(d$event_status), "\n")'
md5 -q data/cohort.csv
```

Expected:
- `604 520 84 501 67 36`
- md5 `676d190d1d2bbea0387ce6ed3f2ba7de` (see "Reference numbers" if it differs)

- [ ] **Step 7: Run the tests to verify they pass**

Run:

```bash
Rscript data-raw/validate.R
uv run pytest tests/python/test_data_files.py -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS ... ]`
- Python: `3 passed`

- [ ] **Step 8: Commit**

```bash
git add DESCRIPTION renv.lock pyproject.toml uv.lock data-raw data/cohort.csv data/codebooks/cohort.csv tests/testthat/helper-data.R tests/testthat/test-data-cohort.R tests/testthat/test-data-codebooks.R tests/python/test_data_files.py
git commit -m "Generate synthetic cohort with built-in teaching effects and codebook

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: PROMs in long format

**Files:**
- Create: `data-raw/R/gen_proms.R`
- Modify: `data-raw/generate.R`
- Create (generated): `data/proms_long.csv`, `data/codebooks/proms_long.csv`
- Test: `tests/testthat/test-data-proms.R`

**Interfaces:**
- Consumes: `make_cohort()` output (including `.recovery`) and `clamp()` (Task 1).
- Produces: `make_proms_long(cohort, seed = 20261008)`. It returns a tibble with `case_id, patient_id, visit, visit_days, instrument, prom_score, vr12_pcs, vr12_mcs, walking_aid`. There are 4 rows per case, `visit` takes the values `preop, 6wk, 3mo, 1yr`, and a missed visit has every measure NA.

- [ ] **Step 1: Write the failing test**

`tests/testthat/test-data-proms.R`:

```r
cohort <- read_tidy("cohort.csv")
proms  <- read_tidy("proms_long.csv")

wide <- function(col) {
  tidyr::pivot_wider(proms[, c("case_id", "visit", col)],
                     names_from = visit, values_from = dplyr::all_of(col))
}

test_that("one row per case x visit, for every cohort case", {
  expect_equal(nrow(dplyr::distinct(proms, case_id, visit)), nrow(proms))
  expect_equal(nrow(proms), 4 * nrow(cohort))
  expect_setequal(unique(proms$case_id), cohort$case_id)
  joined <- dplyr::left_join(proms, cohort[, c("case_id", "patient_id")],
                             by = "case_id", suffix = c("", "_cohort"))
  expect_equal(joined$patient_id, joined$patient_id_cohort)
})

test_that("no PROM visit is recorded after follow-up ended", {
  j <- dplyr::left_join(proms, cohort[, c("case_id", "followup_years")], by = "case_id")
  seen <- !is.na(j$visit_days)
  expect_true(all(j$visit_days[seen] <= j$followup_years[seen] * 365.25 + 4))
})

test_that("a missed visit has every measure missing", {
  missed <- is.na(proms$prom_score)
  expect_true(all(is.na(proms$visit_days[missed])))
  expect_true(all(is.na(proms$vr12_pcs[missed])))
  expect_true(all(is.na(proms$walking_aid[missed])))
})

test_that("visit missingness rises from about 10% to about 25%", {
  miss <- tapply(is.na(proms$prom_score), proms$visit, mean)
  expect_lt(miss[["preop"]], 0.06)
  expect_gt(miss[["6wk"]], 0.05)
  expect_lt(miss[["6wk"]], 0.15)
  expect_gt(miss[["1yr"]], 0.18)
  expect_lt(miss[["1yr"]], 0.32)
})

test_that("1-year PROMs show a ceiling effect", {
  yr1 <- proms$prom_score[proms$visit == "1yr"]
  expect_gte(mean(yr1 == 100, na.rm = TRUE), 0.15)
})

test_that("PROMs improve from pre-op to 1 year", {
  w <- wide("prom_score")
  expect_lt(stats::t.test(w$`1yr`, w$preop, paired = TRUE)$p.value, 0.001)
})

test_that("walking-aid use changes from pre-op to 6 weeks (McNemar)", {
  w <- wide("walking_aid")
  w <- w[!is.na(w$preop) & !is.na(w$`6wk`), ]
  expect_lt(stats::mcnemar.test(table(w$preop, w$`6wk`))$p.value, 0.05)
})

test_that("satisfaction tracks PROM improvement", {
  w <- wide("prom_score")
  at <- match(cohort$case_id, w$case_id)
  gain <- w$`1yr`[at] - w$preop[at]
  rho <- stats::cor(cohort$satisfaction_1yr, gain, method = "spearman",
                    use = "complete.obs")
  expect_gt(rho, 0.3)
})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "data-proms")'`
Expected: error `'.../data/proms_long.csv' does not exist`.

- [ ] **Step 3: Write the generator and wire it in**

`data-raw/R/gen_proms.R`:

```r
# PROMs in long format: one row per case x visit (preop, 6wk, 3mo, 1yr).
# A missed visit keeps its row with every measure NA, so "expected but not
# completed" stays visible. No visit is recorded after follow-up ended.

make_proms_long <- function(cohort, seed = 20261008) {
  set.seed(seed)
  visits <- tibble::tibble(
    visit     = c("preop", "6wk", "3mo", "1yr"),
    nominal   = c(-14L, 42L, 90L, 365L),
    jitter    = c(13L, 7L, 14L, 30L),
    p_missing = c(0.03, 0.10, 0.15, 0.16),
    gain_tha  = c(0, 22, 34, 44),
    gain_tka  = c(0, 12, 24, 34),
    rec_frac  = c(0, 0.5, 0.8, 1),
    pcs_gain  = c(0, 4, 10, 14),
    aid_prob  = c(0.35, 0.60, 0.25, 0.10)
  )
  n <- nrow(cohort)
  case_base <- tibble::tibble(
    case_id    = cohort$case_id,
    patient_id = cohort$patient_id,
    procedure  = cohort$procedure,
    age        = cohort$age,
    recovery   = cohort$.recovery,
    fu_days    = cohort$followup_years * 365.25,
    pre_mean   = ifelse(cohort$procedure == "THA", 46, 50) - 0.15 * (cohort$bmi - 30),
    pre_dev    = stats::rnorm(n, 0, 12)
  )

  grid <- tidyr::expand_grid(case_base, visits)
  m <- nrow(grid)
  is_pre <- grid$visit == "preop"
  gain <- ifelse(grid$procedure == "THA", grid$gain_tha, grid$gain_tka)

  score <- ifelse(
    is_pre,
    grid$pre_mean + grid$pre_dev,
    grid$pre_mean + gain + 0.5 * grid$pre_dev +
      10 * grid$recovery * grid$rec_frac + stats::rnorm(m, 0, 8))
  pcs <- 31 + grid$pcs_gain + 0.15 * (score - grid$pre_mean - gain) + stats::rnorm(m, 0, 6)
  mcs <- 50 + c(preop = 0, `6wk` = 1, `3mo` = 2, `1yr` = 3)[grid$visit] +
    stats::rnorm(m, 0, 9)
  aid <- stats::rbinom(m, 1, stats::plogis(
    stats::qlogis(grid$aid_prob) + 0.05 * (grid$age - 66) -
      0.3 * grid$recovery * (!is_pre)))
  visit_days <- grid$nominal + sample(-1:1, m, TRUE) *
    as.integer(round(stats::runif(m, 0, grid$jitter)))

  missed <- stats::runif(m) < grid$p_missing | visit_days > grid$fu_days

  out <- tibble::tibble(
    case_id     = grid$case_id,
    patient_id  = grid$patient_id,
    visit       = grid$visit,
    visit_days  = as.integer(visit_days),
    instrument  = ifelse(grid$procedure == "THA", "HOOS JR", "KOOS JR"),
    prom_score  = round(clamp(score, 0, 100), 1),
    vr12_pcs    = round(clamp(pcs, 0, 100), 1),
    vr12_mcs    = round(clamp(mcs, 0, 100), 1),
    walking_aid = as.integer(aid)
  )
  measures <- c("visit_days", "prom_score", "vr12_pcs", "vr12_mcs", "walking_aid")
  out[missed, measures] <- NA
  out
}
```

`data-raw/generate.R`: replace the body below the `dir.create` lines with:

```r
cohort <- make_cohort()
proms  <- make_proms_long(cohort)

write_tidy(cohort, "data/cohort.csv")
write_tidy(proms,  "data/proms_long.csv")

write_codebooks(codebooks()[c("cohort", "proms_long")], "data/codebooks")
message("Synthetic data written to data/")
```

- [ ] **Step 4: Generate and run the tests**

Run:

```bash
Rscript data-raw/generate.R
Rscript -e 'cat(nrow(read.csv("data/proms_long.csv")), "\n")'
Rscript data-raw/validate.R
uv run pytest tests/python/test_data_files.py -q
```

Expected:
- `2416`
- R: `FAIL 0`
- Python: `5 passed` (two codebooks × two parametrized tests, plus the dates test)

- [ ] **Step 5: Commit**

```bash
git add data-raw/R/gen_proms.R data-raw/generate.R data/proms_long.csv data/codebooks/proms_long.csv tests/testthat/test-data-proms.R
git commit -m "Generate PROMs (HOOS JR/KOOS JR, VR-12, walking aid) in long format

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Matched implant triplets

**Files:**
- Create: `data-raw/R/gen_matched.R`
- Modify: `data-raw/generate.R`
- Create (generated): `data/matched_sets.csv`, `data/codebooks/matched_sets.csv`
- Test: `tests/testthat/test-data-matched.R`

**Interfaces:**
- Consumes: `make_cohort()` output.
- Produces: `make_matched_sets(cohort)`. It is deterministic (no seed) and returns `set_id, case_id, procedure, implant, age, sex, bmi, asa, followup_years, event_status`.

- [ ] **Step 1: Write the failing test**

`tests/testthat/test-data-matched.R`:

```r
cohort  <- read_tidy("cohort.csv")
matched <- read_tidy("matched_sets.csv")

test_that("matched sets are true triplets of distinct patients", {
  expect_equal(anyDuplicated(matched$case_id), 0)
  expect_true(all(matched$case_id %in% cohort$case_id))
  s <- matched |>
    dplyr::mutate(patient_id = cohort$patient_id[match(case_id, cohort$case_id)]) |>
    dplyr::group_by(set_id) |>
    dplyr::summarise(n = dplyr::n(), imps = paste(sort(implant), collapse = ""),
                     procs = dplyr::n_distinct(procedure), sexes = dplyr::n_distinct(sex),
                     asas = dplyr::n_distinct(asa), age_rng = diff(range(age)),
                     bmi_rng = diff(range(bmi)), pats = dplyr::n_distinct(patient_id))
  expect_gte(nrow(s), 40)
  expect_true(all(s$n == 3 & s$imps == "ABC" & s$procs == 1 & s$sexes == 1 & s$asas == 1))
  expect_true(all(s$age_rng <= 6 & s$bmi_rng <= 6 & s$pats == 3))
})

test_that("matched rows copy their values from the cohort", {
  j <- dplyr::left_join(matched, cohort, by = "case_id", suffix = c("", "_cohort"))
  for (col in c("procedure", "implant", "age", "sex", "bmi", "asa",
                "followup_years", "event_status")) {
    expect_equal(j[[col]], j[[paste0(col, "_cohort")]], label = col)
  }
})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "data-matched")'`
Expected: error `'.../data/matched_sets.csv' does not exist`.

- [ ] **Step 3: Write the generator and wire it in**

`data-raw/R/gen_matched.R`:

```r
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
```

`data-raw/generate.R`: replace the body below the `dir.create` lines with:

```r
cohort  <- make_cohort()
proms   <- make_proms_long(cohort)
matched <- make_matched_sets(cohort)

write_tidy(cohort,  "data/cohort.csv")
write_tidy(proms,   "data/proms_long.csv")
write_tidy(matched, "data/matched_sets.csv")

write_codebooks(codebooks()[c("cohort", "proms_long", "matched_sets")], "data/codebooks")
message("Synthetic data written to data/")
```

- [ ] **Step 4: Generate and run the tests**

Run:

```bash
Rscript data-raw/generate.R
Rscript -e 'd <- read.csv("data/matched_sets.csv"); cat(nrow(d), length(unique(d$set_id)), "\n")'
Rscript data-raw/validate.R
```

Expected:
- `177 59`
- R: `FAIL 0`

- [ ] **Step 5: Commit**

```bash
git add data-raw/R/gen_matched.R data-raw/generate.R data/matched_sets.csv data/codebooks/matched_sets.csv tests/testthat/test-data-matched.R
git commit -m "Generate matched implant triplets for stratified Cox examples

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Radiographic reliability readings

**Files:**
- Create: `data-raw/R/gen_reliability.R`
- Modify: `data-raw/generate.R`
- Create (generated): `data/radiographic_reliability.csv`, `data/codebooks/radiographic_reliability.csv`
- Test: `tests/testthat/test-data-reliability.R`

**Interfaces:**
- Produces:
  - `cpak_class(mpta, ldfa)`, which returns `"I"`–`"IX"`
  - `make_reliability(seed = 20261018, n_knees = 60)`, which returns `knee_id, rater, session, hka_deg, mpta_deg, ldfa_deg, cpak_class`

- [ ] **Step 1: Write the failing test**

`tests/testthat/test-data-reliability.R`:

```r
rel <- read_tidy("radiographic_reliability.csv")
session1 <- rel[rel$session == 1, ]

test_that("one row per knee x rater x session, 60 knees", {
  expect_equal(nrow(dplyr::distinct(rel, knee_id, rater, session)), nrow(rel))
  expect_equal(dplyr::n_distinct(rel$knee_id), 60)
  expect_equal(nrow(rel), 60 * 2 * 2)
})

test_that("CPAK class follows from each reading's own MPTA and LDFA", {
  ahka <- rel$mpta_deg - rel$ldfa_deg
  jlo  <- rel$mpta_deg + rel$ldfa_deg
  col <- ifelse(ahka < -2, 1L, ifelse(ahka > 2, 3L, 2L))
  row <- ifelse(jlo < 177, 0L, ifelse(jlo > 183, 2L, 1L))
  expect_equal(rel$cpak_class, as.character(utils::as.roman(row * 3L + col)))
})

test_that("raters agree well on HKA, with a small systematic bias", {
  hka <- tidyr::pivot_wider(session1[, c("knee_id", "rater", "hka_deg")],
                            names_from = rater, values_from = hka_deg)
  icc <- irr::icc(hka[, c("R1", "R2")], model = "twoway", type = "agreement",
                  unit = "single")$value
  expect_gt(icc, 0.80)
  expect_lt(icc, 0.95)
  bias <- mean(hka$R2 - hka$R1)
  expect_gt(bias, 0.3)
  expect_lt(bias, 0.7)
})

test_that("CPAK classification agreement is moderate to substantial", {
  cpak <- tidyr::pivot_wider(session1[, c("knee_id", "rater", "cpak_class")],
                             names_from = rater, values_from = cpak_class)
  k <- irr::kappa2(cpak[, c("R1", "R2")])$value
  expect_gt(k, 0.5)
  expect_lt(k, 0.85)
})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "data-reliability")'`
Expected: error `'.../data/radiographic_reliability.csv' does not exist`.

- [ ] **Step 3: Write the generator and wire it in**

`data-raw/R/gen_reliability.R`:

```r
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
```

`data-raw/generate.R`: replace the body below the `dir.create` lines with:

```r
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
```

- [ ] **Step 4: Generate and run the tests**

Run:

```bash
Rscript data-raw/generate.R
Rscript data-raw/validate.R
uv run pytest tests/python/test_data_files.py -q
```

Expected:
- R: `FAIL 0`
- Python: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add data-raw/R/gen_reliability.R data-raw/generate.R data/radiographic_reliability.csv data/codebooks/radiographic_reliability.csv tests/testthat/test-data-reliability.R
git commit -m "Generate two-rater, two-session radiographic reliability readings

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Messy abstraction workbook and its answer key

**Files:**
- Create: `data-raw/R/gen_messy_workbook.R`
- Modify: `data-raw/generate.R`
- Create (generated): `data/messy_abstraction_workbook.xlsx`, `data/answer-keys/abstraction_workbook_tidy.csv`, `data/codebooks/abstraction_workbook_tidy.csv`
- Test: `tests/testthat/test-data-workbook.R`, `tests/python/test_messy_files.py`

**Interfaces:**
- Consumes: the cohort and PROMs (Tasks 1–2).
- Produces:
  - `make_abstraction_truth(cohort, proms, seed = 20261011)`. It returns 120 rows (60 per site) with `.name, .mrn, case_id, site, surgery_date, age, sex, bmi, asa, diabetes, hypertension, sleep_apnea, procedure, side, los_days, revised, prom_preop_date, prom_preop, prom_1yr_date, prom_1yr`. `write_tidy` drops `.name` and `.mrn`.
  - `write_messy_workbook(truth, path, seed = 20261012)`, which writes sheets `Site A` and `Site B`. Site B has the extra `MUA` column and a `"Study ID "` header with a trailing space.
  - Helpers `missing_code`, `fmt_date_text`, `cell_date`, `cell_number`, `render_sheet_values` and `write_one_sheet`.
  - The answer key used by page 1's tidying lesson (Phase 2).

- [ ] **Step 1: Write the failing tests**

`tests/testthat/test-data-workbook.R`:

```r
wb_path <- data_path("messy_abstraction_workbook.xlsx")
key <- read_tidy("answer-keys/abstraction_workbook_tidy.csv")

raw_sheet <- function(sheet) {
  readxl::read_excel(wb_path, sheet = sheet, col_names = FALSE, col_types = "text",
                     .name_repair = "minimal")
}

test_that("two site tabs whose columns do not line up", {
  expect_equal(readxl::excel_sheets(wb_path), c("Site A", "Site B"))
  a <- raw_sheet("Site A")
  b <- raw_sheet("Site B")
  expect_equal(ncol(b), ncol(a) + 1)
  expect_true("MUA" %in% unlist(b[4, ]))
  expect_false("MUA" %in% unlist(a[4, ]))
})

test_that("each tab holds its answer-key cases, two duplicates, and a totals row", {
  for (s in c("Site A", "Site B")) {
    raw <- raw_sheet(s)
    ids <- trimws(raw[[3]][-(1:4)])
    case_ids <- ids[!is.na(ids) & grepl("^C\\d{4}$", ids)]
    expect_setequal(unique(case_ids), key$case_id[key$site == s])
    expect_equal(sum(duplicated(case_ids)), 2)
    expect_equal(raw[[1]][nrow(raw)], "TOTAL")
  }
})

test_that("names and MRNs in the workbook are obviously fake", {
  for (s in c("Site A", "Site B")) {
    body <- raw_sheet(s)[-(1:4), ]
    body <- body[!is.na(body[[1]]) & body[[1]] != "TOTAL", ]
    expect_true(all(grepl("^TESTPATIENT, ", body[[1]])))
    expect_true(all(grepl("^SYN-\\d{6}$", body[[2]])))
  }
})

test_that("the answer key matches the cohort and carries no names or MRNs", {
  cohort <- read_tidy("cohort.csv")
  expect_equal(nrow(key), 120)
  expect_true(all(key$case_id %in% cohort$case_id))
  expect_false(any(grepl("TESTPATIENT|SYN-", unlist(key))))
  j <- dplyr::left_join(key, cohort, by = "case_id", suffix = c("", "_cohort"))
  for (col in c("site", "surgery_date", "age", "sex", "procedure", "side", "revised")) {
    expect_equal(j[[col]], j[[paste0(col, "_cohort")]], label = col)
  }
})
```

`tests/python/test_messy_files.py` (workbook part; Task 6 appends the survey test):

```python
"""Python-side checks on the messy files: they open in pandas and openpyxl, the
color-coded revisions are visible to Python, and the reshape lesson's answer
key is reachable in Python as well as R."""

from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
WORKBOOK = DATA / "messy_abstraction_workbook.xlsx"
KEYS = DATA / "answer-keys"


def test_workbook_opens_and_red_fill_marks_exactly_the_revisions():
    wb = openpyxl.load_workbook(WORKBOOK)
    key = pd.read_csv(KEYS / "abstraction_workbook_tidy.csv")
    red = set()
    for ws in wb.worksheets:
        header = [str(c.value).strip() if c.value is not None else None for c in ws[4]]
        col = header.index("Study ID") + 1
        for row in range(5, ws.max_row + 1):
            cell = ws.cell(row=row, column=col)
            if cell.fill.fgColor.rgb == "FFFF9999":
                red.add(cell.value)
    assert red == set(key.loc[key["revised"] == 1, "case_id"])


def test_workbook_reads_in_pandas():
    sheets = pd.read_excel(WORKBOOK, sheet_name=None, header=None, dtype=str)
    assert list(sheets) == ["Site A", "Site B"]
    assert sheets["Site B"].shape[1] == sheets["Site A"].shape[1] + 1
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "data-workbook")'
uv run pytest tests/python/test_messy_files.py -q
```

Expected:
- R: error, the workbook path does not exist
- Python: `2 failed` (`FileNotFoundError`)

- [ ] **Step 3: Write the generator and wire it in**

`data-raw/R/gen_messy_workbook.R`:

```r
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
  ifelse(style == "mdy",
         sprintf("%d/%d/%s", as.integer(format(d, "%m")), as.integer(format(d, "%d")),
                 format(d, "%y")),
         ifelse(style == "iso", format(d, "%Y-%m-%d"),
                gsub(" +", " ", format(d, "%B %e %Y"))))
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
  rev_year <- format(t$surgery_date + round(stats::runif(n, 30, 1500)), "%Y")
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
```

`data-raw/generate.R`: replace the body below the `dir.create` lines with:

```r
cohort  <- make_cohort()
proms   <- make_proms_long(cohort)
matched <- make_matched_sets(cohort)
rel     <- make_reliability()
truth   <- make_abstraction_truth(cohort, proms)

write_tidy(cohort,  "data/cohort.csv")
write_tidy(proms,   "data/proms_long.csv")
write_tidy(matched, "data/matched_sets.csv")
write_tidy(rel,     "data/radiographic_reliability.csv")

write_messy_workbook(truth, "data/messy_abstraction_workbook.xlsx")
write_tidy(truth, "data/answer-keys/abstraction_workbook_tidy.csv")

write_codebooks(codebooks()[c("cohort", "proms_long", "matched_sets",
                              "radiographic_reliability",
                              "abstraction_workbook_tidy")], "data/codebooks")
message("Synthetic data written to data/")
```

- [ ] **Step 4: Generate, look at it, and run the tests**

Run:

```bash
Rscript data-raw/generate.R
uv run python -c "
import openpyxl
ws = openpyxl.load_workbook('data/messy_abstraction_workbook.xlsx')['Site B']
for row in ws.iter_rows(min_row=1, max_row=6, values_only=True):
    print(row)
print(sorted(str(m) for m in ws.merged_cells.ranges))"
Rscript data-raw/validate.R
uv run pytest tests/python -q
```

Expected:
- The workbook printout shows:
  - a banner row containing `SYNTHETIC DATA - NOT REAL PATIENTS`
  - a group-header row (`Patient`, `Surgery`, `Pre-op PROM`, `1-yr PROM`)
  - a header row that includes `'Study ID '` and `'MUA'`
  - merged ranges `A1:Q1`, `A2:Q2`, `A3:C3`, `D3:L3`, `M3:N3`, `O3:P3`
- R: `FAIL 0`
- Python: all pass

- [ ] **Step 5: Commit**

```bash
git add data-raw/R/gen_messy_workbook.R data-raw/generate.R data/messy_abstraction_workbook.xlsx data/answer-keys/abstraction_workbook_tidy.csv data/codebooks/abstraction_workbook_tidy.csv tests/testthat/test-data-workbook.R tests/python/test_messy_files.py
git commit -m "Generate messy two-site abstraction workbook with exact answer key

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Messy survey export and its answer key

**Files:**
- Create: `data-raw/R/gen_survey.R`
- Modify: `data-raw/generate.R`, `tests/python/test_messy_files.py` (append)
- Create (generated): `data/messy_survey_export.csv`, `data/answer-keys/survey_items_long.csv`, `data/codebooks/survey_items_long.csv`
- Test: `tests/testthat/test-data-survey.R`, and the appended Python test

**Interfaces:**
- Consumes: the cohort and PROMs.
- Produces:
  - `survey_visits` and `survey_items` (KOOS JR 7 items, HOOS JR 6)
  - `make_survey_items(cohort, proms, seed = 20261013)`, which returns `case_id, instrument, visit, item, response`
  - `survey_column_name(instrument, item, visit)`
  - `write_messy_survey(items, path, seed = 20261014)`

- [ ] **Step 1: Write the failing tests**

`tests/testthat/test-data-survey.R`:

```r
test_that("the survey export has a metadata row and reshapes exactly to its answer key", {
  path <- data_path("messy_survey_export.csv")
  lines <- readLines(path, n = 2)
  expect_match(lines[2], "^Response ID,Study ID,Instrument,")
  wide <- readr::read_csv(path, skip = 2, col_names = strsplit(lines[1], ",")[[1]],
                          col_types = readr::cols(.default = "c"))
  expect_equal(nrow(wide), 150)
  long <- wide |>
    tidyr::pivot_longer(-c(ResponseId, case_id, instrument),
                        names_to = c("inst", "item", "visit"),
                        names_pattern = "(KOOS|HOOS)_Q(\\d)_(.*)",
                        values_to = "response") |>
    dplyr::filter(substr(instrument, 1, 4) == inst) |>
    dplyr::mutate(item = as.integer(item), response = as.integer(response),
                  visit_order = match(visit, c("preop", "6wk", "3mo", "1yr"))) |>
    dplyr::arrange(case_id, visit_order, item) |>
    dplyr::select(case_id, instrument, visit, item, response)
  expected <- read_tidy("answer-keys/survey_items_long.csv")
  expect_equal(as.data.frame(long), as.data.frame(expected), ignore_attr = TRUE)
})
```

Append to `tests/python/test_messy_files.py`:

```python


def test_survey_export_reshapes_to_answer_key():
    visit_order = {"preop": 0, "6wk": 1, "3mo": 2, "1yr": 3}
    wide = pd.read_csv(DATA / "messy_survey_export.csv", skiprows=[1], dtype=str)
    long = wide.melt(
        id_vars=["ResponseId", "case_id", "instrument"],
        var_name="column",
        value_name="response",
    )
    parts = long["column"].str.extract(r"(?P<inst>KOOS|HOOS)_Q(?P<item>\d)_(?P<visit>.+)")
    long = pd.concat([long, parts], axis=1)
    long = long[long["instrument"].str[:4] == long["inst"]]
    long = long.assign(
        item=long["item"].astype(int),
        response=pd.to_numeric(long["response"]),
        order=long["visit"].map(visit_order),
    ).sort_values(["case_id", "order", "item"])
    got = long[["case_id", "instrument", "visit", "item", "response"]].reset_index(drop=True)
    expected = pd.read_csv(KEYS / "survey_items_long.csv")
    pd.testing.assert_frame_equal(got, expected, check_dtype=False)
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", filter = "data-survey")'
uv run pytest tests/python/test_messy_files.py -q
```

Expected:
- R: error, `messy_survey_export.csv` does not exist
- Python: `1 failed, 2 passed`

- [ ] **Step 3: Write the generator and wire it in**

`data-raw/R/gen_survey.R`:

```r
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
```

`data-raw/generate.R`: replace the whole file with the final version:

```r
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
message("Synthetic data written to data/")
```

- [ ] **Step 4: Generate and run the tests**

Run:

```bash
Rscript data-raw/generate.R
wc -l data/messy_survey_export.csv data/answer-keys/survey_items_long.csv
Rscript data-raw/validate.R
uv run pytest tests/python -q
```

Expected:
- `152 data/messy_survey_export.csv` and `3957 data/answer-keys/survey_items_long.csv` (3,956 rows plus the header)
- R: `FAIL 0`
- Python: all pass

- [ ] **Step 5: Commit**

```bash
git add data-raw/R/gen_survey.R data-raw/generate.R data/messy_survey_export.csv data/answer-keys/survey_items_long.csv data/codebooks/survey_items_long.csv tests/testthat/test-data-survey.R tests/python/test_messy_files.py
git commit -m "Generate wide KOOS JR/HOOS JR survey export with long answer key

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Data-collection template

**Files:**
- Create: `data-raw/make_template.R`
- Create (generated): `templates/data-collection-template.xlsx`
- Test: `tests/python/test_template.py`

**Interfaces:**
- Produces: `templates/data-collection-template.xlsx` with sheets `README, data, dictionary, missing_codes`. Every `data` column except `study_id` has dropdown or range validation. Page 1 of Phase 2 teaches with it.

- [ ] **Step 1: Write the failing test**

`tests/python/test_template.py`:

```python
"""The data-collection template validates every field except the study ID."""

from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]


def test_template_validates_every_field_but_the_id():
    wb = openpyxl.load_workbook(ROOT / "templates" / "data-collection-template.xlsx")
    assert wb.sheetnames == ["README", "data", "dictionary", "missing_codes"]
    ws = wb["data"]
    header = {c.column_letter: c.value for c in ws[1]}
    rules = {}
    for dv in ws.data_validations.dataValidation:
        letter = str(dv.sqref).split(":")[0].rstrip("0123456789")
        rules[header[letter]] = dv
    assert set(rules) == set(header.values()) - {"study_id"}
    assert rules["sex"].type == "list"
    assert rules["sex"].formula1 == '"Female,Male,Not recorded"'
    assert (rules["bmi"].type, rules["bmi"].formula1, rules["bmi"].formula2) == ("decimal", "10", "80")
    assert rules["surgery_date"].type == "date"


def test_template_has_no_patient_identifier_columns():
    wb = openpyxl.load_workbook(ROOT / "templates" / "data-collection-template.xlsx")
    header = [c.value.lower() for c in wb["data"][1]]
    for banned in ["name", "mrn", "dob", "birth"]:
        assert not any(banned in h for h in header), banned
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/python/test_template.py -q`
Expected: `2 failed` (`FileNotFoundError`).

- [ ] **Step 3: Write the template builder**

`data-raw/make_template.R`:

```r
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
```

- [ ] **Step 4: Build and run the tests**

Run:

```bash
Rscript data-raw/make_template.R
uv run pytest tests/python/test_template.py -q
```

Expected:
- `Wrote templates/data-collection-template.xlsx`
- `2 passed`

- [ ] **Step 5: Commit**

```bash
git add data-raw/make_template.R templates/data-collection-template.xlsx tests/python/test_template.py
git commit -m "Add data-collection template with dropdown and range validation

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Reproducibility, privacy, docs, and wiring

**Files:**
- Create: `tests/testthat/test-data-reproducible.R`, `tests/testthat/test-data-privacy.R`, `data/README.md`
- Modify:
  - `tests/testthat/test-data-codebooks.R` (append)
  - `Justfile` (add `data`)
  - `.github/workflows/checks.yml` (run every Python test)
  - `getting-started/check_setup.R` and `getting-started/check_setup.py` (data check)
  - `getting-started/setup.qmd` (no-clone section)
  - `tests/site/test_getting_started.py` (append)
  - `CLAUDE.md` (data rule)

**Interfaces:**
- Consumes: every generator above.
- Produces:
  - `just data`
  - a CI step that runs the Python data tests
  - setup checks that also confirm `data/cohort.csv` is readable

- [ ] **Step 1: Write the failing tests**

`tests/testthat/test-data-reproducible.R`:

```r
# The committed CSVs must be exactly what the generator produces: no hand
# edits, and the seeds really do fix the output. (The .xlsx files embed
# timestamps, so they are checked by content tests instead.)

test_that("regenerating reproduces every committed CSV byte for byte", {
  gen_dir <- testthat::test_path("..", "..", "data-raw", "R")
  env <- new.env()
  for (f in list.files(gen_dir, pattern = "[.]R$", full.names = TRUE)) sys.source(f, envir = env)

  cohort <- env$make_cohort()
  proms  <- env$make_proms_long(cohort)
  items  <- env$make_survey_items(cohort, proms)
  fresh <- list(
    "cohort.csv"                                = cohort,
    "proms_long.csv"                            = proms,
    "matched_sets.csv"                          = env$make_matched_sets(cohort),
    "radiographic_reliability.csv"              = env$make_reliability(),
    "answer-keys/abstraction_workbook_tidy.csv" = env$make_abstraction_truth(cohort, proms),
    "answer-keys/survey_items_long.csv"         = items
  )
  out <- withr::local_tempdir()
  for (name in names(fresh)) {
    path <- file.path(out, basename(name))
    env$write_tidy(fresh[[name]], path)
    expect_identical(readLines(path), readLines(data_path(name)), label = name)
  }
  survey <- file.path(out, "messy_survey_export.csv")
  env$write_messy_survey(items, survey)
  expect_identical(readLines(survey), readLines(data_path("messy_survey_export.csv")),
                   label = "messy_survey_export.csv")

  books <- file.path(out, "codebooks")
  dir.create(books)
  env$write_codebooks(env$codebooks(), books)
  for (f in list.files(books)) {
    expect_identical(readLines(file.path(books, f)), readLines(data_path("codebooks", f)),
                     label = paste("codebook", f))
  }
})
```

`tests/testthat/test-data-privacy.R`:

```r
test_that("no real-looking identifiers in any CSV", {
  files <- list.files(data_path(), pattern = "[.]csv$", recursive = TRUE, full.names = TRUE)
  expect_gt(length(files), 0)
  txt <- unlist(lapply(files, readLines))
  expect_false(any(grepl("\\b\\d{3}-\\d{2}-\\d{4}\\b", txt)))  # SSN-shaped
  expect_false(any(grepl("@", txt, fixed = TRUE)))             # e-mail addresses
  expect_false(any(grepl("\\b\\d{7,}\\b", txt)))               # MRN-shaped digit runs
})
```

Append to `tests/testthat/test-data-codebooks.R`:

```r

test_that("each tidy dataset and answer key has a codebook", {
  expect_setequal(books, c("cohort.csv", "proms_long.csv", "matched_sets.csv",
                           "radiographic_reliability.csv",
                           "abstraction_workbook_tidy.csv", "survey_items_long.csv"))
})
```

Append to `tests/site/test_getting_started.py`:

```python


def test_setup_page_shows_how_to_read_data_without_cloning(site):
    text = load("getting-started/setup.html").get_text()
    url = ("https://raw.githubusercontent.com/Total-Joint-Specialists/"
           "example-stats-analysis/main/data/cohort.csv")
    assert url in text
```

- [ ] **Step 2: Run them**

Run:

```bash
Rscript data-raw/validate.R
quarto render getting-started/setup.qmd && uv run pytest tests/site/test_getting_started.py -q
```

Expected:
- R: the reproducibility, privacy and codebook-completeness tests **pass already**. The generator has been deterministic since Task 1, and the privacy and completeness rules held all along. These tests guard against future regressions.
- Site: `test_setup_page_shows_how_to_read_data_without_cloning` FAILS.

To prove the reproducibility test bites, append a space to the last line of `data/cohort.csv` and run `Rscript data-raw/validate.R`.
Expected: `regenerating reproduces every committed CSV byte for byte` FAILS for `cohort.csv`.

Restore the file with `git checkout data/cohort.csv`.

- [ ] **Step 3: Add the data check to both setup scripts**

In `getting-started/check_setup.R`, insert above the line starting `cat(if (ok)`:

```r
report("practice data readable (data/cohort.csv)",
       file.exists("data/cohort.csv") && nrow(utils::read.csv("data/cohort.csv")) > 0,
       "run this from the example-stats-analysis folder")
```

In `getting-started/check_setup.py`, insert above the line starting `print("\nAll good`:

```python
cohort = Path("data/cohort.csv")
report("practice data readable (data/cohort.csv)",
       cohort.exists() and len(cohort.read_text(encoding="utf-8").splitlines()) > 1,
       "run this from the example-stats-analysis folder")
```

Also add `from pathlib import Path` below `import sys` at the top of `check_setup.py`.

- [ ] **Step 4: Add the no-clone section to `getting-started/setup.qmd`**

Insert this section immediately before `## Troubleshooting`:

````markdown
## Reading the data without cloning

You can try any example without steps 5–8. Point the read function at GitHub instead of the `data/` folder:

::: {.panel-tabset group="language"}
## R

```r
cohort <- readr::read_csv("https://raw.githubusercontent.com/Total-Joint-Specialists/example-stats-analysis/main/data/cohort.csv")
```

## Python

```python
import pandas as pd

cohort = pd.read_csv("https://raw.githubusercontent.com/Total-Joint-Specialists/example-stats-analysis/main/data/cohort.csv")
```
:::

In any example, replace `"data/"` with `"https://raw.githubusercontent.com/Total-Joint-Specialists/example-stats-analysis/main/data/"`.
````

- [ ] **Step 5: Write `data/README.md`**

```markdown
# data/

**Every file here is synthetic.** The people, dates, scores and readings were
invented by `data-raw/generate.R`. None of them describe real patients.
Revision rates are deliberately higher than real-world rates, so the survival
examples have enough events.

Never edit these files by hand. Change `data-raw/` and run `just data`. A test
fails if the committed CSVs differ from what the generator produces.

## Tidy datasets (codebooks in `codebooks/`)

| File | One row per | Used for |
|------|------|------|
| `cohort.csv` | primary THA/TKA case (604 cases, 520 patients, 84 bilateral) | Table 1, most of the test catalog, regression, survival |
| `proms_long.csv` | case × visit (pre-op, 6 wk, 3 mo, 1 yr) | paired tests, repeated measures, mixed models |
| `matched_sets.csv` | case in a matched triplet (implants A, B, C) | stratified Cox |
| `radiographic_reliability.csv` | knee × rater × session | ICC, Bland-Altman, kappa |

## Messy files (for the tidy-data lesson)

| File | What's wrong with it |
|------|------|
| `messy_abstraction_workbook.xlsx` | Two site tabs whose columns don't line up, banner and totals rows, merged headers, mixed date formats, units typed into numbers, five ways to say "missing", color as data, duplicate rows |
| `messy_survey_export.csv` | One column per item per visit, plus a metadata row under the header |

## Answer keys (`answer-keys/`)

The exact tidy result each messy file should become. Try the exercises in
[Tidy data](https://total-joint-specialists.github.io/example-stats-analysis/foundations/01-tidy-data.html)
before you look.
```

- [ ] **Step 6: Add the `data` recipe, CI step, and data rule**

Append to `Justfile`:

```just

# Regenerate the synthetic data and template, then check them in both languages
data:
    Rscript data-raw/generate.R
    Rscript data-raw/make_template.R
    Rscript data-raw/validate.R
    uv run pytest tests/python -q
```

In `.github/workflows/checks.yml`, replace the step named `Repo tests (gitignore, docs)` with:

```yaml
      - name: Python tests (data files, template, setup check, repo)
        run: uv run pytest tests/python -q
```

In `CLAUDE.md`, add this as golden rule 9:

```markdown
9. **Never hand-edit `data/` or `templates/`.** Change `data-raw/` and run `just data`. Seeds are fixed (see `docs/superpowers/plans/2026-10-05-phase-1-synthetic-data.md`). Never change a seed or parameter to make a test pass.
```

- [ ] **Step 7: Run everything**

Run: `just data && just test && just check`
Expected:
- `just data` writes the data and template; R `FAIL 0`; Python all pass
- `just test`: R `FAIL 0`; Python all pass
- `just check`: site tests all pass; lychee `0 Errors`
- `git status --short data templates` prints nothing. Regenerating changed no CSV; the `.xlsx` files may show as modified because they embed a timestamp. If they do, run `git checkout data/messy_abstraction_workbook.xlsx templates/data-collection-template.xlsx`.

- [ ] **Step 8: Commit**

```bash
git add tests/testthat/test-data-reproducible.R tests/testthat/test-data-privacy.R tests/testthat/test-data-codebooks.R tests/site/test_getting_started.py data/README.md Justfile .github/workflows/checks.yml getting-started/check_setup.R getting-started/check_setup.py getting-started/setup.qmd CLAUDE.md
git commit -m "Guard data reproducibility and privacy; wire data into setup, CI, docs

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

After this task, finish the branch with superpowers:finishing-a-development-branch (PR to `main`). Merging triggers the publish workflow.
