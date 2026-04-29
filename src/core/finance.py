from typing import List, Dict
import numpy as np
import numpy_financial as npf

def npv(rate: float, cashflows: List[float]) -> float:
    return npf.npv(rate, cashflows)

def irr(cashflows: List[float]) -> float:
    return float(npf.irr(cashflows))

def simple_payback(cashflows: List[float]) -> int:
    # Cashflows start at t=0; return the earliest year index when cumulative cashflow becomes positive.
    # If it never turns positive, return -1.
    cum = 0.0
    for t, cf in enumerate(cashflows):
        cum += cf
        if cum >= 0:
            return t
    return -1

def lcoe(discount_rate: float, costs: List[float], energies: List[float]) -> float:
    # LCOE = (sum of discounted costs) / (sum of discounted energy outputs)
    years = np.arange(len(costs))
    disc = (1 + discount_rate) ** years
    return (np.sum(np.array(costs) / disc)) / (np.sum(np.array(energies) / disc))

def cashflow_pv_batt(capex_pv: float, capex_batt: float,
                     opex_rate: float, years: int,
                     annual_savings: List[float], salvage: float = 0.0) -> List[float]:
    # t=0: negative investment; t>=1: annual savings minus O&M cost; add salvage value in the final year if any.
    cfs = [- (capex_pv + capex_batt)]
    for y in range(1, years + 1):
        opex = opex_rate * (capex_pv + capex_batt)
        cf = annual_savings[y - 1] - opex
        if y == years and salvage:
            cf += salvage
        cfs.append(cf)
    return cfs
