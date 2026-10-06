"""Part 3 · Survival analysis: Kaplan-Meier and Cox regression in full (spec section 4, pages 13-14).
tests/site/test_free_form.py checks what every free-form page shares."""

from sitelib import code_of, load, section, text_of

KM = "survival/13-kaplan-meier.html"
COX = "survival/14-cox-regression.html"


# ---- page 13: Kaplan-Meier and the log-rank test -----------------------------

def test_kaplan_meier_curves_show_numbers_at_risk_and_a_ci_band(site):
    found = section(KM, "kaplan-meier")
    code = code_of(found)
    assert "add_risktable(" in code and "add_confidence_interval()" in code and "add_at_risk_counts(" in code
    panes = found.select("div.panel-tabset div.tab-pane")
    assert len(panes) == 2 and all(pane.select("img") for pane in panes), "the curve is drawn in both languages"


def test_survivorship_is_reported_at_2_5_and_10_years_with_cis_and_numbers_at_risk(site):
    results = " ".join(text_of(q) for q in section(KM, "survivorship").select("blockquote"))
    for years in ["at 2 years", "at 5 years", "at 10 years"]:
        assert years in results, years
    assert results.count("95% CI") >= 3 and "remained at risk" in results


def test_median_follow_up_uses_reverse_kaplan_meier(site):
    found = section(KM, "follow-up")
    assert "reverse Kaplan-Meier" in " ".join(text_of(q) for q in found.select("blockquote"))
    assert "5.62 years" in text_of(found)


def test_log_rank_covers_two_groups_and_three_or_more(site):
    found = section(KM, "log-rank")
    outputs = " ".join(out.get_text() for out in found.select(".cell-output"))
    assert "on 1 degrees of freedom" in outputs and "on 2 degrees of freedom" in outputs
    assert "Mantel-Haenszel" in text_of(found)


def test_competing_risks_compare_the_cumulative_incidence_with_one_minus_km(site):
    text = text_of(section(KM, "competing-risks"))
    for phrase in ["Aalen-Johansen", "1 − Kaplan-Meier", "Gray's test", "Python has no mature implementation of Gray's test"]:
        assert phrase in text, phrase


# ---- page 14: Cox regression ---------------------------------------------------

def test_covariates_are_chosen_in_advance_with_enough_events(site):
    text = text_of(section(COX, "choosing-covariates"))
    assert "chosen before you look" in text and "10 events per term" in text


def test_proportional_hazards_are_checked_on_the_built_in_violation(site):
    found = section(COX, "proportional-hazards")
    assert "Schoenfeld" in text_of(found) and "cox.zph(" in code_of(found)
    plotted = [tabset for tabset in found.select("div.panel-tabset")
               if all(pane.select("img") for pane in tabset.select("div.tab-pane"))]
    assert plotted, "the residual plot is drawn in both languages"
    assert "approach" in code_of(plotted[0])


def test_remedies_cover_stratification_and_a_time_split(site):
    code = code_of(section(COX, "remedies"))
    for call in ["strata(approach)", 'strata=["approach"]', "survSplit(", "CoxTimeVaryingFitter("]:
        assert call in code, call


def test_stratified_cox_covers_matched_sets_and_bilateral_patients(site):
    found = section(COX, "stratified-cox")
    hrefs = [a["href"] for a in found.select("a[href]")]
    for target in ["07-two-paired-groups.html#stratified-cox", "09-three-plus-matched.html#stratified-cox"]:
        assert any(href.endswith(target) for href in hrefs), target
    code = code_of(found)
    assert "cluster = patient_id" in code and 'cluster_col="patient_id"' in code


def test_fine_gray_is_labeled_r_only(site):
    found = section(COX, "fine-gray")
    assert "(R only)" in found.select_one("h2").get_text()
    assert found.select("pre.r") and not found.select("pre.python")
    assert "subdistribution hazard ratio" in text_of(found)


def test_reporting_gives_univariable_and_multivariable_hazard_ratios(site):
    found = section(COX, "reporting")
    table = found.select_one("table")
    assert table is not None and "Univariable" in text_of(table) and "Multivariable" in text_of(table)
    assert "Univariable HR (95% CI)" in " ".join(out.get_text() for out in found.select(".cell-output"))


# ---- final review fixes ------------------------------------------------------

def test_reported_models_all_allow_for_bilateral_patients(site):
    """The Methods promise robust standard errors, so both columns of the table use them."""
    found = section(COX, "reporting")
    table = text_of(found.select_one("table"))
    assert "1.87, 5.04" in table and "1.92, 5.28" in table   # implant C, univariable and multivariable, clustered
    printed = " ".join(out.get_text() for out in found.select(".cell-output"))
    assert "3.07 (1.87 to 5.04)" in printed and "3.19 (1.92 to 5.28)" in printed
    methods = next(text_of(q) for q in found.select("blockquote") if "Methods:" in text_of(q))
    assert "In the Cox models, robust standard errors" in methods


def test_imprecise_estimates_are_not_described_as_effects(site):
    """Explanatory prose follows the same rule as the Results: no clear evidence isn't evidence of none."""
    for page, phrase in [(KM, "does worse early and better later"), (KM, "but the curves crossed"),
                         (COX, "Death doesn't depend on the implant"), (COX, "age barely changes"),
                         (COX, "a later one in the other direction")]:
        assert phrase not in text_of(load(page)), f"{page}: {phrase!r}"


def test_a_moving_hazard_ratio_is_not_proof_of_confounding(site):
    """Hazard ratios shift when a strong predictor is added, even without confounding."""
    text = text_of(section(COX, "univariable-multivariable"))
    assert "the covariates were confounding the unadjusted one" not in text
    assert "even without confounding" in text


def test_results_give_every_estimate_its_ci_and_every_count_its_percentage(site):
    km_results = " ".join(text_of(q) for q in section(KM, "competing-risks").select("blockquote"))
    assert "24.0% (95% CI 19.3% to 29.0%)" in km_results
    cox_results = " ".join(text_of(q) for q in section(COX, "reporting").select("blockquote"))
    assert "81 of 600 procedures (13.5%)" in cox_results
