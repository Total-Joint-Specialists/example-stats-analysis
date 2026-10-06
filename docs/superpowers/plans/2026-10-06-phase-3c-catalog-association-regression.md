# Phase 3c: Test Catalog, Association and Regression (Pages 10–12) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the last three catalog stubs with finished pages, one per row of the decision table:
- `catalog/10-association.qmd`: Pearson correlation, Spearman correlation and contingency coefficients
- `catalog/11-predict-from-one.qmd`: simple linear, nonlinear and nonparametric regression, simple logistic regression and Cox regression
- `catalog/12-predict-from-several.qmd`: multiple linear and nonlinear regression (with splines), multiple logistic regression and Cox regression

The plan also fixes a project-wide bug found while prototyping: Quarto ignores `execute: message: false` on knitr pages, so CLAUDE.md rule 10 never worked. It also folds in the three test-harness minors deferred from Phase 3b.

**Architecture:**
- Same structure as Phases 3a and 3b:
  - knitr-engine pages, each decision-table cell an `##` section with the spec §6 anatomy as `###` steps
  - hidden `check_agree()` R ⟷ Python checks, a `# Prose guard`, and a data-checksum stamp
  - exercise solutions that are executed chunks
- Messages are now hidden once, project-wide, through knitr's own chunk default in `_quarto.yml`. The dead `execute: message: false` lines come out of nine pages, which are re-rendered.
- Source rules:
  - read chunk options in any order
  - keep function, lambda and comprehension names inside their scope
  - ignore `set.seed(` in comments
- The two reporting tests from the Phase 3b review now cover pages 10–12 too.

**Tech Stack:**
- R: tidyverse, survival, ggsurvfit, effectsize, DescTools, splines, and deming (new, for Theil-Sen)
- Python: pandas 3, scipy (`curve_fit`, `theilslopes`), statsmodels (OLS, Logit, `lowess`, patsy's `cr()` splines), lifelines
- Quarto 1.9.37

**Spec:** `docs/superpowers/specs/2026-10-05-tjs-stats-tutorials-design.md`, especially:
- §3.2: rows 10–12 anchors and their interpretations (contingency coefficients = φ, Cramér's V, Pearson's C; nonparametric regression = LOESS and Theil-Sen; multiple nonlinear = a multi-predictor `nls` model plus restricted cubic splines; survival cells link to page 14)
- §4: effect sizes (r / ρ + CI; coefficients + CI and R²; odds ratios + CI; hazard ratios + CI)
- §6: page anatomy
- §8: quality checks

## Global Constraints

- **`engine: knitr` per page.** Every page with code declares `engine: knitr` and `toc-depth: 2` in its own front matter. Don't add `execute: message: false`: Quarto ignores it for knitr, and `_quarto.yml` now sets knitr's own `opts_chunk: message: false` for every page.
- **Tabsets:** `::: {.panel-tabset group="language"}`, with `## R` first and `## Python` second.
- **Hidden agreement checks:**
  - A hidden Python chunk sets `chk = {name: float(...)}`.
  - A hidden R chunk then calls `check_agree(list(name = <R value>), reticulate::py$chk)`.
  - Never pass DataFrames, sets or `pd.NA` through `reticulate::py`.
  - A looser `tol` always carries a comment saying why.
- **Quiet output:**
  - Chunks that call `library()` add `#| warning: false`. No page may show stderr output.
  - Call DescTools, effectsize and deming as `pkg::fun()`; don't attach them.
  - Never assign to `_` in a Python chunk.
  - Give a matplotlib return value that isn't a plot object a name (`legend = ax.legend()`, `bars = ax.bar(...)`); reticulate prints a bare tuple such as `ax.set_xlim()`'s.
- **Section anatomy (spec §6, CLAUDE.md rule 13):**
  - A `**The question:**` line comes first.
  - Then these `###` steps, in order: When to use it, Look at the data first, Run it, Read the output, Effect size and 95% CI, How to report it.
  - How to report it holds a `> **Methods:**` and a `> **Results:**` blockquote.
  - Each section has a ⚠️ box, and a 🔀 box wherever R and Python defaults differ.
  - Extra structure inside a step uses plain paragraphs, never another `###`.
- **Self-contained sections:**
  - A section's first R block calls `library()` and `read_csv("data/...")`.
  - Its first Python block imports and calls `pd.read_csv("data/...")`.
  - Every name its visible Python uses is defined within the section.
- **Prose guard:** one hidden R chunk headed `# Prose guard`, immediately before `## Exercises {#exercises}`. It `stopifnot()`s every quoted number, including the numbers in exercise solutions, and recomputes those itself because it runs before the solution chunks.
- **Data stamp:** each page has the `<!-- data-checksum: … -->` chunk.
- **Solutions:** exercise solutions are executed `{r}` / `{python}` chunks inside `::: {.callout-tip collapse="true"}` titled `Solution`, after the sentence "The solutions use the packages and data loaded in the sections above, so run the page from the top first."
- **Freeze:** render every changed page and commit its `_freeze/` directory. After a deliberately failed render, delete the leftover `catalog/<page>_files/` folder.
- **Reporting conventions:**
  - mean (SD) or median (IQR)
  - n (%)
  - p to 3 decimals, with a floor of "p < 0.001" and a ceiling of "p > 0.999"
  - a 95% CI with every estimate; one-sided effect-size CIs are labeled "one-sided"
  - a non-significant result is "imprecise" or "no clear evidence", never "similar" or "no difference"
- **Regression CIs:** R's `confint()` profiles `glm()` and `nls()` fits; pages quote it and give Python's Wald CI in the 🔀 box.
- **Branching:** work on branch `phase-3c-catalog`, in a worktree under `.worktrees/phase-3c`, created from `main`.
- **Commit trailer:** every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A message from a package reaches the page.** Before this plan, `execute: message: false` hid nothing; R's `confint()` prints "Waiting for profiling to be done..." on every profile CI. Tests:
   - `tests/site/test_sources.py::test_messages_are_hidden_by_knitr_for_every_page` (Task 2)
   - `test_catalog.py::test_page_shows_no_warnings_or_package_messages`
   - the Task 4 mutation step removes the `_quarto.yml` setting and watches page 11 fail
2. **A reader quotes R's profile CI while Python prints a Wald CI,** or the reverse. Every page that fits a `glm()` or `nls()` names both CIs in its 🔀 box, and the hidden check compares the Wald CI (`confint.default()`) with Python's. The Task 4 mutation proves that check notices a profile CI.
3. **A reader copies one section's Python, and it relies on a name made inside a lambda or comprehension elsewhere.** Test: `test_sources.py::test_rule_keeps_function_and_comprehension_names_inside_them` (Task 2), plus the existing `test_each_catalog_section_python_runs_on_its_own`.
4. **Repeated measures fitted as if independent.** The nonlinear examples use up to four scores per joint, so their CIs are too narrow. Test: `tests/site/test_catalog.py::test_curve_fits_warn_that_repeated_scores_narrow_the_cis` (Task 4). It requires each curve-fit section's ⚠️ box to say so and to link to page 16.
5. **Too many predictors for the events.** Pages 11 and 12 state the 10-events-per-predictor rule and keep to it: 51 complications for 5 predictors, 81 revisions for 5 terms, 30 facility discharges for 3. The prose guard pins every count.

## Plan rulings (made while prototyping)

- **Examples:**
  - **Pearson:** BMI and operative time (r = 0.45), the effect built into the data (spec §5.4).
  - **Spearman:** PROM improvement and 1-year satisfaction (ρ = 0.38), also built in. Satisfaction is a 1–5 rating with many ties. HOOS JR and KOOS JR are pooled, with a ⚠️ box about pooling two instruments.
  - **Contingency coefficients:** ASA class by hypertension, a 4 × 2 table with every expected count above 7.8, gives Cramér's V = 0.20 and C = 0.19. φ needs a 2 × 2 table, so exercise 3 uses sex by sleep apnea (φ = 0.18).
  - **Linear regression:** operative time on BMI.
  - **Nonlinear regression:** KOOS JR recovery, `plateau − (plateau − start) × e^(−days/τ)`. Pre-op visits (1 to 27 days before surgery) count as day 0.
  - **Nonparametric regression:** 1-year on pre-op KOOS JR. 15% of 1-year scores sit at the ceiling. The page draws a LOWESS curve and fits a Theil-Sen slope.
  - **Logistic regression:** complications on age per decade (OR 2.12).
  - **Cox regression (page 11):** revision on age per decade, HR 1.25 (0.98 to 1.59). It is the only continuous predictor of revision near significance, and the page reports it honestly as imprecise.
  - **Multiple linear regression:** operative time on BMI, age, sex and procedure.
  - **Multiple nonlinear regression:**
    - The question is whether hips recover faster than knees (τ differs by 27.5 days). τ is measured in days, so it compares across HOOS JR and KOOS JR; the start and plateau, in points, don't.
    - The spline part checks whether BMI's effect on operative time bends: F = 0.58, p = 0.562, so the straight line stands.
    - A VR-12 bend with age (p = 0.02) was found only by testing ten pairs, so it is deliberately **not** used.
  - **Multiple logistic regression:** complications on age, BMI, ASA (numeric), diabetes and sex, about 10 events per predictor.
  - **Cox regression (page 12):** implant adjusted for age, sex and BMI. The unexpected sex effect (HR 0.51) is flagged as exploratory.
- **Profile vs Wald CIs:**
  - R's visible code uses `confint()`, which profiles `glm()` and `nls()` fits. Python prints Wald CIs.
  - The hidden logistic checks compare estimates, SEs and the Wald CI (`confint.default()`) with `tol = 1e-4`, because `glm()` stops once the deviance settles, one step before statsmodels.
  - The hidden `nls` checks compare estimates and SEs with `tol = 1e-4`, because both sides approximate the curve's derivatives numerically.
  - Each tolerance carries a comment. CLAUDE.md rule 16 records the convention.
- **LOESS is taught as LOWESS.** The spec names LOESS. The page uses LOWESS, Cleveland's original robust form of the same local smoother, because R's `lowess()` and statsmodels' `lowess()` give identical curves. The 🔀 box names ggplot2's `loess()` as a close relative that draws a slightly different curve.
- **Theil-Sen:**
  - R's new deming package matches scipy's slope, and scipy's `method="joint"` intercept, exactly.
  - Both CIs use Sen's method, but deming corrects for ties in x only, so the CIs differ slightly. Per spec §8.2 they are documented in the 🔀 box, not checked.
  - The alternative R package mblm gives a CI that is far too narrow, so it isn't used.
  - The LOWESS curves are checked at three points: R's `lowess()` and statsmodels' `lowess()` agree once statsmodels gets R's `delta`.
- **Spearman's CI:** DescTools' `SpearmanRho()` in R. In Python the same Fisher-z formula is written out in three lines; scipy has no CI.
- **Splines:**
  - R's `splines::ns(df = 3)` and patsy's `cr()` give identical fits (same R², same F) when Python passes R's knots explicitly.
  - Harrell's `rms::rcs()` places knots differently; the 🔀 box says so. rms isn't added.
- **Rounding ties:**
  - The BMI t statistic is 12.385: R's `summary(lm)` prints 12.38 and `cor.test()` prints 12.385. Both pages quote t = 12.4.
- **Quiet pages:**
  - Prototyping showed that Quarto passes `execute: message` to knitr only as an unrecognized key. knitr's `opts_current$get("message")` is TRUE on every page.
  - Pages 1–9 were quiet only because nothing on them emitted a message. Phase 3b removed one such message case by case.
  - `_quarto.yml` now sets `knitr: opts_chunk: message: false`, and the nine dead lines are removed.
  - Re-rendering those pages changes nothing but:
    - gt's random table IDs on page 2
    - the jittered boxplot PNG on page 6, because `geom_jitter()` is random
- **Folded in from Phase 3b:** the three harness minors (scope-blind undefined names, `set.seed(` in comments, hidden-chunk option order). The two reporting tests from the Phase 3b review now cover pages 10–12, with r, ρ, φ, odds and hazard ratios added to the effect-size pattern.
- **Not changed:** exercise R/Python pairs have no `check_agree()`, as on pages 4–9.

## Reference results (prototype, 2026-10-06, R 4.6.0 / Python 3.13 / pandas 3.0.6 / scipy 1.18.1 / statsmodels 0.15.0)

All three pages rendered with every hidden check passing. Full suite:
- testthat `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- pytest `tests/python`: 80 passed
- pytest `tests/site`: 214 passed
- lychee: 0 errors

Mutation checks (each failed as it should):
- page 10 without `exact = FALSE`: the no-warnings test catches R's ties warning
- page 11's Wald check given a profile CI: `disagree on 'low'`
- page 11 without the `_quarto.yml` knitr setting: the no-warnings test catches "Waiting for profiling to be done..."
- page 12 without lifelines' tighter convergence: `disagree on 'hr_b'`

| Page | Numbers |
|---|---|
| 10 | BMI and operative time: r = 0.45 (0.39 to 0.51); improvement and satisfaction: ρ = 0.38 (0.30 to 0.46), n = 404; ASA class and hypertension: χ² = 23.2, df = 3, V = 0.20, C = 0.19 |
| 11 | operative time = 42.8 + 1.37 × BMI (1.15 to 1.58), R² = 0.20; KOOS JR plateau 84.2 (82.6 to 85.9), half the gain by 56 days (49 to 64); Theil-Sen slope 0.39 (0.28 to 0.51), n = 246; complications OR 2.12 per 10 years (1.53 to 2.98); revision HR 1.25 per 10 years (0.98 to 1.59) |
| 12 | BMI 1.27 minutes per kg/m² adjusted (1.06 to 1.49), R² = 0.27; knees' τ 27.5 days longer (15.9 to 40.1); spline F = 0.58, p = 0.562; complications OR 2.08 per 10 years (1.46 to 3.02) and 1.39 per 5 kg/m² (1.03 to 1.86); implant C HR 3.19 adjusted (1.92 to 5.29) |

---

### Task 1: deming and the setup checks

**Files:**
- Modify: `DESCRIPTION`, `renv.lock`, `getting-started/check_setup.R`, `tests/python/test_check_setup.py`

**Interfaces:**
- Produces: the R package deming, which page 11 uses for Theil-Sen regression.

- [ ] **Step 1: Create the worktree and build the current site**

```bash
git checkout main && git pull
git worktree add .worktrees/phase-3c -b phase-3c-catalog main
cd .worktrees/phase-3c
uv sync && Rscript -e 'renv::restore(prompt = FALSE)'
quarto render && uv run pytest tests/site -q
```

Expected: `164 passed`.

- [ ] **Step 2: Write the failing checks**

In `getting-started/check_setup.R`, replace

```r
"ggsurvfit", "rstatix")) {
```

with

```r
"ggsurvfit", "rstatix", "deming")) {
```

In `tests/python/test_check_setup.py`, replace

```python
"ggsurvfit", "rstatix"]:
```

with

```python
"ggsurvfit", "rstatix", "deming"]:
```

- [ ] **Step 3: Run them to verify they fail**

Run: `Rscript -e 'testthat::test_dir("tests/testthat", filter = "check_setup")'`

Expected: "check_setup.R passes in a working project" FAILS. Running `Rscript getting-started/check_setup.R` reports `R package deming PROBLEM`.

- [ ] **Step 4: Install and lock deming**

In `DESCRIPTION`, replace

```
    DescTools,

```

with

```
    deming,
    DescTools,

```

Run:

```bash
Rscript -e 'renv::install("deming", prompt = FALSE)'
Rscript -e 'renv::snapshot(prompt = FALSE)'
python3 -c "import json; print('deming' in json.load(open('renv.lock'))['Packages'])"
```

Expected: `True`. The snapshot adds only deming, which has no dependencies of its own.

- [ ] **Step 5: Run all the tests**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
uv run pytest tests/site -q
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- Python: `80 passed`
- site: `164 passed`

- [ ] **Step 6: Commit**

```bash
git add DESCRIPTION renv.lock getting-started/check_setup.R tests/python/test_check_setup.py
git commit -m "Add deming (Theil-Sen regression) and its setup check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Quiet pages that work, and harder source rules

Four changes to the test harness and the build:
- **Quiet pages:** Quarto ignores `execute: message: false` for knitr. Hide messages with knitr's own default in `_quarto.yml`, and remove the dead lines from nine pages.
- **Chunk options in any order:** a chunk counts as hidden when `#| include: false` is any of its options, not only the first (deferred from Phase 3b).
- **Scoped names:** names made inside a function, lambda or comprehension don't count for the rest of the section (deferred from Phase 3b).
- **Seeds in comments don't count** (deferred from Phase 3b).

**Files:**
- Modify: `tests/site/test_sources.py`, `tests/python/test_repo_docs.py`, `_quarto.yml`, `CLAUDE.md`
- Modify (front matter only): `foundations/01-tidy-data.qmd`, `foundations/02-demographics.qmd`, `foundations/03-distributions.qmd`, `catalog/04-describe-one-group.qmd`, `catalog/05-one-group-vs-hypothetical.qmd`, `catalog/06-two-unpaired-groups.qmd`, `catalog/07-two-paired-groups.qmd`, `catalog/08-three-plus-unmatched.qmd`, `catalog/09-three-plus-matched.qmd`
- Modify: `_freeze/` for those nine pages (re-render; commit it)

**Interfaces:**
- Consumes: `test_sources.py`'s `HIDDEN_CHUNK`, `VISIBLE_CHUNK`, `undefined_names()`, `unseeded_bootstrap()` and `qmd_files()` (Phases 3a–3b).
- Produces:
  - `chunks(text, hidden)`, `hidden_chunks(text)`, `visible_chunks(text)`, which replace the two regexes
  - a scoped `undefined_names(code) -> set`
  - `PAGE_EXECUTE_MESSAGE`
  - `_quarto.yml`'s `knitr: opts_chunk: message: false`, which pages 10–12 rely on

- [ ] **Step 1: Write the tests**

In `tests/site/test_sources.py`, after the line

````python
HIDDEN_CHUNK = re.compile(r"```\{(r|python)\}\n#\| include: false\n(.*?)\n```", re.DOTALL)
````

add (after two blank lines):

````python
def test_chunk_options_can_come_in_any_order():
    text = "```{python}\n#| echo: false\n#| include: false\nchk = 1\n```\n\n```{r}\n#| warning: false\nlibrary(x)\n```\n"
    assert hidden_chunks(text) == [("python", "#| echo: false\n#| include: false\nchk = 1")]
    assert visible_chunks(text) == [("r", "#| warning: false\nlibrary(x)")]
````

After the line

````python
    assert undefined_names("import numpy as np\nx = [1]\nf = lambda v: v + 1\nprint(np.mean(x), f(2))") == set()
````

(the end of `test_rule_finds_names_a_section_never_defines`) add (after two blank lines):

````python
def test_rule_keeps_function_and_comprehension_names_inside_them():
    assert undefined_names("f = lambda scores: scores + 1\nprint(scores)") == {"scores"}
    assert undefined_names("squares = [v * v for v in range(3)]\nprint(v)") == {"v"}
    assert undefined_names("def g(a):\n    b = a + 1\n    return b\nprint(g(1), b)") == {"b"}
    assert undefined_names("def g(days):\n    return days * k\nk = 2\nprint(g(1))") == set()
````

In `test_rule_catches_an_unseeded_bootstrap_ci`, after the line

````python
    assert not unseeded_bootstrap("```{r}\n# kendalls_w() warns about ties\nx <- 1\n```")
````

add

````python
    assert unseeded_bootstrap("```{r}\n# set.seed(1) is not needed\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
    assert unseeded_bootstrap("```{r}\nx <- 1  # set.seed(1) later\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
````

and append to the end of the file (after two blank lines):

````python
# ---- quiet pages -------------------------------------------------------------
# Quarto silently ignores `message` under a page's `execute:` key on knitr pages, so
# messages such as "Waiting for profiling to be done..." reached the page. knitr's own
# chunk default, set once in _quarto.yml, hides them.

PAGE_EXECUTE_MESSAGE = re.compile(r"^execute:\n(?:  .*\n)*?  message:", re.MULTILINE)


def test_rule_catches_a_page_level_message_option():
    assert PAGE_EXECUTE_MESSAGE.search("---\nengine: knitr\nexecute:\n  message: false\n---\n")
    assert not PAGE_EXECUTE_MESSAGE.search("---\nengine: knitr\nexecute:\n  freeze: auto\n---\n")


def test_messages_are_hidden_by_knitr_for_every_page():
    config = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    assert re.search(r"^knitr:\n  opts_chunk:\n    message: false$", config, re.MULTILINE)
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files() if PAGE_EXECUTE_MESSAGE.search(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Quarto ignores `execute: message`; remove it from: " + ", ".join(offenders)
````

In `tests/python/test_repo_docs.py`, replace

```python
                 'a ceiling of "p > 0.999"', "Bootstrap CIs are seeded"]:
```

with

```python
                 'a ceiling of "p > 0.999"', "Bootstrap CIs are seeded", "opts_chunk"]:
```

- [ ] **Step 2: Run them to verify which fail**

Run:

```bash
uv run pytest tests/site/test_sources.py -q
uv run pytest tests/python/test_repo_docs.py -q
```

Expected: `4 failed, 21 passed`, then `1 failed, 2 passed`:
- `test_chunk_options_can_come_in_any_order` (NameError: `hidden_chunks` isn't defined yet)
- `test_rule_keeps_function_and_comprehension_names_inside_them`
- `test_rule_catches_an_unseeded_bootstrap_ci`, on the comment cases
- `test_messages_are_hidden_by_knitr_for_every_page`, listing the nine pages
- `test_claude_md_states_the_golden_rules`, on `opts_chunk`

- [ ] **Step 3: Implement the rules**

In `tests/site/test_sources.py`, replace the line

````python
HIDDEN_CHUNK = re.compile(r"```\{(r|python)\}\n#\| include: false\n(.*?)\n```", re.DOTALL)
````

with

````python
CHUNK = re.compile(r"```\{(r|python)\}\n(.*?)\n```", re.DOTALL)


def chunks(text, hidden):
    """(language, code) for each R or Python chunk that is hidden (`#| include: false`
    among its options, in any order) or, with hidden=False, shown on the page."""
    found = []
    for lang, code in CHUNK.findall(text):
        options = []
        for line in code.splitlines():
            if not line.startswith("#|"):
                break
            options.append(line.strip())
        if ("#| include: false" in options) == hidden:
            found.append((lang, code))
    return found


def hidden_chunks(text):
    return chunks(text, hidden=True)


def visible_chunks(text):
    return chunks(text, hidden=False)
````

delete the line

````python
VISIBLE_CHUNK = re.compile(r"```\{(r|python)\}\n(?!#\| include: false)(.*?)\n```", re.DOTALL)
````

and point the eight call sites at the new helpers:

```bash
sed -i '' 's/HIDDEN_CHUNK\.findall(/hidden_chunks(/; s/VISIBLE_CHUNK\.findall(/visible_chunks(/' tests/site/test_sources.py
grep -c "HIDDEN_CHUNK\|VISIBLE_CHUNK" tests/site/test_sources.py
```

Expected: `0`.

Replace

````python
def undefined_names(code):
    """Names the code reads but never imports, assigns or defines (statement order ignored)."""
    defined, used = set(dir(builtins)), set()
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Name):
            (used if isinstance(node.ctx, ast.Load) else defined).add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            defined.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
    return used - defined
````

with

````python
def undefined_names(code):
    """Names the code reads but never imports, assigns or defines (statement order ignored).
    Names made inside a function, lambda or comprehension count only inside it."""
    defined, used = set(dir(builtins)), set()

    def visit(node, local):
        bind = defined if local is None else local
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            if isinstance(node, ast.FunctionDef):
                bind.add(node.name)
            inner = set(local or ()) | {arg.arg for arg in ast.walk(node.args) if isinstance(arg, ast.arg)}
            for default in node.args.defaults + [d for d in node.args.kw_defaults if d]:
                visit(default, local)
            for child in (node.body if isinstance(node.body, list) else [node.body]):
                visit(child, inner)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            inner = set(local or ())
            for generator in node.generators:
                visit(generator.iter, local)
                visit(generator.target, inner)
                for condition in generator.ifs:
                    visit(condition, inner)
            for part in ([node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]):
                visit(part, inner)
        elif isinstance(node, ast.Name):
            if not isinstance(node.ctx, ast.Load):
                bind.add(node.id)
            elif local is None or node.id not in local:
                used.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            bind.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        else:
            for child in ast.iter_child_nodes(node):
                visit(child, local)

    visit(ast.parse(code), None)
    return used - defined
````

and replace

````python
def unseeded_bootstrap(text):
    for code in R_CHUNK.findall(text):
        for line in code.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if any(f in line for f in BOOTSTRAP_CI_FUNCTIONS) and "ci = NULL" not in line:
                if "set.seed(" not in code[:code.index(line)]:
                    return True
    return False
````

with

````python
def unseeded_bootstrap(text):
    for code in R_CHUNK.findall(text):
        seeded = False
        for line in code.splitlines():
            line = line.split("#", 1)[0]   # comments don't count
            seeded = seeded or "set.seed(" in line
            if any(f in line for f in BOOTSTRAP_CI_FUNCTIONS) and "ci = NULL" not in line and not seeded:
                return True
    return False
````

- [ ] **Step 4: Run the source rules**

Run: `uv run pytest tests/site/test_sources.py -q`

Expected: `1 failed, 24 passed`. Only `test_messages_are_hidden_by_knitr_for_every_page` still fails. The scoped name rule and the reordered chunk parser accept every existing page.

- [ ] **Step 5: Hide messages through knitr**

In `_quarto.yml`, replace

```yaml
execute:
  freeze: auto
```

with

```yaml
execute:
  freeze: auto

# Quarto ignores `message` under `execute:` for knitr pages; knitr's own chunk
# default hides messages on every page.
knitr:
  opts_chunk:
    message: false
```

Remove the two dead front-matter lines from the nine pages:

```bash
uv run python - <<'EOF'
from pathlib import Path
for page in ["foundations/01-tidy-data", "foundations/02-demographics", "foundations/03-distributions",
             "catalog/04-describe-one-group", "catalog/05-one-group-vs-hypothetical", "catalog/06-two-unpaired-groups",
             "catalog/07-two-paired-groups", "catalog/08-three-plus-unmatched", "catalog/09-three-plus-matched"]:
    path = Path(page + ".qmd")
    text = path.read_text(encoding="utf-8")
    assert text.count("execute:\n  message: false\n") == 1, page
    path.write_text(text.replace("execute:\n  message: false\n", ""), encoding="utf-8")
EOF
```

In `CLAUDE.md`'s golden rule 10, replace

```markdown
10. **Quiet pages.** Pages with code set `execute: message: false` in their front matter, and chunks that call `library()` add `#| warning: false`.
```

with

```markdown
10. **Quiet pages.** `_quarto.yml` hides messages on every page through knitr's own default (`knitr: opts_chunk: message: false`). Quarto silently ignores `message` under a page's `execute:` key, so don't put it there. Chunks that call `library()` add `#| warning: false`.
```

- [ ] **Step 6: Re-render the nine pages and confirm nothing visible changed**

Run:

```bash
for page in foundations/01-tidy-data foundations/02-demographics foundations/03-distributions \
            catalog/04-describe-one-group catalog/05-one-group-vs-hypothetical catalog/06-two-unpaired-groups \
            catalog/07-two-paired-groups catalog/08-three-plus-unmatched catalog/09-three-plus-matched; do
  quarto render "$page.qmd" || break
done
uv run python - <<'EOF'
import json, re, subprocess
for page in ["foundations/01-tidy-data", "foundations/02-demographics", "foundations/03-distributions",
             "catalog/04-describe-one-group", "catalog/05-one-group-vs-hypothetical", "catalog/06-two-unpaired-groups",
             "catalog/07-two-paired-groups", "catalog/08-three-plus-unmatched", "catalog/09-three-plus-matched"]:
    path = f"_freeze/{page}/execute-results/html.json"
    old = json.loads(subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, text=True, check=True).stdout)
    new = json.load(open(path))
    before = old["result"]["markdown"].replace("execute:\n  message: false\n", "")
    after = new["result"]["markdown"]
    ids = set(re.findall(r'<div id="([a-z]{10})"', before + after))   # gt makes random table ids
    same = re.sub("|".join(ids), "ID", before) == re.sub("|".join(ids), "ID", after) if ids else before == after
    print(page, "unchanged" if same else "CHANGED")
EOF
git status --short _freeze
```

Expected:
- every page prints `unchanged`
- `git status` lists the nine `execute-results/html.json` files, plus `catalog/06-two-unpaired-groups/figure-html/unnamed-chunk-13-1.png`, because its `geom_jitter()` is random on every render

- [ ] **Step 7: Run all the tests**

Run:

```bash
uv run pytest tests/site -q
uv run pytest tests/python -q
```

Expected: site `168 passed`; Python `80 passed`.

- [ ] **Step 8: Commit**

```bash
git add tests/site/test_sources.py tests/python/test_repo_docs.py _quarto.yml CLAUDE.md \
        foundations/0[1-3]-*.qmd catalog/0[4-9]-*.qmd _freeze/foundations _freeze/catalog
git commit -m "Hide messages through knitr's own default (Quarto ignores execute: message); harder chunk, scope and seed rules

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Page 10, Quantify association between two variables

**Files:**
- Modify: `catalog/10-association.qmd` (replace the stub)
- Create: `_freeze/catalog/10-association/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Phase 3b's `test_catalog.py` (`WRITTEN`, `THREE_GROUP_PAGES` and the two reporting tests)
  - Task 2's `_quarto.yml` message setting
  - `data/cohort.csv`, `data/proms_long.csv`
- Produces:
  - page 10 anchors `#pearson`, `#spearman` and `#contingency-coefficients`
  - `test_catalog.py`'s `REPORTING_PAGES`

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
]
```

replace

```python
THREE_GROUP_PAGES = [page for page in WRITTEN if page.startswith(("catalog/08-", "catalog/09-"))]
```

with

```python
THREE_GROUP_PAGES = [page for page in WRITTEN if page.startswith(("catalog/08-", "catalog/09-"))]
REPORTING_PAGES = [page for page in WRITTEN if page >= "catalog/08-"]   # pages written since the Phase 3b review
```

replace

```python
@pytest.mark.parametrize("page", THREE_GROUP_PAGES)
def test_reports_never_turn_no_evidence_into_no_difference(site, page):
```

with

```python
@pytest.mark.parametrize("page", REPORTING_PAGES)
def test_reports_never_turn_no_evidence_into_no_difference(site, page):
```

replace

```python
@pytest.mark.parametrize("page", THREE_GROUP_PAGES)
def test_exercise_answers_follow_the_reporting_conventions(site, page):
```

with

```python
@pytest.mark.parametrize("page", REPORTING_PAGES)
def test_exercise_answers_follow_the_reporting_conventions(site, page):
```

and replace

```python
        if re.search(r"(ω²|ε²|η²( p)?|Kendall's W|Cramér's V) = [\d.]+", text):
```

with

```python
        if re.search(r"(ω²|ε²|η²( p)?|Kendall's W|Cramér's V|\br|ρ|φ) = [\d.]+|(odds|hazard) ratio [\d.]+", text):
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `10 failed, 170 passed`. 10 of the 12 new page-10 tests fail; the no-warnings and short-outputs tests pass trivially on a stub.

- [ ] **Step 3: Write the page**

Replace `catalog/10-association.qmd` with:

````markdown
---
title: "10 · Quantify association between two variables"
description: "Pearson correlation, Spearman correlation and contingency coefficients: how strongly two things go together."
engine: knitr
toc-depth: 2
---

```{r}
#| include: false
source("R/check_agree.R")
```

```{r}
#| echo: false
#| output: asis
# Stamp the data version into the page; tests/site/test_freshness.py checks it.
cat(sprintf("<!-- data-checksum: %s -->", unname(tools::md5sum("data/CHECKSUMS.md5"))))
```

Two things measured on the same patients: BMI and operative time, PROM improvement and satisfaction, ASA class and hypertension. The tests on this page don't compare groups. They put **one number on how strongly the two go together**, with a 95% CI. If you want to **predict** one from the other, use regression ([page 11](11-predict-from-one.qmd)).

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

## Pearson correlation {#pearson}

**The question:** How closely does operative time track BMI?

### When to use it

- Two **measurements** on the same patients, and you want one number for how closely they move together along a **straight line**.
- Both are roughly normal, without extreme outliers, and the scatter plot looks like a cloud stretched along a line.
- If either is skewed or ordinal, has outliers, or the points follow a curve → [Spearman correlation](#spearman).
- If you want to predict one from the other, or adjust for other variables → [linear regression](11-predict-from-one.qmd#linear-regression).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3.5
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

ggplot(cohort, aes(bmi, op_time_min)) +
  geom_point(alpha = 0.4) +   # see-through points show where they pile up
  labs(x = "BMI, kg/m²", y = "Operative time, minutes")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.scatter(cohort["bmi"], cohort["op_time_min"], alpha=0.4)   # see-through points show where they pile up
ax.set_xlabel("BMI, kg/m²")
ax.set_ylabel("Operative time, minutes")
plt.show()
```
:::

The points drift upward from left to right, along a rough line, with no extreme outliers.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
bmi_corr <- cor.test(cohort$bmi, cohort$op_time_min)   # Pearson is the default
bmi_corr
```

## Python

```{python}
bmi_corr = stats.pearsonr(cohort["bmi"], cohort["op_time_min"])
print(bmi_corr)
print(bmi_corr.confidence_interval(confidence_level=0.95))
```
:::

```{python}
#| include: false
bmi_ci = bmi_corr.confidence_interval(confidence_level=0.95)
chk = {"r": float(bmi_corr.statistic), "p": float(bmi_corr.pvalue), "low": float(bmi_ci.low), "high": float(bmi_ci.high)}
```

```{r}
#| include: false
check_agree(list(r = unname(bmi_corr$estimate), p = bmi_corr$p.value,
                 low = bmi_corr$conf.int[1], high = bmi_corr$conf.int[2]), reticulate::py$chk)
```

### Read the output

- **cor** (R) or **statistic** (Python): Pearson's **r = 0.45**. It runs from −1 (a perfect falling line) through 0 (no straight-line relationship) to +1 (a perfect rising line).
- **t = 12.4, df = 598:** the test statistic, with 600 procedures minus two degrees of freedom. Python doesn't print it.
- **p < 0.001** (R prints `< 2.2e-16`): a correlation this strong would be very unlikely if BMI and operative time were unrelated.
- **95% CI 0.39 to 0.51.**

### Effect size and 95% CI

**r is the effect size**: r = 0.45 (95% CI 0.39 to 0.51). As a rough guide, 0.1 is small, 0.3 medium and 0.5 large. Squaring it gives the share of the variation in operative time that goes with BMI: r² = 0.20, about a fifth.

### How to report it

> **Methods:** The association between BMI and operative time was measured with Pearson's correlation coefficient (r).
>
> **Results:** Operative time rose with BMI (Pearson r = 0.45, 95% CI 0.39 to 0.51, p < 0.001; n = 600 procedures).

::: {.callout-warning}
## ⚠️ Watch out: r only sees straight lines, and isn't cause
A relationship that rises and then falls can have r close to 0, and one outlier can create or hide a correlation, so always look at the scatter plot first. And a correlation doesn't say which causes which, or whether something else (procedure type, surgeon) drives both. To adjust for other variables, use [multiple regression](12-predict-from-several.qmd#multiple-linear-regression).
:::

## Spearman correlation {#spearman}

**The question:** Are patients whose HOOS JR or KOOS JR improved more from before surgery to 1 year also more satisfied?

### When to use it

- Two variables on the same patients, at least one of them **ordinal** (satisfaction from 1 to 5), **skewed**, or with **outliers**.
- The relationship goes one way (always up, or always down) but needn't be a straight line. Spearman's ρ (rho) is Pearson's r calculated on the **ranks**.
- If both are roughly normal and the relationship is a straight line → [Pearson correlation](#pearson).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)
proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

change <- proms |>
  filter(visit %in% c("preop", "1yr")) |>
  select(case_id, visit, prom_score) |>
  pivot_wider(names_from = visit, values_from = prom_score) |>   # one row per case: preop and 1yr side by side
  mutate(improvement = `1yr` - preop) |>
  inner_join(select(cohort, case_id, satisfaction_1yr), by = "case_id") |>
  filter(!is.na(improvement), !is.na(satisfaction_1yr))          # both answers needed

ggplot(change, aes(factor(satisfaction_1yr), improvement)) +
  geom_boxplot() +
  labs(x = "Satisfaction at 1 year (1 = very dissatisfied, 5 = very satisfied)", y = "Improvement, points")

change |>
  group_by(satisfaction_1yr) |>
  summarise(n = n(), median_improvement = median(improvement))
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")
proms = pd.read_csv("data/proms_long.csv")

wide = proms[proms["visit"].isin(["preop", "1yr"])].pivot(index="case_id", columns="visit", values="prom_score")
wide["improvement"] = wide["1yr"] - wide["preop"]   # one row per case: preop and 1yr side by side
change = wide.join(cohort.set_index("case_id")["satisfaction_1yr"]).dropna(subset=["improvement", "satisfaction_1yr"])

levels = [1, 2, 3, 4, 5]
fig, ax = plt.subplots(figsize=(6, 3))
parts = ax.boxplot([change.loc[change["satisfaction_1yr"] == level, "improvement"] for level in levels], tick_labels=levels)
ax.set_xlabel("Satisfaction at 1 year (1 = very dissatisfied, 5 = very satisfied)")
ax.set_ylabel("Improvement, points")
plt.show()

print(change.groupby("satisfaction_1yr")["improvement"].agg(["count", "median"]))
```
:::

404 procedures have both a pre-op and a 1-year score and a satisfaction answer. The median improvement climbs with each satisfaction level, from 25.4 points among the 14 very dissatisfied to 43.8 among the 198 very satisfied. Satisfaction has only five values, so there are many ties.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
satisfaction_corr <- cor.test(change$improvement, change$satisfaction_1yr,
                              method = "spearman", exact = FALSE)   # ties: no exact p-value
satisfaction_corr
```

## Python

```{python}
satisfaction_corr = stats.spearmanr(change["improvement"], change["satisfaction_1yr"])
print(satisfaction_corr)
```
:::

```{python}
#| include: false
chk = {"rho": float(satisfaction_corr.statistic), "p": float(satisfaction_corr.pvalue)}
```

```{r}
#| include: false
check_agree(list(rho = unname(satisfaction_corr$estimate), p = satisfaction_corr$p.value), reticulate::py$chk)
```

### Read the output

- **rho** (R) or **statistic** (Python): **ρ = 0.38**. Like r, it runs from −1 to +1; here it says patients with larger improvements tend to give higher satisfaction scores.
- **S = 6764534** (R only): the test statistic, built from the differences between the two rankings. You don't need to report it.
- **p < 0.001** (R prints `1.111e-15`): a correlation this strong would be very unlikely if improvement and satisfaction were unrelated.

### Effect size and 95% CI

**ρ is the effect size.** Neither `cor.test()` nor scipy gives its 95% CI, so R uses DescTools and Python uses the formula behind it (Fisher's z transformation).

::: {.panel-tabset group="language"}
## R

```{r}
DescTools::SpearmanRho(change$improvement, change$satisfaction_1yr, conf.level = 0.95)
```

## Python

```{python}
rho, n = satisfaction_corr.statistic, len(change)
z = np.arctanh(rho)                                 # Fisher's z: makes the CI symmetric
half_width = stats.norm.ppf(0.975) / np.sqrt(n - 3)
print(rho, np.tanh(z - half_width), np.tanh(z + half_width))
```
:::

```{python}
#| include: false
chk = {"low": float(np.tanh(z - half_width)), "high": float(np.tanh(z + half_width))}
```

```{r}
#| include: false
satisfaction_rho <- DescTools::SpearmanRho(change$improvement, change$satisfaction_1yr, conf.level = 0.95)
check_agree(list(low = satisfaction_rho[["lwr.ci"]], high = satisfaction_rho[["upr.ci"]]), reticulate::py$chk)
```

ρ = 0.38 (95% CI 0.30 to 0.46): a moderate association, using the same rough guide as for r.

### How to report it

> **Methods:** The association between improvement in HOOS JR or KOOS JR from before surgery to 1 year and satisfaction at 1 year was measured with Spearman's rank correlation coefficient (ρ).
>
> **Results:** Among 404 procedures with both scores and a satisfaction answer, greater improvement went with higher satisfaction (Spearman ρ = 0.38, 95% CI 0.30 to 0.46, p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: two instruments in one number
Hip patients answer HOOS JR and knee patients KOOS JR. Both run from 0 to 100, but a point on one isn't guaranteed to mean the same as a point on the other. Pooling them is fine for a first look; in a paper, analyze hips and knees separately or say why you pooled them.
:::

::: {.callout-tip}
## 🔀 R vs Python: ties and the CI
- With fewer than 1290 patients, R's `cor.test()` tries an **exact** p-value. With ties it can't compute one, so it warns and falls back to the usual approximation, the one scipy always uses. `exact = FALSE` asks for the approximation directly, without the warning.
- Neither gives a CI for ρ. DescTools' `SpearmanRho()` and the Python formula use the same method: Fisher's z with a standard error of 1/√(n − 3).
:::

## Contingency coefficients {#contingency-coefficients}

**The question:** How strongly is ASA class linked with hypertension?

### When to use it

- Two **categorical** variables on the same patients. The chi-square test ([page 8](08-three-plus-unmatched.qmd#chi-square)) asks whether they're linked at all; a contingency coefficient says **how strongly**.
- **Phi (φ)** is for 2 × 2 tables. **Cramér's V** works for any table size and equals φ (without its sign) on a 2 × 2 table. Both run from 0 (no link) to 1 (each category of one predicts the other exactly).
- **Pearson's contingency coefficient (C)** is older. Its maximum is below 1 and depends on the table's size (0.71 for a table with two columns), which makes it hard to read, so prefer V.
- The chi-square p-value needs every **expected** count to be at least 5.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

asa_hypertension <- table(asa = cohort$asa, hypertension = cohort$hypertension)   # 1 = hypertension
asa_hypertension
round(100 * prop.table(asa_hypertension, margin = 1), 1)   # row percentages
```

## Python

```{python}
import pandas as pd
from scipy import stats

cohort = pd.read_csv("data/cohort.csv")

asa_hypertension = pd.crosstab(cohort["asa"], cohort["hypertension"])   # 1 = hypertension
print(asa_hypertension)
print((100 * pd.crosstab(cohort["asa"], cohort["hypertension"], normalize="index")).round(1))   # row percentages
```
:::

Hypertension becomes more common with each ASA class: from 12 of 36 (33.3%) in ASA 1 to 16 of 18 (88.9%) in ASA 4.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
asa_test <- chisq.test(asa_hypertension)
asa_test
min(asa_test$expected)   # smallest expected count
```

## Python

```{python}
asa_test = stats.chi2_contingency(asa_hypertension)
print(asa_test.statistic, asa_test.dof, asa_test.pvalue)
print(asa_test.expected_freq.min())   # smallest expected count
```
:::

```{python}
#| include: false
chk = {"chi2": float(asa_test.statistic), "df": float(asa_test.dof), "p": float(asa_test.pvalue)}
```

```{r}
#| include: false
check_agree(list(chi2 = unname(asa_test$statistic), df = unname(asa_test$parameter), p = asa_test$p.value), reticulate::py$chk)
```

### Read the output

- **X-squared = 23.18:** the chi-square statistic. **df = 3:** (4 ASA classes − 1) × (2 columns − 1).
- **p < 0.001** (R prints `3.702e-05`): a link this strong would be very unlikely if hypertension were equally common in every ASA class.
- **Smallest expected count 7.83** (ASA 4 without hypertension): every expected count is at least 5, so the p-value is reliable.

### Effect size and 95% CI

::: {.panel-tabset group="language"}
## R

```{r}
effectsize::cramers_v(asa_hypertension, adjust = FALSE)   # see the R vs Python box
effectsize::pearsons_c(asa_hypertension)
```

## Python

```{python}
print(stats.contingency.association(asa_hypertension, method="cramer"))    # Cramér's V
print(stats.contingency.association(asa_hypertension, method="pearson"))   # Pearson's C
```
:::

```{python}
#| include: false
chk = {"v": float(stats.contingency.association(asa_hypertension, method="cramer")),
       "c": float(stats.contingency.association(asa_hypertension, method="pearson"))}
```

```{r}
#| include: false
asa_v <- effectsize::cramers_v(asa_hypertension, adjust = FALSE)
asa_c <- effectsize::pearsons_c(asa_hypertension)
check_agree(list(v = asa_v$Cramers_v, c = asa_c$Pearsons_c), reticulate::py$chk)
```

**Cramér's V = 0.20**, a small-to-medium association (as a rough guide for tables with two rows or columns, 0.1 is small, 0.3 medium and 0.5 large). R also prints a one-sided 95% CI (0.12 to 1.00): V can't be negative, so only its lower bound is informative. scipy doesn't compute this CI. Pearson's C is 0.19 here, but its ceiling for this table is 0.71, not 1, so the same number means more than it seems: one more reason to report V.

### How to report it

> **Methods:** The association between ASA class and hypertension was tested with the chi-square test, with Cramér's V as the effect size.
>
> **Results:** Hypertension was more common at higher ASA classes, from 12 of 36 procedures (33.3%) in ASA 1 to 16 of 18 (88.9%) in ASA 4 (χ² = 23.2, df = 3, p < 0.001; Cramér's V = 0.20, one-sided 95% CI 0.12 to 1.00).

::: {.callout-warning}
## ⚠️ Watch out: V gives the strength, not the pattern
Shuffling the rows of the table doesn't change V, so V can't say that hypertension rises **steadily** with ASA class. The row percentages show the pattern; put them in your Results. If the categories are ordered and you expect a trend, a test for trend can be more powerful than the plain chi-square test.
:::

::: {.callout-tip}
## 🔀 R vs Python: Cramér's V has two versions
effectsize's `cramers_v()` and `phi()` apply a small-sample bias correction by default (here V = 0.18), while scipy's `association()` doesn't. `adjust = FALSE` turns it off so the two match; whichever you use, say which in your Methods. On a 2 × 2 table, `association(method="cramer")` gives φ without its sign.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
asa_rows <- prop.table(asa_hypertension, margin = 1)
change_medians <- change |> group_by(satisfaction_1yr) |> summarise(n = n(), median = median(improvement))
los_rho <- cor.test(cohort$los_days, cohort$age, method = "spearman", exact = FALSE)
los_ci <- DescTools::SpearmanRho(cohort$los_days, cohort$age, conf.level = 0.95)
apnea_table <- table(sex = cohort$sex, sleep_apnea = cohort$sleep_apnea)
apnea_phi <- effectsize::phi(apnea_table, adjust = FALSE)
stopifnot(
  sum(table(cohort$patient_id) == 2) == 80, nrow(cohort) == 600,
  round(unname(bmi_corr$estimate), 2) == 0.45, round(bmi_corr$conf.int, 2) == c(0.39, 0.51),
  round(unname(bmi_corr$statistic), 1) == 12.4, unname(bmi_corr$parameter) == 598, bmi_corr$p.value < 0.001,
  round(unname(bmi_corr$estimate)^2, 2) == 0.20,
  nrow(change) == 404, change_medians$n[c(1, 5)] == c(14, 198), round(change_medians$median[c(1, 5)], 1) == c(25.4, 43.8),
  all(diff(change_medians$median) > 0),
  round(unname(satisfaction_corr$estimate), 2) == 0.38, round(unname(satisfaction_corr$statistic)) == 6764534,
  satisfaction_corr$p.value < 0.001, signif(satisfaction_corr$p.value, 4) == 1.111e-15,
  round(satisfaction_rho[["lwr.ci"]], 2) == 0.30, round(satisfaction_rho[["upr.ci"]], 2) == 0.46,
  asa_hypertension[, "1"] == c(12, 155, 156, 16), rowSums(asa_hypertension) == c(36, 300, 246, 18),
  round(100 * asa_rows[c(1, 4), "1"], 1) == c(33.3, 88.9), all(diff(asa_rows[, "1"]) > 0),
  round(unname(asa_test$statistic), 2) == 23.18, round(unname(asa_test$statistic), 1) == 23.2,
  unname(asa_test$parameter) == 3, asa_test$p.value < 0.001, signif(asa_test$p.value, 4) == 3.702e-05,
  round(min(asa_test$expected), 2) == 7.83, which.min(asa_test$expected) == 4,   # row ASA 4, column 0
  round(asa_v$Cramers_v, 2) == 0.20, round(asa_v$CI_low, 2) == 0.12, round(asa_c$Pearsons_c, 2) == 0.19,
  round(sqrt(1 / 2), 2) == 0.71,
  round(effectsize::cramers_v(asa_hypertension)$Cramers_v, 2) == 0.18,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(cor(cohort$age, cohort$op_time_min), 2) == 0.14,
  round(cor.test(cohort$age, cohort$op_time_min)$conf.int, 2) == c(0.06, 0.22),
  cor.test(cohort$age, cohort$op_time_min)$p.value < 0.001, round(cor(cohort$age, cohort$op_time_min)^2, 2) == 0.02,
  round(unname(los_rho$estimate), 2) == 0.15, los_rho$p.value < 0.001,
  round(los_ci[["lwr.ci"]], 2) == 0.07, round(los_ci[["upr.ci"]], 2) == 0.22,
  apnea_table[, "1"] == c(43, 69), rowSums(apnea_table) == c(343, 257),
  round(100 * prop.table(apnea_table, 1)[, "1"], 1) == c(12.5, 26.8),
  round(unname(chisq.test(apnea_table, correct = FALSE)$statistic), 1) == 19.8,
  chisq.test(apnea_table, correct = FALSE)$p.value < 0.001,
  round(apnea_phi$phi, 2) == 0.18, round(apnea_phi$CI_low, 2) == 0.11
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** How strongly is operative time linked with **age**? Report Pearson's r with its 95% CI.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
cor.test(cohort$age, cohort$op_time_min)
```

## Python

```{python}
age_corr = stats.pearsonr(cohort["age"], cohort["op_time_min"])
print(age_corr, age_corr.confidence_interval(confidence_level=0.95))
```
:::

Operative time rose only slightly with age (Pearson r = 0.14, 95% CI 0.06 to 0.22, p < 0.001). The association is clear but weak: age goes with about 2% of the variation in operative time (r² = 0.02), against 20% for BMI.
:::

**2.** A colleague asks whether older patients stay in hospital longer. Which correlation would you use, and what do you find?

::: {.callout-tip collapse="true"}
## Solution
Length of stay is strongly right-skewed with many ties ([page 3](../foundations/03-distributions.qmd#transform)): **Spearman correlation**.

::: {.panel-tabset group="language"}
## R

```{r}
cor.test(cohort$los_days, cohort$age, method = "spearman", exact = FALSE)
DescTools::SpearmanRho(cohort$los_days, cohort$age, conf.level = 0.95)
```

## Python

```{python}
los_corr = stats.spearmanr(cohort["los_days"], cohort["age"])
z, half_width = np.arctanh(los_corr.statistic), stats.norm.ppf(0.975) / np.sqrt(len(cohort) - 3)
print(los_corr, np.tanh(z - half_width), np.tanh(z + half_width))
```
:::

Older patients tended to stay slightly longer (Spearman ρ = 0.15, 95% CI 0.07 to 0.22, p < 0.001), a weak association.
:::

**3.** Is sleep apnea more common in men than in women, and how strongly is it linked with sex? Write the Results sentence with φ.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
apnea <- table(sex = cohort$sex, sleep_apnea = cohort$sleep_apnea)
apnea
chisq.test(apnea, correct = FALSE)   # no continuity correction, to match phi
effectsize::phi(apnea, adjust = FALSE)
```

## Python

```{python}
apnea = pd.crosstab(cohort["sex"], cohort["sleep_apnea"])
print(apnea)
apnea_test = stats.chi2_contingency(apnea, correction=False)
print(apnea_test.statistic, apnea_test.dof, apnea_test.pvalue)
print(stats.contingency.association(apnea, method="cramer"))   # phi without its sign, on a 2 × 2 table
```
:::

"Sleep apnea was more common in men (69 of 257, 26.8%) than in women (43 of 343, 12.5%) (χ² = 19.8, df = 1, p < 0.001; φ = 0.18, one-sided 95% CI 0.11 to 1.00)."
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/10-association.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `180 passed`.

- [ ] **Step 5: Prove the page stays quiet, then restore**

In the `#spearman` section's Run it block, change `method = "spearman", exact = FALSE)   # ties: no exact p-value` to `method = "spearman")`. Then run:

```bash
quarto render catalog/10-association.qmd
uv run pytest tests/site/test_catalog.py -q -k "no_warnings and 10-"
```

Expected:
- The render completes, because R falls back to the same approximation as scipy.
- `test_page_shows_no_warnings_or_package_messages[catalog/10-association.html]` FAILS on R's warning that it cannot compute an exact p-value with ties.

Undo the change, then run:

```bash
rm -rf catalog/10-association_files
quarto render catalog/10-association.qmd
uv run pytest tests/site -q
```

Expected: `180 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/10-association.qmd _freeze/catalog/10-association tests/site/test_catalog.py
git commit -m "Write page 10, association: Pearson, Spearman, contingency coefficients

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Page 11, Predict a value from another variable

**Files:**
- Modify: `catalog/11-predict-from-one.qmd` (replace the stub)
- Create: `_freeze/catalog/11-predict-from-one/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Task 1's deming
  - Task 2's `_quarto.yml` message setting, without which R's profile CIs print "Waiting for profiling to be done..."
  - Task 3's `WRITTEN` and `REPORTING_PAGES`
  - `data/cohort.csv`, `data/proms_long.csv`
- Produces:
  - page 11 anchors `#linear-regression`, `#nonlinear-regression`, `#nonparametric-regression`, `#logistic-regression` and `#cox`
  - `SURVIVAL_LINKS` entries for pages 11 and 12
  - `REPEATED_SCORE_SECTIONS` and `test_curve_fits_warn_that_repeated_scores_narrow_the_cis`

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
    "catalog/11-predict-from-one.html",
]
```

replace

```python
    ("catalog/09-three-plus-matched.html", "stratified-cox"): "survival/14-cox-regression.html",
```

with

```python
    ("catalog/09-three-plus-matched.html", "stratified-cox"): "survival/14-cox-regression.html",
    ("catalog/11-predict-from-one.html", "cox"): "survival/14-cox-regression.html",
    ("catalog/12-predict-from-several.html", "cox"): "survival/14-cox-regression.html",
```

and append (after two blank lines):

```python
# ---- curve fits on repeated scores -------------------------------------------

REPEATED_SCORE_SECTIONS = [cell for cell in [("catalog/11-predict-from-one.html", "nonlinear-regression"),
                                             ("catalog/12-predict-from-several.html", "multiple-nonlinear-regression")]
                           if cell[0] in WRITTEN]


@pytest.mark.parametrize("page,anchor", REPEATED_SCORE_SECTIONS)
def test_curve_fits_warn_that_repeated_scores_narrow_the_cis(site, page, anchor):
    """Each joint contributes up to four scores, so least-squares CIs are too narrow; page 16 handles that."""
    warnings = [box for box in section(page, anchor).select("div.callout-warning") if "too narrow" in text_of(box)]
    assert warnings, f"{page}#{anchor}: no warning that the CIs are too narrow"
    assert any(a["href"].endswith("beyond/16-mixed-models.html") for a in warnings[0].select("a[href]"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `16 failed, 182 passed`. 16 of the 18 new page-11 tests fail, including the survival link and the repeated-scores warning; the no-warnings and short-outputs tests pass trivially on a stub.

- [ ] **Step 3: Write the page**

Replace `catalog/11-predict-from-one.qmd` with:

````markdown
---
title: "11 · Predict a value from another variable"
description: "Simple linear and nonlinear regression, nonparametric regression, simple logistic regression and Cox regression: how an outcome changes with one predictor."
engine: knitr
toc-depth: 2
---

```{r}
#| include: false
source("R/check_agree.R")
```

```{r}
#| echo: false
#| output: asis
# Stamp the data version into the page; tests/site/test_freshness.py checks it.
cat(sprintf("<!-- data-checksum: %s -->", unname(tools::md5sum("data/CHECKSUMS.md5"))))
```

A correlation ([page 10](10-association.qmd)) says how strongly two things go together. **Regression** says **how much the outcome changes for each unit of the predictor**, and lets you predict the outcome for a new patient. Which regression depends on the outcome: a measurement on a straight line or a curve, a measurement that isn't normal, a yes/no outcome, or time until an event. With several predictors at once, see [page 12](12-predict-from-several.qmd).

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

## Simple linear regression {#linear-regression}

**The question:** How much longer does the operation take for each extra point of BMI?

### When to use it

- The outcome is a **measurement**, and you want to know how much it changes **per unit of one predictor**, or to predict it.
- The relationship is roughly a **straight line**, and each patient's outcome is independent of the others'.
- The **residuals** (each patient's distance from the line) are roughly normal, with a similar spread all along the line. Check them after fitting.
- If the relationship curves → [nonlinear regression](#nonlinear-regression). If the outcome is skewed or has a ceiling → [nonparametric regression](#nonparametric-regression). If it's yes/no → [logistic regression](#logistic-regression).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3.5
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

ggplot(cohort, aes(bmi, op_time_min)) +
  geom_point(alpha = 0.4) +
  geom_smooth(method = "lm", se = FALSE) +   # the least-squares line
  labs(x = "BMI, kg/m²", y = "Operative time, minutes")
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

cohort = pd.read_csv("data/cohort.csv")

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.scatter(cohort["bmi"], cohort["op_time_min"], alpha=0.4)
slope, intercept = np.polyfit(cohort["bmi"], cohort["op_time_min"], deg=1)   # the least-squares line
bmi_range = np.array([cohort["bmi"].min(), cohort["bmi"].max()])
ax.plot(bmi_range, intercept + slope * bmi_range)
ax.set_xlabel("BMI, kg/m²")
ax.set_ylabel("Operative time, minutes")
plt.show()
```
:::

The points scatter around a rising straight line, with no curve and no extreme outliers.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
bmi_model <- lm(op_time_min ~ bmi, data = cohort)   # outcome ~ predictor
summary(bmi_model)
confint(bmi_model)
```

## Python

```{python}
bmi_model = smf.ols("op_time_min ~ bmi", data=cohort).fit()   # outcome ~ predictor
print(bmi_model.summary())
```
:::

```{python}
#| include: false
chk = {"intercept": float(bmi_model.params["Intercept"]), "slope": float(bmi_model.params["bmi"]),
       "se": float(bmi_model.bse["bmi"]), "low": float(bmi_model.conf_int().loc["bmi", 0]),
       "high": float(bmi_model.conf_int().loc["bmi", 1]), "r2": float(bmi_model.rsquared), "f": float(bmi_model.fvalue)}
```

```{r}
#| include: false
bmi_fit <- summary(bmi_model)
check_agree(list(intercept = coef(bmi_model)[["(Intercept)"]], slope = coef(bmi_model)[["bmi"]],
                 se = bmi_fit$coefficients["bmi", "Std. Error"], low = confint(bmi_model)["bmi", 1],
                 high = confint(bmi_model)["bmi", 2], r2 = bmi_fit$r.squared, f = unname(bmi_fit$fstatistic["value"])),
            reticulate::py$chk)
```

### Read the output

- **Intercept = 42.8:** the predicted operative time at a BMI of 0. That's impossible, so on its own it means nothing; it anchors the line.
- **bmi = 1.37:** the **slope**. Each extra kg/m² of BMI goes with 1.37 more minutes of operative time, on average.
- **Std. Error 0.11, t = 12.4, p < 0.001:** the slope's uncertainty, and the test of whether it's zero (no relationship).
- **95% CI 1.15 to 1.58** (R's `confint()`; Python's `[0.025 0.975]` columns).
- **R-squared = 0.20:** BMI accounts for a fifth of the variation in operative time, the same as r² on [page 10](10-association.qmd#pearson).
- **Residual standard error 14.7** (R only): the typical distance of a patient's operative time from the line, in minutes.

Before trusting the line, plot the residuals against the fitted values: they should form a band of even width around 0, with no curve.

::: {.panel-tabset group="language"}
## R

```{r}
#| fig-height: 3
tibble(fitted = fitted(bmi_model), residual = resid(bmi_model)) |>
  ggplot(aes(fitted, residual)) +
  geom_point(alpha = 0.4) +
  geom_hline(yintercept = 0) +
  labs(x = "Fitted operative time, minutes", y = "Residual, minutes")
```

## Python

```{python}
fig, ax = plt.subplots(figsize=(6, 3))
ax.scatter(bmi_model.fittedvalues, bmi_model.resid, alpha=0.4)
ax.axhline(0, color="black")
ax.set_xlabel("Fitted operative time, minutes")
ax.set_ylabel("Residual, minutes")
plt.show()
```
:::

They do here: an even band, with no curve and no funnel shape.

### Effect size and 95% CI

The **slope** with its 95% CI is the effect size: 1.37 minutes per kg/m² (95% CI 1.15 to 1.58). Scale it to a difference that matters clinically: 5 kg/m² of BMI goes with 6.8 more minutes (95% CI 5.8 to 7.9). **R² = 0.20** says how much of the variation the line explains.

### How to report it

> **Methods:** Operative time was modeled on BMI with simple linear regression.
>
> **Results:** Operative time rose by 1.37 minutes for each 1 kg/m² of BMI (95% CI 1.15 to 1.58, p < 0.001; R² = 0.20), or 6.8 minutes (95% CI 5.8 to 7.9) per 5 kg/m².

::: {.callout-warning}
## ⚠️ Watch out: the line is an average, and only inside your data
The line predicts the **average** operative time at each BMI. Individual patients scatter around it by about 15 minutes either way (the residual standard error), so it's a poor tool for scheduling one patient's case. And BMI here runs from 18.0 to 44.5: don't use the line to predict outside that range.
:::

## Nonlinear regression {#nonlinear-regression}

**The question:** How quickly does KOOS JR recover after knee replacement, and where does it level off?

### When to use it

- The outcome follows a **curve whose shape you know in advance**, and the curve's numbers mean something: here a starting score, a plateau and a recovery rate.
- You supply the formula and rough starting guesses, and the program finds the values that fit best (nonlinear least squares).
- If you don't know the shape → [splines](12-predict-from-several.qmd#multiple-nonlinear-regression) or [LOWESS](#nonparametric-regression). If it's a straight line → [linear regression](#linear-regression).

The recovery curve used here:

$$\text{score} = \text{plateau} - (\text{plateau} - \text{start}) \times e^{-\text{days}/\tau}$$

- **start:** the score on the day of surgery.
- **plateau:** the level the score settles at.
- **τ (tau):** the time constant. After τ days patients have made 63% of their eventual gain, and half of it after τ × ln 2 ≈ 0.69 τ days.

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3.5
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

koos <- proms |>
  filter(instrument == "KOOS JR", !is.na(prom_score)) |>
  mutate(days = pmax(visit_days, 0))   # pre-op visits (1-27 days before surgery) count as day 0

ggplot(koos, aes(days, prom_score)) +
  geom_point(alpha = 0.2) +
  labs(x = "Days since surgery", y = "KOOS JR")

nrow(koos)                # scores
n_distinct(koos$case_id)  # knees
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit

proms = pd.read_csv("data/proms_long.csv")

koos = proms[proms["instrument"] == "KOOS JR"].dropna(subset=["prom_score"]).copy()
koos["days"] = koos["visit_days"].clip(lower=0)   # pre-op visits (1-27 days before surgery) count as day 0

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.scatter(koos["days"], koos["prom_score"], alpha=0.2)
ax.set_xlabel("Days since surgery")
ax.set_ylabel("KOOS JR")
plt.show()

print(len(koos), koos["case_id"].nunique())   # scores, knees
```
:::

1146 scores from 330 knees. The scores climb steeply over the first 3 months, then more slowly toward 1 year: a curve that levels off, not a straight line.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
recovery <- nls(prom_score ~ plateau - (plateau - start) * exp(-days / tau),
                data = koos,
                start = list(plateau = 85, start = 50, tau = 100))   # rough guesses read off the plot
summary(recovery)
```

## Python

```{python}
def recovery_curve(days, plateau, start, tau):
    return plateau - (plateau - start) * np.exp(-days / tau)

estimates, covariance = curve_fit(recovery_curve, koos["days"], koos["prom_score"],
                                  p0=[85, 50, 100])   # rough guesses read off the plot
standard_errors = np.sqrt(np.diag(covariance))
print(pd.DataFrame({"estimate": estimates, "std_error": standard_errors}, index=["plateau", "start", "tau"]))
```
:::

```{python}
#| include: false
chk = {"plateau": float(estimates[0]), "start": float(estimates[1]), "tau": float(estimates[2]),
       "se_plateau": float(standard_errors[0]), "se_tau": float(standard_errors[2])}
```

```{r}
#| include: false
recovery_coef <- summary(recovery)$coefficients
check_agree(list(plateau = recovery_coef["plateau", "Estimate"], start = recovery_coef["start", "Estimate"],
                 tau = recovery_coef["tau", "Estimate"], se_plateau = recovery_coef["plateau", "Std. Error"],
                 se_tau = recovery_coef["tau", "Std. Error"]),
            reticulate::py$chk, tol = 1e-4)   # both approximate the curve's derivatives numerically, so they agree to ~5 digits
```

### Read the output

- **plateau = 84.2:** KOOS JR levels off at about 84 points.
- **start = 49.8:** the estimated score on the day of surgery.
- **tau = 80.9:** the time constant in days.
- **Std. Error:** each estimate's uncertainty. The t values and p-values test whether each number is zero, which nobody doubts here; ignore them.
- **Residual standard error 12.33 on 1143 degrees of freedom** (R only): individual scores scatter about 12 points around the curve.

### Effect size and 95% CI

The curve's numbers, with their 95% CIs, are the effect sizes. Half of the eventual gain comes after τ × ln 2 days.

::: {.panel-tabset group="language"}
## R

```{r}
confint(recovery)                       # profile CIs; see the R vs Python box
log(2) * coef(recovery)[["tau"]]        # days to half of the eventual gain
log(2) * confint(recovery)["tau", ]
```

## Python

```{python}
t_crit = stats.t.ppf(0.975, df=len(koos) - 3)   # 3 parameters
print(pd.DataFrame({"low": estimates - t_crit * standard_errors, "high": estimates + t_crit * standard_errors},
                   index=["plateau", "start", "tau"]))
print(np.log(2) * estimates[2])                  # days to half of the eventual gain
```
:::

KOOS JR rose from about 49.8 points (95% CI 48.5 to 51.2) on the day of surgery toward a plateau of 84.2 (95% CI 82.6 to 85.9). Half of the gain came by about 56 days, 8 weeks (95% CI 49 to 64).

### How to report it

> **Methods:** KOOS JR was modeled against days since surgery with an exponential recovery curve fitted by nonlinear least squares, counting the pre-op score as the score on the day of surgery.
>
> **Results:** In 330 knees (1146 scores), KOOS JR rose from an estimated 49.8 points (95% CI 48.5 to 51.2) at surgery toward a plateau of 84.2 points (95% CI 82.6 to 85.9), with half of the gain reached by about 56 days (95% CI 49 to 64).

::: {.callout-warning}
## ⚠️ Watch out: each knee appears up to four times
Nonlinear least squares treats the 1146 scores as 1146 independent patients, but they come from 330 knees. Scores from the same knee are related, so the CIs here are too narrow. A mixed model ([page 16](../beyond/16-mixed-models.qmd)) accounts for this. And if the fit fails to converge, try starting guesses closer to what the plot shows.
:::

::: {.callout-tip}
## 🔀 R vs Python: two kinds of CI
- R's `nls()` and scipy's `curve_fit()` use different fitting algorithms but find the same estimates and standard errors.
- R's `confint()` **profiles** the fit: it moves each number away from its estimate until the fit gets significantly worse. scipy gives only the standard errors, so the Python code uses estimate ± t × standard error. The two CIs differ slightly; here τ's CI runs from 71.0 to 92.5 days in R and 69.9 to 91.8 in Python. Either is fine; say which you used.
:::

## Nonparametric regression {#nonparametric-regression}

**The question:** How does KOOS JR at 1 year depend on KOOS JR before surgery, when many patients reach the ceiling of 100?

### When to use it

- The outcome is a measurement that **isn't normal**: it has a ceiling, a skew or outliers, so the residuals of a straight line won't be normal.
- **LOWESS** (locally weighted smoothing) draws the shape without a formula: it fits many small lines, each to the points near it, and joins them into a smooth curve. It gives a picture, not a p-value.
- The **Theil-Sen slope** is the median of the slopes between every pair of patients. A few extreme patients barely move it, and its CI comes from ranks, not from normal residuals.
- If the residuals are roughly normal → [linear regression](#linear-regression).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3.5
library(tidyverse)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)

koos_wide <- proms |>
  filter(instrument == "KOOS JR", visit %in% c("preop", "1yr")) |>
  select(case_id, visit, prom_score) |>
  pivot_wider(names_from = visit, values_from = prom_score) |>   # one row per knee
  rename(one_year = `1yr`) |>
  filter(!is.na(preop), !is.na(one_year))

smooth <- lowess(koos_wide$preop, koos_wide$one_year)   # LOWESS curve, R's defaults

ggplot(koos_wide, aes(preop, one_year)) +
  geom_point(alpha = 0.4) +
  geom_line(data = tibble(preop = smooth$x, one_year = smooth$y), linewidth = 1) +
  labs(x = "KOOS JR before surgery", y = "KOOS JR at 1 year")

nrow(koos_wide)
sum(koos_wide$one_year == 100)   # at the ceiling
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.nonparametric.smoothers_lowess import lowess

proms = pd.read_csv("data/proms_long.csv")

koos_wide = (proms[(proms["instrument"] == "KOOS JR") & proms["visit"].isin(["preop", "1yr"])]
             .pivot(index="case_id", columns="visit", values="prom_score")   # one row per knee
             .dropna(subset=["preop", "1yr"]))

smooth = lowess(koos_wide["1yr"], koos_wide["preop"], frac=2/3, it=3,
                delta=0.01 * np.ptp(koos_wide["preop"]))   # R's lowess() defaults

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.scatter(koos_wide["preop"], koos_wide["1yr"], alpha=0.4)
ax.plot(smooth[:, 0], smooth[:, 1], linewidth=2)
ax.set_xlabel("KOOS JR before surgery")
ax.set_ylabel("KOOS JR at 1 year")
plt.show()

print(len(koos_wide), (koos_wide["1yr"] == 100).sum())   # knees, at the ceiling
```
:::

```{python}
#| include: false
chk = {"low_end": float(smooth[0, 1]), "middle": float(smooth[100, 1]), "high_end": float(smooth[-1, 1])}
```

```{r}
#| include: false
check_agree(list(low_end = smooth$y[1], middle = smooth$y[101], high_end = smooth$y[length(smooth$y)]), reticulate::py$chk)
```

246 knees have both scores, and 37 of them (15.0%) score the maximum of 100 at 1 year. The LOWESS curve rises steadily from about 70 to about 99 across the range of pre-op scores.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
koos_slope <- deming::theilsen(one_year ~ preop, data = koos_wide)
coef(koos_slope)     # intercept and slope
koos_slope$ci[2, ]   # 95% CI for the slope
```

## Python

```{python}
koos_slope = stats.theilslopes(koos_wide["1yr"], koos_wide["preop"], method="joint")   # see the R vs Python box
print(koos_slope)
```
:::

```{python}
#| include: false
chk = {"slope": float(koos_slope.slope), "intercept": float(koos_slope.intercept)}
```

```{r}
#| include: false
check_agree(list(slope = coef(koos_slope)[["preop"]], intercept = coef(koos_slope)[["(Intercept)"]]), reticulate::py$chk)
```

### Read the output

- **preop** (R) or **slope** (Python) **= 0.39:** each extra point before surgery goes with 0.39 more points at 1 year (the median of all the pairwise slopes).
- **Intercept = 65.4:** the predicted 1-year score for a pre-op score of 0; it anchors the line.
- **95% CI for the slope:** 0.28 to 0.51 in R, 0.27 to 0.52 in Python (`low_slope`, `high_slope`). The R vs Python box explains the difference.

### Effect size and 95% CI

The **Theil-Sen slope** with its CI is the effect size: 0.39 points at 1 year per pre-op point (95% CI 0.28 to 0.51). An ordinary least-squares line gives 0.43; the two would differ more if a few unusual patients pulled the least-squares line.

### How to report it

> **Methods:** Because 1-year KOOS JR clustered at the ceiling, its relationship with pre-op KOOS JR was described with a LOWESS smoother and summarized with the Theil-Sen slope.
>
> **Results:** Among 246 knees, 37 (15.0%) scored 100 at 1 year. KOOS JR at 1 year rose with KOOS JR before surgery (Theil-Sen slope 0.39 points per point, 95% CI 0.28 to 0.51).

::: {.callout-warning}
## ⚠️ Watch out: robust isn't ceiling-proof
Theil-Sen resists outliers, but nothing can see above a ceiling: the 37 knees at 100 might have scored higher on a longer scale, so the true slope at the top of the range is unknown. And a LOWESS curve is least reliable at its two ends, where it rests on few patients.
:::

::: {.callout-tip}
## 🔀 R vs Python: Theil-Sen intercepts and CIs, LOWESS settings
- **Intercept:** scipy's default (`method="separate"`) computes it as median(y) − slope × median(x). deming computes median(y − slope × x), which scipy calls `method="joint"`. The slope is the same either way.
- **CI:** both use Sen's rank method, but deming adjusts for tied values of x only, and scipy for ties in both x and y, so the limits differ a little.
- **LOWESS:** R's `lowess()` and statsmodels' `lowess()` run the same algorithm, but statsmodels' defaults differ (it sets `delta` to 0), so the Python code spells out R's settings. ggplot2's `geom_smooth()` uses a different smoother, `loess()`, which draws a similar but not identical curve.
:::

## Simple logistic regression {#logistic-regression}

**The question:** Does the risk of a complication within 90 days rise with age?

### When to use it

- The outcome is **yes/no** (complication or not), and you want the **odds ratio** per unit of one predictor.
- It assumes the log odds change in a straight line with the predictor: each extra decade multiplies the odds by the same amount.
- You need enough patients with the outcome: a common rule of thumb is at least 10 per predictor.
- If the outcome is time until an event → [Cox regression](#cox).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(age_10 = age / 10)   # age in decades, so the odds ratio is per 10 years

by_age <- cohort |>
  mutate(age_band = cut(age, breaks = c(-Inf, 59, 69, 79, Inf), labels = c("under 60", "60-69", "70-79", "80+"))) |>
  group_by(age_band) |>
  summarise(n = n(), complications = sum(complication_90d), percent = 100 * mean(complication_90d))
by_age

ggplot(by_age, aes(age_band, percent)) +
  geom_col() +
  labs(x = "Age at surgery", y = "Complications within 90 days, %")
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

cohort = pd.read_csv("data/cohort.csv")
cohort["age_10"] = cohort["age"] / 10   # age in decades, so the odds ratio is per 10 years

bands = pd.cut(cohort["age"], bins=[-np.inf, 59, 69, 79, np.inf], labels=["under 60", "60-69", "70-79", "80+"])
by_age = cohort.groupby(bands, observed=True)["complication_90d"].agg(n="count", complications="sum", percent="mean")
by_age["percent"] = 100 * by_age["percent"]
print(by_age)

fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.bar(by_age.index.astype(str), by_age["percent"])
ax.set_xlabel("Age at surgery")
ax.set_ylabel("Complications within 90 days, %")
plt.show()
```
:::

Complications followed 5 of 151 procedures (3.3%) in patients under 60 and 14 of 53 (26.4%) in patients aged 80 or more; 51 of 600 overall.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
age_model <- glm(complication_90d ~ age_10, family = binomial, data = cohort)   # binomial = yes/no outcome
summary(age_model)
```

## Python

```{python}
age_model = smf.logit("complication_90d ~ age_10", data=cohort).fit(disp=False)   # disp=False: no fitting messages
print(age_model.summary())
```
:::

```{python}
#| include: false
wald = age_model.conf_int()
chk = {"coef": float(age_model.params["age_10"]), "se": float(age_model.bse["age_10"]),
       "p": float(age_model.pvalues["age_10"]), "low": float(wald.loc["age_10", 0]), "high": float(wald.loc["age_10", 1])}
```

```{r}
#| include: false
age_coef <- summary(age_model)$coefficients
check_agree(list(coef = age_coef["age_10", "Estimate"], se = age_coef["age_10", "Std. Error"], p = age_coef["age_10", "Pr(>|z|)"],
                 low = confint.default(age_model)["age_10", 1], high = confint.default(age_model)["age_10", 2]),
            reticulate::py$chk, tol = 1e-4)   # glm() stops once the deviance settles, a step before statsmodels does
```

### Read the output

- **age_10 = 0.75:** the change in the **log odds** of a complication per 10 years of age. Log odds are hard to read, so turn the coefficient into an odds ratio (next step).
- **Std. Error 0.17, z = 4.42, p < 0.001:** the test of whether age matters at all.
- **Intercept = −7.49:** the log odds at age 0, which only anchors the line.
- **Null and residual deviance** (R) or **LLR p-value** (Python): how much better the model fits with age than without it.

### Effect size and 95% CI

The **odds ratio** is e raised to the coefficient.

::: {.panel-tabset group="language"}
## R

```{r}
exp(cbind(odds_ratio = coef(age_model), confint(age_model)))   # profile CIs; see the R vs Python box
```

## Python

```{python}
odds_ratios = np.exp(pd.concat([age_model.params, age_model.conf_int()], axis=1))   # Wald CIs
odds_ratios.columns = ["odds_ratio", "low", "high"]
print(odds_ratios)
```
:::

Each 10 years of age multiplied the odds of a complication by 2.12 (95% CI 1.53 to 2.98).

### How to report it

> **Methods:** The association between age and complications within 90 days was estimated with logistic regression, with age in 10-year units.
>
> **Results:** Complications followed 51 of 600 procedures (8.5%). Each 10 years of age was associated with higher odds of a complication (odds ratio 2.12, 95% CI 1.53 to 2.98, p < 0.001).

::: {.callout-warning}
## ⚠️ Watch out: a straight line on the log-odds scale is an assumption
The model says each decade multiplies the odds by the same 2.12. The table above suggests otherwise: the rate barely changes between the 60s and the 70s, then jumps after 80. Check the shape before trusting a single odds ratio; [splines](12-predict-from-several.qmd#multiple-nonlinear-regression) let the effect bend. And an odds ratio isn't a risk ratio: the two are close only when the outcome is rare, as it is here (8.5%).
:::

::: {.callout-tip}
## 🔀 R vs Python: profile and Wald CIs
R's `confint()` on a `glm()` **profiles** the likelihood, which is more accurate in small samples. statsmodels' `conf_int()` uses the simpler **Wald** method (estimate ± 1.96 standard errors), which gives 1.52 to 2.95 here; R's `confint.default()` does the same. Say which you used.
:::

## Cox regression {#cox}

**The question:** Does the hazard of revision rise with age at surgery?

### When to use it

- The outcome is **time until an event** (revision), and the predictor is a **measurement** (age).
- Cox regression gives a **hazard ratio per unit** of the predictor. Choose a unit that means something: per 10 years, not per year.
- It assumes the hazard ratio stays the same over time (**proportional hazards**) and that the log hazard changes in a straight line with age. [Page 14](../survival/14-cox-regression.qmd) shows how to check both and covers Cox regression in full.

### Look at the data first

Splitting age in two is only for the picture; the model uses age as a number.

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 4.5
library(tidyverse)
library(survival)
library(ggsurvfit)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(age_10 = age / 10,                                                  # age in decades
         age_group = if_else(age >= 70, "70 or older", "under 70"))          # for the plot only

survfit2(Surv(followup_years, revised) ~ age_group, data = cohort, conf.type = "log-log") |>
  ggsurvfit() +
  add_risktable() +
  scale_ggsurvfit() +
  labs(x = "Years since surgery", y = "Revision-free survival")
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.plotting import add_at_risk_counts

cohort = pd.read_csv("data/cohort.csv")
cohort["age_10"] = cohort["age"] / 10                                         # age in decades
cohort["age_group"] = cohort["age"].map(lambda age: "70 or older" if age >= 70 else "under 70")   # for the plot only

fig, ax = plt.subplots(figsize=(7, 4.5))
curves = []
for group_name, group in cohort.groupby("age_group"):
    km = KaplanMeierFitter(label=group_name).fit(group["followup_years"], group["revised"])
    km.plot_survival_function(ax=ax, ci_show=False)
    curves.append(km)
ax.set_xlabel("Years since surgery")
ax.set_ylabel("Revision-free survival")
add_at_risk_counts(*curves, ax=ax)
plt.tight_layout()
plt.show()
```
:::

29 of 200 procedures in patients aged 70 or older were revised, against 52 of 400 in younger patients. The curves separate a little, with wide overlap.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
age_cox <- coxph(Surv(followup_years, revised) ~ age_10, data = cohort)
summary(age_cox)
```

## Python

```{python}
age_cox = CoxPHFitter().fit(cohort[["followup_years", "revised", "age_10"]],
                            duration_col="followup_years", event_col="revised")
print(age_cox.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]])
print(age_cox.log_likelihood_ratio_test().test_statistic)   # overall likelihood ratio test
```
:::

```{python}
#| include: false
row = age_cox.summary.loc["age_10"]
chk = {"hr": float(row["exp(coef)"]), "low": float(row["exp(coef) lower 95%"]), "high": float(row["exp(coef) upper 95%"]),
       "p": float(row["p"]), "lr": float(age_cox.log_likelihood_ratio_test().test_statistic)}
```

```{r}
#| include: false
age_hr <- summary(age_cox)$conf.int
check_agree(list(hr = age_hr["age_10", "exp(coef)"], low = age_hr["age_10", "lower .95"], high = age_hr["age_10", "upper .95"],
                 p = summary(age_cox)$coefficients["age_10", "Pr(>|z|)"], lr = unname(summary(age_cox)$logtest["test"])),
            reticulate::py$chk)
```

### Read the output

- **exp(coef) = 1.25:** the hazard ratio per 10 years of age: the hazard of revision is 1.25 times higher for a patient 10 years older.
- **lower .95 / upper .95 = 0.98 to 1.59:** the 95% CI, which includes 1 (no difference).
- **Pr(>|z|) = 0.073:** the p-value for age.
- **Likelihood ratio test = 3.23 on 1 df, p = 0.07:** the overall test; with one predictor it says the same as the p-value for age.
- **Concordance = 0.56** (R only): how often the model ranks two patients' revision times correctly. 0.5 is a coin toss, so age alone predicts revision poorly.

### Effect size and 95% CI

The **hazard ratio per 10 years**, 1.25 (95% CI 0.98 to 1.59), is the effect size. The CI is wide: the data fit a small decrease in hazard with age as well as a 59% increase per decade.

### How to report it

> **Methods:** The association between age at surgery and revision was estimated with Cox proportional hazards regression, with age in 10-year units.
>
> **Results:** The hazard of revision was 1.25 times higher per 10 years of age, but the estimate was imprecise (95% CI 0.98 to 1.59, p = 0.073).

::: {.callout-warning}
## ⚠️ Watch out: older patients die before they can be revised
Deaths are treated as censored here. Older patients die sooner, so fewer of them live long enough to need a revision. That can hide an age effect, or create one. [Page 13](../survival/13-kaplan-meier.qmd) covers these competing risks.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
bmi_ci <- confint(bmi_model)
recovery_ci <- confint(recovery)
age_ci <- exp(confint(age_model))
age_wald <- exp(confint.default(age_model))
koos_ls <- coef(lm(one_year ~ preop, data = koos_wide))
ex_age <- lm(op_time_min ~ age, data = cohort)
ex_facility <- glm(I(discharge == "facility") ~ age_10, family = binomial, data = cohort)
ex_hoos <- proms |> filter(instrument == "HOOS JR", !is.na(prom_score)) |> mutate(days = pmax(visit_days, 0))
ex_hoos_fit <- nls(prom_score ~ plateau - (plateau - start) * exp(-days / tau), data = ex_hoos,
                   start = list(plateau = 85, start = 50, tau = 100))
ex_hoos_ci <- confint(ex_hoos_fit)
stopifnot(
  sum(table(cohort$patient_id) == 2) == 80, nrow(cohort) == 600,
  round(coef(bmi_model), 2) == c(42.83, 1.37), round(bmi_fit$coefficients["bmi", "Std. Error"], 2) == 0.11,
  round(bmi_fit$coefficients["bmi", "t value"], 1) == 12.4, bmi_fit$coefficients["bmi", "Pr(>|t|)"] < 0.001,
  round(bmi_ci["bmi", ], 2) == c(1.15, 1.58), round(bmi_fit$r.squared, 2) == 0.20, round(bmi_fit$sigma, 1) == 14.7,
  round(5 * coef(bmi_model)[["bmi"]], 1) == 6.8, round(5 * bmi_ci["bmi", ], 1) == c(5.8, 7.9),
  range(cohort$bmi) == c(18.0, 44.5),
  range(proms$visit_days[proms$visit == "preop"], na.rm = TRUE) == c(-27, -1),
  nrow(koos) == 1146, n_distinct(koos$case_id) == 330,
  round(recovery_coef[, "Estimate"], 1) == c(84.2, 49.8, 80.9), round(summary(recovery)$sigma, 2) == 12.33,
  df.residual(recovery) == 1143,
  round(recovery_ci["plateau", ], 1) == c(82.6, 85.9), round(recovery_ci["start", ], 1) == c(48.5, 51.2),
  round(recovery_ci["tau", ], 1) == c(71.0, 92.5),
  round(log(2) * coef(recovery)[["tau"]]) == 56, round(log(2) * recovery_ci["tau", ]) == c(49, 64),
  round(log(2) * coef(recovery)[["tau"]] / 7) == 8, round(1 - exp(-1), 2) == 0.63, round(log(2), 2) == 0.69,
  round(recovery_coef["tau", "Estimate"] + c(-1, 1) * qt(0.975, 1143) * recovery_coef["tau", "Std. Error"], 1) == c(69.9, 91.8),
  nrow(koos_wide) == 246, sum(koos_wide$one_year == 100) == 37, round(100 * mean(koos_wide$one_year == 100), 1) == 15.0,
  round(smooth$y[1]) == 70, round(smooth$y[length(smooth$y)]) == 99,
  round(coef(koos_slope), 2) == c(65.39, 0.39), round(koos_slope$ci[2, ], 2) == c(0.28, 0.51),
  round(koos_ls[["preop"]], 2) == 0.43,
  round(age_coef["age_10", c("Estimate", "Std. Error", "z value")], 2) == c(0.75, 0.17, 4.42),
  round(age_coef["(Intercept)", "Estimate"], 2) == -7.49, age_coef["age_10", "Pr(>|z|)"] < 0.001,
  round(exp(coef(age_model))[["age_10"]], 2) == 2.12, round(age_ci["age_10", ], 2) == c(1.53, 2.98),
  round(age_wald["age_10", ], 2) == c(1.52, 2.95),
  by_age$n == c(151, 249, 147, 53), by_age$complications[c(1, 4)] == c(5, 14),
  round(by_age$percent[c(1, 4)], 1) == c(3.3, 26.4), sum(cohort$complication_90d) == 51,
  round(100 * mean(cohort$complication_90d), 1) == 8.5,
  sum(cohort$age >= 70) == 200, sum(cohort$revised[cohort$age >= 70]) == 29, sum(cohort$revised[cohort$age < 70]) == 52,
  round(age_hr["age_10", c("exp(coef)", "lower .95", "upper .95")], 2) == c(1.25, 0.98, 1.59),
  round(summary(age_cox)$coefficients["age_10", "Pr(>|z|)"], 3) == 0.073,
  round(unname(summary(age_cox)$logtest["test"]), 2) == 3.23, round(unname(summary(age_cox)$logtest["pvalue"]), 2) == 0.07,
  round(unname(summary(age_cox)$concordance[1]), 2) == 0.56,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(coef(ex_age)[["age"]], 2) == 0.24, round(confint(ex_age)["age", ], 2) == c(0.11, 0.38),
  summary(ex_age)$coefficients["age", "Pr(>|t|)"] < 0.001, round(summary(ex_age)$r.squared, 2) == 0.02,
  sum(cohort$discharge == "facility") == 30,
  round(exp(coef(ex_facility))[["age_10"]], 2) == 2.06, round(exp(confint(ex_facility))["age_10", ], 2) == c(1.37, 3.17),
  summary(ex_facility)$coefficients["age_10", "Pr(>|z|)"] < 0.001,
  nrow(ex_hoos) == 906, n_distinct(ex_hoos$case_id) == 270,
  round(coef(ex_hoos_fit), 1) == c(87.9, 45.6, 53.4),
  round(ex_hoos_ci["plateau", ], 1) == c(86.3, 89.4), round(ex_hoos_ci["start", ], 1) == c(44.2, 46.9),
  round(log(2) * coef(ex_hoos_fit)[["tau"]]) == 37, round(log(2) * ex_hoos_ci["tau", ]) == c(33, 41)
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** How much does operative time change with **age**? Fit a simple linear regression and report the slope with its 95% CI.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
age_time <- lm(op_time_min ~ age, data = cohort)
summary(age_time)$coefficients
confint(age_time)
summary(age_time)$r.squared
```

## Python

```{python}
age_time = smf.ols("op_time_min ~ age", data=cohort).fit()
print(age_time.params, age_time.conf_int(), age_time.rsquared, sep="\n")
```
:::

Operative time rose by 0.24 minutes per year of age (95% CI 0.11 to 0.38, p < 0.001), or about 2.4 minutes per decade. Age explains only 2% of the variation (R² = 0.02), against 20% for BMI.
:::

**2.** A colleague asks whether older patients are more likely to be discharged to a facility rather than home. Which regression would you use, and what do you find?

::: {.callout-tip collapse="true"}
## Solution
The outcome is yes/no (facility or home) and the predictor is a measurement: **simple logistic regression**. Only 30 patients went to a facility, enough for one predictor.

::: {.panel-tabset group="language"}
## R

```{r}
facility_model <- glm(I(discharge == "facility") ~ age_10, family = binomial, data = cohort)
exp(cbind(odds_ratio = coef(facility_model), confint(facility_model)))
summary(facility_model)$coefficients
```

## Python

```{python}
cohort["facility"] = (cohort["discharge"] == "facility").astype(int)
facility_model = smf.logit("facility ~ age_10", data=cohort).fit(disp=False)
facility_ors = np.exp(pd.concat([facility_model.params, facility_model.conf_int()], axis=1))
facility_ors.columns = ["odds_ratio", "low", "high"]
print(facility_ors, facility_model.pvalues, sep="\n")
```
:::

Each 10 years of age was associated with higher odds of discharge to a facility (odds ratio 2.06, 95% CI 1.37 to 3.17, p < 0.001; R's profile CI).
:::

**3.** Fit the recovery curve to **HOOS JR** (hip replacements) and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
hoos <- proms |>
  filter(instrument == "HOOS JR", !is.na(prom_score)) |>
  mutate(days = pmax(visit_days, 0))
hip_recovery <- nls(prom_score ~ plateau - (plateau - start) * exp(-days / tau),
                    data = hoos, start = list(plateau = 85, start = 50, tau = 100))
coef(hip_recovery)
confint(hip_recovery)
log(2) * confint(hip_recovery)["tau", ]
c(scores = nrow(hoos), hips = n_distinct(hoos$case_id))
```

## Python

```{python}
hoos = proms[proms["instrument"] == "HOOS JR"].dropna(subset=["prom_score"]).copy()
hoos["days"] = hoos["visit_days"].clip(lower=0)
hip_estimates, hip_covariance = curve_fit(recovery_curve, hoos["days"], hoos["prom_score"], p0=[85, 50, 100])
print(hip_estimates, np.sqrt(np.diag(hip_covariance)), np.log(2) * hip_estimates[2])
print(len(hoos), hoos["case_id"].nunique())
```
:::

"In 270 hips (906 scores), HOOS JR rose from an estimated 45.6 points (95% CI 44.2 to 46.9) at surgery toward a plateau of 87.9 points (95% CI 86.3 to 89.4), with half of the gain reached by about 37 days (95% CI 33 to 41)."

Hips seem to recover faster than knees (half the gain by about 5 weeks, against 8). To test that difference, fit both in one model ([page 12](12-predict-from-several.qmd#multiple-nonlinear-regression)).
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/11-predict-from-one.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `198 passed`.

- [ ] **Step 5: Prove the Wald check and the message setting bite, then restore**

First, in the `#logistic-regression` section's hidden R check, change `low = confint.default(age_model)["age_10", 1], high = confint.default(age_model)["age_10", 2]),` to `low = confint(age_model)["age_10", 1], high = confint(age_model)["age_10", 2]),` (R's profile CI). Run `quarto render catalog/11-predict-from-one.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'low'`. Undo the change.

Second, delete these three lines from `_quarto.yml`:

```yaml
knitr:
  opts_chunk:
    message: false
```

Then run:

```bash
rm -rf catalog/11-predict-from-one_files
quarto render catalog/11-predict-from-one.qmd
uv run pytest tests/site/test_catalog.py -q -k "no_warnings and 11-"
```

Expected: `test_page_shows_no_warnings_or_package_messages[catalog/11-predict-from-one.html]` FAILS, showing "Waiting for profiling to be done...". Restore the three lines (`git checkout -- _quarto.yml`), then run:

```bash
quarto render catalog/11-predict-from-one.qmd
uv run pytest tests/site -q
```

Expected: `198 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/11-predict-from-one.qmd _freeze/catalog/11-predict-from-one tests/site/test_catalog.py
git commit -m "Write page 11, predict from one variable: linear, nonlinear, nonparametric, logistic, Cox

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Page 12, Predict a value from several variables

**Files:**
- Modify: `catalog/12-predict-from-several.qmd` (replace the stub)
- Create: `_freeze/catalog/12-predict-from-several/` (render output; commit it)
- Modify: `tests/site/test_catalog.py`

**Interfaces:**
- Consumes:
  - Task 4's `WRITTEN`, `SURVIVAL_LINKS` and `REPEATED_SCORE_SECTIONS` (their page-12 entries activate now) and page 11's anchors (`#nonlinear-regression`, `#logistic-regression`, `#exercises`)
  - `data/cohort.csv`, `data/proms_long.csv`
- Produces: page 12 anchors `#multiple-linear-regression`, `#multiple-nonlinear-regression`, `#multiple-logistic-regression` and `#cox`, which pages 10 and 11 link to.

- [ ] **Step 1: Write the failing tests**

In `tests/site/test_catalog.py`, replace

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
    "catalog/11-predict-from-one.html",
]
```

with

```python
WRITTEN = [
    "catalog/04-describe-one-group.html",
    "catalog/05-one-group-vs-hypothetical.html",
    "catalog/06-two-unpaired-groups.html",
    "catalog/07-two-paired-groups.html",
    "catalog/08-three-plus-unmatched.html",
    "catalog/09-three-plus-matched.html",
    "catalog/10-association.html",
    "catalog/11-predict-from-one.html",
    "catalog/12-predict-from-several.html",
]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/site -q`

Expected: `14 failed, 200 passed`. 14 of the 16 new page-12 tests fail, including its survival link and repeated-scores warning, which activate now.

- [ ] **Step 3: Write the page**

Replace `catalog/12-predict-from-several.qmd` with:

````markdown
---
title: "12 · Predict a value from several variables"
description: "Multiple linear and nonlinear regression, multiple logistic regression and Cox regression: the effect of each predictor, adjusted for the others."
engine: knitr
toc-depth: 2
---

```{r}
#| include: false
source("R/check_agree.R")
```

```{r}
#| echo: false
#| output: asis
# Stamp the data version into the page; tests/site/test_freshness.py checks it.
cat(sprintf("<!-- data-checksum: %s -->", unname(tools::md5sum("data/CHECKSUMS.md5"))))
```

Outcomes rarely depend on one thing. Heavier patients may take longer to operate on, but so may older ones, and knees take longer than hips. **Multiple regression** puts several predictors in one model, so each coefficient is that predictor's effect **with the others held fixed**: adjusted for them. The regressions are the same four as on [page 11](11-predict-from-one.qmd), with more than one predictor.

::: {.callout-note}
## 💡 How every section on this page works
Each section answers one question about the practice cohort. Its first code block loads the packages and the data, so you can jump straight to the section you need. Run that section's blocks in order, top to bottom.

To keep the code short, the examples use every case, including the 80 patients who had both sides operated on. In a real study, decide how to handle them ([page 3](../foundations/03-distributions.qmd#paired)) and say what you did.
:::

## Multiple linear regression {#multiple-linear-regression}

**The question:** Does BMI still predict operative time once age, sex and procedure are taken into account?

### When to use it

- The outcome is a **measurement**, and you want the effect of each of **several predictors**, adjusted for the others.
- The assumptions of [simple linear regression](11-predict-from-one.qmd#linear-regression) still apply: straight-line effects, independent patients, and residuals that are roughly normal with an even spread.
- Choose the predictors **before** looking at the results, from what you know clinically. As a rule of thumb, allow at least 10 to 20 patients per predictor.
- If an effect may bend → [splines](#multiple-nonlinear-regression). If the outcome is yes/no → [multiple logistic regression](#multiple-logistic-regression).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3.5
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

ggplot(cohort, aes(bmi, op_time_min, colour = procedure)) +
  geom_point(alpha = 0.5) +
  labs(x = "BMI, kg/m²", y = "Operative time, minutes", colour = "Procedure")

cohort |>
  group_by(procedure) |>
  summarise(n = n(), mean = mean(op_time_min), sd = sd(op_time_min))
```

## Python

```{python}
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

cohort = pd.read_csv("data/cohort.csv")

fig, ax = plt.subplots(figsize=(6, 3.5))
for procedure, group in cohort.groupby("procedure"):
    ax.scatter(group["bmi"], group["op_time_min"], alpha=0.5, label=procedure)
ax.set_xlabel("BMI, kg/m²")
ax.set_ylabel("Operative time, minutes")
legend = ax.legend(title="Procedure")
plt.show()

print(cohort.groupby("procedure")["op_time_min"].agg(["count", "mean", "std"]))
```
:::

Operative time rises with BMI for both procedures, and TKAs take longer than THAs on average: 88.3 minutes (SD 16.2) against 79.8 (SD 15.5).

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
time_model <- lm(op_time_min ~ bmi + age + sex + procedure, data = cohort)   # predictors joined with +
summary(time_model)
confint(time_model)
```

## Python

```{python}
time_model = smf.ols("op_time_min ~ bmi + age + sex + procedure", data=cohort).fit()   # predictors joined with +
print(time_model.summary())
```
:::

```{python}
#| include: false
ci = time_model.conf_int()
chk = {"bmi": float(time_model.params["bmi"]), "age": float(time_model.params["age"]),
       "male": float(time_model.params["sex[T.Male]"]), "tka": float(time_model.params["procedure[T.TKA]"]),
       "bmi_low": float(ci.loc["bmi", 0]), "bmi_high": float(ci.loc["bmi", 1]),
       "r2": float(time_model.rsquared), "adj_r2": float(time_model.rsquared_adj)}
```

```{r}
#| include: false
time_fit <- summary(time_model)
time_ci <- confint(time_model)
check_agree(list(bmi = coef(time_model)[["bmi"]], age = coef(time_model)[["age"]], male = coef(time_model)[["sexMale"]],
                 tka = coef(time_model)[["procedureTKA"]], bmi_low = time_ci["bmi", 1], bmi_high = time_ci["bmi", 2],
                 r2 = time_fit$r.squared, adj_r2 = time_fit$adj.r.squared), reticulate::py$chk)
```

### Read the output

Each coefficient is the change in operative time for one unit of that predictor, **with the other predictors held fixed**:

- **bmi = 1.27:** 1.27 more minutes per kg/m² (95% CI 1.06 to 1.49), for patients of the same age, sex and procedure.
- **age = 0.27:** 0.27 more minutes per year of age (95% CI 0.15 to 0.39).
- **sexMale** (R) or **sex[T.Male]** (Python) **= −1.48:** men took 1.48 minutes less than women, but the CI (−3.81 to 0.84) includes 0. Women are the reference group because "Female" comes first alphabetically.
- **procedureTKA = 6.74:** TKAs took 6.74 minutes longer than THAs (95% CI 4.40 to 9.08).
- **Multiple R-squared = 0.27, adjusted R-squared = 0.26:** the four predictors together explain about a quarter of the variation. The adjusted value is penalized for the number of predictors.
- **F-statistic, p < 0.001:** the test that all four predictors together explain nothing.

### Effect size and 95% CI

The **adjusted coefficients** with their 95% CIs are the effect sizes, with **R²** for the model as a whole. BMI's coefficient fell only a little after adjustment, from 1.37 minutes per kg/m² on its own ([page 11](11-predict-from-one.qmd#linear-regression)) to 1.27: age, sex and procedure explain little of BMI's link with operative time.

### How to report it

> **Methods:** Operative time was modeled with multiple linear regression on BMI, age, sex and procedure, chosen before the analysis.
>
> **Results:** Adjusted for age, sex and procedure, each 1 kg/m² of BMI was associated with 1.27 minutes longer operative time (95% CI 1.06 to 1.49, p < 0.001). TKAs took 6.74 minutes longer than THAs (95% CI 4.40 to 9.08), and each year of age added 0.27 minutes (95% CI 0.15 to 0.39). The model explained 27% of the variation in operative time (R² = 0.27).

::: {.callout-warning}
## ⚠️ Watch out: "adjusted" isn't "caused", and more predictors isn't better
Adjusting removes the part of an effect explained by the variables **in** the model, not by the ones you left out or never measured, so an adjusted coefficient still isn't proof of cause. Choose the predictors in advance and stop there: adding variables until something becomes significant, or dropping those that don't (stepwise selection), gives results that won't replicate.
:::

::: {.callout-tip}
## 🔀 R vs Python: names for the same coefficients
Both programs use the first category alphabetically as the reference (Female, THA). R names the coefficients `sexMale` and `procedureTKA`; statsmodels names them `sex[T.Male]` and `procedure[T.TKA]` (T for "treatment" coding). The numbers are the same.
:::

## Multiple nonlinear regression {#multiple-nonlinear-regression}

**The question:** Do hips recover faster than knees after joint replacement?

### When to use it

- **The curve's shape is known, but its numbers may depend on other variables.** Extend the [recovery curve](11-predict-from-one.qmd#nonlinear-regression) so that each of its numbers can differ between hips and knees, and fit one model with nonlinear least squares.
- **The shape isn't known.** Let a measured predictor's effect bend with a **spline**: a flexible curve made of short cubic pieces joined smoothly at points called knots. A **natural** (or **restricted**) cubic spline is a straight line beyond the outer knots, which keeps it from flailing at the ends. Splines fit inside an ordinary linear, logistic or Cox model, and they're the usual way to check whether a straight line is good enough.
- If every effect is a straight line → [multiple linear regression](#multiple-linear-regression).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
#| fig-height: 3.5
library(tidyverse)
library(splines)

proms <- read_csv("data/proms_long.csv", show_col_types = FALSE)
cohort <- read_csv("data/cohort.csv", show_col_types = FALSE)

recovery_data <- proms |>
  filter(!is.na(prom_score)) |>
  mutate(days = pmax(visit_days, 0),                        # pre-op visits count as day 0
         joint = if_else(instrument == "HOOS JR", "hip", "knee"),
         knee = as.numeric(joint == "knee"))                # 1 = knee, 0 = hip

ggplot(recovery_data, aes(days, prom_score, colour = joint)) +
  geom_point(alpha = 0.15) +
  labs(x = "Days since surgery", y = "HOOS JR (hips) or KOOS JR (knees)", colour = "Joint")

count(recovery_data, joint)
```

## Python

```{python}
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy import stats
from scipy.optimize import curve_fit
from statsmodels.stats.anova import anova_lm

proms = pd.read_csv("data/proms_long.csv")
cohort = pd.read_csv("data/cohort.csv")

recovery_data = proms.dropna(subset=["prom_score"]).copy()
recovery_data["days"] = recovery_data["visit_days"].clip(lower=0)             # pre-op visits count as day 0
recovery_data["knee"] = (recovery_data["instrument"] == "KOOS JR").astype(int)   # 1 = knee, 0 = hip

fig, ax = plt.subplots(figsize=(6, 3.5))
for knee, group in recovery_data.groupby("knee"):
    ax.scatter(group["days"], group["prom_score"], alpha=0.15, label="knee" if knee else "hip")
ax.set_xlabel("Days since surgery")
ax.set_ylabel("HOOS JR (hips) or KOOS JR (knees)")
legend = ax.legend(title="Joint")
plt.show()

print(recovery_data["knee"].value_counts())
```
:::

2052 scores: 906 from hips and 1146 from knees. Both rise and level off; the hip scores seem to get there sooner.

### Run it

Each of the curve's three numbers gets a value for hips and a difference for knees: for a knee, `plateau = plateau_hip + plateau_diff`, and the same for `start` and `tau`.

::: {.panel-tabset group="language"}
## R

```{r}
recovery_by_joint <- function(days, knee, plateau_hip, plateau_diff, start_hip, start_diff, tau_hip, tau_diff) {
  plateau <- plateau_hip + plateau_diff * knee   # knee = 0 for hips, 1 for knees
  start <- start_hip + start_diff * knee
  tau <- tau_hip + tau_diff * knee
  plateau - (plateau - start) * exp(-days / tau)
}

joint_recovery <- nls(
  prom_score ~ recovery_by_joint(days, knee, plateau_hip, plateau_diff, start_hip, start_diff, tau_hip, tau_diff),
  data = recovery_data,
  start = list(plateau_hip = 85, plateau_diff = 0, start_hip = 50, start_diff = 0, tau_hip = 60, tau_diff = 0)
)
summary(joint_recovery)
```

## Python

```{python}
def recovery_by_joint(x, plateau_hip, plateau_diff, start_hip, start_diff, tau_hip, tau_diff):
    days, knee = x
    plateau = plateau_hip + plateau_diff * knee   # knee = 0 for hips, 1 for knees
    start = start_hip + start_diff * knee
    tau = tau_hip + tau_diff * knee
    return plateau - (plateau - start) * np.exp(-days / tau)

names = ["plateau_hip", "plateau_diff", "start_hip", "start_diff", "tau_hip", "tau_diff"]
estimates, covariance = curve_fit(recovery_by_joint, (recovery_data["days"], recovery_data["knee"]),
                                  recovery_data["prom_score"], p0=[85, 0, 50, 0, 60, 0])
standard_errors = np.sqrt(np.diag(covariance))
print(pd.DataFrame({"estimate": estimates, "std_error": standard_errors}, index=names))
```
:::

```{python}
#| include: false
chk = {"tau_hip": float(estimates[4]), "tau_diff": float(estimates[5]), "plateau_diff": float(estimates[1]),
       "start_diff": float(estimates[3]), "se_tau_diff": float(standard_errors[5])}
```

```{r}
#| include: false
joint_coef <- summary(joint_recovery)$coefficients
check_agree(list(tau_hip = joint_coef["tau_hip", "Estimate"], tau_diff = joint_coef["tau_diff", "Estimate"],
                 plateau_diff = joint_coef["plateau_diff", "Estimate"], start_diff = joint_coef["start_diff", "Estimate"],
                 se_tau_diff = joint_coef["tau_diff", "Std. Error"]),
            reticulate::py$chk, tol = 1e-4)   # both approximate the curve's derivatives numerically, so they agree to ~5 digits
```

When you don't know the shape, use a spline instead. Here a natural cubic spline lets BMI's effect on operative time bend, and an F test asks whether the bend improves on the straight line of the [multiple linear regression](#multiple-linear-regression).

::: {.panel-tabset group="language"}
## R

```{r}
straight <- lm(op_time_min ~ bmi + age + sex + procedure, data = cohort)
bendy <- lm(op_time_min ~ ns(bmi, df = 3) + age + sex + procedure, data = cohort)   # ns(): natural cubic spline
anova(straight, bendy)   # does the bend improve the fit?
```

## Python

```{python}
bmi_knots = list(cohort["bmi"].quantile([1/3, 2/3]))         # the same knots R's ns(df = 3) uses
bmi_low, bmi_high = cohort["bmi"].min(), cohort["bmi"].max()

straight = smf.ols("op_time_min ~ bmi + age + sex + procedure", data=cohort).fit()
bendy = smf.ols("op_time_min ~ cr(bmi, knots=bmi_knots, lower_bound=bmi_low, upper_bound=bmi_high, constraints='center')"
                " + age + sex + procedure", data=cohort).fit()   # cr(): natural cubic spline
print(anova_lm(straight, bendy))   # does the bend improve the fit?
```
:::

```{python}
#| include: false
bend_test = anova_lm(straight, bendy)
chk = {"f": float(bend_test.loc[1, "F"]), "p": float(bend_test.loc[1, "Pr(>F)"]), "r2": float(bendy.rsquared)}
```

```{r}
#| include: false
bend_test <- anova(straight, bendy)
check_agree(list(f = bend_test$F[2], p = bend_test$`Pr(>F)`[2], r2 = summary(bendy)$r.squared), reticulate::py$chk)
```

### Read the output

The recovery curve:

- **plateau_hip, start_hip, tau_hip:** the hip curve, the same as fitting hips alone ([page 11, exercise 3](11-predict-from-one.qmd#exercises)): τ = 53.4 days.
- **tau_diff = 27.5:** knees' time constant is 27.5 days longer, so knees recover more slowly.
- **plateau_diff = −3.66, start_diff = 4.25:** the knee curve starts 4.25 points higher and levels off 3.66 points lower; see the warning below before reading anything into these.

The spline:

- **F = 0.58, p = 0.562:** letting BMI's effect bend doesn't improve the fit. Keep the straight line.

### Effect size and 95% CI

The **differences between hips and knees**, with their 95% CIs, are the effect sizes.

::: {.panel-tabset group="language"}
## R

```{r}
confint(joint_recovery)                                          # profile CIs
log(2) * c(hip = coef(joint_recovery)[["tau_hip"]],
           knee = coef(joint_recovery)[["tau_hip"]] + coef(joint_recovery)[["tau_diff"]])   # days to half the gain
log(2) * confint(joint_recovery)["tau_diff", ]                   # difference in days to half the gain
```

## Python

```{python}
t_crit = stats.t.ppf(0.975, df=len(recovery_data) - 6)   # 6 parameters
print(pd.DataFrame({"low": estimates - t_crit * standard_errors, "high": estimates + t_crit * standard_errors}, index=names))
print(np.log(2) * estimates[4], np.log(2) * (estimates[4] + estimates[5]))   # days to half the gain: hips, knees
```
:::

The time constant was 27.5 days longer for knees (95% CI 15.9 to 40.1). Half of the eventual gain took about 37 days after a hip replacement and 56 days after a knee replacement, a difference of 19 days (95% CI 11 to 28).

### How to report it

> **Methods:** HOOS JR (hips) and KOOS JR (knees) were modeled against days since surgery with an exponential recovery curve whose start, plateau and time constant could differ between hips and knees, fitted by nonlinear least squares. Whether BMI's effect on operative time was linear was checked by adding a natural cubic spline (3 degrees of freedom) and comparing the models with an F test.
>
> **Results:** Knees recovered more slowly than hips: the time constant was 27.5 days longer (95% CI 15.9 to 40.1), so half of the eventual gain took about 56 days after knee replacement and 37 days after hip replacement. Allowing BMI's effect on operative time to bend did not improve the fit (F = 0.58, df = 2 and 593, p = 0.562).

::: {.callout-warning}
## ⚠️ Watch out: two questionnaires, and repeated scores
Hips answer HOOS JR and knees KOOS JR. A point on one isn't guaranteed to equal a point on the other, so the differences in start and plateau mix up the joints with the questionnaires. The time constant is measured in days, not points, so it compares cleanly. As on [page 11](11-predict-from-one.qmd#nonlinear-regression), each joint contributes up to four scores, so these CIs are too narrow; a mixed model ([page 16](../beyond/16-mixed-models.qmd)) handles that.
:::

::: {.callout-tip}
## 🔀 R vs Python: splines and CIs
- R's `ns()` and Python's `cr()` (from patsy, the formula library statsmodels uses) build the same natural cubic spline only when the knots match. `ns(df = 3)` puts knots at the 1/3 and 2/3 quantiles and at the minimum and maximum, so the Python code sets those explicitly. Other tools, like `rms::rcs()`, place the knots elsewhere and give slightly different curves.
- As on [page 11](11-predict-from-one.qmd#nonlinear-regression), R's `confint()` profiles the nonlinear fit, while the Python code uses estimate ± t × standard error, so the CIs differ slightly (τ difference: 15.3 to 39.7 days in Python).
:::

## Multiple logistic regression {#multiple-logistic-regression}

**The question:** Which patient factors predict a complication within 90 days?

### When to use it

- The outcome is **yes/no**, and you want the **odds ratio** for each of several predictors, adjusted for the others.
- The assumptions of [simple logistic regression](11-predict-from-one.qmd#logistic-regression) still apply, for every measured predictor.
- **Events limit predictors.** A common rule of thumb is at least 10 patients **with** the outcome per predictor. With 51 complications, this model can afford about five.
- If the outcome is time until an event → [Cox regression](#cox).

### Look at the data first

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(age_10 = age / 10,   # per 10 years
         bmi_5 = bmi / 5)     # per 5 kg/m²

cohort |>
  group_by(complication_90d) |>
  summarise(n = n(), age = mean(age), bmi = mean(bmi), asa = mean(asa),
            diabetes_percent = 100 * mean(diabetes), male_percent = 100 * mean(sex == "Male"))
```

## Python

```{python}
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

cohort = pd.read_csv("data/cohort.csv")
cohort["age_10"] = cohort["age"] / 10   # per 10 years
cohort["bmi_5"] = cohort["bmi"] / 5     # per 5 kg/m²
cohort["male"] = (cohort["sex"] == "Male").astype(int)

print(cohort.groupby("complication_90d")[["age", "bmi", "asa", "diabetes", "male"]].mean())
print(cohort["complication_90d"].value_counts())
```
:::

The 51 patients with a complication were older on average (71.2 against 65.0 years), with a higher BMI (32.3 against 30.3) and a slightly higher ASA class. Diabetes was a little more common (11.8% against 9.1%), and men a little less common (39.2% against 43.2%).

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
complication_model <- glm(complication_90d ~ age_10 + bmi_5 + asa + diabetes + sex,
                          family = binomial, data = cohort)
summary(complication_model)
```

## Python

```{python}
complication_model = smf.logit("complication_90d ~ age_10 + bmi_5 + asa + diabetes + sex",
                               data=cohort).fit(disp=False)
print(complication_model.summary())
```
:::

```{python}
#| include: false
params, errors = complication_model.params, complication_model.bse
chk = {"age": float(params["age_10"]), "bmi": float(params["bmi_5"]), "asa": float(params["asa"]),
       "diabetes": float(params["diabetes"]), "male": float(params["sex[T.Male]"]),
       "se_age": float(errors["age_10"]), "se_bmi": float(errors["bmi_5"])}
```

```{r}
#| include: false
complication_coef <- summary(complication_model)$coefficients
check_agree(list(age = complication_coef["age_10", "Estimate"], bmi = complication_coef["bmi_5", "Estimate"],
                 asa = complication_coef["asa", "Estimate"], diabetes = complication_coef["diabetes", "Estimate"],
                 male = complication_coef["sexMale", "Estimate"], se_age = complication_coef["age_10", "Std. Error"],
                 se_bmi = complication_coef["bmi_5", "Std. Error"]),
            reticulate::py$chk, tol = 1e-4)   # glm() stops once the deviance settles, a step before statsmodels does
```

### Read the output

- Each **coefficient** is the change in the log odds of a complication per unit of that predictor, adjusted for the others; the next step turns them into odds ratios.
- **age_10: p < 0.001** and **bmi_5: p = 0.029:** age and BMI each predict complications, even allowing for the other.
- **asa (p = 0.592), diabetes (p = 0.789), sexMale (p = 0.849):** no clear evidence for these, once age and BMI are in the model.
- ASA class is entered as a number (1 to 4), so it counts as one predictor with one odds ratio per class. As four separate groups it would use three of the model's five or so predictors.

### Effect size and 95% CI

::: {.panel-tabset group="language"}
## R

```{r}
exp(cbind(odds_ratio = coef(complication_model), confint(complication_model)))   # profile CIs
```

## Python

```{python}
odds_ratios = np.exp(pd.concat([complication_model.params, complication_model.conf_int()], axis=1))   # Wald CIs
odds_ratios.columns = ["odds_ratio", "low", "high"]
print(odds_ratios)
```
:::

The **adjusted odds ratios** are the effect sizes: 2.08 per 10 years of age (95% CI 1.46 to 3.02) and 1.39 per 5 kg/m² of BMI (95% CI 1.03 to 1.86). The CIs for ASA class (1.16 per class, 0.68 to 2.00), diabetes (0.88, 0.31 to 2.15) and male sex (0.94, 0.51 to 1.72) are wide.

### How to report it

> **Methods:** Complications within 90 days were modeled with multiple logistic regression on age (per 10 years), BMI (per 5 kg/m²), ASA class, diabetes and sex, chosen before the analysis.
>
> **Results:** Complications followed 51 of 600 procedures (8.5%). Older age (odds ratio 2.08 per 10 years, 95% CI 1.46 to 3.02) and higher BMI (odds ratio 1.39 per 5 kg/m², 95% CI 1.03 to 1.86) were independently associated with complications. The estimates for ASA class (1.16 per class, 95% CI 0.68 to 2.00), diabetes (0.88, 95% CI 0.31 to 2.15) and male sex (0.94, 95% CI 0.51 to 1.72) were imprecise.

::: {.callout-warning}
## ⚠️ Watch out: too few events
With 51 complications, five predictors is already at the limit. Add more and the odds ratios become unstable: their CIs balloon, and some may shoot off toward 0 or infinity. If you have more candidate predictors than events allow, choose the most important ones clinically, in advance; don't let p-values choose them for you.
:::

::: {.callout-tip}
## 🔀 R vs Python: profile and Wald CIs, again
As on [page 11](11-predict-from-one.qmd#logistic-regression), R's `confint()` profiles the likelihood and statsmodels uses Wald CIs. With few events the two can differ in the second decimal: for diabetes, 0.31 to 2.15 in R and 0.33 to 2.30 in Python. Say which you used.
:::

## Cox regression {#cox}

**The question:** Does implant C still carry a higher hazard of revision after adjusting for age, sex and BMI?

### When to use it

- The outcome is **time until an event** (revision), and you want each predictor's **hazard ratio**, adjusted for the others.
- **Events limit predictors**, as in logistic regression: about 10 events per predictor. 81 revisions allow about eight; implant (which uses two, B and C against A), age, sex and BMI use five.
- Proportional hazards must hold for every predictor. [Page 14](../survival/14-cox-regression.qmd) shows how to check it and covers Cox regression in full.

### Look at the data first

Adjusting matters when the groups differ in other ways. Compare the implants:

::: {.panel-tabset group="language"}
## R

```{r}
#| warning: false
library(tidyverse)
library(survival)

cohort <- read_csv("data/cohort.csv", show_col_types = FALSE) |>
  mutate(age_10 = age / 10, bmi_5 = bmi / 5)   # per 10 years, per 5 kg/m²

cohort |>
  group_by(implant) |>
  summarise(n = n(), revised = sum(revised), age = mean(age), male_percent = 100 * mean(sex == "Male"), bmi = mean(bmi))
```

## Python

```{python}
import pandas as pd
from lifelines import CoxPHFitter

cohort = pd.read_csv("data/cohort.csv")
cohort["age_10"] = cohort["age"] / 10   # per 10 years
cohort["bmi_5"] = cohort["bmi"] / 5     # per 5 kg/m²
cohort["male"] = (cohort["sex"] == "Male").astype(int)

print(cohort.groupby("implant").agg(n=("case_id", "count"), revised=("revised", "sum"), age=("age", "mean"),
                                    male=("male", "mean"), bmi=("bmi", "mean")))
```
:::

38 of 137 implant C procedures were revised, against 25 of 246 for A and 18 of 217 for B. The three groups are alike in age (65 to 66 years on average), sex (42% to 44% men) and BMI (about 30 to 31), so adjustment shouldn't change much.

### Run it

::: {.panel-tabset group="language"}
## R

```{r}
adjusted_cox <- coxph(Surv(followup_years, revised) ~ implant + age_10 + sex + bmi_5, data = cohort)
summary(adjusted_cox)
```

## Python

```{python}
adjusted_cox = CoxPHFitter().fit(
    cohort[["followup_years", "revised", "implant", "age_10", "sex", "bmi_5"]],
    duration_col="followup_years", event_col="revised", formula="implant + age_10 + sex + bmi_5",
    fit_options={"precision": 1e-9},   # stop only when fully converged; see the R vs Python box
)
print(adjusted_cox.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]])
print(adjusted_cox.log_likelihood_ratio_test().test_statistic)   # overall likelihood ratio test
```
:::

```{python}
#| include: false
rows = adjusted_cox.summary
chk = {"hr_b": float(rows.loc["implant[T.B]", "exp(coef)"]), "hr_c": float(rows.loc["implant[T.C]", "exp(coef)"]),
       "low_c": float(rows.loc["implant[T.C]", "exp(coef) lower 95%"]), "high_c": float(rows.loc["implant[T.C]", "exp(coef) upper 95%"]),
       "hr_age": float(rows.loc["age_10", "exp(coef)"]), "hr_male": float(rows.loc["sex[T.Male]", "exp(coef)"]),
       "hr_bmi": float(rows.loc["bmi_5", "exp(coef)"]), "lr": float(adjusted_cox.log_likelihood_ratio_test().test_statistic)}
```

```{r}
#| include: false
adjusted_hr <- summary(adjusted_cox)$conf.int
check_agree(list(hr_b = adjusted_hr["implantB", "exp(coef)"], hr_c = adjusted_hr["implantC", "exp(coef)"],
                 low_c = adjusted_hr["implantC", "lower .95"], high_c = adjusted_hr["implantC", "upper .95"],
                 hr_age = adjusted_hr["age_10", "exp(coef)"], hr_male = adjusted_hr["sexMale", "exp(coef)"],
                 hr_bmi = adjusted_hr["bmi_5", "exp(coef)"], lr = unname(summary(adjusted_cox)$logtest["test"])),
            reticulate::py$chk)
```

### Read the output

- **implantC = 3.19 (95% CI 1.92 to 5.29):** adjusted for age, sex and BMI, implant C carried about three times the hazard of revision of implant A, almost the same as without adjustment (3.07, [page 8](08-three-plus-unmatched.qmd#cox)).
- **implantB = 0.83 (95% CI 0.45 to 1.52):** imprecise, as before.
- **sexMale = 0.51 (95% CI 0.32 to 0.81, p = 0.005):** men had about half the hazard of revision of women.
- **age_10 = 1.22 (95% CI 0.96 to 1.57)** and **bmi_5 = 1.03 (95% CI 0.84 to 1.27):** imprecise.
- **Likelihood ratio test = 39.1 on 5 df, p < 0.001:** the five terms together predict revision.

### Effect size and 95% CI

The **adjusted hazard ratios** with their 95% CIs are the effect sizes. The one the question asks about: implant C against A, 3.19 (95% CI 1.92 to 5.29).

### How to report it

> **Methods:** Revision was modeled with Cox proportional hazards regression on implant (reference A), age (per 10 years), sex and BMI (per 5 kg/m²), chosen before the analysis.
>
> **Results:** After adjustment for age, sex and BMI, implant C was associated with a higher hazard of revision than implant A (hazard ratio 3.19, 95% CI 1.92 to 5.29, p < 0.001); the estimate for implant B was imprecise (0.83, 95% CI 0.45 to 1.52). Men had a lower hazard of revision than women (hazard ratio 0.51, 95% CI 0.32 to 0.81).

::: {.callout-warning}
## ⚠️ Watch out: the unexpected finding
The sex difference wasn't the question; the model was built to adjust for sex, not to test it. An unplanned finding like this is a reason for a new study, not a conclusion: report it as exploratory. And check proportional hazards for every predictor before trusting any of them ([page 14](../survival/14-cox-regression.qmd)).
:::

::: {.callout-tip}
## 🔀 R vs Python: convergence and names
As on [page 8](08-three-plus-unmatched.qmd#cox), lifelines' default convergence rule stops a little early (a hazard ratio of 0.82915 for implant B instead of 0.82912), so the Python code tightens it with `fit_options={"precision": 1e-9}`. lifelines names the terms `implant[T.C]` and `sex[T.Male]`; R names them `implantC` and `sexMale`.
:::

```{r}
#| include: false
# Prose guard: numbers quoted in the text above. If the data change, update the text.
by_procedure <- cohort |> group_by(procedure) |> summarise(mean = mean(op_time_min), sd = sd(op_time_min))
joint_ci <- confint(joint_recovery)
joint_wald <- joint_coef[, "Estimate"] + outer(joint_coef[, "Std. Error"], c(-1, 1) * qt(0.975, nrow(recovery_data) - 6))
complication_or <- exp(coef(complication_model))
complication_ci <- exp(confint(complication_model))
complication_wald <- exp(confint.default(complication_model))
by_complication <- cohort |> group_by(complication_90d) |>
  summarise(n = n(), age = mean(age), bmi = mean(bmi), diabetes = 100 * mean(diabetes), male = 100 * mean(sex == "Male"))
by_implant <- cohort |> group_by(implant) |> summarise(n = n(), revised = sum(revised), age = mean(age), male = 100 * mean(sex == "Male"), bmi = mean(bmi))
adjusted_p <- summary(adjusted_cox)$coefficients[, "Pr(>|z|)"]
unadjusted_hr <- exp(coef(coxph(Surv(followup_years, revised) ~ implant, data = cohort)))
ex_surgeon <- lm(op_time_min ~ bmi + age + sex + procedure + surgeon, data = cohort)
ex_surgeon_test <- anova(time_model, ex_surgeon)
ex_facility <- glm(I(discharge == "facility") ~ age_10 + sex + asa, family = binomial, data = cohort)
ex_facility_ci <- exp(confint(ex_facility))
ex_line <- glm(complication_90d ~ age, family = binomial, data = cohort)
ex_bend <- glm(complication_90d ~ ns(age, df = 3), family = binomial, data = cohort)
ex_bend_test <- anova(ex_line, ex_bend, test = "LRT")
stopifnot(
  sum(table(cohort$patient_id) == 2) == 80, nrow(cohort) == 600,
  round(by_procedure$mean, 1) == c(79.8, 88.3), round(by_procedure$sd, 1) == c(15.5, 16.2),
  round(coef(time_model)[c("bmi", "age", "sexMale", "procedureTKA")], 2) == c(1.27, 0.27, -1.48, 6.74),
  round(time_ci["bmi", ], 2) == c(1.06, 1.49), round(time_ci["age", ], 2) == c(0.15, 0.39),
  round(time_ci["sexMale", ], 2) == c(-3.81, 0.84), round(time_ci["procedureTKA", ], 2) == c(4.40, 9.08),
  round(time_fit$r.squared, 2) == 0.27, round(time_fit$adj.r.squared, 2) == 0.26,
  pf(time_fit$fstatistic[1], time_fit$fstatistic[2], time_fit$fstatistic[3], lower.tail = FALSE) < 0.001,
  round(coef(lm(op_time_min ~ bmi, data = cohort))[["bmi"]], 2) == 1.37,
  nrow(recovery_data) == 2052, sum(recovery_data$knee) == 1146, sum(recovery_data$knee == 0) == 906,
  round(joint_coef["tau_hip", "Estimate"], 1) == 53.4, round(joint_coef["tau_diff", "Estimate"], 1) == 27.5,
  round(joint_coef[c("plateau_diff", "start_diff"), "Estimate"], 2) == c(-3.66, 4.25),
  round(joint_ci["tau_diff", ], 1) == c(15.9, 40.1), round(joint_wald["tau_diff", ], 1) == c(15.3, 39.7),
  round(log(2) * joint_coef["tau_hip", "Estimate"]) == 37,
  round(log(2) * sum(joint_coef[c("tau_hip", "tau_diff"), "Estimate"])) == 56,
  round(log(2) * joint_coef["tau_diff", "Estimate"]) == 19, round(log(2) * joint_ci["tau_diff", ]) == c(11, 28),
  round(bend_test$F[2], 2) == 0.58, round(bend_test$`Pr(>F)`[2], 3) == 0.562,
  bend_test$Df[2] == 2, bend_test$Res.Df[2] == 593,
  sum(cohort$complication_90d) == 51, round(100 * mean(cohort$complication_90d), 1) == 8.5,
  by_complication$n == c(549, 51), round(by_complication$age, 1) == c(65.0, 71.2), round(by_complication$bmi, 1) == c(30.3, 32.3),
  round(by_complication$diabetes, 1) == c(9.1, 11.8), round(by_complication$male, 1) == c(43.2, 39.2),
  complication_coef["age_10", "Pr(>|z|)"] < 0.001, round(complication_coef["bmi_5", "Pr(>|z|)"], 3) == 0.029,
  round(complication_coef[c("asa", "diabetes", "sexMale"), "Pr(>|z|)"], 3) == c(0.592, 0.789, 0.849),
  round(complication_or[c("age_10", "bmi_5", "asa", "diabetes", "sexMale")], 2) == c(2.08, 1.39, 1.16, 0.88, 0.94),
  round(complication_ci["age_10", ], 2) == c(1.46, 3.02), round(complication_ci["bmi_5", ], 2) == c(1.03, 1.86),
  round(complication_ci["asa", ], 2) == c(0.68, 2.00), round(complication_ci["diabetes", ], 2) == c(0.31, 2.15),
  round(complication_ci["sexMale", ], 2) == c(0.51, 1.72), round(complication_wald["diabetes", ], 2) == c(0.33, 2.30),
  by_implant$n == c(246, 217, 137), by_implant$revised == c(25, 18, 38), sum(cohort$revised) == 81,
  round(range(by_implant$age)) == c(65, 66), round(range(by_implant$male)) == c(42, 44), round(range(by_implant$bmi)) == c(30, 31),
  round(adjusted_hr[, "exp(coef)"], 2) == c(0.83, 3.19, 1.22, 0.51, 1.03),
  round(adjusted_hr["implantC", c("lower .95", "upper .95")], 2) == c(1.92, 5.29),
  round(adjusted_hr["implantB", c("lower .95", "upper .95")], 2) == c(0.45, 1.52),
  round(adjusted_hr["sexMale", c("lower .95", "upper .95")], 2) == c(0.32, 0.81),
  round(adjusted_hr["age_10", c("lower .95", "upper .95")], 2) == c(0.96, 1.57),
  round(adjusted_hr["bmi_5", c("lower .95", "upper .95")], 2) == c(0.84, 1.27),
  round(adjusted_p[["sexMale"]], 3) == 0.005, adjusted_p[["implantC"]] < 0.001,
  round(unname(summary(adjusted_cox)$logtest["test"]), 1) == 39.1, summary(adjusted_cox)$logtest["pvalue"] < 0.001,
  round(unadjusted_hr[["implantC"]], 2) == 3.07,
  round(reticulate::py_eval("float(CoxPHFitter().fit(cohort[['followup_years', 'revised', 'implant', 'age_10', 'sex', 'bmi_5']], duration_col='followup_years', event_col='revised', formula='implant + age_10 + sex + bmi_5').summary.loc['implant[T.B]', 'exp(coef)'])"), 5) == 0.82915,
  round(adjusted_hr["implantB", "exp(coef)"], 5) == 0.82912,
  # exercise solutions (recomputed here: the guard runs before the solution chunks)
  round(ex_surgeon_test$F[2], 2) == 0.09, round(ex_surgeon_test$`Pr(>F)`[2], 3) == 0.911,
  round(coef(ex_surgeon)[["bmi"]], 2) == 1.27, round(confint(ex_surgeon)["bmi", ], 2) == c(1.06, 1.49),
  round(coef(ex_surgeon)[c("surgeonS2", "surgeonS3")], 2) == c(0.07, 0.60),
  round(confint(ex_surgeon)["surgeonS2", ], 2) == c(-2.57, 2.72), round(confint(ex_surgeon)["surgeonS3", ], 2) == c(-2.28, 3.48),
  sum(cohort$discharge == "facility") == 30,
  round(exp(coef(ex_facility))[c("age_10", "sexMale", "asa")], 2) == c(2.08, 1.36, 1.06),
  round(ex_facility_ci["age_10", ], 2) == c(1.34, 3.31), round(ex_facility_ci["sexMale", ], 2) == c(0.63, 2.89),
  round(ex_facility_ci["asa", ], 2) == c(0.58, 1.94),
  round(ex_bend_test$Deviance[2], 2) == 3.49, ex_bend_test$Df[2] == 2, round(ex_bend_test$`Pr(>Chi)`[2], 3) == 0.175,
  round(exp(10 * coef(ex_line)[["age"]]), 2) == 2.12, round(exp(10 * confint(ex_line)["age", ]), 2) == c(1.53, 2.98),
  sum(cohort$age >= 80) == 53, sum(cohort$complication_90d[cohort$age >= 80]) == 14
)
```

## Exercises {#exercises}

The solutions use the packages and data loaded in the sections above, so run the page from the top first.

**1.** Add **surgeon** to the multiple linear regression for operative time. Does it improve the model, and does BMI's coefficient change?

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
with_surgeon <- lm(op_time_min ~ bmi + age + sex + procedure + surgeon, data = cohort)
anova(time_model, with_surgeon)                            # does surgeon add anything?
confint(with_surgeon)[c("bmi", "surgeonS2", "surgeonS3"), ]
coef(with_surgeon)[c("bmi", "surgeonS2", "surgeonS3")]
```

## Python

```{python}
from statsmodels.stats.anova import anova_lm

with_surgeon = smf.ols("op_time_min ~ bmi + age + sex + procedure + surgeon", data=cohort).fit()
print(anova_lm(time_model, with_surgeon))
surgeon_table = pd.concat([with_surgeon.params, with_surgeon.conf_int()], axis=1)
surgeon_table.columns = ["estimate", "low", "high"]
print(surgeon_table.loc[["bmi", "surgeon[T.S2]", "surgeon[T.S3]"]])
```
:::

Adding surgeon doesn't improve the model (F = 0.09, df = 2 and 593, p = 0.911): compared with S1, S2's operations took 0.07 minutes longer (95% CI −2.57 to 2.72) and S3's 0.60 minutes longer (95% CI −2.28 to 3.48). BMI's coefficient is unchanged at 1.27 minutes per kg/m² (95% CI 1.06 to 1.49).
:::

**2.** A colleague wants to know which patient factors predict discharge to a facility rather than home. Only 30 patients went to a facility. Which model would you use, how many predictors can it take, and what do you find with age, sex and ASA class?

::: {.callout-tip collapse="true"}
## Solution
The outcome is yes/no: **multiple logistic regression**. With 30 events, the rule of thumb allows about three predictors, so choose them in advance; age, sex and ASA class are reasonable choices.

::: {.panel-tabset group="language"}
## R

```{r}
facility_model <- glm(I(discharge == "facility") ~ age_10 + sex + asa, family = binomial, data = cohort)
exp(cbind(odds_ratio = coef(facility_model), confint(facility_model)))
```

## Python

```{python}
cohort["facility"] = (cohort["discharge"] == "facility").astype(int)
facility_model = smf.logit("facility ~ age_10 + sex + asa", data=cohort).fit(disp=False)
facility_ors = np.exp(pd.concat([facility_model.params, facility_model.conf_int()], axis=1))
facility_ors.columns = ["odds_ratio", "low", "high"]
print(facility_ors)
```
:::

Older age was associated with discharge to a facility (odds ratio 2.08 per 10 years, 95% CI 1.34 to 3.31; R's profile CI). The estimates for male sex (1.36, 95% CI 0.63 to 2.89) and ASA class (1.06 per class, 95% CI 0.58 to 1.94) were imprecise.
:::

**3.** On [page 11](11-predict-from-one.qmd#logistic-regression), complications seemed to jump after age 80. Fit age as a natural cubic spline (3 degrees of freedom) in the logistic regression, compare it with the straight line, and write the Results sentence.

::: {.callout-tip collapse="true"}
## Solution

::: {.panel-tabset group="language"}
## R

```{r}
line_model <- glm(complication_90d ~ age, family = binomial, data = cohort)
bend_model <- glm(complication_90d ~ ns(age, df = 3), family = binomial, data = cohort)
anova(line_model, bend_model, test = "LRT")   # likelihood ratio test
```

## Python

```{python}
age_knots = list(cohort["age"].quantile([1/3, 2/3]))
age_low, age_high = cohort["age"].min(), cohort["age"].max()
line_model = smf.logit("complication_90d ~ age", data=cohort).fit(disp=False)
bend_model = smf.logit("complication_90d ~ cr(age, knots=age_knots, lower_bound=age_low, upper_bound=age_high,"
                       " constraints='center')", data=cohort).fit(disp=False)
lr = 2 * (bend_model.llf - line_model.llf)    # likelihood ratio statistic
print(lr, stats.chi2.sf(lr, df=2))           # 2 extra degrees of freedom
```
:::

"Allowing the effect of age to bend, with a natural cubic spline, did not clearly improve the fit over a straight line (likelihood ratio χ² = 3.49, df = 2, p = 0.175), so age was modeled as linear: each 10 years multiplied the odds of a complication by 2.12 (95% CI 1.53 to 2.98)."

The jump after 80 rests on 14 complications in 53 patients, too few to pin down a curve.
:::
````

- [ ] **Step 4: Render it and run the tests**

Run:

```bash
quarto render catalog/12-predict-from-several.qmd
uv run pytest tests/site -q
```

Expected: the render completes, then `214 passed`.

- [ ] **Step 5: Prove the Cox check bites, then restore**

In the `#cox` section's Run it block (Python), delete the line `    fit_options={"precision": 1e-9},   # stop only when fully converged; see the R vs Python box`, then run `quarto render catalog/12-predict-from-several.qmd`.

Expected: the render FAILS with `check_agree(): R and Python disagree on 'hr_b'`. Undo the change, then run:

```bash
rm -rf catalog/12-predict-from-several_files
quarto render catalog/12-predict-from-several.qmd
uv run pytest tests/site -q
```

Expected: `214 passed`.

- [ ] **Step 6: Commit**

```bash
git add catalog/12-predict-from-several.qmd _freeze/catalog/12-predict-from-several tests/site/test_catalog.py
git commit -m "Write page 12, predict from several variables: multiple linear, nonlinear with splines, logistic, Cox

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Record the regression-CI convention and run everything

**Files:**
- Modify: `CLAUDE.md`, `tests/python/test_repo_docs.py`

- [ ] **Step 1: Write the failing test**

In `tests/python/test_repo_docs.py`, replace

```python
                 'a ceiling of "p > 0.999"', "Bootstrap CIs are seeded", "opts_chunk"]:
```

with

```python
                 'a ceiling of "p > 0.999"', "Bootstrap CIs are seeded", "opts_chunk",
                 "Regression CIs"]:
```

Run: `uv run pytest tests/python/test_repo_docs.py -q`

Expected: `test_claude_md_states_the_golden_rules` FAILS on `Regression CIs`.

- [ ] **Step 2: Update CLAUDE.md**

After golden rule 15,

```markdown
15. **Bootstrap CIs are seeded.** effectsize computes some CIs by bootstrap (`rank_epsilon_squared()`, `kendalls_w()`), so their printed CI changes on every render. Call `set.seed(2026)` just before them in the same chunk, or pass `ci = NULL` where only the estimate is needed (prose guards). `tests/site/test_sources.py` enforces this.
```

add rule 16:

```markdown
16. **Regression CIs.** R's `confint()` profiles the likelihood of `glm()` and `nls()` fits; statsmodels and scipy give Wald CIs (estimate ± z or t × standard error). Pages quote R's profile CI and give Python's in the 🔀 box. The hidden check compares estimates and standard errors (and, for `glm()`, the Wald CI from `confint.default()`) with `tol = 1e-4` and a comment, because the two sides stop iterating, or approximate derivatives, slightly differently.
```

- [ ] **Step 3: Run everything**

Run:

```bash
Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
uv run pytest tests/python -q
quarto render
uv run pytest tests/site -q
lychee --offline --include-fragments --no-progress _site
git status --short
```

Expected:
- R: `[ FAIL 0 | WARN 0 | SKIP 0 | PASS 238 ]`
- Python: `80 passed`
- `quarto render` re-executes nothing
- site: `214 passed`
- lychee: `0 Errors`
- `git status` shows only `CLAUDE.md` and `tests/python/test_repo_docs.py`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md tests/python/test_repo_docs.py
git commit -m "CLAUDE.md: record Phase 3c convention (profile vs Wald regression CIs)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
