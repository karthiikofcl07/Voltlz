from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.data.india_ev_data import CHARGERS, VEHICLES
from backend.app.services.energy import RangeInputs, battery_health, hybrid_model
from backend.app.services.geo import city_options, distance_to_polyline_km, haversine_km, interpolate_route, normalize_location, route_distance_km
from backend.app.services.pdf import build_trip_pdf

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "voltnav.sqlite3"
JWT_SECRET = os.getenv("JWT_SECRET", "voltnav-local-development-secret")

app = FastAPI(title="VoltNav 2.0 API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    name: str = "Arjun Mehta"
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RangeRequest(BaseModel):
    vehicle_model: str = "Tata Nexon EV Max"
    battery_percent: float = 80
    battery_capacity_kwh: float | None = None
    average_speed: float = 82
    ambient_temp: float = 24
    elevation_gain_m: float = 700
    wind_speed: float = 12
    humidity: float = 56
    passenger_count: int = 2
    cargo_weight_kg: float = 35
    regen_efficiency: float = 0.18
    tire_pressure_psi: float = 34
    driving_style: str = "Balanced"
    hvac_usage: str = "Auto"
    road_type: str = "Highway"
    traffic_density: str = "Moderate"


class TripPlanRequest(RangeRequest):
    origin: str = "Delhi, India"
    destination: str = "Manali, Himachal Pradesh"
    departure_time: str = "2026-07-05T07:30:00"
    driving_mode: str = "Safe"
    connector: str = "CCS2"
    charger_priority: str = "Balanced"


class AssistantRequest(BaseModel):
    message: str
    trip_id: int | None = None


class VehicleProfileRequest(BaseModel):
    vehicle_model: str = "Tata Nexon EV Max"
    odometer_km: int = 18400
    vehicle_age_months: int = 18
    fast_charge_ratio: float = 0.32
    cycles: int = 512
    hot_days: int = 110


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    if not conn.execute("SELECT id FROM users WHERE email=?", ("arjun@voltnav.demo",)).fetchone():
        conn.execute(
            "INSERT INTO users (name,email,password_hash,created_at) VALUES (?,?,?,?)",
            ("Arjun Mehta", "arjun@voltnav.demo", hash_password("voltnav123"), now_iso()),
        )
    user = conn.execute("SELECT id FROM users WHERE email=?", ("arjun@voltnav.demo",)).fetchone()
    if user and not conn.execute("SELECT id FROM vehicles WHERE user_id=?", (user["id"],)).fetchone():
        vehicle = VehicleProfileRequest().model_dump()
        vehicle["health"] = battery_health(vehicle["vehicle_age_months"], vehicle["fast_charge_ratio"], vehicle["cycles"], vehicle["hot_days"])
        conn.execute("INSERT INTO vehicles (user_id,payload,created_at) VALUES (?,?,?)", (user["id"], json.dumps(vehicle), now_iso()))
    conn.commit()
    conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 160_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 160_000).hex()
    return hmac.compare_digest(candidate, digest)


def token_for(user_id: int) -> str:
    payload = {"sub": user_id, "iat": int(time.time()), "exp": int(time.time()) + 60 * 60 * 24 * 7}
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(JWT_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def decode_token(token: str) -> int:
    try:
        raw, sig = token.split(".", 1)
        good = hmac.new(JWT_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, good):
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode())
        if payload["exp"] < time.time():
            raise ValueError("expired")
        return int(payload["sub"])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    user_id = decode_token(authorization.split(" ", 1)[1])
    conn = db()
    row = conn.execute("SELECT id,name,email,created_at FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return dict(row)


def charger_wait_minutes(charger: dict, departure_hour: int = 8) -> int:
    commute_penalty = 7 if departure_hour in {8, 9, 18, 19, 20} else 0
    availability_penalty = round((1 - charger["availability"]) * 35)
    power_bonus = -2 if charger["power_kw"] >= 120 else 1
    return max(0, int(availability_penalty + commute_penalty + power_bonus))


def charger_score(charger: dict, detour_km: float, priority: str) -> float:
    cost_weight = 0.18 if priority == "Cheapest" else 0.10
    power_weight = 0.42 if priority == "Fastest" else 0.28
    return round(
        charger["reliability"] * 32
        + charger["availability"] * 24
        + min(charger["power_kw"], 180) / 180 * 100 * power_weight
        - charger["price_per_kwh"] * cost_weight
        - detour_km * 0.34
        + charger["rating"] * 2.5,
        2,
    )


def candidate_chargers(route: list[dict], connector: str) -> list[dict]:
    candidates = []
    for charger in CHARGERS:
        detour, route_km = distance_to_polyline_km(charger, route)
        if detour <= 95 and connector in charger["connectors"]:
            enriched = dict(charger)
            enriched["detour_km"] = round(detour, 1)
            enriched["route_km"] = round(route_km, 1)
            enriched["available_probability"] = round(charger["availability"] * charger["reliability"] * 100)
            enriched["wait_minutes"] = charger_wait_minutes(charger)
            candidates.append(enriched)
    return sorted(candidates, key=lambda c: c["route_km"])


def plan_stops(req: TripPlanRequest, route: list[dict], distance_km: float, prediction: dict) -> tuple[list[dict], float, str]:
    vehicle = VEHICLES.get(req.vehicle_model, VEHICLES["Tata Nexon EV Max"])
    capacity = req.battery_capacity_kwh or vehicle["usable_kwh"]
    buffer_map = {"Safe": 0.25, "Balanced": 0.16, "Risky": 0.08}
    buffer = buffer_map.get(req.driving_mode, 0.16)
    whkm = prediction["consumption_wh_km"]
    range_per_soc = (capacity * 1000 / whkm) / 100
    current_soc = max(5, min(100, req.battery_percent))
    current_km = 0.0
    stops = []
    candidates = candidate_chargers(route, req.connector)
    max_stops = 6
    while len(stops) < max_stops:
        reachable_km = max(0, (current_soc - buffer * 100) * range_per_soc)
        if current_km + reachable_km >= distance_km:
            break
        window = [
            c for c in candidates
            if current_km + 25 <= c["route_km"] <= current_km + reachable_km and c["id"] not in {s["charger"]["id"] for s in stops}
        ]
        if not window:
            window = [
                c for c in candidates
                if current_km + 25 <= c["route_km"] <= current_km + max(20, current_soc * range_per_soc * 0.94)
                and c["id"] not in {s["charger"]["id"] for s in stops}
            ]
        if not window:
            return stops, current_soc, "Insufficient charger density on the selected corridor"
        selected = max(window, key=lambda c: charger_score(c, c["detour_km"], req.charger_priority))
        consumed_soc = (selected["route_km"] - current_km) / range_per_soc
        arrival_soc = max(2, current_soc - consumed_soc)
        next_candidates = [c["route_km"] for c in candidates if c["route_km"] > selected["route_km"] + 20]
        next_target_km = min(next_candidates + [distance_km])
        needed_soc = ((next_target_km - selected["route_km"]) / range_per_soc) + buffer * 100 + 6
        target_soc = min(88, max(62, needed_soc))
        if target_soc <= arrival_soc + 4:
            target_soc = min(88, arrival_soc + 18)
        energy_added = max(0, (target_soc - arrival_soc) * capacity / 100)
        effective_kw = min(selected["power_kw"], vehicle["max_dc_kw"]) * 0.82
        charge_minutes = max(10, round(energy_added / max(10, effective_kw) * 60))
        stop = {
            "charger": selected,
            "arrival_soc": round(arrival_soc, 1),
            "departure_soc": round(target_soc, 1),
            "energy_added_kwh": round(energy_added, 1),
            "charge_minutes": charge_minutes,
            "wait_minutes": selected["wait_minutes"],
            "score": charger_score(selected, selected["detour_km"], req.charger_priority),
            "reason": "Best combined score for charger power, availability, reliability, cost, and detour on this corridor."
        }
        stops.append(stop)
        current_soc = target_soc
        current_km = selected["route_km"]
    final_soc = max(0, current_soc - (distance_km - current_km) / range_per_soc)
    return stops, round(final_soc, 1), "OK"


def trip_payload(req: TripPlanRequest, user_id: int | None = None) -> dict:
    start = normalize_location(req.origin)
    end = normalize_location(req.destination)
    route = interpolate_route(start, end, 64)
    distance_km = round(route_distance_km(route), 1)
    terrain_gain = max(req.elevation_gain_m, haversine_km(start, end) * (3.8 if end["lat"] > 30 else 1.2))
    range_req = RangeInputs(**(req.model_dump() | {"elevation_gain_m": terrain_gain}))
    prediction = hybrid_model.predict(range_req)
    stops, arrival_soc, plan_status = plan_stops(req, route, distance_km, prediction)
    drive_minutes = round(distance_km / max(35, req.average_speed) * 60)
    charge_minutes = sum(s["charge_minutes"] + s["wait_minutes"] for s in stops)
    total_minutes = drive_minutes + charge_minutes
    kwh_used = round(distance_km * prediction["consumption_wh_km"] / 1000, 1)
    charge_cost = round(sum(s["energy_added_kwh"] * s["charger"]["price_per_kwh"] for s in stops))
    petrol_equiv = round(distance_km / 15.5 * 108)
    electric_running = round(kwh_used * 7.2 + charge_cost)
    petrol_savings = max(0, petrol_equiv - electric_running)
    co2_saved = round(distance_km * 0.121 - kwh_used * 0.035, 1)
    risk_score = 0
    risk_score += 38 if arrival_soc < 12 else 22 if arrival_soc < 22 else 6
    risk_score += 24 if len(candidate_chargers(route, req.connector)) < 2 else 8
    risk_score += 16 if req.traffic_density == "Heavy" else 5
    risk_score += 12 if req.ambient_temp > 38 or req.ambient_temp < 10 else 3
    risk_score += 14 if plan_status != "OK" else 0
    risk_level = "Safe" if risk_score < 35 else "Moderate" if risk_score < 62 else "Risky"
    assistant = (
        f"VoltNav recommends {len(stops)} charging stop{'s' if len(stops) != 1 else ''}. "
        f"The plan preserves a {req.driving_mode.lower()} buffer and targets {arrival_soc}% arrival battery. "
        f"Stops are ranked by power, predicted availability, wait time, connector compatibility, cost, and route detour."
    )
    energy_series = [
        {"label": f"{i:02d}:00", "consumption": round(prediction["consumption_wh_km"] * (0.92 + (i % 5) * 0.035), 1)}
        for i in range(6, 20, 2)
    ]
    payload = {
        "id": None,
        "origin": start["label"],
        "destination": end["label"],
        "vehicle_model": req.vehicle_model,
        "distance_km": distance_km,
        "drive_time": format_minutes(drive_minutes),
        "charging_time": format_minutes(charge_minutes),
        "total_time": format_minutes(total_minutes),
        "departure_time": req.departure_time,
        "route": route,
        "candidate_chargers": candidate_chargers(route, req.connector),
        "recommended_stops": stops,
        "arrival_battery_percent": arrival_soc,
        "prediction": prediction,
        "risk": {"level": risk_level, "score": min(100, risk_score), "status": plan_status},
        "cost": {
            "charging_cost": charge_cost,
            "electric_running_cost": electric_running,
            "petrol_equivalent_cost": petrol_equiv,
            "petrol_savings": petrol_savings,
            "avg_price_per_kwh": round(charge_cost / max(1, sum(s["energy_added_kwh"] for s in stops)), 1) if stops else 0
        },
        "carbon": {"co2_saved_kg": max(0, co2_saved), "trees_equivalent": round(max(0, co2_saved) / 21.7, 1)},
        "analytics": {"energy_series": energy_series, "efficiency_km_kwh": round(1000 / prediction["consumption_wh_km"], 1), "kwh_used": kwh_used},
        "assistant_summary": assistant,
        "created_at": now_iso(),
        "user_id": user_id
    }
    return payload


def format_minutes(minutes: int) -> str:
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model_ready": hybrid_model.ready, "chargers": len(CHARGERS), "cities": len(city_options())}


@app.post("/api/auth/register")
def register(req: RegisterRequest) -> dict:
    conn = db()
    try:
        cur = conn.execute(
            "INSERT INTO users (name,email,password_hash,created_at) VALUES (?,?,?,?)",
            (req.name, req.email.lower(), hash_password(req.password), now_iso()),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc
    user_id = cur.lastrowid
    conn.close()
    return {"token": token_for(user_id), "user": {"id": user_id, "name": req.name, "email": req.email.lower()}}


@app.post("/api/auth/login")
def login(req: LoginRequest) -> dict:
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE email=?", (req.email.lower(),)).fetchone()
    conn.close()
    if not row or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": token_for(row["id"]), "user": {"id": row["id"], "name": row["name"], "email": row["email"]}}


@app.get("/api/me")
def me(user: dict = Depends(current_user)) -> dict:
    return {"user": user}


@app.get("/api/meta")
def meta() -> dict:
    return {"cities": city_options(), "vehicles": VEHICLES, "connectors": ["CCS2", "Type 2", "CHAdeMO"]}


@app.post("/api/range/predict")
def predict_range(req: RangeRequest) -> dict:
    return hybrid_model.predict(RangeInputs(**req.model_dump()))


@app.post("/api/trips/plan")
def create_trip(req: TripPlanRequest, user: dict = Depends(current_user)) -> dict:
    payload = trip_payload(req, user["id"])
    conn = db()
    cur = conn.execute("INSERT INTO trips (user_id,payload,created_at) VALUES (?,?,?)", (user["id"], json.dumps(payload), now_iso()))
    conn.commit()
    payload["id"] = cur.lastrowid
    conn.execute("UPDATE trips SET payload=? WHERE id=?", (json.dumps(payload), cur.lastrowid))
    conn.commit()
    conn.close()
    return payload


@app.get("/api/trips/history")
def history(user: dict = Depends(current_user)) -> dict:
    conn = db()
    rows = conn.execute("SELECT id,payload,created_at FROM trips WHERE user_id=? ORDER BY id DESC LIMIT 20", (user["id"],)).fetchall()
    conn.close()
    trips = []
    for row in rows:
        payload = json.loads(row["payload"])
        payload["id"] = row["id"]
        trips.append(payload)
    if not trips:
        demo = trip_payload(TripPlanRequest(), user["id"])
        demo["id"] = 0
        trips.append(demo)
    return {"trips": trips}


@app.get("/api/chargers/search")
def chargers(q: str = "", connector: str = "CCS2") -> dict:
    query = q.lower().strip()
    data = []
    for c in CHARGERS:
        if connector not in c["connectors"]:
            continue
        if query and query not in c["name"].lower() and query not in c["city"].lower() and query not in c["network"].lower():
            continue
        item = dict(c)
        item["available_probability"] = round(c["availability"] * c["reliability"] * 100)
        item["wait_minutes"] = charger_wait_minutes(c)
        data.append(item)
    return {"chargers": data}


@app.post("/api/vehicles/profile")
def vehicle_profile(req: VehicleProfileRequest, user: dict = Depends(current_user)) -> dict:
    payload = req.model_dump()
    payload["health"] = battery_health(req.vehicle_age_months, req.fast_charge_ratio, req.cycles, 115)
    conn = db()
    conn.execute("INSERT INTO vehicles (user_id,payload,created_at) VALUES (?,?,?)", (user["id"], json.dumps(payload), now_iso()))
    conn.commit()
    conn.close()
    return payload


@app.get("/api/analytics/summary")
def analytics(user: dict = Depends(current_user)) -> dict:
    conn = db()
    rows = conn.execute("SELECT payload FROM trips WHERE user_id=? ORDER BY id DESC LIMIT 12", (user["id"],)).fetchall()
    conn.close()
    trips = [json.loads(row["payload"]) for row in rows] or [trip_payload(TripPlanRequest(), user["id"])]
    total_km = round(sum(t["distance_km"] for t in trips), 1)
    savings = round(sum(t["cost"]["petrol_savings"] for t in trips))
    co2 = round(sum(t["carbon"]["co2_saved_kg"] for t in trips), 1)
    charge_time = sum(parse_time(t["charging_time"]) for t in trips)
    return {
        "total_distance_km": total_km,
        "total_savings_inr": savings,
        "co2_saved_kg": co2,
        "total_charging_time": format_minutes(charge_time),
        "trip_count": len(trips),
        "monthly": [
            {"label": "Week 1", "km": round(total_km * 0.19), "savings": round(savings * 0.18), "co2": round(co2 * 0.18, 1)},
            {"label": "Week 2", "km": round(total_km * 0.24), "savings": round(savings * 0.23), "co2": round(co2 * 0.24, 1)},
            {"label": "Week 3", "km": round(total_km * 0.21), "savings": round(savings * 0.20), "co2": round(co2 * 0.21, 1)},
            {"label": "Week 4", "km": round(total_km * 0.36), "savings": round(savings * 0.39), "co2": round(co2 * 0.37, 1)}
        ],
        "charger_mix": {"Fast Charging": 62, "Home Charging": 25, "Destination": 13},
        "eco_score": min(98, 74 + len(trips) * 3)
    }


def parse_time(value: str) -> int:
    h = 0
    m = 0
    if "h" in value:
        h = int(value.split("h")[0])
        rest = value.split("h", 1)[1]
        m = int(rest.replace("m", "").strip() or "0")
    elif "m" in value:
        m = int(value.replace("m", "").strip())
    return h * 60 + m


@app.post("/api/assistant/chat")
def assistant(req: AssistantRequest, user: dict = Depends(current_user)) -> dict:
    trip = None
    conn = db()
    if req.trip_id:
        row = conn.execute("SELECT payload FROM trips WHERE id=? AND user_id=?", (req.trip_id, user["id"])).fetchone()
        trip = json.loads(row["payload"]) if row else None
    if not trip:
        row = conn.execute("SELECT payload FROM trips WHERE user_id=? ORDER BY id DESC LIMIT 1", (user["id"],)).fetchone()
        trip = json.loads(row["payload"]) if row else trip_payload(TripPlanRequest(), user["id"])
    conn.close()
    msg = req.message.lower()
    if "skip" in msg and trip["recommended_stops"]:
        answer = f"Skipping {trip['recommended_stops'][0]['charger']['name']} would reduce your arrival buffer below the configured risk target. Use Risky mode only if weather and traffic stay favorable."
    elif "cost" in msg or "money" in msg or "save" in msg:
        answer = f"This trip is estimated to cost INR {trip['cost']['charging_cost']} for paid charging and save about INR {trip['cost']['petrol_savings']} versus petrol."
    elif "80" in msg or "100" in msg or "charge" in msg:
        answer = "Charge to 80-88% at DC stations. Above that, charging tapers and usually increases total journey time unless the next corridor has sparse chargers."
    elif "why" in msg and trip["recommended_stops"]:
        stop = trip["recommended_stops"][0]
        answer = f"{stop['charger']['name']} was selected because it has {stop['charger']['power_kw']} kW power, {stop['charger']['available_probability']}% predicted availability, low detour, and enough onward range."
    else:
        answer = trip["assistant_summary"]
    return {"answer": answer, "trip_id": trip.get("id")}


@app.get("/api/trips/{trip_id}/pdf")
def trip_pdf(trip_id: int, user: dict = Depends(current_user)) -> Response:
    conn = db()
    row = conn.execute("SELECT payload FROM trips WHERE id=? AND user_id=?", (trip_id, user["id"])).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Trip not found")
    pdf = build_trip_pdf(json.loads(row["payload"]))
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="voltnav-trip-{trip_id}.pdf"'})


init_db()
