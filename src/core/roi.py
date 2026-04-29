# src/core/roi.py
from dataclasses import dataclass

@dataclass
class ROICalcInputs:
    # farm_size: str
    annual_consumption_kwh: float
    roof_capacity_kw: float
    budget_eur: float
    location: str = "IE"
    orientation: str = "South"
    shading: str = "None"
    panel_efficiency: float = 0.18
    battery_roundtrip_eff: float = 0.90
    self_consumption_ratio: float = 0.70
    electricity_price_eur_per_kwh: float = 0.30
    export_price_eur_per_kwh: float = 0.12
    cost_per_kw_eur: float = 1000.0

def _orientation_factor(orientation: str) -> float:
    return {"South": 1.0, "East": 0.92, "West": 0.92}.get(orientation, 1.0)

def _shading_factor(shading: str) -> float:
    return {"None": 1.0, "Moderate": 0.9, "Severe": 0.75}.get(shading, 1.0)

def capex_required(p: ROICalcInputs, desired_kw: float) -> float:
    eff_factor = max(min(p.panel_efficiency / 0.18, 1.2), 0.7)
    orient_factor = _orientation_factor(p.orientation)
    shade_factor = _shading_factor(p.shading)
    return desired_kw * p.cost_per_kw_eur * (1.0 / eff_factor) * (1.05 / orient_factor) * (1.1 / shade_factor)

def pick_system_size_kw(p: ROICalcInputs) -> float:
    # 目标: 覆盖~70%年用电，受屋顶kW上限约束
    target_kwh = p.annual_consumption_kwh * 0.7
    kw_needed = target_kwh / 1200.0
    return max(1.0, min(kw_needed, p.roof_capacity_kw))

def compute_roi(p: ROICalcInputs, annual_pv_kwh: float, capex_eur: float):
    # 自用电量（再受年负荷约束），只在这部分计入电池往返效率
    potential_self_use = annual_pv_kwh * p.self_consumption_ratio
    self_use_kwh = min(p.annual_consumption_kwh, potential_self_use) * p.battery_roundtrip_eff
    export_kwh   = max(annual_pv_kwh - self_use_kwh, 0.0)

    annual_saving = (
        self_use_kwh * p.electricity_price_eur_per_kwh +
        export_kwh   * p.export_price_eur_per_kwh
    )
    payback_years = (capex_eur / annual_saving) if annual_saving > 0 else None
    return annual_saving, payback_years
