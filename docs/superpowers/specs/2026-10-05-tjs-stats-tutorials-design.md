# TJS Statistics Tutorials — Design Spec

**Date:** 2026-10-05
**Status:** Approved in brainstorming; awaiting written-spec review
**Repo:** `Total-Joint-Specialists/example-stats-analysis` (public)
**Site:** `https://total-joint-specialists.github.io/example-stats-analysis/`

---

## 1. Purpose

A public tutorial website plus repository that teaches Total Joint Specialists (TJS)
research assistants how to prepare data and run the statistical analyses used in
TJS arthroplasty research, in **R, Python, or both**.

**Audience:** research assistants who are **beginners in both statistics and
coding** (pre-meds, medical students). Every concept is explained from scratch;
every code block is commented for someone who has never programmed.

**Success looks like:** an RA starting a real TJS project can

1. find their analysis on the home-page decision table (goal × data type),
2. open the worked example, understand why that test fits,
3. copy and adapt the code in their language,
4. write the Methods and Results sentences in JOA/JBJS style, and
5. prove their tidied data still agrees with what was collected.

## 2. Decisions made in brainstorming

| Topic | Decision |
|---|---|
| Audience level | Beginners in both statistics and code |
| Hosting | Public GitHub repo (the org's first) + GitHub Pages site. Org is on GitHub Free, where Pages requires a public repo |
| Data | Synthetic only. No PHI ever enters this repo |
| Languages | Single page per topic, explanation written once, **R ⟷ Python tabs** on every code block, tab choice synced site-wide |
| Exercises | 2–4 per page, solutions in collapsed callouts (R/Python tabs inside) |
| Table granularity | **One page per row** of the decision table, one section per column |
| Extras beyond the table | Post-hoc & multiplicity; effect sizes & CIs (woven into every page); mixed models for repeated PROMs; agreement & reliability |
| Survival | Dedicated part: Kaplan-Meier (incl. competing risks) and Cox regression |
| Normality teaching stance | Visual-first; formal tests as supporting evidence; normality is about within-group distributions / residuals; robustness at larger n; bounded PROMs with ceiling effects often favor rank-based methods |
| Licensing | CC BY 4.0 for prose/content; MIT for code |

## 3. Site map

```
Home (index.qmd) — the decision table, every cell a deep link

Getting started
  0.1  Install & set up                getting-started/setup.qmd
  0.2  How to use this site            getting-started/using-this-site.qmd
  0.3  Working with real TJS data      getting-started/real-data.qmd

Part 1 — Foundations
  1   Tidy data                        foundations/01-tidy-data.qmd
  2   Demographics (Table 1)           foundations/02-demographics.qmd
  3   Distributions & choosing a test  foundations/03-distributions.qmd

Part 2 — Test catalog (one page per table row)
  4   Describe one group               catalog/04-describe-one-group.qmd
  5   Compare one group to a hypothetical value
                                       catalog/05-one-group-vs-hypothetical.qmd
  6   Compare two unpaired groups      catalog/06-two-unpaired-groups.qmd
  7   Compare two paired groups        catalog/07-two-paired-groups.qmd
  8   Compare 3+ unmatched groups      catalog/08-three-plus-unmatched.qmd
  9   Compare 3+ matched groups        catalog/09-three-plus-matched.qmd
  10  Quantify association             catalog/10-association.qmd
  11  Predict from one variable        catalog/11-predict-from-one.qmd
  12  Predict from several variables   catalog/12-predict-from-several.qmd

Part 3 — Survival analysis
  13  Kaplan-Meier & the log-rank test survival/13-kaplan-meier.qmd
  14  Cox proportional hazards         survival/14-cox-regression.qmd

Part 4 — Beyond the table
  15  Post-hoc tests & multiple comparisons  beyond/15-post-hoc.qmd
  16  Mixed models for repeated PROMs        beyond/16-mixed-models.qmd
  17  Agreement & reliability                beyond/17-agreement.qmd

Part 5 — Putting it together
  18  Example study report             report/18-example-report.qmd
```

Pages not yet built appear in the navigation as stubs marked **"Coming soon"**.

### 3.1 Home page: the decision table

The supplied table is rebuilt as an HTML table. Each non-empty cell links to its
section anchor on the row page. Changes from the supplied image:

- Credited to its original source: Harvey Motulsky, *Intuitive Biostatistics*
  (Oxford University Press) / GraphPad Statistics Guide. The orthoteers.co.uk
  link is not cited.
- "Cochrane Q" is corrected to **Cochran's Q**.
- The asterisks are dropped. In the original they meant "not covered in this
  book", which no longer applies.
- A second, smaller table, **"Beyond the table"**, links to pages 13–17.
- An intro paragraph explains how to read it: pick your **goal** (row), then
  your **data type** (column). If you are unsure which column, see page 3.

### 3.2 Cell → anchor map

| Row (page) | Gaussian | Rank / non-Gaussian | Binomial | Survival |
|---|---|---|---|---|
| 4 Describe one group | `#mean-sd` | `#median-iqr` | `#proportion` | `#kaplan-meier` |
| 5 One group vs hypothetical | `#one-sample-t` | `#wilcoxon-signed-rank` | `#chi-square-gof`, `#binomial-test` | (empty in source table) |
| 6 Two unpaired | `#unpaired-t` | `#mann-whitney` | `#fisher-chi-square` | `#log-rank` |
| 7 Two paired | `#paired-t` | `#wilcoxon-signed-rank` | `#mcnemar` | `#stratified-cox` |
| 8 3+ unmatched | `#one-way-anova` | `#kruskal-wallis` | `#chi-square` | `#cox` |
| 9 3+ matched | `#repeated-measures-anova` | `#friedman` | `#cochran-q` | `#stratified-cox` |
| 10 Association | `#pearson` | `#spearman` | `#contingency-coefficients` | (empty in source table) |
| 11 Predict from one | `#linear-regression`, `#nonlinear-regression` | `#nonparametric-regression` | `#logistic-regression` | `#cox` |
| 12 Predict from several | `#multiple-linear-regression`, `#multiple-nonlinear-regression` | (empty in source table) | `#multiple-logistic-regression` | `#cox` |

Interpretations of ambiguous cells:

- **Row 6 survival, "Log-rank or Mantel-Haenszel":** the Mantel-Haenszel
  (Mantel-Cox) test *is* the log-rank test; the page says so.
- **Rows 7 and 9 survival, "conditional proportional hazards regression":** taught
  as a Cox model stratified by matched set / patient.
- **Row 10 binomial, "contingency coefficients":** phi, Cramér's V, and
  Pearson's contingency coefficient C.
- **Row 11 ranks, "nonparametric regression":** LOESS (smoothing) and Theil-Sen
  (robust slope).
- **Row 12 Gaussian, "multiple nonlinear regression":** a multi-predictor `nls`
  model, plus restricted cubic splines as the modern default for non-linear
  continuous predictors.
- **Survival cells in rows 8, 11 and 12:** a short worked example on the row
  page, with a link to the full treatment on page 14.

## 4. Page content outlines

### 0.1 Install & set up
Positron (recommended; one editor for R and Python), R, Python via `uv`, git,
and a GitHub account with org access. Clone the repo, open it as a folder,
`renv::restore()`, `uv sync`, run a first line. Each step has screenshots or
exact commands, plus a "how to tell it worked" check. RStudio and VS Code are
covered as alternatives in a short section.

### 0.2 How to use this site
Choosing a language (the tabs remember it). Copying code. Where to do exercises
(`scratch/`, which git ignores). The site-wide **reporting conventions**:

- continuous variables: mean (SD) if roughly symmetric, median (IQR) if not
- categorical variables: n (%)
- p-values: three decimals, floor "p < 0.001", never "p = 0.000"
- 95% confidence intervals with every effect estimate
- Table 1 laid out the way JOA/JBJS expect

### 0.3 Working with real TJS data
- PHI never enters a git repo; `data/` is gitignored in project repos.
- HIPAA Safe Harbor's 18 identifiers, with the TJS-specific traps (age ≥ 90,
  dates, MRNs in file names).
- Never paste PHI into AI chatbots or websites.
- Where TJS data lives (Google Sheets / Drive) and how project repos read it.
- The "golden rules" pattern used in existing TJS repos: read everything as
  text at ingest, type columns as a logged step, map columns by name not
  position.

### 1 Tidy data
1. **What tidy means:** every variable a column, every observation a row, every
   type of observational unit its own table. Shown with TJS examples.
2. **Collecting tidy data:** designing a collection sheet and data dictionary
   before abstraction starts. Walks through `templates/data-collection-template.xlsx`
   (dropdown validation, one header row, no merged cells, no color-as-data, one
   value per cell, explicit missing codes, ISO dates).
3. **Tidying untidy data:** step by step through `messy_abstraction_workbook.xlsx`
   (combining misaligned tabs by column name, removing title and total rows,
   parsing mixed dates, stripping units, unifying missing codes, recoding sex,
   splitting the comorbidity list into indicator columns, recovering color-coded
   meaning from the notes column, de-duplicating). Then `messy_survey_export.csv`
   from wide to long.
4. **Verifying integrity:** checks that need no truth file, since real projects
   never have one: row and ID counts, ID uniqueness, per-column summaries before
   vs after, cross-tabs of every recode (old value × new value), range checks,
   and a random spot-check against the source. Then compare the result to the
   truth file (`cohort.csv`) to show the checks catch real errors. A deliberately
   introduced bug demonstrates a check failing.

### 2 Demographics (Table 1)
- One-group descriptive table.
- By-group table with p-values; why standardized mean differences (SMDs) are
  preferred over p-values for baseline balance in matched or observational
  cohorts.
- Choosing mean (SD) vs median (IQR) per variable (links to page 3).
- Reporting missing data counts.
- Exporting to Word.
- R uses `gtsummary` + `flextable`; Python uses `tableone`.

### 3 Distributions & choosing a test
- Why distribution shape matters.
- Histograms, density plots, QQ plots.
- Shapiro-Wilk and its limits: over-powered at large n, under-powered at small n.
- Check within groups / residuals, not the pooled sample.
- Robustness at about 30 or more per group.
- Skew (length of stay) and ceiling effects (1-year PROMs).
- Transformations (log) and when not to bother.
- Ordinal data (Likert satisfaction) always goes in the rank column.
- Paired vs unpaired; matched vs unmatched.
- A flowchart that lands on a cell of the home table.
- **p-values vs effect sizes and CIs:** what each tells you, so the effect-size
  steps on later pages make sense.

### 4–12 Test catalog
Each section follows the page anatomy in §6. Effect sizes per test:

| Test | Effect size reported |
|---|---|
| Unpaired t (Welch) | mean difference + 95% CI; Hedges' g |
| Mann-Whitney U | Hodges-Lehmann median difference + CI; rank-biserial r |
| Fisher / chi-square (2×2) | odds ratio + CI; risk difference + CI |
| Paired t | mean change + CI; Cohen's d_z |
| Wilcoxon signed-rank | Hodges-Lehmann pseudomedian + CI; matched-pairs rank-biserial r |
| McNemar | discordant-pair odds ratio + CI |
| One-way ANOVA | ω² |
| Kruskal-Wallis | ε² |
| Chi-square (r×c) / contingency | Cramér's V |
| Repeated-measures ANOVA | partial η² (generalized η² noted) |
| Friedman | Kendall's W |
| Cochran's Q | proportions per condition + pairwise differences |
| Pearson / Spearman | r / ρ + CI |
| Linear regression | coefficients + CI; R² |
| Logistic regression | odds ratios + CI |
| Log-rank / Cox | hazard ratio + CI |

**Page 8** and **page 9** end with a short "Which groups differ?" section that
links to page 15. **Page 9** notes that repeated-measures ANOVA drops anyone with
a missed visit, and links to page 16.

### 13 Kaplan-Meier & the log-rank test
- Censoring explained in plain language.
- Choosing time zero (surgery date).
- Event definition (all-cause revision).
- KM curve with numbers-at-risk table and CI band.
- Survivorship at 2, 5 and 10 years with CI.
- Median follow-up via reverse KM.
- Log-rank for 2 and for 3 or more groups.
- **Competing risks:** why 1 − KM overstates revision risk when patients die
  first; cumulative incidence function (Aalen-Johansen); Gray's test in R. Python
  lacks a mature Gray's test, and the page says so.

### 14 Cox proportional hazards regression
- Hazard ratio in plain language.
- Univariable → multivariable.
- Choosing covariates a priori; events-per-variable guidance.
- Checking proportional hazards: Schoenfeld residuals and plots, demonstrated on
  the built-in violation (THA approach effect on early revision).
- Remedies: stratification, time-split or time-varying effect.
- Stratified Cox for matched sets and bilateral patients.
- Fine-Gray subdistribution hazards briefly, R only, labeled as such.
- Reporting: HR table plus Methods/Results text.

### 15 Post-hoc tests & multiple comparisons
- Why running many tests inflates false positives.
- Tukey HSD after ANOVA.
- Games-Howell when variances are unequal.
- Dunn's test (Holm-adjusted) after Kruskal-Wallis.
- Pairwise chi-square / Fisher with Holm after r×c chi-square.
- Pairwise Wilcoxon / Conover after Friedman.
- Bonferroni vs Holm vs FDR (Benjamini-Hochberg) and when each fits.
- Pre-specified vs exploratory comparisons.

### 16 Mixed models for repeated PROMs
- Why repeated-measures ANOVA fails with missed visits.
- Random intercept per patient; time as categorical vs continuous.
- Group × time interaction.
- Estimated marginal means per visit with CIs (`emmeans`).
- Bilateral patients (case nested in patient) mentioned with a pointer.
- Reporting.
- R uses `lme4` + `lmerTest`; Python uses `statsmodels` MixedLM. The
  Satterthwaite degrees-of-freedom difference is noted.

### 17 Agreement & reliability
- Reliability vs agreement.
- ICC: choosing the form (two-way random, absolute agreement, single vs average
  rater) and interpretation thresholds (Koo & Li 2016).
- Inter- and intra-rater designs from the HKA data.
- Bland-Altman plot, bias and limits of agreement.
- Cohen's kappa and weighted kappa for CPAK class.
- Reporting.

### 18 Example study report
A complete mini-study on the synthetic data, written as a short manuscript:

1. Research question.
2. Tidy the raw workbook.
3. Integrity checks.
4. Table 1.
5. Distribution checks.
6. Primary analysis.
7. A survival analysis.
8. Methods and Results sections.

Rendered to HTML (on the site) and to `.docx` (downloadable). It shows what
"done" looks like.

## 5. Synthetic data

### 5.1 Principle

One generator script (`data-raw/generate.R`, fixed seed) builds the **tidy truth
first**, then derives every messy file *from* the truth. Module 1's tidying
exercise therefore has an exactly known correct answer. All outputs are committed
to `data/`. Both languages read the same files.

Every file is marked synthetic in:

- `data/README.md`
- each codebook
- a `# SYNTHETIC DATA` note on the home page

Names and MRNs in the messy files are obviously fake (e.g. `TESTPATIENT, ALPHA`,
MRN `SYN-000123`).

### 5.2 Tidy datasets

Each dataset has a codebook `data/codebooks/<name>.csv` with columns
variable, label, type, units, allowed values, and notes.

**`cohort.csv`**: one row per primary procedure. About 600 cases from about 520
patients; about 80 patients are bilateral.

- **IDs and setting:** `case_id`, `patient_id`, `site` (Site A / Site B),
  `surgeon` (S1–S3), `procedure` (THA / TKA), `side`, `surgery_date`
  (synthetic, 2016–2024)
- **Demographics:** `age`, `sex`, `bmi`, `asa` (1–4), `diabetes`,
  `hypertension`, `sleep_apnea`, `smoker` (never / former / current), `cci`
- **Perioperative:** `anesthesia` (spinal / general), `approach` (THA only:
  anterior / posterior), `implant` (A / B / C), `op_time_min`, `los_days`,
  `discharge` (home / facility)
- **Outcomes:** `readmit_90d`, `complication_90d`, `satisfaction_1yr`
  (1–5 Likert)
- **Survival:** `followup_years`, `event_status` (0 = censored,
  1 = revision, 2 = death), `revised` (0/1)

**`proms_long.csv`**: one row per case × visit (preop, 6wk, 3mo, 1yr).

- Columns: `case_id`, `patient_id`, `visit`, `visit_days`, `instrument`
  (HOOS JR / KOOS JR), `prom_score` (0–100), `vr12_pcs`, `vr12_mcs`,
  `walking_aid` (yes / no)
- Realistic missingness increasing at later visits (target about 10% at 6wk
  rising to about 25% at 1yr).

**`matched_sets.csv`**: one row per case in a matched triplet (one case per
implant design A, B and C). Matched on age (±3 y), sex, BMI (±3) and ASA.

- Columns: `set_id`, `case_id`, `implant`, matching variables,
  `followup_years`, `event_status`
- Derived from `cohort.csv` (case IDs reference it).
- Used for stratified Cox (pairs = A vs C subset, so the implant C effect is visible; triplets = all three).

**`radiographic_reliability.csv`**: one row per knee × rater × session.

- About 60 knees, 2 raters × 2 sessions.
- Columns: `knee_id`, `rater`, `session`, `hka_deg`, `mpta_deg`, `ldfa_deg`,
  `cpak_class` (I–IX, computed from that reading's MPTA and LDFA).

### 5.3 Messy datasets

**`messy_abstraction_workbook.xlsx`**, derived from a subset of `cohort.csv`
plus PROM pre-op and 1-yr scores:

- Two tabs (`Site A`, `Site B`). `Site B` has an extra column inserted mid-sheet.
- Two title/banner rows above the header; merged header cells; a totals row at
  the bottom.
- Mixed date formats (`3/4/24`, `2024-03-04`, `March 4 2024`, Excel serials).
- Numbers stored as text with units (`32.1 kg/m2`, `BMI 31`).
- Missing values coded as `N/A`, `unk`, `-`, `999`, or blank.
- Sex coded `M` / `F` / `male` / `Female` / `f`.
- Comorbidities as a comma-separated list in one cell (`DM, HTN, OSA`).
- Revision status shown only by cell fill color, with a partially redundant
  free-text `Notes` column.
- PROMs as repeated `Date` / `Score` column pairs per visit.
- About 2% exact-duplicate rows.

**`messy_survey_export.csv`**: wide export from a survey platform.

- One column per item per visit (`KOOS_Q1_preop` … `KOOS_Q7_1yr`).
- A metadata row under the header; item-level missing values.
- The lesson is the wide → long reshape only. Its tidy target is one row per
  case × visit × item. Converting items to the 0–100 interval score is **not**
  taught here, because it depends on the published KOOS JR / HOOS JR
  conversion tables.

### 5.3a Answer keys

`data/answer-keys/` holds the generator's truth for each messy file:

- `abstraction_workbook_tidy.csv`: the subset of `cohort.csv` columns plus
  pre-op / 1-yr PROM scores that the workbook encodes
- `survey_items_long.csv`

Page 1's reference solutions are checked against these files (§8.4).

### 5.4 Built-in effects

The generator builds these effects in. `data-raw/validate.R` asserts each one
after every regeneration, and the build fails if any is missing.

| Effect | Teaches | Assertion |
|---|---|---|
| TKA BMI > THA BMI by about 1.5 | unpaired t, Table 1 | Welch p < 0.01 |
| Sex unrelated to 90-day readmission | a true null result | Fisher p > 0.2 |
| LOS right-skewed, many 0–1 days | non-normal data, rank tests | skewness > 1.5 |
| 1-yr PROM ceiling effect | rank tests, page 3 | ≥ 15% at max score |
| PROM improves pre → 1yr | paired tests, mixed models | paired p < 0.001 |
| Implant C has a higher revision hazard (built in as HR 2.5) | log-rank, Cox | HR 1.5–3.5, log-rank p < 0.05 |
| Mortality rises with age (Gompertz, 2%/yr at 66); deaths ≥ revisions in the oldest group | competing risks | 1−KM exceeds the CIF by ≥ 2 points at 10 yr |
| Posterior THA approach multiplies revision hazard ×10 in the first 6 months only | PH violation | `cox.zph` p < 0.01 for approach (km and rank transforms) |
| Raters agree well but not perfectly; rater 2 bias of about +0.5° | ICC, Bland-Altman, kappa | ICC 0.80–0.95; mean bias 0.3–0.7°; CPAK kappa 0.5–0.85 |
| Walking-aid use rises at 6 weeks, falls by 1 year | McNemar, Cochran's Q | McNemar pre-op vs 6 wk p < 0.05 |
| Satisfaction tracks PROM improvement | Spearman | ρ > 0.3 |
| Age vs op time weakly related; BMI vs op time moderately related | correlation, regression | r(BMI, op time) 0.3–0.5 |

Revision rates are inflated (about 13% overall; 1−KM 22% at 10 years) so the survival
lessons have enough events; the codebook says so. Each generator has a fixed
seed, chosen in prototyping so every assertion passes; regenerating with a
different seed is not supported. Tests also require regenerating to reproduce
the committed CSVs byte for byte.

### 5.5 Data-collection template

`templates/data-collection-template.xlsx` contains:

- a `data` sheet with one header row and data-validation dropdowns
- a `dictionary` sheet
- a `missing_codes` sheet
- a `README` sheet

It is generated by script (`data-raw/make_template.R`), so it stays consistent
with the codebook conventions.

## 6. Page anatomy

Each **test section** on pages 4–12 follows this order:

1. **The question in TJS terms.** One sentence.
2. **When to use it.** Assumptions checklist, plus "if not → alternative" links.
3. **Look at the data first.** A plot.
4. **Run it.** R ⟷ Python tabset. Comments every line or two. No clever
   one-liners. Each language block loads its own data, so it can be copied
   and run on its own.
5. **Read the output.** Printed output with every number labeled.
6. **Effect size + 95% CI.**
7. **How to report it.** A Methods sentence and a Results sentence, following
   §4 0.2 conventions.
8. **⚠️ Common mistakes.**
9. **🔀 R vs Python**, only where the defaults differ.
10. **Hidden agreement check** (not rendered; see §8).

Foundation, survival, beyond and report pages use the same building blocks
with free-form structure.

**Callouts**, used consistently:

| Callout | Purpose | Quarto type |
|---|---|---|
| 💡 In plain language | intuition, no jargon | `callout-note` |
| ⚠️ Watch out | common mistakes | `callout-warning` |
| 🔀 R vs Python | differing defaults | `callout-tip` |
| 🔍 Under the hood | math, collapsed | `callout-note`, `collapse="true"` |

**Exercises** come at the end of each page. There are 2–4, rising in difficulty:

1. Rerun the analysis on a different variable.
2. Read a scenario, choose the test, and justify the choice.
3. Write the Results sentence.

Solutions sit in `callout-tip collapse="true"`, with an R ⟷ Python tabset inside.

**Code style:**

- R: tidyverse idiom, `library()` calls at the top of the page's first R block,
  native pipe `|>`.
- Python: pandas + scipy / statsmodels / lifelines / pingouin, explicit imports
  at the top of the first Python block.
- Data paths are project-relative (`data/cohort.csv`). The setup page also
  shows the raw GitHub URL alternative for anyone who has not cloned the repo.
- Plots: ggplot2 in R, matplotlib / seaborn in Python.

## 7. Technical architecture

### 7.1 Repository layout

```
example-stats-analysis/
├── _quarto.yml               # website config; explicit render list
├── index.qmd                 # home: decision table
├── getting-started/  foundations/  catalog/  survival/  beyond/  report/
├── data/                     # committed synthetic data
│   ├── README.md
│   ├── codebooks/
│   ├── cohort.csv  proms_long.csv  matched_sets.csv  radiographic_reliability.csv
│   ├── messy_abstraction_workbook.xlsx  messy_survey_export.csv
│   └── answer-keys/
├── data-raw/                 # generate.R, validate.R, make_template.R
├── templates/                # data-collection-template.xlsx
├── R/                        # site helpers (check_agree.R)
├── tests/                    # testthat/ (R), python/ (data), site/ (built-site checks)
├── _freeze/                  # committed computed results
├── renv.lock  renv/  .Rprofile
├── pyproject.toml  uv.lock  .python-version
├── Justfile                  # maintainer commands
├── .github/workflows/        # publish.yml, checks.yml
├── scratch/                  # gitignored; RA practice space
├── docs/superpowers/         # specs and plans (excluded from site render)
├── README.md  CLAUDE.md  LICENSE (MIT)  LICENSE-CONTENT (CC BY 4.0)
```

### 7.2 Rendering

- Quarto website. **Every page with executable code declares `engine: knitr`
  in its own front matter.** Quarto ignores `engine` in `_quarto.yml` and in
  `_metadata.yml` (verified), and a Python-only page would otherwise run in
  Jupyter against the system Python. A source test enforces this.
- Python chunks run through `reticulate`
  against the project's `uv` virtualenv (`RETICULATE_PYTHON` set in
  `.Rprofile` to `.venv/bin/python`).
- `execute-dir: project`, so `data/...` paths resolve from the repo root in
  both languages. Phase 0 verifies this for reticulate Python chunks.
- `freeze: auto`. Computed output is stored in `_freeze/` and committed.
- `project.render` lists the content directories and `index.qmd` explicitly,
  so `README.md`, `CLAUDE.md`, `docs/` and `tests/` are **not** rendered into the site.
- Tabsets use `group="language"`, so the language choice persists across
  pages.
- Theme: `flatly` (light) / `darkly` (dark), matching existing TJS reports.
  Site navigation in a docked left sidebar; page table of contents on the right;
  code-copy buttons.

### 7.3 Environments

**R (`renv`):**

- **Core and data:** tidyverse, janitor, readxl, openxlsx2 (template and
  messy-file generation: merged cells, fills, validation). Not `openxlsx`:
  version 4.2.9 writes a dangling drawing reference that Python's openpyxl
  refuses to open (verified)
- **Tables and output:** gtsummary, gt, flextable, broom, broom.mixed,
  knitr, reticulate
- **Survival:** survival, ggsurvfit, tidycmprsk
- **Models and effect sizes:** lme4, lmerTest, emmeans, effectsize
- **Testing:** testthat, withr
- **Reliability and specialist tests:** irr, DescTools (Cochran's Q,
  Hodges-Lehmann), rstatix (Dunn, Games-Howell), PMCMRplus (Conover after
  Friedman)

**Python (`uv`, Python 3.12+):**

- **Core:** pandas, numpy, openpyxl
- **Statistics:** scipy, statsmodels, lifelines, pingouin, scikit-posthocs
- **Tables and plots:** tableone, matplotlib, seaborn
- **Dev only:** pytest, beautifulsoup4 (site tests)

R packages are declared in a `DESCRIPTION` file and locked with renv's
explicit snapshot. Each phase adds only the packages it uses.

**macOS prerequisite:** `renv::install()` / `renv::restore()` run a compiler
check that fails if Xcode is installed but its license is unaccepted (verified
on the maintainer's Mac). Fix once with `sudo xcodebuild -license accept`; the
setup page lists it under troubleshooting.

**Maintainer commands (`Justfile`):** `just setup` (renv restore + uv sync),
`just data` (generate + validate), `just preview`, `just render`, `just check`.
RA-facing instructions never require `just`.

### 7.4 Publishing

GitHub Action `publish.yml`, triggered on push to `main`:

- uses `quarto-dev/quarto-actions` (Quarto pinned to 1.9.37, the maintainer's
  local version) to render from `_freeze/` and publish to the `gh-pages` branch
- needs no R or Python

If a page changed without its freeze being refreshed, the Action fails
(R is not installed). That failure is the intended signal.

GitHub Pages serves from `gh-pages`.

## 8. Quality checks

1. **Render halts on error.** Quarto's default; `error: true` is never set.
2. **R ⟷ Python agreement.** After each test section, a hidden R chunk calls
   `check_agree(list(<R values>), list(<reticulate::py$... values>))`
   (`R/check_agree.R`, sourced in a hidden chunk at the top of each page;
   default `tol = 1e-6`, relative to magnitude):
   - It compares the test statistic, the p-value, and the point estimate where
     both languages compute the same quantity.
   - A mismatch, a missing value, or a non-number stops the render.
   - Where defaults differ (Welch vs Student, continuity corrections, exact vs
     asymptotic), both blocks set the method explicitly.
   - CIs computed by genuinely different methods are documented in the
     🔀 callout, not checked.
3. **Synthetic-data validation.** `data-raw/validate.R` asserts every §5.4
   effect plus structural checks: ID uniqueness, foreign keys between files,
   allowed values per codebook, and no real-looking PHI patterns.
4. **Module 1 answer key.** Page 1's reference tidying solutions must
   reproduce `data/answer-keys/` exactly (`waldo::compare` /
   `pandas.testing.assert_frame_equal`). A mismatch stops the render.
5. **Site checks.** `checks.yml` builds the site from `_freeze/` on every PR
   and push, then runs the pytest site tests (pages present, anchors present,
   tabs grouped, solutions collapsed, coming-soon marking consistent, `engine:
   knitr` declared) and lychee with fragment checking. Maintainers install
   lychee from its GitHub release binary (Homebrew needs the Xcode license).
6. **Human review.** Each page or small group of pages is merged via PR and
   reviewed by the TJS research lead before going live.
7. **Reproducible data.** Regenerating must reproduce every committed CSV
   byte for byte.

## 9. Build phases

Each phase is independently reviewable and publishable.

| Phase | Deliverables |
|---|---|
| 0 | Repo scaffold; `_quarto.yml`; renv + uv environments; reticulate wiring verified; publish + site-checks Actions; home decision table (links to stub pages); Getting Started 0.1–0.3; README, CLAUDE.md, licenses; GitHub repo created + Pages enabled (**confirm with owner before creating the public repo and enabling Pages**) |
| 1 | `data-raw/generate.R`, `validate.R`, `make_template.R`; all datasets, codebooks, and the collection template |
| 2 | Pages 1–3 |
| 3 | Pages 4–12 |
| 4 | Pages 13–14 |
| 5 | Pages 15–17 |
| 6 | Page 18 |

Each phase gets its own implementation plan. Phases 0 and 1 are planned first.

## 10. Out of scope (candidates for later)

- Sample size / power analysis
- Propensity-score matching *methods* (the matched file arrives pre-matched)
- Multiple imputation (missingness is reported, not imputed)
- Bayesian methods, machine learning, meta-analysis
- REDCap-specific workflows
- A reusable template repo for new TJS projects
- Ordinal (proportional-odds) regression for Likert outcomes

## 11. Risks

| Risk | Mitigation |
|---|---|
| reticulate + knitr working-directory or plotting quirks for Python chunks | Verified in Phase 0 with a smoke-test page before any content is written |
| A Python library lacks an equivalent method | State it on the page and show R; never hand-roll untested statistics |
| Synthetic data regenerated and lessons silently change | `validate.R` assertions + R ⟷ Python checks + frozen outputs reviewed in PR diffs |
| An RA commits real data to this public repo | `.gitignore` covers `scratch/`; page 0.3 and the README state the rule; this repo holds only `data/` synthetic files |
| Package updates change numeric output | `renv.lock` / `uv.lock` pin versions; freeze isolates the published site |
