# src/core/abm_model.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import math
import numpy as np

# ----------------------------- Utilities -----------------------------

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def days_in_month(month: int) -> int:
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month == 2:
        return 28  # Non-leap year, same as original code
    return 30


def monthly_interpolated_per_day(month: int, day: int, monthly_totals: List[float]) -> float:
    """
    Given 12 monthly total values for an equipment type (same as the original scalar inputs),
    compute the *daily factor* for the given day in that month
    by linear interpolation between adjacent months and dividing by the number of days in the current month.
    """
    m_idx = month - 1
    cur = monthly_totals[m_idx]
    nxt = monthly_totals[(m_idx + 1) % 12]

    ndays_cur = days_in_month(month)
    ndays_next = days_in_month(1 if month == 12 else month + 1)

    # The original logic effectively transitions linearly between the “per day” values of adjacent months
    cur_per_day = cur / ndays_cur
    next_per_day = nxt / ndays_next
    t = max(0, min(1, day / ndays_cur))  # between 0 and 1
    return cur_per_day + t * (next_per_day - cur_per_day)


def apply_cap_with_rollover(series: List[float], cap: float | None) -> List[float]:
    """Apply a power cap to hourly energy use; overflow is rolled over to the next hour; last hour overflow is discarded."""
    if cap is None:
        return series
    s = series[:]
    for i in range(24):
        if s[i] > cap:
            overflow = s[i] - cap
            s[i] = cap
            if i < 23:
                s[i + 1] += overflow
            # no rollover for the last hour
    return s


# ----------------------------- Base class -----------------------------

class Agents:
    """
    Base class for all agents: stores farm parameters and common calculations.
    """

    def __init__(
            self,
            farm_name: str,
            n_milking_machines: int,
            month: int,
            day: int,
            eq_name: str,
            milking_time: List[int],
            n_cows: int,
            milk_cooling_system: str,
            electric_water_heating: str,
    ):
        self.farm_name = farm_name
        self.eq_id = eq_name
        self.n_mm = n_milking_machines
        self.month = month
        self.day = day
        self.milking_time = milking_time  # [morning_hour, evening_hour]
        self.n_cows = n_cows
        self.milk_cooling_system = milk_cooling_system
        self.electric_water_heating = electric_water_heating

        # Each cow = 12 minutes per unit; round up to nearest hour for duration approximation
        self.time_of_milking = int(math.ceil(self.n_cows * (12.0 / 60.0) / max(1, self.n_mm)))

        # Constant from original code
        self.milk_per_day = 21

    # To be implemented by subclasses
    def consumption(self, hour: int) -> float:
        return 0.0

    def total_consumption(self) -> List[float]:
        return [self.consumption(h) for h in range(24)]

    def milk_day(self) -> float:
        return self.milk_per_day


# ----------------------------- Equipment -----------------------------

class WaterHeater(Agents):
    """
    Electric water heater (active only if electric_water_heating == 'YES')
    Original formula: daily = n_cows*day_factor + 1840 + n_mm*180.5 + n_cows*275
    Then distributed hourly with a cap of 3400 W; overflow rolls over.
    """
    MONTHLY = [2270, 3840, 4330, 3980, 3720, 3280, 3290, 3250, 3180, 3390, 3330, 2280]

    def consumption(self, hour: int) -> float:
        if self.electric_water_heating != "YES":
            return 0.0

        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = (day_factor * self.n_cows) + 1840 + self.n_mm * 180.5 + self.n_cows * 275

        max_hot_water = 3110.0

        # Distribute the daily load into full-power hours + one fractional hour (same as original logic)
        full_hours = int(np.floor(con_daily / max_hot_water))
        remainder = con_daily % max_hot_water

        if 0 < hour <= full_hours:
            return max_hot_water
        if hour == full_hours + 1 and remainder > 0:
            return remainder
        return 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3400.0)


class MilkCooling(Agents):
    """
    Milk cooling (DX only, same as original)
    - Daily total: interpolated from monthly array
    - 4/7 during morning milking, 3/7 during evening
    - Duration: from milking start, lasting time_of_milking hours
    - cap=3800 W
    """
    MONTHLY_DX = [1230, 2560, 5350, 6930, 7900, 7810, 7390, 6570, 5650, 4750, 3100, 1550]

    def consumption(self, hour: int) -> float:
        if self.milk_cooling_system != "DX":
            return 0.0

        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY_DX)
        con_daily = self.n_cows * day_factor

        morning_share = con_daily * (4.0 / 7.0)
        evening_share = con_daily * (3.0 / 7.0)
        # morning_share = con_daily * 0.5
        # evening_share = con_daily * 0.5
        dur = max(1, self.time_of_milking)

        if self.milking_time[0] <= hour < self.milking_time[0] + dur:
            return morning_share / dur
        if self.milking_time[1] <= hour < self.milking_time[1] + dur:
            return evening_share / dur

        return 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3800.0)


class MilkHarvesting(Agents):
    """
    Milking machine load
    - Daily total interpolated from monthly array, split evenly between morning/evening
    - Time window: starts 1 hour after milking start, lasting time_of_milking hours
    - cap=3000 W
    """
    MONTHLY = [1180, 2910, 3980, 4180, 4300, 3910, 3890, 3760, 3630, 3660, 2780, 1290]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        half = (self.n_cows * day_factor) / 2.0
        dur = max(1, self.time_of_milking)

        if self.milking_time[0] + 1 <= hour < self.milking_time[0] + 1 + dur:
            return half / dur
        if self.milking_time[1] + 1 <= hour < self.milking_time[1] + 1 + dur:
            return half / dur
        return 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3000.0)


class Lights(Agents):
    """Lighting: evenly distributed over 24 hours; cap=3400 W (same as original)."""
    MONTHLY = [851, 1330, 1200, 804, 644, 536, 436, 451, 541, 774, 925, 770]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = self.n_cows * day_factor
        return con_daily / 24.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3400.0)


class Others(Agents):
    """
    Other loads (a conceptual group including lights + scrapper + effluent pump + compressor, as in original)
    In the original model: active only at (morning+1) and (evening+1), each using daily*0.5; cap=2300 W.
    """
    MONTHLY = [4380, 4970, 4730, 3330, 2980, 2510, 2700, 2620, 2520, 2310, 2740, 3710]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = self.n_cows * day_factor
        if hour == self.milking_time[0] + 1:
            return con_daily * 0.5
        if hour == self.milking_time[1] + 1:
            return con_daily * 0.5
        return 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=2300.0)


class EffluentPump(Agents):
    """Effluent pump: active only at (morning+1); cap=3400 W."""
    MONTHLY = [98, 149, 212, 219, 231, 193, 234, 208, 194, 237, 201, 110]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = self.n_cows * day_factor
        return con_daily if hour == self.milking_time[0] + 1 else 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3400.0)


class WashPump(Agents):
    """Wash pump: active only at (morning+1); cap=3400 W."""
    MONTHLY = [283, 340, 435, 450, 437, 432, 449, 461, 441, 426, 467, 361]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = self.n_cows * day_factor
        return con_daily if hour == self.milking_time[0] + 1 else 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3400.0)


class Scrapper(Agents):
    """Scraper: active only at (morning+1); cap=3400 W."""
    MONTHLY = [1550, 1310, 979, 422, 198, 72.5, 96, 111, 125, 915, 2210, 2110]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = self.n_cows * day_factor
        return con_daily if hour == self.milking_time[0] + 1 else 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3400.0)


class Compressor(Agents):
    """Compressor: active at both (morning+1) and (evening+1), each using daily*0.5; cap=3400 W."""
    MONTHLY = [218, 314, 392, 476, 376, 361, 370, 361, 334, 360, 298, 205]

    def consumption(self, hour: int) -> float:
        day_factor = monthly_interpolated_per_day(self.month, self.day, self.MONTHLY)
        con_daily = self.n_cows * day_factor
        if hour == self.milking_time[0] + 1:
            return con_daily * 0.5
        if hour == self.milking_time[1] + 1:
            return con_daily * 0.5
        return 0.0

    def total_consumption(self) -> List[float]:
        series = super().total_consumption()
        return apply_cap_with_rollover(series, cap=3400.0)


# ----------------------------- Farm -----------------------------

class Farm:
    """
    Farm: assembles all agents, outputs 24-hour total load curve and total daily energy consumption.
    """

    def __init__(
            self,
            name: str,
            n_cows: int,
            n_milking_machines: int,
            month: int,
            day: int,
            start_milking: List[int] = [7, 15],
            milk_cooling_system: str = "DX",
            electric_water_heating: str = "YES",
    ):
        self.name = name
        self.n_cows = n_cows
        self.n_mm = n_milking_machines
        self.month = month
        self.day = day
        self.milking_time = start_milking
        self.milk_cooling_system = milk_cooling_system
        self.electric_water_heating = electric_water_heating

        self.set_agents()

    def set_agents(self):
        self.agents: List[Agents] = [
            Others(self.name, self.n_mm, self.month, self.day, "others", self.milking_time, self.n_cows,
                   self.milk_cooling_system, self.electric_water_heating),
            # Lights(self.name, self.n_mm, self.month, self.day, "lights", self.milking_time, self.n_cows, self.milk_cooling_system, self.electric_water_heating),
            WaterHeater(self.name, self.n_mm, self.month, self.day, "water_heater", self.milking_time, self.n_cows,
                        self.milk_cooling_system, self.electric_water_heating),
            MilkCooling(self.name, self.n_mm, self.month, self.day, "milk_cooling", self.milking_time, self.n_cows,
                        self.milk_cooling_system, self.electric_water_heating),
            # EffluentPump(self.name, self.n_mm, self.month, self.day, "effluent_pump", self.milking_time, self.n_cows, self.milk_cooling_system, self.electric_water_heating),
            # Compressor(self.name, self.n_mm, self.month, self.day, "compressor", self.milking_time, self.n_cows, self.milk_cooling_system, self.electric_water_heating),
            WashPump(self.name, self.n_mm, self.month, self.day, "wash_pump", self.milking_time, self.n_cows,
                     self.milk_cooling_system, self.electric_water_heating),
            # Scrapper(self.name, self.n_mm, self.month, self.day, "scrapper", self.milking_time, self.n_cows, self.milk_cooling_system, self.electric_water_heating),
            MilkHarvesting(self.name, self.n_mm, self.month, self.day, "milking_machine", self.milking_time,
                           self.n_cows, self.milk_cooling_system, self.electric_water_heating),
        ]
        return self.agents

    # Hourly total load curve
    def t_consumption(self) -> List[float]:
        total = np.zeros(24, dtype=float)
        for agent in self.agents:
            total += np.array(agent.total_consumption(), dtype=float)
        return list(total)

    # Total daily energy (Wh)
    def total_consumption(self) -> float:
        return float(sum(self.t_consumption()))


# ----------------------------- Simulation shortcut -----------------------------

@dataclass
class DayResult:
    hourly_total: List[float]  # length 24, in Wh
    total_wh: float  # total daily consumption Wh
    peak_w: float  # peak power W
    peak_hour: int  # hour of peak
    breakdown: Dict[str, List[float]]  # per-equipment hourly breakdown (Wh)


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

    hourly_total = farm.t_consumption()
    breakdown = {a.eq_id: a.total_consumption() for a in farm.agents}
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
