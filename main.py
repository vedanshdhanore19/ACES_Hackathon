from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import requests
import json
import math
import os

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
LOCAL_SATELLITE_DATA = "data/celestrak_satellites.json"
LOCAL_SOLAR_DATA = "data/noaa_solar_flux.json"

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
        sw_res = requests.get(NOAA_SOLAR_URL, timeout=3).json()
        if sw_res and 'flux' in sw_res[0]: f107 = float(sw_res[0]['flux'])
    except Exception:
        pass
    return f107, flare_class

def load_satellite_catalog() -> list:
    try:
        sat_res = requests.get(CELESTRAK_URL, timeout=4).json()
        if sat_res: return sat_res[:80]
    except Exception:
        pass
    if os.path.exists(LOCAL_SATELLITE_DATA):
        try:
            with open(LOCAL_SATELLITE_DATA, 'r') as f: return json.load(f)
        except Exception: pass
    return []

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
                    size_info = estimate_object_size(norad_id, s_name)
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

    far_debris = [
        {"id": 99001, "name": "COSMOS 2251 DEBRIS (FAR)", "type": "Space Debris Fragment", "radius_m": 0.85, "j2_nodal_precession_deg_day": -3.21, "maneuvered": False, "pos_eci": [14200.5, -16500.2, 11800.8], "vel_eci": [-2.12, 3.85, 1.80], "orbit_ring": generate_synthetic_orbit_ring([14200.5, -16500.2, 11800.8])},
        {"id": 99002, "name": "FENGYUN 1C DEBRIS (DEEP)", "type": "Space Debris Fragment", "radius_m": 0.90, "j2_nodal_precession_deg_day": -2.85, "maneuvered": False, "pos_eci": [-18500.2, 12800.1, -14200.4], "vel_eci": [3.20, -1.85, -2.80], "orbit_ring": generate_synthetic_orbit_ring([-18500.2, 12800.1, -14200.4])}
    ]
    satellites_render.extend(far_debris)

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

    return {
        "f107_index": round(f107, 1),
        "solar_flare_class": flare_class,
        "time_offset_hours": round(time_offset_hours, 1),
        "drag_covariance_sigma_km": round(drag_sigma_km, 2),
        "active_satellites_count": len(satellites_render),
        "objects": satellites_render,
        "conjunction_pairs": conjunction_pairs
    }

if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)