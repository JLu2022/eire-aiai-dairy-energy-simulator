from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


@dataclass(frozen=True)
class GroupScenario:
    name: str
    years: List[int]
    annual_load_kwh: float
    annual_solar_generation_kwh: float
    discount_rate: float
    lifespan_years: int
    maintenance_rate: float
    energy_prices_cents: Dict[int, float]
    pv_cost_eur: Dict[int, float]
    subsidy_rate: Dict[int, float]
    alpha: float
    beta: float
    initial_adopters: int = 360
    total_farmers: int = 18000
    normalize_utility: bool = False


def _forecast_variants() -> Dict[str, GroupScenario]:
    base_prices = {
        2023: 26.775, 2024: 16.275, 2025: 15.225, 2026: 11.55,
        2027: 11.025, 2028: 10.71, 2029: 11.55, 2030: 12.075,
    }
    base_costs = {
        2023: 13000, 2024: 13000, 2025: 13000, 2026: 8000,
        2027: 7000, 2028: 6500, 2029: 6000, 2030: 5950,
    }
    years = list(base_prices.keys())
    subsidy_60 = {y: 0.6 for y in years}
    common = dict(
        years=years,
        annual_load_kwh=26000.0,
        annual_solar_generation_kwh=10157.0,
        discount_rate=0.05,
        lifespan_years=25,
        maintenance_rate=0.02,
        alpha=3e-5,
        beta=-6.34,
        total_farmers=18000,
        initial_adopters=360,
        normalize_utility=False,
    )
    return {
        "forecasting_baseline": GroupScenario(
            name="WP4 Forecasting baseline (2023–2030)",
            energy_prices_cents=base_prices,
            pv_cost_eur=base_costs,
            subsidy_rate=subsidy_60,
            **common,
        ),
        "forecasting_pv_minus5_grid_plus5": GroupScenario(
            name="WP4 Forecasting: PV -5%, electricity +5%",
            energy_prices_cents={2023:25.5,2024:15.5,2025:14.5,2026:11.0,2027:10.5,2028:10.2,2029:11.0,2030:11.5},
            pv_cost_eur={2023:12350,2024:12350,2025:12350,2026:7600,2027:6650,2028:6175,2029:5700,2030:5650},
            subsidy_rate=subsidy_60,
            **common,
        ),
        "forecasting_pv_minus10_grid_plus10": GroupScenario(
            name="WP4 Forecasting: PV -10%, electricity +10%",
            energy_prices_cents={2023:28.05,2024:17.05,2025:15.95,2026:12.1,2027:11.55,2028:11.22,2029:12.1,2030:12.65},
            pv_cost_eur={2023:11700,2024:11700,2025:11700,2026:7200,2027:6300,2028:5850,2029:5400,2030:5355},
            subsidy_rate=subsidy_60,
            **common,
        ),
        "forecasting_pv_plus5_grid_minus5": GroupScenario(
            name="WP4 Forecasting: PV +5%, electricity -5%",
            energy_prices_cents={2023:24.225,2024:14.725,2025:13.775,2026:10.45,2027:9.975,2028:9.69,2029:10.45,2030:10.925},
            pv_cost_eur={2023:13650,2024:11550,2025:9450,2026:8400,2027:7350,2028:6825,2029:6300,2030:6247},
            subsidy_rate=subsidy_60,
            **common,
        ),
        "forecasting_pv_plus10_grid_minus10": GroupScenario(
            name="WP4 Forecasting: PV +10%, electricity -10%",
            energy_prices_cents={2023:22.95,2024:13.95,2025:13.05,2026:9.9,2027:9.45,2028:9.18,2029:9.9,2030:10.35},
            pv_cost_eur={2023:14300,2024:12100,2025:9900,2026:8800,2027:7700,2028:7150,2029:6600,2030:6545},
            subsidy_rate=subsidy_60,
            **common,
        ),
    }


def _baseline_scenario() -> Dict[str, GroupScenario]:
    prices = {
        2005: 13.445, 2006: 13.445, 2007: 13.445, 2008: 13.445, 2009: 11.84,
        2010: 10.635, 2011: 11.455, 2012: 13.43, 2013: 13.855, 2014: 13.745,
        2015: 13.79, 2016: 12.75, 2017: 12.49, 2018: 13.55, 2019: 13.27,
        2020: 13.43, 2021: 17.08, 2022: 22.02,
    }
    costs = {
        2005:50000,2006:50000,2007:50000,2008:50000,2009:50000,2010:50000,
        2011:45000,2012:40000,2013:36000,2014:32000,2015:21000,2016:21000,
        2017:18000,2018:13300,2019:13300,2020:13300,2021:13300,2022:13300,
    }
    years = list(prices.keys())
    subsidy = {y: 0.0 for y in years}
    for y in years:
        if y >= 2015:
            subsidy[y] = 0.4
    return {
        "baseline_historical": GroupScenario(
            name="WP4 Historical baseline (2005–2022)",
            years=years,
            annual_load_kwh=26000.0,
            annual_solar_generation_kwh=10157.0,
            discount_rate=0.05,
            lifespan_years=25,
            maintenance_rate=0.02,
            energy_prices_cents=prices,
            pv_cost_eur=costs,
            subsidy_rate=subsidy,
            alpha=3e-5,
            beta=-6.34,
            initial_adopters=0,
            total_farmers=18000,
            normalize_utility=False,
        )
    }


def _icccmla_scenario() -> Dict[str, GroupScenario]:
    prices = {2023:28.589, 2024:20.916, 2025:21.553, 2026:22.19, 2027:22.82, 2028:23.46, 2029:24.10, 2030:24.73}
    years = list(prices.keys())
    subsidy = {y: 0.4 for y in years}
    costs = {y:13000 for y in years}
    return {
        "icccmla_linear_price": GroupScenario(
            name="WP4 ICCCMLA linear-price scenario (2023–2030)",
            years=years,
            annual_load_kwh=26000.0,
            annual_solar_generation_kwh=10157.0,
            discount_rate=0.05,
            lifespan_years=10,
            maintenance_rate=0.02,
            energy_prices_cents=prices,
            pv_cost_eur=costs,
            subsidy_rate=subsidy,
            alpha=2.2,
            beta=-5.8,
            initial_adopters=360,
            total_farmers=18000,
            normalize_utility=True,
        )
    }


SCENARIOS: Dict[str, GroupScenario] = {}
SCENARIOS.update(_baseline_scenario())
SCENARIOS.update(_forecast_variants())
SCENARIOS.update(_icccmla_scenario())


def annual_savings(load_kwh: float, solar_kwh: float, price_cents: float) -> float:
    without_solar_cost = load_kwh * (price_cents / 100.0)
    with_solar_cost = max(load_kwh - solar_kwh, 0.0) * (price_cents / 100.0)
    return without_solar_cost - with_solar_cost


def subsidy_eur(cost_eur: float, subsidy_rate: float) -> float:
    return cost_eur * subsidy_rate


def discounted_annual_savings(annual_savings_eur: float, maintenance_cost_eur: float, discount_rate: float, lifespan_years: int) -> float:
    total = 0.0
    for year in range(1, lifespan_years + 1):
        total += (annual_savings_eur - maintenance_cost_eur) / ((1.0 + discount_rate) ** year)
    return total


def economic_utility_for_year(s: GroupScenario, year: int) -> float:
    pv_cost = s.pv_cost_eur[year]
    a_sav = annual_savings(s.annual_load_kwh, s.annual_solar_generation_kwh, s.energy_prices_cents[year])
    maintenance = s.maintenance_rate * pv_cost
    discounted = discounted_annual_savings(a_sav, maintenance, s.discount_rate, s.lifespan_years)
    subsidy = subsidy_eur(pv_cost, s.subsidy_rate.get(year, 0.0))
    return discounted + subsidy - pv_cost


def probability_for_year(s: GroupScenario, year: int, utility_mean: float | None = None, utility_std: float | None = None) -> float:
    utility = economic_utility_for_year(s, year)
    if s.normalize_utility:
        mean = utility if utility_mean is None else utility_mean
        std = 1.0 if utility_std in (None, 0.0) else utility_std
        z = s.alpha * ((utility - mean) / std) + s.beta
    else:
        z = s.alpha * utility + s.beta
    return float(np.clip(1.0 / (1.0 + np.exp(-z)), 0.0, 1.0))


def scenario_year_table(key: str):
    s = SCENARIOS[key]
    utilities = [economic_utility_for_year(s, y) for y in s.years]
    mean = float(np.mean(utilities)) if utilities else 0.0
    std = float(np.std(utilities)) if utilities else 1.0
    rows = []
    for y, u in zip(s.years, utilities):
        a_sav = annual_savings(s.annual_load_kwh, s.annual_solar_generation_kwh, s.energy_prices_cents[y])
        prob = probability_for_year(s, y, mean, std)
        rows.append({
            'year': y,
            'electricity_price_cents_per_kwh': s.energy_prices_cents[y],
            'pv_cost_eur': s.pv_cost_eur[y],
            'subsidy_rate': s.subsidy_rate.get(y, 0.0),
            'annual_savings_eur': a_sav,
            'economic_utility_eur': u,
            'adoption_probability': prob,
        })
    return rows


def simulate_group_scenario(key: str, seed: int = 42, total_farmers: int | None = None, initial_adopters: int | None = None):
    s = SCENARIOS[key]
    total = int(total_farmers or s.total_farmers)
    adopted = int(initial_adopters if initial_adopters is not None else s.initial_adopters)
    rng = np.random.default_rng(seed)

    utilities = [economic_utility_for_year(s, y) for y in s.years]
    mean = float(np.mean(utilities)) if utilities else 0.0
    std = float(np.std(utilities)) if utilities else 1.0

    adoption_rate, cumulative, probabilities = [], [], []
    for y in s.years:
        remaining = max(0, total - adopted)
        p = probability_for_year(s, y, mean, std)
        new = int(rng.binomial(remaining, p)) if remaining > 0 else 0
        adopted += new
        probabilities.append(p)
        cumulative.append(adopted)
        adoption_rate.append(adopted / total if total > 0 else 0.0)
    return {
        'scenario': s,
        'years': s.years,
        'probabilities': probabilities,
        'adoption_rate': adoption_rate,
        'cumulative': cumulative,
    }
