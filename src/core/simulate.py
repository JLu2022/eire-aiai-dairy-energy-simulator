from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

from src.core.abm_model import Farm  # ← or replace with Farm imported from your energy.py if needed

@dataclass
class DayResult:
    hourly_total: List[float]           # length 24, unit Wh
    total_wh: float                     # total daily energy consumption (Wh)
    peak_w: float                       # peak power (W)
    peak_hour: int                      # hour of peak occurrence
    breakdown: Dict[str, List[float]]   # hourly profile for each device (Wh)

def simulate_one_day(
    n_cows: int,
    n_milking_units: int,
    month: int,
    day: int,
    start_morning: int = 7,
    start_evening: int = 17,
    milk_cooling_system: str = "DX",
    electric_water_heating: str = "YES",
) -> DayResult:
    farm = Farm(
        "demo_farm",
        n_cows,
        n_milking_units,
        month,
        day,
        start_milking=[start_morning, start_evening],
        milk_cooling_system=milk_cooling_system,
        electric_water_heating=electric_water_heating,
    )
    farm.set_agents()

    # Total load curve (24h)
    hourly_total = list(farm.t_consumption())  # Wh

    # Breakdown by equipment
    breakdown = {}
    for agent in farm.agents:
        breakdown[agent.eq_id] = agent.total_consumption()  # list of length 24

    total_wh = float(sum(hourly_total))
    peak_w = float(max(hourly_total))
    peak_hour = int(np.argmax(hourly_total))

    return DayResult(
        hourly_total=hourly_total,
        total_wh=total_wh,
        peak_w=peak_w,
        peak_hour=peak_hour,
        breakdown=breakdown,
    )
