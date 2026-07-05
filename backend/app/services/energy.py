from __future__ import annotations

import math
from dataclasses import dataclass

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    import numpy as np
except Exception:  # pragma: no cover - fallback for minimal installs
    GradientBoostingRegressor = None
    RandomForestRegressor = None
    np = None

from backend.app.data.india_ev_data import VEHICLES


@dataclass
class RangeInputs:
    vehicle_model: str
    battery_percent: float
    battery_capacity_kwh: float | None = None
    average_speed: float = 82
    ambient_temp: float = 28
    elevation_gain_m: float = 300
    wind_speed: float = 8
    humidity: float = 55
    passenger_count: int = 2
    cargo_weight_kg: float = 30
    regen_efficiency: float = 0.18
    tire_pressure_psi: float = 34
    driving_style: str = "Balanced"
    hvac_usage: str = "Auto"
    road_type: str = "Highway"
    traffic_density: str = "Moderate"


def _vehicle(model: str) -> dict:
    return VEHICLES.get(model) or VEHICLES["Tata Nexon EV Max"]


def physics_consumption_wh_km(inputs: RangeInputs) -> float:
    vehicle = _vehicle(inputs.vehicle_model)
    mass = 1450 + inputs.passenger_count * 72 + inputs.cargo_weight_kg
    speed_ms = inputs.average_speed / 3.6
    rho = 1.225 * (273.15 / (273.15 + inputs.ambient_temp))
    cd_a = 0.72
    rolling = 0.011
    drivetrain = 0.88
    drag_wh_km = 0.5 * rho * cd_a * speed_ms**2 / drivetrain / 3.6
    rolling_wh_km = rolling * mass * 9.81 / drivetrain / 3.6
    elevation_wh_km = max(0, inputs.elevation_gain_m) * mass * 9.81 / 3600 / max(1, 100) / drivetrain
    temp_factor = 1 + max(0, 18 - inputs.ambient_temp) * 0.012 + max(0, inputs.ambient_temp - 34) * 0.009
    wind_factor = 1 + max(0, inputs.wind_speed - 10) * 0.006
    tire_factor = 1 + max(0, 33 - inputs.tire_pressure_psi) * 0.012
    style_factor = {"Eco": 0.91, "Balanced": 1.0, "Aggressive": 1.15}.get(inputs.driving_style, 1.0)
    hvac_factor = {"Off": 0.97, "Eco": 1.02, "Auto": 1.06, "High": 1.13}.get(inputs.hvac_usage, 1.06)
    traffic_factor = {"Light": 0.97, "Moderate": 1.04, "Heavy": 1.13}.get(inputs.traffic_density, 1.04)
    regen_credit = min(0.22, inputs.regen_efficiency) * (1.0 if inputs.road_type != "Expressway" else 0.55)
    base = vehicle["base_efficiency_wh_km"] * 0.42 + drag_wh_km + rolling_wh_km + elevation_wh_km
    return round(base * temp_factor * wind_factor * tire_factor * style_factor * hvac_factor * traffic_factor * (1 - regen_credit), 1)


class HybridRangeModel:
    """Small bundled ensemble with deterministic synthetic EV physics training data.

    XGBoost can be plugged in when installed; the default GradientBoosting +
    RandomForest ensemble keeps the project dependency-light and runnable.
    """

    def __init__(self):
        self.ready = False
        self.gb = None
        self.rf = None
        if GradientBoostingRegressor and RandomForestRegressor and np is not None:
            self._train()

    def _train(self):
        rng = np.random.default_rng(42)
        rows, y = [], []
        models = list(VEHICLES)
        for _ in range(700):
            model = rng.choice(models)
            data = RangeInputs(
                vehicle_model=model,
                battery_percent=float(rng.uniform(15, 100)),
                average_speed=float(rng.uniform(35, 115)),
                ambient_temp=float(rng.uniform(5, 43)),
                elevation_gain_m=float(rng.uniform(0, 1800)),
                wind_speed=float(rng.uniform(0, 32)),
                humidity=float(rng.uniform(20, 95)),
                passenger_count=int(rng.integers(1, 6)),
                cargo_weight_kg=float(rng.uniform(0, 180)),
                regen_efficiency=float(rng.uniform(0.08, 0.23)),
                tire_pressure_psi=float(rng.uniform(29, 38)),
                driving_style=str(rng.choice(["Eco", "Balanced", "Aggressive"])),
                hvac_usage=str(rng.choice(["Off", "Eco", "Auto", "High"])),
                road_type=str(rng.choice(["City", "Highway", "Expressway", "Hills"])),
                traffic_density=str(rng.choice(["Light", "Moderate", "Heavy"]))
            )
            whkm = physics_consumption_wh_km(data) * float(rng.normal(1, 0.035))
            rows.append(self._features(data))
            y.append(whkm)
        self.gb = GradientBoostingRegressor(random_state=7, n_estimators=110, max_depth=3).fit(rows, y)
        self.rf = RandomForestRegressor(random_state=7, n_estimators=80, max_depth=8).fit(rows, y)
        self.ready = True

    def _features(self, inputs: RangeInputs) -> list[float]:
        vehicle = _vehicle(inputs.vehicle_model)
        return [
            vehicle["base_efficiency_wh_km"], vehicle["capacity_kwh"], inputs.battery_percent,
            inputs.average_speed, inputs.ambient_temp, inputs.elevation_gain_m, inputs.wind_speed,
            inputs.humidity, inputs.passenger_count, inputs.cargo_weight_kg, inputs.regen_efficiency,
            inputs.tire_pressure_psi, {"Eco": 0, "Balanced": 1, "Aggressive": 2}.get(inputs.driving_style, 1),
            {"Off": 0, "Eco": 1, "Auto": 2, "High": 3}.get(inputs.hvac_usage, 2),
            {"City": 0, "Highway": 1, "Expressway": 2, "Hills": 3}.get(inputs.road_type, 1),
            {"Light": 0, "Moderate": 1, "Heavy": 2}.get(inputs.traffic_density, 1)
        ]

    def predict(self, inputs: RangeInputs) -> dict:
        vehicle = _vehicle(inputs.vehicle_model)
        capacity = inputs.battery_capacity_kwh or vehicle["usable_kwh"]
        physics_wh = physics_consumption_wh_km(inputs)
        if self.ready:
            x = [self._features(inputs)]
            ml_wh = (float(self.gb.predict(x)[0]) * 0.58) + (float(self.rf.predict(x)[0]) * 0.42)
        else:
            ml_wh = physics_wh * 1.01
        fused_wh = round(physics_wh * 0.52 + ml_wh * 0.48, 1)
        usable = capacity * max(0, min(100, inputs.battery_percent)) / 100
        range_km = round((usable * 1000) / max(fused_wh, 1), 1)
        confidence = max(82, min(97, 94 - abs(physics_wh - ml_wh) / 9))
        return {
            "range_km": range_km,
            "consumption_wh_km": fused_wh,
            "physics_wh_km": round(physics_wh, 1),
            "ml_wh_km": round(ml_wh, 1),
            "confidence": round(confidence, 1),
            "usable_energy_kwh": round(usable, 2)
        }


hybrid_model = HybridRangeModel()


def battery_health(vehicle_age_months: int, fast_charge_ratio: float, cycles: int, hot_days: int) -> dict:
    fade = vehicle_age_months * 0.055 + cycles * 0.012 + fast_charge_ratio * 5.2 + hot_days * 0.006
    soh = max(70, 100 - fade)
    replacement_years = max(1.5, (soh - 70) / 2.6)
    return {
        "state_of_health": round(soh, 1),
        "capacity_fade": round(100 - soh, 1),
        "replacement_timeline_years": round(replacement_years, 1),
        "recommendation": "Limit frequent 100% DC fast charging" if fast_charge_ratio > 0.45 else "Battery pattern is healthy"
    }
