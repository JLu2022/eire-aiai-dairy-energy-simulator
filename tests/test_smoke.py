from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.group_models import (  # noqa: E402
    SCENARIOS,
    annual_savings,
    discounted_annual_savings,
    economic_utility_for_year,
    simulate_group_scenario,
)
from src.core.simulate import simulate_one_day  # noqa: E402


def test_farm_energy_simulation_smoke() -> None:
    result = simulate_one_day(
        n_cows=55,
        n_milking_units=10,
        month=1,
        day=15,
        start_morning=7,
        start_evening=17,
        milk_cooling_system="DX",
        electric_water_heating="YES",
    )

    assert len(result.hourly_total) == 24
    assert result.total_wh > 0
    assert result.peak_w > 0
    assert 0 <= result.peak_hour <= 23
    assert len(result.breakdown) > 0
    assert math.isclose(sum(result.hourly_total), result.total_wh, rel_tol=1e-6)


def test_group_scenario_simulation_smoke() -> None:
    output = simulate_group_scenario("baseline_historical", seed=42, total_farmers=18000, initial_adopters=0)

    years = output["years"]
    probabilities = output["probabilities"]
    adoption_rate = output["adoption_rate"]
    cumulative = output["cumulative"]

    assert len(years) > 0
    assert len(years) == len(probabilities) == len(adoption_rate) == len(cumulative)
    assert all(0.0 <= p <= 1.0 for p in probabilities)
    assert all(0.0 <= r <= 1.0 for r in adoption_rate)
    assert all(cumulative[i] <= cumulative[i + 1] for i in range(len(cumulative) - 1))


def test_notebook_aligned_roi_smoke() -> None:
    scenario = SCENARIOS["baseline_historical"]
    year = 2005

    savings = annual_savings(
        scenario.annual_load_kwh,
        scenario.annual_solar_generation_kwh,
        scenario.energy_prices_cents[year],
    )
    maintenance = scenario.maintenance_rate * scenario.pv_cost_eur[year]
    discounted = discounted_annual_savings(
        savings,
        maintenance,
        scenario.discount_rate,
        scenario.lifespan_years,
    )
    utility = economic_utility_for_year(scenario, year)

    assert isinstance(savings, float)
    assert isinstance(discounted, float)
    assert isinstance(utility, float)
    assert savings > 0
    assert scenario.pv_cost_eur[year] > 0
