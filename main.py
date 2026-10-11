from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import requests
import json
import math
import os
import hmac
from fastapi.responses import JSONResponse

app = FastAPI(title="Advanced SSA Kinematic Radar & J2 Perturbation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json"
NOAA_SOLAR_URL = "https://services.swpc.noaa.gov/json/f107_cm_radio_flux.json"
NOAA_XRAY_URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_SATELLITE_DATA = os.path.join(BASE_DIR, "data", "celestrak_satellites.json")
LOCAL_SOLAR_DATA = os.path.join(BASE_DIR, "data", "noaa_solar_flux.json")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
CELESTRAK_DEBRIS_URLS = [
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=TLE",
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=fengyun-1c-debris&FORMAT=TLE",
]
DEBRIS_CACHE = {"fetched_at": None, "objects": []}
DEBRIS_CACHE_SECONDS = 900
LIVE_DATA = os.environ.get("SSA_LIVE_DATA", "0") == "1"  # default: stable bundled data, same as local demo
EMBEDDED_SATELLITES = [{"OBJECT_NAME": "ISS (ZARYA)", "OBJECT_ID": "1998-067A", "EPOCH": "2026-10-11T08:15:30.000", "MEAN_MOTION": 15.4892112, "ECCENTRICITY": 0.0006782, "INCLINATION": 51.6415, "RA_OF_ASC_NODE": 120.4512, "ARG_OF_PERICENTER": 85.1204, "MEAN_ANOMALY": 275.112, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 25544, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 14500, "BSTAR": 0.000124, "MEAN_MOTION_DOT": 2.1e-05, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 25544U 98067A   26284.34409722  .00021000  00000-0  12400-3 0  9993", "TLE_LINE2": "2 25544  51.6415 120.4512 0006782  85.1204 275.1120 15.48921120145003"}, {"OBJECT_NAME": "COSMOS 2251 DEBRIS", "OBJECT_ID": "1993-036KW", "EPOCH": "2026-10-11T07:45:12.000", "MEAN_MOTION": 14.8210451, "ECCENTRICITY": 0.0012104, "INCLINATION": 74.0312, "RA_OF_ASC_NODE": 215.1042, "ARG_OF_PERICENTER": 110.4512, "MEAN_ANOMALY": 250.1204, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 34102, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 8200, "BSTAR": 0.00045, "MEAN_MOTION_DOT": 8.5e-05, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 34102U 93036KW  26284.32305556  .00008500  00000-0  45000-3 0  9991", "TLE_LINE2": "2 34102  74.0312 215.1042 0012104 110.4512 250.1204 14.82104510 82001"}, {"OBJECT_NAME": "STARLINK-3104", "OBJECT_ID": "2021-082A", "EPOCH": "2026-10-11T09:00:00.000", "MEAN_MOTION": 15.0612, "ECCENTRICITY": 0.00015, "INCLINATION": 53.05, "RA_OF_ASC_NODE": 180.12, "ARG_OF_PERICENTER": 90.0, "MEAN_ANOMALY": 270.0, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 49120, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 5000, "BSTAR": 5e-05, "MEAN_MOTION_DOT": 1e-05, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 49120U 21082A   26284.37500000  .00001000  00000-0  50000-4 0  9992", "TLE_LINE2": "2 49120  53.0500 180.1200 0001500  90.0000 270.0000 15.06120000 50004"}, {"OBJECT_NAME": "FENGYUN 1C DEBRIS", "OBJECT_ID": "1999-025AV", "EPOCH": "2026-10-11T08:30:10.000", "MEAN_MOTION": 14.2104512, "ECCENTRICITY": 0.0025104, "INCLINATION": 98.621, "RA_OF_ASC_NODE": 45.1204, "ARG_OF_PERICENTER": 180.4512, "MEAN_ANOMALY": 180.1204, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 29810, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 11200, "BSTAR": 0.00082, "MEAN_MOTION_DOT": 0.00012, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 29810U 99025AV  26284.35428241  .00012000  00000-0  82000-3 0  9998", "TLE_LINE2": "2 29810  98.6210  45.1204 0025104 180.4512 180.1204 14.21045120112005"}, {"OBJECT_NAME": "ONEWEB-0182", "OBJECT_ID": "2020-098B", "EPOCH": "2026-10-11T09:12:00.000", "MEAN_MOTION": 13.12045, "ECCENTRICITY": 0.00012, "INCLINATION": 87.4, "RA_OF_ASC_NODE": 310.2, "ARG_OF_PERICENTER": 45.0, "MEAN_ANOMALY": 315.0, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 47312, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 3400, "BSTAR": 3e-05, "MEAN_MOTION_DOT": 5e-06, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 47312U 20098B   26284.38333333  .00000500  00000-0  30000-4 0  9997", "TLE_LINE2": "2 47312  87.4000 310.2000 0001200  45.0000 315.0000 13.12045000 34008"}, {"OBJECT_NAME": "COSMOS 2251 DEBRIS 2", "OBJECT_ID": "1993-036KX", "EPOCH": "2026-10-11T07:45:12.000", "MEAN_MOTION": 14.8210451, "ECCENTRICITY": 0.0012104, "INCLINATION": 74.0312, "RA_OF_ASC_NODE": 150.2, "ARG_OF_PERICENTER": 110.4512, "MEAN_ANOMALY": 95.4, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 34103, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 8200, "BSTAR": 0.00045, "MEAN_MOTION_DOT": 8.5e-05, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 34103U 93036KW  26284.32305556  .00008500  00000-0  45000-3 0  9998", "TLE_LINE2": "2 34103  74.0312 150.2000 0012104 110.4512  95.4000 14.82104510 82004"}, {"OBJECT_NAME": "FENGYUN 1C DEBRIS 2", "OBJECT_ID": "1999-025AW", "EPOCH": "2026-10-11T08:30:10.000", "MEAN_MOTION": 14.2104512, "ECCENTRICITY": 0.0025104, "INCLINATION": 98.621, "RA_OF_ASC_NODE": 100.7, "ARG_OF_PERICENTER": 180.4512, "MEAN_ANOMALY": 60.3, "EPHEMERIS_TYPE": 0, "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": 29811, "ELEMENT_SET_NO": 999, "REV_AT_EPOCH": 11200, "BSTAR": 0.00082, "MEAN_MOTION_DOT": 0.00012, "MEAN_MOTION_DDOT": 0.0, "TLE_LINE1": "1 29811U 99025AV  26284.35428241  .00012000  00000-0  82000-3 0  9993", "TLE_LINE2": "2 29811  98.6210 100.7000 0025104 180.4512  60.3000 14.21045120112003"}]
EMBEDDED_SOLAR = [{"time_tag": "2026-10-11 11:00:00", "flux": 168.5, "f107": 168.5}]
MAX_DEBRIS_OBJECTS = int(os.environ.get("SSA_MAX_DEBRIS", "30"))
MAX_PAIR_RECORDS = int(os.environ.get("SSA_MAX_PAIRS", "150"))

MANEUVERED_SATELLITES = {}

J2_EARTH = 1.08263e-3
R_EARTH_KM = 6378.137
MU_EARTH = 398600.4418

def compute_j2_nodal_precession(semimajor_axis_km: float, inclination_deg: float) -> float:
    if semimajor_axis_km <= R_EARTH_KM:
        return 0.0
    inc_rad = math.radians(inclination_deg)
    p = semimajor_axis_km
    n = math.sqrt(MU_EARTH / (p**3))
    domega_rad_sec = -1.5 * J2_EARTH * ((R_EARTH_KM / p)**2) * n * math.cos(inc_rad)
    return round(math.degrees(domega_rad_sec) * 86400.0, 3)

def estimate_object_size(norad_id: int, obj_name: str) -> dict:
    name_upper = obj_name.upper()
    if "ISS" in name_upper:
        return {"radius_m": 54.0, "type": "Space Station"}
    elif "STARLINK" in name_upper or "ONEWEB" in name_upper:
        return {"radius_m": 3.2, "type": "Active Satellite Payload"}
    elif "DEBRIS" in name_upper or "R/B" in name_upper or "FENGYUN" in name_upper or "COSMOS" in name_upper:
        return {"radius_m": 0.85, "type": "Space Debris Fragment"}
    return {"radius_m": 2.1, "type": "Active Satellite Payload"}

def generate_synthetic_orbit_ring(pos_eci):
    r_mag = math.sqrt(sum(p**2 for p in pos_eci))
    points = []
    for step in range(60):
        theta = (step / 60.0) * 2.0 * math.pi
        x = r_mag * math.cos(theta)
        y = r_mag * math.sin(theta)
        z = pos_eci[2] * math.sin(theta * 0.5)
        points.append([round(x, 2), round(y, 2), round(z, 2)])
    return points

def load_solar_weather(solar_flux_override: float = None) -> tuple:
    f107 = 150.0
    flare_class = "C-CLASS NORMAL"
    if solar_flux_override is not None:
        f107 = float(solar_flux_override)
        if f107 > 280: flare_class = "X-CLASS SEVERE STORM"
        elif f107 > 200: flare_class = "M-CLASS MODERATE FLARE"
        elif f107 > 120: flare_class = "C-CLASS NORMAL"
        else: flare_class = "A/B-CLASS QUIET SUN"
        return f107, flare_class
    try:
        if not LIVE_DATA: raise RuntimeError("offline")
        sw_res = requests.get(NOAA_SOLAR_URL, timeout=3).json()
        if sw_res and 'flux' in sw_res[0]: f107 = float(sw_res[0]['flux'])
    except Exception:
        pass
    return f107, flare_class

def load_debris_catalog() -> list:
    """Load catalogued debris from CelesTrak, caching responses for 15 minutes."""
    if not LIVE_DATA:
        return []
    now = datetime.utcnow()
    cached_at = DEBRIS_CACHE.get("fetched_at")
    if cached_at and (now - cached_at).total_seconds() < DEBRIS_CACHE_SECONDS:
        return DEBRIS_CACHE.get("objects", [])

    found = {}
    for url in CELESTRAK_DEBRIS_URLS:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            lines = [line.strip() for line in response.text.splitlines() if line.strip()]
            # CelesTrak TLE format is name / line 1 / line 2 per object.
            index = 0
            while index + 2 < len(lines):
                name, line1, line2 = lines[index:index + 3]
                if line1.startswith("1 ") and line2.startswith("2 "):
                    catalog_id = line1[2:7].strip()
                    found[str(catalog_id)] = {
                        "OBJECT_NAME": name.lstrip("0 ").strip(),
                        "NORAD_CAT_ID": int(catalog_id),
                        "TLE_LINE1": line1,
                        "TLE_LINE2": line2,
                        "_catalog_type": "Space Debris Fragment",
                    }
                    index += 3
                else:
                    index += 1
        except Exception:
            # A single unavailable debris group should not stop the dashboard.
            continue

    # Cache successful results, including an empty list, to avoid hammering the provider.
    if found or DEBRIS_CACHE.get("fetched_at") is None:
        DEBRIS_CACHE["fetched_at"] = now
        DEBRIS_CACHE["objects"] = list(found.values())
    return DEBRIS_CACHE.get("objects", [])


def load_satellite_catalog() -> list:
    if LIVE_DATA:
        try:
            sat_res = requests.get(CELESTRAK_URL, timeout=4).json()
            if sat_res: return sat_res[:80]
        except Exception:
            pass
    # Demo mode: same embedded catalog everywhere (local and Vercel).
    return [dict(row) for row in EMBEDDED_SATELLITES]

# --- Operator sign-in -------------------------------------------------------
# Credentials come from the environment; the defaults are for local demos only.
OPERATOR_EMAIL = os.environ.get("SSA_OPERATOR_EMAIL", "operator@ssa.local")
OPERATOR_PASSWORD = os.environ.get("SSA_OPERATOR_PASSWORD", "orbit2026")

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    ok_email = hmac.compare_digest(email.encode(), OPERATOR_EMAIL.lower().encode())
    ok_pass = hmac.compare_digest(password.encode(), OPERATOR_PASSWORD.encode())
    if ok_email and ok_pass:
        return {"status": "success", "operator": OPERATOR_EMAIL}
    return JSONResponse({"status": "error", "detail": "Invalid credentials"}, status_code=401)

@app.post("/api/maneuver")
async def apply_maneuver(request: Request):
    data = await request.json()
    sat_name = data.get("sat_name")
    strategy = data.get("strategy", "A")
    offset = 2500.0 if strategy == "A" else 5000.0
    
    MANEUVERED_SATELLITES[sat_name] = {
        "offset_eci": [offset, offset * 0.5, -offset * 0.3],
        "strategy": strategy
    }
    return {"status": "success", "sat_name": sat_name, "offset_applied": offset}

@app.get("/api/conjunctions")
def get_conjunctions(solar_flux_override: float = None, time_offset_hours: float = 0.0):
    f107, flare_class = load_solar_weather(solar_flux_override)
    sat_data = load_satellite_catalog()
    known_ids = {str(row.get("NORAD_CAT_ID")) for row in sat_data}
    debris_rows = [d for d in load_debris_catalog() if str(d.get("NORAD_CAT_ID")) not in known_ids]
    if len(debris_rows) > MAX_DEBRIS_OBJECTS > 0:
        step = len(debris_rows) / MAX_DEBRIS_OBJECTS
        debris_rows = [debris_rows[int(i * step)] for i in range(MAX_DEBRIS_OBJECTS)]
    sat_data.extend(debris_rows)
    drag_sigma_km = 0.8 + (f107 / 100.0) * 1.8

    satellites_render = []
    now = datetime.utcnow() + timedelta(hours=time_offset_hours)
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

    if sat_data:
        for idx, sat_obj in enumerate(sat_data):
            try:
                sat_rec = Satrec.twoline2rv(sat_obj['TLE_LINE1'], sat_obj['TLE_LINE2'])
                e, pos, vel = sat_rec.sgp4(jd, fr)
                if e == 0:
                    s_name = sat_obj.get('OBJECT_NAME', f'SAT-{idx}')
                    norad_id = sat_obj.get('NORAD_CAT_ID', 10000 + idx)
                    is_catalog_debris = sat_obj.get("_catalog_type") == "Space Debris Fragment"
                    size_info = estimate_object_size(norad_id, s_name)
                    if is_catalog_debris:
                        size_info = {"radius_m": size_info["radius_m"], "type": "Space Debris Fragment"}
                    r_mag = math.sqrt(sum(p**2 for p in pos))
                    inc_deg = math.degrees(sat_rec.inclo)
                    j2_precession = compute_j2_nodal_precession(r_mag, inc_deg)
                    
                    pos_list = [round(p, 3) for p in pos]
                    is_maneuvered = False
                    if s_name in MANEUVERED_SATELLITES:
                        m = MANEUVERED_SATELLITES[s_name]["offset_eci"]
                        pos_list[0] += m[0]
                        pos_list[1] += m[1]
                        pos_list[2] += m[2]
                        is_maneuvered = True

                    satellites_render.append({
                        "id": norad_id,
                        "name": s_name,
                        "type": size_info['type'],
                        "radius_m": size_info['radius_m'],
                        "j2_nodal_precession_deg_day": j2_precession,
                        "maneuvered": is_maneuvered,
                        "pos_eci": pos_list,
                        "vel_eci": [round(v, 4) for v in vel],
                        "orbit_ring": generate_synthetic_orbit_ring(pos_list)
                    })
            except Exception:
                continue

    if not satellites_render:
        fallback_sats = [
            {"id": 49120, "name": "STARLINK-3104", "type": "Active Satellite Payload", "radius_m": 3.2, "pos_eci": [4210.5, 3100.2, 5100.8], "vel_eci": [-1.2, 7.1, 2.3]},
            {"id": 49121, "name": "STARLINK-3105", "type": "Active Satellite Payload", "radius_m": 3.2, "pos_eci": [4214.2, 3103.8, 5103.1], "vel_eci": [-1.15, 7.08, 2.28]},
            {"id": 25544, "name": "ISS (ZARYA)", "type": "Space Station", "radius_m": 54.0, "pos_eci": [-2100.4, 5500.1, 3800.6], "vel_eci": [6.5, 1.1, -3.8]},
            {"id": 47312, "name": "ONEWEB-0182", "type": "Active Satellite Payload", "radius_m": 2.8, "pos_eci": [-2095.1, 5508.3, 3805.2], "vel_eci": [6.42, 1.18, -3.75]}
        ]
        for s in fallback_sats:
            s["j2_nodal_precession_deg_day"] = -5.12
            s["maneuvered"] = s["name"] in MANEUVERED_SATELLITES
            if s["maneuvered"]:
                m = MANEUVERED_SATELLITES[s["name"]]["offset_eci"]
                s["pos_eci"][0] += m[0]
                s["pos_eci"][1] += m[1]
                s["pos_eci"][2] += m[2]
            s["orbit_ring"] = generate_synthetic_orbit_ring(s["pos_eci"])
            satellites_render.append(s)

    # Debris markers now come from catalogued CelesTrak debris records, not hardcoded positions.
    conjunction_pairs = []
    num_objs = len(satellites_render)
    for i in range(num_objs):
        for j in range(i + 1, num_objs):
            s1, s2 = satellites_render[i], satellites_render[j]
            is_sat1 = "Debris" not in s1["type"]
            is_sat2 = "Debris" not in s2["type"]
            if is_sat1 or is_sat2:
                conjunction_pairs.append({
                    "sat1_name": s1["name"],
                    "sat2_name": s2["name"],
                    "event_type": "SATELLITE ↔ SATELLITE CONJUNCTION" if (is_sat1 and is_sat2) else "SATELLITE ↔ DEBRIS CONJUNCTION"
                })

    if len(conjunction_pairs) > MAX_PAIR_RECORDS:
        pos_by_name = {o["name"]: o["pos_eci"] for o in satellites_render}
        conjunction_pairs.sort(key=lambda p: math.dist(pos_by_name[p["sat1_name"]], pos_by_name[p["sat2_name"]]))
        conjunction_pairs = conjunction_pairs[:MAX_PAIR_RECORDS]

    return {
        "f107_index": round(f107, 1),
        "solar_flare_class": flare_class,
        "time_offset_hours": round(time_offset_hours, 1),
        "drag_covariance_sigma_km": round(drag_sigma_km, 2),
        "active_satellites_count": len(satellites_render),
        "objects": satellites_render,
        "conjunction_pairs": conjunction_pairs
    }

# Frontend lives in public/. Vercel serves public/** from its CDN; this mount serves the same files locally.
if os.path.isdir(PUBLIC_DIR):
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)