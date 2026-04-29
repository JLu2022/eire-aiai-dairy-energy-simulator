# src/core/solar.py
import math
from dataclasses import dataclass

@dataclass
class PVParams:
    efficiency: float = 0.18
    system_size_kw: float = 100.0
    avg_sunlight_h: float = 5.0
    orientation_deg: float = 180.0  # South=180
    tilt_deg: float = 25.0
    shading_factor: float = 0.1
    avg_temperature_c: float = 25.0
    inverter_efficiency: float = 0.95

def _orientation_factor_deg(deg: float) -> float:
    """更贴近经验的朝向修正：南=1.0，东西≈0.92，其它给个温和衰减。"""
    d = abs((deg - 180.0 + 360.0) % 360.0)  # 与正南的偏差
    if d <= 15:   # 近似正南
        return 1.00
    if 60 <= d <= 120:  # 近似东西
        return 0.92
    if 15 < d < 60 or 120 < d < 165:
        return 0.97
    return 0.85  # 明显偏离

def estimate_solar_production(p: PVParams, demand_kwh_day: float = 0.0):
    # 不再把效率乘到装机kW上
    system_kw = max(p.system_size_kw, 0.0)

    orient_factor = _orientation_factor_deg(p.orientation_deg)
    shading_loss = 1.0 - p.shading_factor
    # 温度损失：~0.4%/℃（25℃为基准），更保守一些
    temperature_loss = 1.0 - 0.004 * (p.avg_temperature_c - 25.0)
    derate = max(min(orient_factor * shading_loss * temperature_loss * p.inverter_efficiency, 1.0), 0.0)

    # 产能 = 装机kW × 等效日照小时 × 综合折减
    energy_kwh_day = system_kw * p.avg_sunlight_h * derate
    actual_power_kw = system_kw * derate

    percent_of_demand = (energy_kwh_day / demand_kwh_day * 100.0) if demand_kwh_day > 0 else 0.0
    return {
        "energy_kwh_day": energy_kwh_day,
        "percent_of_demand": percent_of_demand,
        "actual_power_kw": actual_power_kw,
    }
