"""Tests that stdlib function BODIES type-check correctly.

The standard stdlib tests validate call-site type signatures (parameter types,
return types) via ``load_stdlib_functions()``.  These tests go further: they
inline the actual function definitions into the compilation unit so the
typechecker's Phase 1.6 walks every statement inside each function body.

This catches errors such as:
- Mismatched return types inside branches
- Arithmetic on incompatible dimensional types
- Empty-array coercion failures
- Incorrect use of builtins (len, max, min, ...)
"""
# ruff: noqa: W293

import pytest

from tests.conftest import (
    assert_compiles_successfully,
    compile_pel_code_with_stdlib,
)

# ---------------------------------------------------------------------------
# Capacity module — full body type-checking  (16 functions)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCapacityBodyTypechecking:
    """Verify every capacity function body is type-consistent."""

    def test_calculate_utilization_body(self):
        """calculate_utilization(Rate, Rate) -> Fraction."""
        pel_code = """
        param u: Rate per Month = 80/1mo {source:"t",method:"observed",confidence:1.0}
        param t_cap: Rate per Month = 100/1mo {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = calculate_utilization(u, t_cap)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_capacity_gap_body(self):
        """capacity_gap(Rate, Rate) -> Rate."""
        pel_code = """
        param d: Rate per Month = 1000/1mo {source:"t",method:"observed",confidence:1.0}
        param a: Rate per Month = 800/1mo {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = capacity_gap(d, a)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_required_capacity_body(self):
        """required_capacity(Rate, Rate, Fraction) -> Fraction."""
        pel_code = """
        param target: Rate per Month = 1000/1mo {source:"t",method:"observed",confidence:1.0}
        param per_unit: Rate per Month = 50/1mo {source:"t",method:"observed",confidence:1.0}
        param eff: Fraction = 0.9 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = required_capacity(target, per_unit, eff)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_effective_capacity_body(self):
        """effective_capacity(Rate, Fraction) -> Rate."""
        pel_code = """
        param c: Rate per Month = 1000/1mo {source:"t",method:"observed",confidence:1.0}
        param e: Fraction = 0.9 {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = effective_capacity(c, e)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_allocate_capacity_body(self):
        """allocate_capacity: handles empty arrays, proportional & priority alloc."""
        pel_code = """
        param tc: Rate per Month = 500/1mo {source:"t",method:"observed",confidence:1.0}
        param d1: Rate per Month = 300/1mo {source:"t",method:"observed",confidence:1.0}
        param d2: Rate per Month = 400/1mo {source:"t",method:"observed",confidence:1.0}
        param p1: Fraction = 0.6 {source:"t",method:"observed",confidence:1.0}
        param p2: Fraction = 0.4 {source:"t",method:"observed",confidence:1.0}
        var result: Array<Rate per Month> = allocate_capacity(tc, [d1, d2], [p1, p2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_capacity_constraint_body(self):
        """capacity_constraint(Rate, Fraction) -> Rate."""
        pel_code = """
        param c: Rate per Month = 1000/1mo {source:"t",method:"observed",confidence:1.0}
        param e: Fraction = 0.85 {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = capacity_constraint(c, e)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_bottleneck_capacity_body(self):
        """bottleneck_capacity(Array<Rate>) -> Int."""
        pel_code = """
        param c1: Rate per Month = 100/1mo {source:"t",method:"observed",confidence:1.0}
        param c2: Rate per Month = 50/1mo {source:"t",method:"observed",confidence:1.0}
        var result: Int = bottleneck_capacity([c1, c2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_parallel_capacity_body(self):
        """parallel_capacity(Array<Rate>) -> Rate."""
        pel_code = """
        param c1: Rate per Month = 100/1mo {source:"t",method:"observed",confidence:1.0}
        param c2: Rate per Month = 200/1mo {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = parallel_capacity([c1, c2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_scale_capacity_body(self):
        """scale_capacity(Rate, Fraction, Count) -> Rate."""
        pel_code = """
        param base: Rate per Month = 100/1mo {source:"t",method:"observed",confidence:1.0}
        param growth: Fraction = 0.1 {source:"t",method:"observed",confidence:1.0}
        param periods: Count = 12 {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = scale_capacity(base, growth, periods)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_capacity_increment_body(self):
        """capacity_increment(Fraction, Fraction) -> Fraction."""
        pel_code = """
        param needed: Fraction = 3.5 {source:"t",method:"observed",confidence:1.0}
        param incr: Fraction = 1.0 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = capacity_increment(needed, incr)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_capacity_lead_time_body(self):
        """capacity_lead_time(String, Fraction) -> Duration<Day>."""
        pel_code = """
        param ctype: String = "cloud" {source:"t",method:"observed",confidence:1.0}
        param qty: Fraction = 5.0 {source:"t",method:"observed",confidence:1.0}
        var result: Duration<Day> = capacity_lead_time(ctype, qty)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_capacity_cost_body(self):
        """capacity_cost(Count, Currency) -> Currency."""
        pel_code = """
        param qty: Count = 10 {source:"t",method:"observed",confidence:1.0}
        param unit_cost: Currency<USD> = $50 {source:"t",method:"observed",confidence:1.0}
        var result: Currency<USD> = capacity_cost(qty, unit_cost)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_peak_utilization_body(self):
        """peak_utilization(Array<Fraction>) -> Fraction."""
        pel_code = """
        param u1: Fraction = 0.7 {source:"t",method:"observed",confidence:1.0}
        param u2: Fraction = 0.9 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = peak_utilization([u1, u2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_average_utilization_body(self):
        """average_utilization(Array<Fraction>) -> Fraction."""
        pel_code = """
        param u1: Fraction = 0.7 {source:"t",method:"observed",confidence:1.0}
        param u2: Fraction = 0.9 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = average_utilization([u1, u2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_utilization_variability_body(self):
        """utilization_variability(Array<Fraction>) -> Fraction, single-pass Welford's."""
        pel_code = """
        param u1: Fraction = 0.7 {source:"t",method:"observed",confidence:1.0}
        param u2: Fraction = 0.9 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = utilization_variability([u1, u2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)

    def test_overutilization_penalty_body(self):
        """overutilization_penalty(Fraction, Fraction, Currency) -> Currency."""
        pel_code = """
        param util: Fraction = 0.95 {source:"t",method:"observed",confidence:1.0}
        param thresh: Fraction = 0.8 {source:"t",method:"observed",confidence:1.0}
        param penalty: Currency<USD> = $1000 {source:"t",method:"observed",confidence:1.0}
        var result: Currency<USD> = overutilization_penalty(util, thresh, penalty)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity"])
        assert_compiles_successfully(ir)


# ---------------------------------------------------------------------------
# Hiring module — full body type-checking  (21 functions)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHiringBodyTypechecking:
    """Verify every hiring function body is type-consistent."""

    def test_hiring_funnel_body(self):
        """hiring_funnel(Count<Applicant>, Array<Fraction>) -> Count<Person>."""
        pel_code = """
        param apps: Count<Applicant> = 200 {source:"t",method:"observed",confidence:1.0}
        param r1: Fraction = 0.3 {source:"t",method:"observed",confidence:1.0}
        param r2: Fraction = 0.5 {source:"t",method:"observed",confidence:1.0}
        var result: Count<Person> = hiring_funnel(apps, [r1, r2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_offer_acceptance_rate_body(self):
        """offer_acceptance_rate(Count<Offer>, Count<Offer>) -> Fraction."""
        pel_code = """
        param offers: Count<Offer> = 100 {source:"t",method:"observed",confidence:1.0}
        param accepts: Count<Offer> = 80 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = offer_acceptance_rate(offers, accepts)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_hiring_velocity_body(self):
        """hiring_velocity(Fraction, Count<Person>) -> Duration<Day>."""
        pel_code = """
        param total_days: Fraction = 120.0 {source:"t",method:"observed",confidence:1.0}
        param hires: Count<Person> = 10 {source:"t",method:"observed",confidence:1.0}
        var result: Duration<Day> = hiring_velocity(total_days, hires)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_cost_per_hire_body(self):
        """cost_per_hire(Currency, Count<Person>) -> Currency."""
        pel_code = """
        param total_cost: Currency<USD> = $50000 {source:"t",method:"observed",confidence:1.0}
        param num_hires: Count<Person> = 10 {source:"t",method:"observed",confidence:1.0}
        var result: Currency<USD> = cost_per_hire(total_cost, num_hires)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_required_headcount_body(self):
        """required_headcount(Rate, Rate, Fraction) -> Count<Person>."""
        pel_code = """
        param target: Rate per Month = 1000/1mo {source:"t",method:"observed",confidence:1.0}
        param prod: Rate per Month = 50/1mo {source:"t",method:"observed",confidence:1.0}
        param ramp: Fraction = 0.75 {source:"t",method:"observed",confidence:1.0}
        var result: Count<Person> = required_headcount(target, prod, ramp)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_hiring_plan_body(self):
        """hiring_plan(Count, Count, Duration, Duration) -> Count<Person>."""
        pel_code = """
        param current: Count<Person> = 30 {source:"t",method:"observed",confidence:1.0}
        param target: Count<Person> = 50 {source:"t",method:"observed",confidence:1.0}
        param horizon: Duration<Month> = 12mo {source:"t",method:"observed",confidence:1.0}
        param period: Duration<Month> = 3mo {source:"t",method:"observed",confidence:1.0}
        var result: Count<Person> = hiring_plan(current, target, horizon, period)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_attrition_replacement_body(self):
        """attrition_replacement(Count<Person>, Rate per Year) -> Count<Person>."""
        pel_code = """
        param hc: Count<Person> = 100 {source:"t",method:"observed",confidence:1.0}
        param attr: Rate per Year = 0.15/1yr {source:"t",method:"observed",confidence:1.0}
        var result: Count<Person> = attrition_replacement(hc, attr)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_growth_hiring_body(self):
        """growth_hiring(Count, Count, Duration) -> Count<Person>."""
        pel_code = """
        param current: Count<Person> = 50 {source:"t",method:"observed",confidence:1.0}
        param target: Count<Person> = 80 {source:"t",method:"observed",confidence:1.0}
        param horizon: Duration<Month> = 6mo {source:"t",method:"observed",confidence:1.0}
        var result: Count<Person> = growth_hiring(current, target, horizon)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_ramp_time_body(self):
        """ramp_time(Duration<Month>, Fraction) -> Duration<Month>."""
        pel_code = """
        param base_ramp: Duration<Month> = 3mo {source:"t",method:"observed",confidence:1.0}
        param quality: Fraction = 0.8 {source:"t",method:"observed",confidence:1.0}
        var result: Duration<Month> = ramp_time(base_ramp, quality)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_ramp_curve_body(self):
        """ramp_curve(Duration<Month>, Duration<Month>, String) -> Fraction."""
        pel_code = """
        param since_hire: Duration<Month> = 3mo {source:"t",method:"observed",confidence:1.0}
        param ramp_dur: Duration<Month> = 6mo {source:"t",method:"observed",confidence:1.0}
        param shape: String = "linear" {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = ramp_curve(since_hire, ramp_dur, shape)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_effective_headcount_body(self):
        """effective_headcount(Count, Count, Fraction) -> Count<Person>."""
        pel_code = """
        param ramped: Count<Person> = 40 {source:"t",method:"observed",confidence:1.0}
        param ramping: Count<Person> = 10 {source:"t",method:"observed",confidence:1.0}
        param avg_progress: Fraction = 0.5 {source:"t",method:"observed",confidence:1.0}
        var result: Count<Person> = effective_headcount(ramped, ramping, avg_progress)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_team_productivity_body(self):
        """team_productivity(Count<Person>, Rate) -> Rate."""
        pel_code = """
        param hc: Count<Person> = 10 {source:"t",method:"observed",confidence:1.0}
        param prod: Rate per Month = 50/1mo {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = team_productivity(hc, prod)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_headcount_capacity_body(self):
        """headcount_capacity(Count<Person>, Rate, Fraction) -> Rate."""
        pel_code = """
        param hc: Count<Person> = 50 {source:"t",method:"observed",confidence:1.0}
        param cap_per: Rate per Month = 20/1mo {source:"t",method:"observed",confidence:1.0}
        param util: Fraction = 0.85 {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = headcount_capacity(hc, cap_per, util)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_team_capacity_body(self):
        """team_capacity(Array<Count<Person>>, Array<Rate>) -> Rate."""
        pel_code = """
        param hc1: Count<Person> = 5 {source:"t",method:"observed",confidence:1.0}
        param hc2: Count<Person> = 8 {source:"t",method:"observed",confidence:1.0}
        param r1: Rate per Month = 20/1mo {source:"t",method:"observed",confidence:1.0}
        param r2: Rate per Month = 25/1mo {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = team_capacity([hc1, hc2], [r1, r2])
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_capacity_per_hire_body(self):
        """capacity_per_hire(Rate, Duration, Duration) -> Rate."""
        pel_code = """
        param full_cap: Rate per Month = 100/1mo {source:"t",method:"observed",confidence:1.0}
        param ramp_m: Duration<Month> = 2mo {source:"t",method:"observed",confidence:1.0}
        param ramp_total: Duration<Month> = 6mo {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = capacity_per_hire(full_cap, ramp_m, ramp_total)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_hiring_lag_impact_body(self):
        """hiring_lag_impact(Rate, Duration, Duration) -> Rate."""
        pel_code = """
        param gap: Rate per Month = 200/1mo {source:"t",method:"observed",confidence:1.0}
        param planned: Duration<Month> = 2mo {source:"t",method:"observed",confidence:1.0}
        param actual: Duration<Month> = 4mo {source:"t",method:"observed",confidence:1.0}
        var result: Rate per Month = hiring_lag_impact(gap, planned, actual)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_recruiting_cost_body(self):
        """recruiting_cost(Count, Currency, Count, Currency) -> Currency."""
        pel_code = """
        param apps: Count<Applicant> = 500 {source:"t",method:"observed",confidence:1.0}
        param cost_app: Currency<USD> = $10 {source:"t",method:"observed",confidence:1.0}
        param interviews: Count<Interview> = 50 {source:"t",method:"observed",confidence:1.0}
        param cost_iv: Currency<USD> = $200 {source:"t",method:"observed",confidence:1.0}
        var result: Currency<USD> = recruiting_cost(apps, cost_app, interviews, cost_iv)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_onboarding_cost_body(self):
        """onboarding_cost(Count<Person>, Currency) -> Currency."""
        pel_code = """
        param hires: Count<Person> = 10 {source:"t",method:"observed",confidence:1.0}
        param cost: Currency<USD> = $5000 {source:"t",method:"observed",confidence:1.0}
        var result: Currency<USD> = onboarding_cost(hires, cost)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_total_talent_cost_body(self):
        """total_talent_cost(Count, Currency, Currency, Duration) -> Currency."""
        pel_code = """
        param hires: Count<Person> = 10 {source:"t",method:"observed",confidence:1.0}
        param cph: Currency<USD> = $5000 {source:"t",method:"observed",confidence:1.0}
        param annual_comp: Currency<USD> = $80000 {source:"t",method:"observed",confidence:1.0}
        param period: Duration<Year> = 1yr {source:"t",method:"observed",confidence:1.0}
        var result: Currency<USD> = total_talent_cost(hires, cph, annual_comp, period)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)

    def test_hire_roi_body(self):
        """hire_roi(Currency, Currency) -> Fraction."""
        pel_code = """
        param value: Currency<USD> = $100000 {source:"t",method:"observed",confidence:1.0}
        param cost: Currency<USD> = $30000 {source:"t",method:"observed",confidence:1.0}
        var result: Fraction = hire_roi(value, cost)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["hiring"])
        assert_compiles_successfully(ir)


# ---------------------------------------------------------------------------
# Cross-module — body type-checking with both modules
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCrossModuleBodyTypechecking:
    """Verify capacity + hiring functions compose correctly."""

    def test_hiring_to_capacity_pipeline(self):
        """Full pipeline: hiring funnel -> headcount -> capacity gap."""
        pel_code = """
        param applicants: Count<Applicant> = 500 {source:"t",method:"observed",confidence:1.0}
        param screen_rate: Fraction = 0.3 {source:"t",method:"observed",confidence:1.0}
        param interview_rate: Fraction = 0.25 {source:"t",method:"observed",confidence:1.0}
        param offer_rate: Fraction = 0.7 {source:"t",method:"observed",confidence:1.0}
        param cap_per_person: Rate per Month = 20/1mo {source:"t",method:"observed",confidence:1.0}
        param utilization: Fraction = 0.85 {source:"t",method:"observed",confidence:1.0}

        var new_hires: Count<Person> = hiring_funnel(applicants, [screen_rate, interview_rate, offer_rate])
        var team_cap: Rate per Month = headcount_capacity(new_hires, cap_per_person, utilization)
        var gap: Rate per Month = capacity_gap(team_cap, 500/1mo)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity", "hiring"])
        assert_compiles_successfully(ir)

    def test_capacity_utilization_with_hiring(self):
        """Calculate utilization based on hired team capacity."""
        pel_code = """
        param hc: Count<Person> = 50 {source:"t",method:"observed",confidence:1.0}
        param cap_pp: Rate per Month = 30/1mo {source:"t",method:"observed",confidence:1.0}
        param util_factor: Fraction = 0.9 {source:"t",method:"observed",confidence:1.0}
        param demand: Rate per Month = 1200/1mo {source:"t",method:"observed",confidence:1.0}

        var supply: Rate per Month = headcount_capacity(hc, cap_pp, util_factor)
        var util_rate: Fraction = calculate_utilization(demand, supply)
        """
        ir = compile_pel_code_with_stdlib(pel_code, ["capacity", "hiring"])
        assert_compiles_successfully(ir)
