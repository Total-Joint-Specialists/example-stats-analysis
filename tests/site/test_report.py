"""Part 5 · Putting it together: the example study report (spec section 4, page 18), on the site and
as a Word manuscript. tests/site/test_free_form.py checks what every free-form page shares."""

import hashlib
import re

import pytest

from sitelib import ROOT, SITE, code_of, docx_text, docx_xml, load, section, text_of

REPORT = "report/18-example-report.html"
WORD = SITE / "report" / "18-example-report.docx"


# ---- the Word version ------------------------------------------------------------------

def test_the_page_offers_the_word_version(site):
    links = [a["href"] for a in load(REPORT).select(".quarto-alternate-formats a[href]")]
    assert links == ["18-example-report.docx"] and WORD.exists()


def test_the_word_version_is_frozen_so_ci_can_rebuild_it_without_r():
    frozen = ROOT / "_freeze" / "report" / "18-example-report"
    assert (frozen / "execute-results" / "docx.json").exists() and (frozen / "figure-docx").is_dir()


def test_the_word_version_is_the_manuscript_only(site):
    text = docx_text(WORD)
    assert text.startswith("Improvement in joint-specific scores") and "Every patient in this report is invented" in text
    assert re.findall(r"^(Aim|Methods|Results)$", text, re.MULTILINE) == ["Aim", "Methods", "Results"]
    for tutorial in ["library(", "import ", "check_agree", "data-checksum", "Exercises", "Tidy the raw workbook"]:
        assert tutorial not in text, tutorial


def test_the_word_version_has_table_1_and_the_revision_figure(site):
    text = docx_text(WORD)
    assert "(Table 1)" in text and "(Figure 1)" in text
    assert "Age, years" in text and "SMD" in text and "Pre-op score (HOOS JR or KOOS JR), points" in text
    assert docx_xml(WORD).count("<w:drawing>") == 1


# ---- the steps ---------------------------------------------------------------------------

def test_the_question_is_written_down_before_the_analysis(site):
    text = text_of(section(REPORT, "question"))
    for part in ["Question:", "Primary outcome:", "Primary analysis:", "Secondary outcome:"]:
        assert part in text, part
    assert "Watch out: two questionnaires" in text


STEP_LINKS = {
    "tidy": "foundations/01-tidy-data.html#tidying",
    "integrity": "foundations/01-tidy-data.html#integrity",
    "table-1": "foundations/02-demographics.html#smd",
    "distributions": "foundations/03-distributions.html",
    "primary-analysis": "catalog/06-two-unpaired-groups.html#unpaired-t",
    "survival": "survival/13-kaplan-meier.html#competing-risks",
}


@pytest.mark.parametrize("anchor,target", STEP_LINKS.items())
def test_each_step_links_to_the_page_that_explains_it(site, anchor, target):
    hrefs = [a["href"].removeprefix("../") for a in section(REPORT, anchor).select("a[href]")]
    assert target in hrefs, hrefs


def test_failed_integrity_checks_stop_the_script(site):
    code = code_of(section(REPORT, "integrity"))
    assert code.count("stopifnot(") >= 4 and code.count("assert ") >= 4
    assert "revised_registry" in code   # the workbook's red fills, checked against the registry


def test_table_1_uses_smds_and_shows_missing_values(site):
    code = code_of(section(REPORT, "table-1"))
    assert 'add_difference(test = everything() ~ "smd")' in code and "smd=True" in code
    assert 'missing_text = "Missing"' in code and "missing=True" in code


def test_the_primary_analysis_is_the_one_planned(site):
    code = code_of(section(REPORT, "primary-analysis"))
    assert "t.test(change ~ procedure" in code and "equal_var=False" in code
    assert "hedges_g(" in code and 'eftype="hedges"' in code


def test_revision_is_a_cumulative_incidence_with_death_competing(site):
    code = code_of(section(REPORT, "survival"))
    assert 'labels = c("censored", "revision", "death")' in code and "CumIncidenceRight(" in code
    assert "event_status == 0" in code   # the reverse Kaplan-Meier follow-up


# ---- the manuscript ----------------------------------------------------------------------

def test_the_manuscript_states_the_caveats_and_the_missing_data(site):
    methods = text_of(section(REPORT, "methods"))
    results = text_of(section(REPORT, "results"))
    assert "points on each joint's own scale" in methods and "treating death as a competing risk" in methods
    assert "Both scores were available for 93 patients (77.5%)" in results


# ---- final review fixes --------------------------------------------------------------------

def test_missing_data_exercise_separates_the_two_reasons_a_score_is_missing(site):
    text = text_of(section(REPORT, "exercises"))
    assert "didn't answer" not in text
    assert "the other 5 TKA patients had no pre-op score" in text and "15 TKA patients (22.4%; p = 0.239)" in text


def test_the_manuscript_does_not_claim_to_update_itself(site):
    text = text_of(section(REPORT, "manuscript"))
    assert "changes every number at once" not in text
    assert "stops the render until every number in the text is updated" in text
    assert "The Discussion is the author's to write" in text


def test_the_methods_give_time_zero_and_censoring(site):
    methods = text_of(section(REPORT, "methods"))
    assert "from the date of surgery to revision" in methods and "(censored)" in methods


def test_the_revision_figure_shows_the_numbers_at_risk(site):
    found = section(REPORT, "survival")
    assert "add_risktable(" in code_of(found) and "17 patients were still followed at 8 years" in text_of(found)


def test_table_1_reports_absolute_smds_without_pooling_the_two_questionnaires(site):
    text = docx_text(WORD)
    assert "absolute standardized mean difference" in text and "Overall" not in text
    assert not re.search(r"(?<![\d.])-0\.\d", text)
    assert not re.search(r"(?<![\d.])-0\.\d", text_of(section(REPORT, "results")))


def test_results_give_the_ceiling_denominators(site):
    assert "15 of 46 THA patients (32.6%)" in text_of(section(REPORT, "results"))


def test_hedges_g_is_read_with_its_ci_in_both_languages(site):
    found = section(REPORT, "primary-analysis")
    assert "runs from a small difference to a large one" in text_of(found) and "compute_esci(" in code_of(found)
    assert "adjusted.pvalues" in code_of(section(REPORT, "exercises"))


def test_the_registry_link_is_checked_on_more_than_revisions(site):
    found = section(REPORT, "integrity")
    code = code_of(found)
    assert "surgery_date_registry" in code and "procedure_registry" in code and "n_distinct(study$patient_id)" in code
    assert "120 different patients" in text_of(found)


def test_the_prose_guard_reads_the_missing_counts_from_the_data():
    page = (ROOT / "report" / "18-example-report.qmd").read_text(encoding="utf-8")
    guard = page[page.index("# Prose guard"):page.index("## Exercises {#exercises}")]
    assert "20 + 47 == 67" not in guard and "is.na(study$prom_1yr)" in guard


def test_the_frozen_word_version_matches_the_current_data_and_ships_flextables_files():
    current = hashlib.md5((ROOT / "data" / "CHECKSUMS.md5").read_bytes()).hexdigest()
    frozen = ROOT / "_freeze" / "report" / "18-example-report" / "execute-results" / "docx.json"
    assert f"data-checksum: {current}" in frozen.read_text(encoding="utf-8")
    assert (ROOT / "_freeze" / "site_libs" / "tabwid-1.1.3").is_dir()
