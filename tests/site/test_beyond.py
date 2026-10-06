"""Part 4 · Beyond the table: post-hoc tests, mixed models, agreement (spec section 4, pages 15-17).
tests/site/test_free_form.py checks what every free-form page shares."""

import pytest

from sitelib import code_of, load, section, text_of

POST_HOC = "beyond/15-post-hoc.html"
MIXED = "beyond/16-mixed-models.html"


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
