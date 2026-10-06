"""Source-level rules for .qmd files (no built site needed)."""

import ast
import builtins
import re

from sitelib import CELL_ANCHORS, ROOT

CONTENT_DIRS = ["getting-started", "foundations", "catalog", "survival", "beyond", "report"]
EXECUTABLE_CHUNK = re.compile(r"^```\{(r|python)[ ,}]", re.MULTILINE)
KNITR = re.compile(r"^engine:\s*knitr\s*$", re.MULTILINE)


def qmd_files():
    files = [ROOT / "index.qmd"]
    for d in CONTENT_DIRS:
        files += sorted((ROOT / d).glob("*.qmd"))
    return files


def front_matter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return match.group(1) if match else ""


def missing_knitr(text: str) -> bool:
    return bool(EXECUTABLE_CHUNK.search(text)) and not KNITR.search(front_matter(text))


def test_rule_catches_python_page_without_knitr():
    assert missing_knitr("---\ntitle: x\n---\n\n```{python}\nprint(1)\n```\n")


def test_rule_accepts_page_that_declares_knitr():
    assert not missing_knitr("---\ntitle: x\nengine: knitr\n---\n\n```{python}\nprint(1)\n```\n")


def test_rule_ignores_display_only_code():
    assert not missing_knitr("---\ntitle: x\n---\n\n```python\nprint(1)\n```\n")


def test_every_page_with_code_declares_knitr():
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files()
                 if missing_knitr(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Add `engine: knitr` to the front matter of: " + ", ".join(offenders)


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


def test_chunk_options_can_come_in_any_order():
    text = "```{python}\n#| echo: false\n#| include: false\nchk = 1\n```\n\n```{r}\n#| warning: false\nlibrary(x)\n```\n"
    assert hidden_chunks(text) == [("python", "#| echo: false\n#| include: false\nchk = 1")]
    assert visible_chunks(text) == [("r", "#| warning: false\nlibrary(x)")]


def test_tidy_page_checks_both_answer_keys_in_both_languages():
    """Spec 8.4: page 1's reference solutions must reproduce the answer keys exactly."""
    chunks = hidden_chunks((ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8"))
    for key in ["abstraction_workbook_tidy.csv", "survey_items_long.csv"]:
        assert any(lang == "r" and key in code and "stopifnot(isTRUE(all.equal(" in code
                   for lang, code in chunks), f"no hidden R check against {key}"
        assert any(lang == "python" and key in code and "assert_frame_equal" in code
                   for lang, code in chunks), f"no hidden Python check against {key}"


def written_pages(*dirs):
    """Pages in these folders that are no longer "(coming soon)" stubs."""
    for d in dirs:
        for path in sorted((ROOT / d).glob("*.qmd")):
            text = path.read_text(encoding="utf-8")
            if "(coming soon)" not in front_matter(text):
                yield f"{d}/{path.name}", text


def test_exercise_solutions_are_executed():
    """Solutions run on every render, so a typo in one can't ship unnoticed."""
    for name, text in written_pages("foundations", "catalog", "survival"):
        exercises = text[text.index("## Exercises {#exercises}"):]
        assert "```r\n" not in exercises and "```python\n" not in exercises, name


def test_pages_guard_the_numbers_in_their_prose():
    for name, text in written_pages("foundations", "catalog", "survival"):
        chunks = hidden_chunks(text)
        assert any(lang == "r" and "Prose guard" in code and "stopifnot(" in code
                   for lang, code in chunks), name


def section(text, start, end):
    """The source between two markers (tabset "## R" headers make heading-based cuts unreliable)."""
    i = text.index(start)
    return text[i:text.index(end, i)]


def test_recode_cross_tabs_compare_raw_values_with_the_result():
    text = (ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8")
    check = section(text, "**3. Cross-tab every recode.**", "**4. Range and logic checks.**")
    assert "left_join(" in check and "merge(" in check


def test_tidy_recodes_send_unexpected_codes_to_missing():
    text = (ROOT / "foundations" / "01-tidy-data.qmd").read_text(encoding="utf-8")
    step5 = section(text, "### Step 5: give every column its real type", "## Reshaping a survey export")
    assert step5.count("case_when(") >= 3      # sex, procedure, side
    assert step5.count("np.select(") >= 2      # procedure, side


def test_quartile_guard_reads_what_the_libraries_display():
    text = (ROOT / "foundations" / "02-demographics.qmd").read_text(encoding="utf-8")
    chunks = hidden_chunks(text)
    assert any(lang == "r" and "table_body" in code and "1 (0–2)" in code for lang, code in chunks)
    assert any(lang == "python" and "1.0 [0.0,1.8]" in code for lang, code in chunks)


# ---- reticulate: never assign to _ ---------------------------------------
# reticulate decides whether to print a statement's value by looking at Python's
# last value, `_`. Code that assigns `_` itself (`_ = ax.hist(...)`) hides
# reticulate's placeholder, and once `_` holds a plot object every later Python
# output on the page is silently dropped. Name the result instead.

PYTHON_CHUNK = re.compile(r"```\{python[^}]*\}\n(.*?)\n```", re.DOTALL)
ASSIGNMENT_TARGET = re.compile(r"^([^=#\n]*?)(?<![=!<>])=(?!=)", re.MULTILINE)
UNDERSCORE_NAME = re.compile(r"(?<![\w.])_(?!\w)")


def assigns_underscore(text):
    return any(UNDERSCORE_NAME.search(target)
               for code in PYTHON_CHUNK.findall(text)
               for target in ASSIGNMENT_TARGET.findall(code))


def test_rule_catches_underscore_assignments():
    assert assigns_underscore("```{python}\n_ = ax.hist(x)\nplt.show()\n```")
    assert assigns_underscore("```{python}\nstat, _ = f(x)\n```")


def test_rule_allows_named_results_and_keyword_arguments():
    assert not assigns_underscore("```{python}\nqq = stats.probplot(x, plot=ax)\nmax_iter = 5\n```")
    assert not assigns_underscore("```{python}\nax.hist(x, bins=30)\n```")


def test_no_python_chunk_assigns_to_underscore():
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files() if assigns_underscore(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Name the result instead of assigning to _ in: " + ", ".join(offenders)


# ---- catalog sections ------------------------------------------------------

CELL_HEADING = re.compile(r"^## .*\{#([a-z0-9-]+)\}\s*$", re.MULTILINE)


def cell_sections(page, text):
    """(anchor, source) for each decision-table cell section of one catalog page, skipping
    other sections such as "Which groups differ?" and the exercises."""
    marks = list(CELL_HEADING.finditer(text))
    for mark, following in zip(marks, marks[1:] + [None]):
        if mark.group(1) in CELL_ANCHORS[page]:
            yield mark.group(1), text[mark.end():following.start() if following else len(text)]


def catalog_sections():
    """(page, anchor, source) for every decision-table section of the written catalog pages."""
    for name, text in written_pages("catalog"):
        for anchor, body in cell_sections(name.replace(".qmd", ".html"), text):
            yield name, anchor, body


def test_cell_sections_skip_sections_that_are_not_table_cells():
    text = "## Cox regression {#cox}\nA\n## Which groups differ? {#which-groups-differ}\nB\n## Exercises {#exercises}\nC\n"
    assert [a for a, _ in cell_sections("catalog/08-three-plus-unmatched.html", text)] == ["cox"]


def test_each_catalog_section_loads_its_own_packages_and_data():
    """Readers arrive from the decision table straight at a section and copy its code."""
    for name, anchor, body in catalog_sections():
        first = {}
        for lang, code in visible_chunks(body):
            first.setdefault(lang, code)
        assert "library(" in first["r"] and 'read_csv("data/' in first["r"], f"{name}#{anchor}: first R block"
        assert "import " in first["python"] and 'read_csv("data/' in first["python"], f"{name}#{anchor}: first Python block"


def test_every_catalog_section_checks_r_against_python():
    for name, anchor, body in catalog_sections():
        hidden = hidden_chunks(body)
        r_checks = sum(lang == "r" and "check_agree(" in code for lang, code in hidden)
        py_values = sum(lang == "python" and "chk = " in code for lang, code in hidden)
        assert r_checks >= 1 and r_checks == py_values, f"{name}#{anchor}: {r_checks} R checks, {py_values} Python chk"


def test_survival_pages_check_r_against_python():
    """Free-form pages have no cell sections, so count the whole page's checks."""
    for name, text in written_pages("survival"):
        hidden = hidden_chunks(text)
        r_checks = sum(lang == "r" and "check_agree(" in code for lang, code in hidden)
        py_values = sum(lang == "python" and "chk = " in code for lang, code in hidden)
        assert r_checks >= 5 and r_checks == py_values, f"{name}: {r_checks} R checks, {py_values} Python chk"


# ---- each section's Python runs on its own -------------------------------

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


def test_rule_finds_names_a_section_never_defines():
    assert undefined_names("import pandas as pd\nprint(np.mean(scores))") == {"np", "scores"}
    assert undefined_names("import numpy as np\nx = [1]\nf = lambda v: v + 1\nprint(np.mean(x), f(2))") == set()


def test_rule_keeps_function_and_comprehension_names_inside_them():
    assert undefined_names("f = lambda scores: scores + 1\nprint(scores)") == {"scores"}
    assert undefined_names("squares = [v * v for v in range(3)]\nprint(v)") == {"v"}
    assert undefined_names("def g(a):\n    b = a + 1\n    return b\nprint(g(1), b)") == {"b"}
    assert undefined_names("def g(days):\n    return days * k\nk = 2\nprint(g(1))") == set()


def test_each_catalog_section_python_runs_on_its_own():
    """Every name a section's visible Python uses is created in that section, so it can be copied alone."""
    for name, anchor, body in catalog_sections():
        code = "\n".join(chunk for lang, chunk in visible_chunks(body) if lang == "python")
        assert undefined_names(code) == set(), f"{name}#{anchor} uses {sorted(undefined_names(code))}"


# ---- bootstrap CIs need a seed ---------------------------------------------
# effectsize computes the CIs of these effect sizes by bootstrap (random resampling),
# so without set.seed() the printed CI changes on every render.

BOOTSTRAP_CI_FUNCTIONS = ("rank_epsilon_squared(", "kendalls_w(")
R_CHUNK = re.compile(r"```\{r[^}]*\}\n(.*?)\n```", re.DOTALL)


def unseeded_bootstrap(text):
    for code in R_CHUNK.findall(text):
        seeded = False
        for line in code.splitlines():
            line = line.split("#", 1)[0]   # comments don't count
            seeded = seeded or "set.seed(" in line
            if any(f in line for f in BOOTSTRAP_CI_FUNCTIONS) and "ci = NULL" not in line and not seeded:
                return True
    return False


def test_rule_catches_an_unseeded_bootstrap_ci():
    assert unseeded_bootstrap("```{r}\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
    assert not unseeded_bootstrap("```{r}\nset.seed(1)\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
    assert not unseeded_bootstrap("```{r}\neffectsize::kendalls_w(y ~ v | id, data = d, ci = NULL)\n```")
    assert not unseeded_bootstrap("```{r}\n# kendalls_w() warns about ties\nx <- 1\n```")
    assert unseeded_bootstrap("```{r}\n# set.seed(1) is not needed\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")
    assert unseeded_bootstrap("```{r}\nx <- 1  # set.seed(1) later\neffectsize::kendalls_w(y ~ v | id, data = d)\n```")


def test_bootstrap_cis_are_seeded():
    offenders = [str(f.relative_to(ROOT)) for f in qmd_files() if unseeded_bootstrap(f.read_text(encoding="utf-8"))]
    assert offenders == [], "Call set.seed() before (or pass ci = NULL to) a bootstrap CI in: " + ", ".join(offenders)


# ---- per-group CIs use each group's own count ------------------------------

def test_looped_wilson_cis_take_each_groups_own_count():
    """prop.test(k, n) over several groups takes n from the data, never a typed number or the first group's n."""
    fixed_n = re.compile(r"prop\.test\(\s*[A-Za-z_][\w.]*\s*,\s*(\d|[\w.$]+\[1\])")
    for name, text in written_pages("catalog"):
        visible_r = "\n".join(code for lang, code in visible_chunks(text) if lang == "r")
        assert not fixed_n.search(visible_r), f"{name}: {fixed_n.search(visible_r).group(0)}"


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
