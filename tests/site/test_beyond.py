"""Part 4 · Beyond the table: post-hoc tests, mixed models, agreement (spec section 4, pages 15-17).
tests/site/test_free_form.py checks what every free-form page shares."""

import re

import pytest

from sitelib import code_of, load, section, text_of

POST_HOC = "beyond/15-post-hoc.html"
MIXED = "beyond/16-mixed-models.html"
AGREEMENT = "beyond/17-agreement.html"


# ---- page 15: post-hoc tests and multiple comparisons ----------------------------

def test_adjustments_are_compared_side_by_side(site):
    found = section(POST_HOC, "adjusting-p-values")
    text = text_of(found)
    for name in ["Bonferroni", "Holm", "Benjamini-Hochberg", "false discovery rate", "family-wise"]:
        assert name in text or name in text_of(section(POST_HOC, "why-adjust")), name
    outputs = [out.get_text() for out in found.select(".cell-output")]
    assert sum(all(column in out for column in ["bonferroni", "holm", "bh"]) for out in outputs) == 2   # R and Python


# Spec section 4, page 15, plus the follow-ups pages 9 and 13 promise.
FOLLOW_UPS = {
    "after-anova": ["TukeyHSD(", "pairwise_tukeyhsd(", "games_howell_test(", "pairwise_gameshowell("],
    "after-kruskal-wallis": ["dunn_test(", "posthoc_dunn("],
    "after-chi-square": ["pairwise_fisher_test(", "fisher_exact("],
    "after-repeated-measures-anova": ["pairwise_t_test(", "pairwise_tests("],
    "after-friedman": ["pairwise_wilcox_test(", "frdAllPairsConoverTest(", "wilcoxon(", "posthoc_conover_friedman("],
    "after-cochran-q": ["mcnemar.test(", "mcnemar("],
    "after-log-rank": ["survdiff(", "pairwise_logrank_test("],
}


@pytest.mark.parametrize("anchor,calls", FOLLOW_UPS.items())
def test_each_overall_test_has_its_follow_up_in_both_languages(site, anchor, calls):
    found = section(POST_HOC, anchor)
    code = code_of(found)
    assert [call for call in calls if call not in code] == []
    assert "holm" in code.lower() or anchor == "after-anova"     # Tukey and Games-Howell adjust themselves


def test_the_overall_test_is_not_a_gate(site):
    """Settles the Phase 3b question: adjusted post-hoc methods don't need a significant overall test first."""
    text = text_of(section(POST_HOC, "overall-test-first"))
    assert "Fisher's least significant difference" in text and "don't need the gate" in text
    assert "p = 0.016" in text                       # the significant-overall, no-significant-pair example


def test_planned_and_exploratory_comparisons_are_distinguished(site):
    text = text_of(section(POST_HOC, "planned-comparisons"))
    assert "pre-specified" in text and "exploratory" in text


# ---- page 16: mixed models ---------------------------------------------------------

def test_mixed_model_page_counts_what_repeated_measures_anova_drops(site):
    text = text_of(section(MIXED, "why-mixed-models"))
    assert "192 knees" in text and "138 knees (42%)" in text
    for kind in ["Missing completely at random", "Missing at random", "Missing not at random"]:
        assert kind in text, kind


def test_random_intercept_and_marginal_means_in_both_languages(site):
    code = code_of(section(MIXED, "random-intercept")) + code_of(section(MIXED, "estimated-marginal-means"))
    for call in ["lmer(", "(1 | case_id)", "mixedlm(", "emmeans(", "marginal_means("]:
        assert call in code, call
    assert "Satterthwaite" in text_of(section(MIXED, "random-intercept"))


def test_time_is_shown_as_categories_and_as_a_curve(site):
    code = code_of(section(MIXED, "time"))
    assert "ns(visit_days" in code and "cr(visit_days" in code


def test_group_by_time_tests_the_interaction(site):
    text = text_of(section(MIXED, "group-by-time"))
    assert "visit:sex" in text and "p = 0.100" in text and "no clear evidence" in text


def test_bilateral_patients_get_a_nested_model_and_a_pointer(site):
    found = section(MIXED, "bilateral")
    assert "(1 | patient_id/case_id)" in text_of(found)
    assert any(a["href"].endswith("survival/14-cox-regression.html#stratified-cox") for a in found.select("a[href]"))


# ---- page 17: agreement and reliability ----------------------------------------------

def test_icc_form_is_named_and_interpreted_with_koo_and_li(site):
    text = text_of(section(AGREEMENT, "icc"))
    for phrase in ["two-way random", "absolute agreement", "single", "Koo and Li", "ICC(A,1)"]:
        assert phrase in text, phrase


def test_inter_and_intra_rater_reliability_are_both_measured(site):
    assert "inter-rater" in text_of(section(AGREEMENT, "icc"))
    text = text_of(section(AGREEMENT, "inter-intra-rater"))
    assert "intra-rater" in text.lower() and "0.915" in text


def test_bland_altman_plot_and_limits_in_both_languages(site):
    found = section(AGREEMENT, "bland-altman")
    plotted = [tabset for tabset in found.select("div.panel-tabset")
               if all(pane.select("img") for pane in tabset.select("div.tab-pane"))]
    assert plotted, "the Bland-Altman plot is drawn in both languages"
    assert "limits of agreement" in text_of(found).lower() and "−2.74° to 3.74°" in text_of(found)


def test_kappa_and_weighted_kappa_with_ordered_categories(site):
    found = section(AGREEMENT, "kappa")
    code = code_of(found)
    assert "CohenKappa(" in code and "cohens_kappa(" in code and "Equal-Spacing" in code and 'wt="linear"' in code
    assert "alphabetically" in text_of(found)


# ---- links into pages 15-17 ----------------------------------------------------------

# Where a sentence promises one topic ("compare the visits with paired tests ... page 15"),
# its link lands on that section, not the top of the page.
SECTION_LINKS = {
    "foundations/03-distributions.html": ["beyond/16-mixed-models.html#bilateral"],
    "catalog/07-two-paired-groups.html": ["beyond/16-mixed-models.html#why-mixed-models",
                                          "beyond/17-agreement.html#bland-altman"],
    "catalog/08-three-plus-unmatched.html": ["beyond/15-post-hoc.html#after-anova", "beyond/15-post-hoc.html#after-kruskal-wallis",
                                             "beyond/15-post-hoc.html#after-chi-square", "beyond/15-post-hoc.html#overall-test-first"],
    "catalog/09-three-plus-matched.html": ["beyond/15-post-hoc.html#after-repeated-measures-anova",
                                           "beyond/15-post-hoc.html#after-friedman", "beyond/15-post-hoc.html#after-cochran-q",
                                           "beyond/16-mixed-models.html#why-mixed-models"],
    "catalog/11-predict-from-one.html": ["beyond/16-mixed-models.html#random-intercept"],
    "catalog/12-predict-from-several.html": ["beyond/16-mixed-models.html#random-intercept"],
    "survival/13-kaplan-meier.html": ["beyond/15-post-hoc.html#after-log-rank"],
}


def beyond_links(page):
    return [a["href"].replace("../", "") for a in load(page).select("main a[href]") if "beyond/1" in a["href"]]


@pytest.mark.parametrize("page,targets", SECTION_LINKS.items())
def test_links_into_pages_15_to_17_land_on_the_section_they_promise(site, page, targets):
    assert [target for target in targets if target not in beyond_links(page)] == []


@pytest.mark.parametrize("page", SECTION_LINKS)
def test_no_link_into_pages_15_to_17_stops_at_the_top_of_the_page(site, page):
    assert [href for href in beyond_links(page) if "#" not in href] == []


def test_post_hoc_tests_are_no_longer_gated_on_the_overall_test(site):
    """Phase 3b's deferred question, settled on page 15: adjusted post-hoc tests don't need a significant overall test."""
    found = section("catalog/08-three-plus-unmatched.html", "which-groups-differ")
    assert "Only run post-hoc tests when the overall test is significant" not in text_of(found)
    assert any(a["href"].endswith("beyond/15-post-hoc.html#overall-test-first") for a in found.select("a[href]"))


# ---- final review fixes ----------------------------------------------------------------

def test_page_16_names_its_planned_comparison_instead_of_leaving_three_unadjusted(site):
    found = section(MIXED, "estimated-marginal-means")
    assert 'adjust = "none"' not in code_of(found) and '"1yr - preop" = c(-1, 0, 0, 1)' in code_of(found)
    methods = next(text_of(q) for q in section(MIXED, "reporting").select("blockquote") if "Methods:" in text_of(q))
    assert "The planned comparison was the change from before surgery to 1 year" in methods
    assert "you didn't plan" in text_of(section(POST_HOC, "overall-test-first"))


def test_holm_description_reproduces_the_table_above_it(site):
    text = text_of(section(POST_HOC, "adjusting-p-values"))
    assert "can't be smaller than the one before it" in text and "takes 0.044" in text


def test_bmi_exercise_answer_names_the_least_certain_pairs(site):
    text = text_of(section(POST_HOC, "exercises"))
    assert "The smallest steps" not in text and "least certain" in text
    assert "protects against any false positive" not in text


def test_post_hoc_results_say_where_the_other_pairs_are(site):
    for anchor in ["after-anova", "planned-comparisons"]:
        results = " ".join(text_of(q) for q in section(POST_HOC, anchor).select("blockquote"))
        assert "Table 2 gives all six pairwise comparisons" in results, anchor
    assert "3.07 (95% CI 1.85 to 5.09" in text_of(section(POST_HOC, "after-log-rank"))


def test_mixed_model_page_states_its_arithmetic_and_missingness_correctly(site):
    text = text_of(load(MIXED))
    assert "8.8² = 78.1" not in text and "8.84² = 78.1" in text
    assert "Men were 2.7 points ahead" in text
    assert "missed completely at random" not in text and "almost entirely at random" in text
    assert "as long as the model describes how a knee's scores are related" in text


def test_agreement_reporting_gives_every_ci_and_says_whose_readings(site):
    found = section(AGREEMENT, "reporting")
    quotes = " ".join(text_of(q) for q in found.select("blockquote"))
    assert "(95% CI −3.48° to −2.00°)" in quotes and "(95% CI 3.00° to 4.48°)" in quotes
    assert "rater 1's intra-rater reliability" in quotes and "each rater's first reading" in quotes
    assert "moderate to substantial (κ = 0.58" in quotes and "moderate to almost perfect (weighted κ = 0.73" in quotes


def test_scikit_learn_kappa_ordering_trap_is_named(site):
    text = text_of(section(AGREEMENT, "kappa"))
    assert "cohen_kappa_score()" in text and "labels=" in text


# ---- deferred Phase 5 minors ---------------------------------------------------------

def test_conover_p_values_are_printed_in_full_in_both_languages(site):
    """Printing R's test object shows every p-value as "<2e-16", so nobody could see that R and Python agree."""
    shown = " ".join(pre.get_text() for pre in section(POST_HOC, "after-friedman").select(".cell-output pre"))
    assert "<2e-16" not in shown
    assert len(re.findall(r"8\.85\d*e-36", shown)) >= 3   # R's table once, Python's symmetric table twice


def test_false_positive_example_says_pairwise_tests_are_not_independent(site):
    """1 − 0.95^6 = 26% is for six independent tests; six pairwise comparisons of four groups give about 20%."""
    text = text_of(section(POST_HOC, "why-adjust"))
    assert "aren't independent" in text and "about 20%" in text
