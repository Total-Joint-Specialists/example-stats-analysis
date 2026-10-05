# data/

**Every file here is synthetic.** The people, dates, scores and readings were
invented by `data-raw/generate.R`. None of them describe real patients.
Revision rates are deliberately higher than real-world rates, so the survival
examples have enough events.

Never edit these files by hand. Change `data-raw/` and run `just data`. A test
fails if the committed CSVs differ from what the generator produces, and
`CHECKSUMS.md5` (written by the generator) lets CI catch a hand-edited CSV too.

## Tidy datasets (codebooks in `codebooks/`)

| File | One row per | Used for |
|------|------|------|
| `cohort.csv` | primary THA/TKA case (600 cases, 520 patients, 80 bilateral) | Table 1, most of the test catalog, regression, survival |
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
