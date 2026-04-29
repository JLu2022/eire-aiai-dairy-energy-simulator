# src/core/adoption_models.py
import numpy as np
import random
from dataclasses import dataclass

TOTAL_FARMERS_DEFAULT = 18000

@dataclass
class Context:
    total_farmers: int = TOTAL_FARMERS_DEFAULT
    seed: int = 42  # for reproducibility

# =========================
# Rule-based version (the simple logic you already use in the UI)
# =========================
def rule_based_decision(farmer, energy_cost, government_incentives, weather_conditions):
    # farmer must have: age, experience, farm_size, location
    if farmer.location == 'rural' and farmer.age > 50 and farmer.experience > 10 and farmer.farm_size > 50 and \
       energy_cost > 0.15 and government_incentives:
        return True
    if farmer.location == 'suburban' and farmer.age < 50 and farmer.experience > 5 and farmer.farm_size > 100 and \
       energy_cost > 0.20 and weather_conditions == 'sunny':
        return True
    return False

# =========================
# Probabilistic version (refactored from your snippet)
# =========================

def _pv_output_random():
    # Reuse your discrete annual PV output per farm (kWh/year)
    return random.choice([2500, 3000, 3500, 4000, 4500])

def _grid_price(t):
    # Linear increase: initial price + annual increment * (t - 1)
    initial_price = 0.13
    price_increase = 0.015
    return initial_price + price_increase * (t - 1)

def probability_of_adoption(Xy, t, total_farmers=TOTAL_FARMERS_DEFAULT):
    """
    Your probability model — with two small but important fixes:
    1) Your original form `prob = beta / (1 + exp(-alpha * util/total))` caps probability at beta.
       A standard logistic is: prob = 1 / (1 + exp(-(b0 + b1*util_scaled))).
    2) The construction of economic utility `util` follows your approach.
    """
    pv_cost, energy_price, n_prev = Xy

    pv_energy = _pv_output_random()
    pv_revenue = pv_energy * energy_price
    grid_cost = pv_energy * _grid_price(t)
    maintenance_cost = 0.02 * pv_cost
    discount_rate = 0.05

    economic_utility = pv_revenue - grid_cost - maintenance_cost
    discounted_utility = economic_utility / ((1 + discount_rate) ** (t - 1))

    # # Logistic parameters (can be exposed in the UI for tuning)
    # b0 = -2.5     # intercept (baseline tendency)
    # b1 = 0.0001   # sensitivity (to discounted utility)
    # util_scaled = discounted_utility / max(total_farmers, 1)
    #
    # # Logistic probability (0–1)
    # prob = 1.0 / (1.0 + np.exp(-(b0 + b1 * util_scaled)))



    # --- 修改：默认参数对齐论文；去掉 /total_farmers 的缩放 ---
    b0 = -6.34     # 原 -2.5
    b1 = 5e-05     # 原 0.0001 可保留，这里改成论文常用量级
    z  = b0 + b1 * discounted_utility
    prob = 1.0 / (1.0 + np.exp(-z))
    # ---------------------------------------------------------
    # Safe clipping
    return float(np.clip(prob, 0.0, 1.0))

def simulate_probability_model(Xy, timesteps=15, ctx: Context = Context()):
    """
    Xy = [pv_cost, energy_price, n_prev0]
    Returns: (adoption_rate_list, cumulative_adopted_list)
    """
    random.seed(ctx.seed)
    np.random.seed(ctx.seed)

    total = ctx.total_farmers
    n_prev = int(Xy[2])
    adoption_rate = [n_prev / total]
    cumulative = [n_prev]

    for t in range(2, timesteps + 1):
        p = probability_of_adoption(Xy, t, total_farmers=total)
        # New adopters this year
        n_new = np.random.binomial(total - n_prev, p)
        n_prev += n_new
        cumulative.append(n_prev)
        adoption_rate.append(n_prev / total)

    return adoption_rate, cumulative

# 在 src/core/adoption_models.py 里追加

from typing import Dict, List
from dataclasses import dataclass

ALPHA_ILIAS = 3e-5
BETA_ILIAS  = -6.34
LIFESPAN_YEARS = 25
DISCOUNT_RATE  = 0.04
MAINT_RATE     = 0.02

@dataclass
class IliasParams:
    annual_load_kwh: float = 26000.0
    annual_pv_kwh: float = 10157.0  # 或 9539.0，看你对齐哪份
    alpha: float = ALPHA_ILIAS
    beta: float = BETA_ILIAS
    lifespan: int = LIFESPAN_YEARS
    discount: float = DISCOUNT_RATE
    maint_rate: float = MAINT_RATE

def _npv(annual_savings_eur: float, pv_cost_eur: float, p: IliasParams) -> float:
    m = p.maint_rate * pv_cost_eur
    return sum((annual_savings_eur - m) / ((1 + p.discount) ** t) for t in range(1, p.lifespan + 1))

def _annual_savings(load_kwh: float, gen_kwh: float, price_cents: float) -> float:
    return (price_cents / 100.0) * min(load_kwh, gen_kwh)

def probability_ilias(year: int, price_cents: float, pv_cost_eur: float, subsidy_rate: float, p: IliasParams) -> float:
    sav = _annual_savings(p.annual_load_kwh, p.annual_pv_kwh, price_cents)
    eu  = _npv(sav, pv_cost_eur, p) - (1.0 - subsidy_rate) * pv_cost_eur

    z   = p.alpha * eu + p.beta
    prob = 1.0 / (1.0 + np.exp(-z))
    return float(np.clip(prob, 0.0, 1.0))

def simulate_probability_model_ilias(
    years: List[int],
    total_farmers: int,
    prices_cents: Dict[int, float],
    pv_cost_eur: Dict[int, float],
    subsidy_rate: Dict[int, float],
    init_adopted: int = 0,
    seed: int = 42,
    p: IliasParams = IliasParams(),
):
    rng = np.random.default_rng(seed)
    adopted = init_adopted
    adoption_rate, cumulative = [], []
    for y in years:
        remaining = max(0, total_farmers - adopted)
        if remaining == 0:
            adoption_rate.append(adopted / total_farmers)
            cumulative.append(adopted)
            continue
        prob = probability_ilias(y, prices_cents[y], pv_cost_eur[y], subsidy_rate.get(y, 0.0), p)
        new  = rng.binomial(remaining, prob)
        adopted += new
        adoption_rate.append(adopted / total_farmers)
        cumulative.append(adopted)
    return adoption_rate, cumulative
