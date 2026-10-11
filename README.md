    # Orbital Risk Engine — Space Traffic Monitoring Prototype

A Python/FastAPI and browser-based prototype for visualizing Earth-orbiting objects, retrieving public orbital and space-weather data, propagating orbital elements with SGP4, and flagging instantaneous close-proximity candidates for inspection.

> **Project status:** Prototype / demonstration software. This is not an operational collision-avoidance service. It does not currently use a database, and a close-proximity flag is not a validated collision probability or a prediction of a future closest approach.

## Contents

- [Overview](#overview)
- [Current capabilities](#current-capabilities)
- [Technology stack](#technology-stack)
- [Data sources and data provenance](#data-sources-and-data-provenance)
- [Architecture and data flow](#architecture-and-data-flow)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Setup and run locally](#setup-and-run-locally)
- [API reference](#api-reference)
- [Configuration](#configuration)
- [Database and persistence](#database-and-persistence)
- [Limitations and interpretation](#limitations-and-interpretation)
- [Troubleshooting](#troubleshooting)
- [Security notes](#security-notes)
- [Possible next steps](#possible-next-steps)
- [References](#references)

## Overview

Orbital Risk Engine is intended to help demonstrate a space-situational-awareness workflow:

1. Request orbital elements from a public catalogue.
2. Propagate available orbital elements to an evaluation time using SGP4.
3. Calculate the current separation between the propagated positions of tracked objects.
4. Return objects, close-proximity candidates, solar-flux context, and calculation timestamps through a REST API.
5. Present the results in a web dashboard.

The application also checks NASA SSCWeb availability and retrieves solar radio-flux data from NOAA SWPC. These are distinct data sources with different roles; NASA SSCWeb is **not** treated as a complete catalogue of all Earth-orbiting satellites and debris.

## Current capabilities

Implemented in the supplied code:

- FastAPI backend served by Uvicorn.
- Static web frontend served from the `static/` directory.
- CelesTrak active-object GP catalogue request, limited to the first 80 valid records in the current implementation.
- Additional CelesTrak debris-group requests for Cosmos 2251 and Fengyun-1C debris, with an in-memory cache.
- SGP4 propagation of available TLE records to the selected evaluation time.
- Current-position Euclidean separation screening; object pairs at or below 80 km are returned as proximity candidates.
- NOAA F10.7 solar radio-flux request with a default value if the request fails.
- NASA SSCWeb observatory-catalogue connectivity check with a five-minute in-memory cache.
- API responses include source labels and UTC calculation timestamps where implemented.
- Basic operator credential check endpoint and a demonstration maneuver endpoint.
- Interactive dashboard and supporting visual assets.

The repository contains multiple UI documents: `static/index.html` is the landing page, while `static/dashboard.html` is the main mission-console/dashboard page. Use the landing page's **Launch mission console** control to navigate into the dashboard.

## Technology stack

| Area | Technology | Role |
|---|---|---|
| Backend language | Python 3 | API logic, data ingestion, orbital calculations |
| API framework | FastAPI | HTTP endpoints and JSON responses |
| ASGI server | Uvicorn | Runs the application locally |
| HTTP client | Requests | Calls public external data APIs |
| Orbital propagation | `sgp4` | Propagates TLE orbital elements to position/velocity state vectors |
| Frontend | HTML, CSS, JavaScript | Landing page and mission dashboard |
| Visualization | Browser-based graphics and included ThreeUI assets | Visual interface and topology/space-themed presentation |
| Data persistence | None currently | API data and maneuver state are not stored in a database |

The installed Python dependencies are listed in `requirements.txt`. The current application does not require Node.js or a frontend build step to run its FastAPI-served static pages.

## Data sources and data provenance

### CelesTrak — orbital catalogue

- Active GP JSON endpoint: `https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json`
- Debris group endpoints are defined in `main.py` for Cosmos 2251 and Fengyun-1C.
- Used for orbital elements and object identifiers that are passed to SGP4.
- The active catalogue is currently limited to the first 80 valid records returned by the request, plus successfully retrieved debris records.

### NASA SSCWeb — observatory catalogue

- API base used by this project: `https://sscweb.gsfc.nasa.gov/WS/sscr/2`
- The application requests the `/observatories` resource for the `/api/data-status` endpoint.
- This is a connectivity/catalogue check. The current conjunction calculation does **not** use NASA SSCWeb as its primary source of Earth-orbiting object elements.

### NOAA SWPC — solar radio flux

- F10.7 endpoint: `https://services.swpc.noaa.gov/json/f107_cm_radio_flux.json`
- The backend uses the returned `flux` field when a valid response is available.
- If the request fails, the implementation retains a default F10.7 value of `150.0`. Check the response and logs before describing the value as live.
- An X-ray endpoint URL is declared in the code, but it is not currently used in the main conjunction response path.

### Important source distinction

The `data_source` field in `/api/conjunctions` identifies CelesTrak plus SGP4 as the source/processing path for the returned orbital objects. NASA SSCWeb's successful status means the observatory catalogue request succeeded; it does not mean NASA supplied every satellite/debris position displayed by this application.

## Architecture and data flow

```text
CelesTrak active GP catalogue ─┐
CelesTrak debris groups ────────┴─> FastAPI backend
                                      │
NOAA SWPC F10.7 endpoint ────────────┤
                                      ├─> SGP4 propagation at evaluation time
NASA SSCWeb observatories ─> status ──┤
                                      ├─> Current-position separation screen
                                      │
                                      └─> JSON API response
                                               │
                                               v
                                      Browser dashboard
```

NASA SSCWeb is currently used by the status endpoint, not as the primary orbital catalogue for the Earth-orbiting object screen. The frontend is served by FastAPI from the local `static/` folder.

## Project structure

```text
Space Traffic Risk Engine/
├── README.md                         # Main project documentation
├── PRD.md                            # Product requirements and intended features
├── architecture.md                   # Architecture notes
├── techstack.md                      # Technology/tooling notes
├── rules.md                          # Development constraints
├── memory.md                         # Project notes/task context
├── REAL_DATA_SOURCES.md              # Data source and no-synthetic-position notes
├── FRONTEND_INTEGRATION.md            # Landing page and frontend integration notes
├── FRONTEND_REFINEMENT.md             # UI refinement notes
├── requirements.txt                  # Python dependencies
├── main.py                           # FastAPI API, external requests, SGP4 and screening
├── data/
│   └── noaa_solar_flux.json           # Local data file; not a database
└── static/
    ├── index.html                    # Landing page
    ├── dashboard.html                # Mission dashboard
    ├── space-console-background.png  # Dashboard background asset
    ├── space-traffic-logo.png        # Logo asset
    ├── cosmic-background.jpg         # Background asset
    └── threeui/                      # Supporting visualization assets/source files
```

## Requirements

- Python 3.10 or newer is recommended.
- Internet access is needed for live CelesTrak, NASA SSCWeb, and NOAA requests.
- A modern browser with JavaScript enabled.
- `pip` for dependency installation.

## Setup and run locally

### 1. Extract the project

Extract the ZIP and open a terminal in the folder containing `main.py` and `requirements.txt`.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, either adjust your local execution policy appropriately or use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the server

From the project root:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Alternatively, the file includes a `__main__` entry point, so `python main.py` starts Uvicorn on port 8000.

### 5. Open the application

- Landing page: <http://127.0.0.1:8000/>
- API documentation: <http://127.0.0.1:8000/docs>
- Data source status: <http://127.0.0.1:8000/api/data-status>
- Conjunction/objects response: <http://127.0.0.1:8000/api/conjunctions>

Keep the terminal running while using the app. The first live request may take a few seconds depending on network/provider response time.

## API reference

### `GET /api/data-status`

Checks whether the backend can retrieve NASA SSCWeb observatories and the CelesTrak active catalogue.

Typical response shape:

```json
{
  "nasa": {
    "status": "connected",
    "provider": "NASA SSCWeb",
    "available_observatories": 0
  },
  "orbital_catalogue": {
    "status": "connected",
    "provider": "CelesTrak",
    "catalogue_objects": 80
  },
  "note": "..."
}
```

The counts above are **illustrative only**, not guaranteed live values. The endpoint may return `unavailable` and an error message if an external provider or network request fails.

### `GET /api/conjunctions`

Retrieves orbital catalogue data, propagates valid records with SGP4, and returns the objects and proximity candidates for the evaluation time.

Optional query parameters:

- `solar_flux_override` — numeric F10.7-like value used for the response's solar-flux context instead of requesting NOAA data.
- `time_offset_hours` — shifts the evaluation timestamp by the requested number of hours before propagation.

Important response fields include:

- `f107_index` — solar flux value used by this request (may be the default if NOAA is unavailable).
- `solar_flare_class` — simple label derived from the override when an override is supplied; otherwise the code uses its default label.
- `drag_covariance_sigma_km` — a prototype scalar derived from F10.7, not a validated covariance matrix or certified uncertainty estimate.
- `active_satellites_count` — number of objects successfully propagated, including any successfully loaded debris objects.
- `data_source` — source/processing label.
- `calculated_at_utc` — time the response was calculated.
- `objects` — propagated positions/velocities and display metadata.
- `conjunction_pairs` — pairs whose **current propagated positions** are within 80 km.

If the live active catalogue cannot be loaded, or no objects can be propagated, the endpoint returns HTTP `503` rather than creating synthetic satellite positions.

### `POST /api/login`

Accepts a JSON body containing `email` and `password`. It checks credentials against environment variables or local demonstration defaults and returns success or HTTP `401`. This endpoint does not currently create a session, issue a token, or enforce authorization on the other endpoints. It must not be treated as production authentication.

### `POST /api/maneuver`

Accepts JSON containing `sat_name` and an optional `strategy`. It stores a demonstration position offset in process memory and returns a success response. This is a UI/prototype simulation, not a validated maneuver plan. The state is lost when the process restarts and is not persisted to a database.

## Configuration

Optional environment variables for the demonstration login endpoint:

| Variable | Purpose | Local default in code |
|---|---|---|
| `SSA_OPERATOR_EMAIL` | Operator email checked by `/api/login` | `operator@ssa.local` |
| `SSA_OPERATOR_PASSWORD` | Operator password checked by `/api/login` | `orbit2026` |

Set your own values before running the application if you use the login endpoint, and do not commit secrets to source control. These defaults are only for local demonstration and should be changed/removed before deployment. Because the endpoint does not establish an authenticated session, changing the credentials alone does not secure the rest of the API.

## Database and persistence

**No database is configured in the current project.** The application currently works by requesting source data and processing it during API calls. A few values are cached in Python process memory, and maneuver offsets are stored in a Python dictionary. The local `data/noaa_solar_flux.json` file is not a database and the current code does not use it as a persistent orbital history store.

Consequences:

- Historical satellite snapshots and conjunction events are not persistently recorded.
- In-memory caches and maneuver state disappear when the backend process restarts.
- There is no database migration or backup workflow.

A practical next step is SQLite for a single-machine prototype. Suggested tables are `satellites`, `orbital_snapshots`, `conjunction_events`, `risk_assessments`, and `data_fetch_logs`. PostgreSQL could be considered later if concurrent access and deployment needs justify it. Keep source name, fetch time, object ID, and calculation time with saved records so the provenance remains clear.

## Limitations and interpretation

1. **Not a certified collision prediction system.** The code compares object positions at one evaluation time. It does not currently propagate all pairs across a 24-hour window to find their future time of closest approach.
2. **An 80 km threshold is a screening threshold only.** A pair inside this distance is a proximity candidate, not proof that a collision is likely. A pair outside it is not guaranteed safe at other times.
3. **No validated probability of collision.** The current scalar `drag_covariance_sigma_km` is a simple heuristic based on F10.7, not a propagated covariance model or a physical probability-of-collision calculation.
4. **Visualization geometry is illustrative.** The generated `orbit_ring` points are synthetic display geometry around the current position, not an SGP4-propagated future orbit path. Do not describe every rendered ring as a precise predicted trajectory.
5. **Frame and coordinate conversion.** SGP4 output positions are in the TEME frame. The current code does not implement a full conversion to Earth-fixed coordinates for precision mapping.
6. **Object size/type are estimates.** Some size/type labels are assigned using name-based heuristics, not a verified object-properties database.
7. **Limited catalogue size.** The active catalogue is capped at 80 valid records per request, so it does not screen the entire public catalogue.
8. **Solar flux fallback.** NOAA failure can leave the default value of 150.0 in use. The response does not currently expose a robust field confirming whether the flux value was live or defaulted.
9. **No persistent database.** Historical comparisons and long-term trend reports are not available unless added separately.
10. **Authentication is incomplete.** The login endpoint checks credentials but does not protect other endpoints with a session/token system.
11. **External dependency.** Data retrieval depends on provider availability, network access, and their current response formats.

For a judge/demo presentation, describe the current system as a prototype for orbital data ingestion, propagation, visualization, and current-position proximity screening. Present future closest-approach prediction, rigorous uncertainty propagation, collision probability, persistent storage, and production authentication as future work unless they have been implemented and tested separately.

## Troubleshooting

### `uvicorn` is not recognized

Activate the virtual environment and run `python -m pip install -r requirements.txt`. You can also start with `python -m uvicorn main:app --reload --port 8000`.

### `/api/conjunctions` returns HTTP 503

- Check that the computer has internet access.
- Open `https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json` in a browser.
- Check the terminal output for the error detail.
- Retry later if the provider is unavailable or rate-limiting requests.

### NASA status is unavailable but the dashboard opens

The frontend can load locally even when NASA SSCWeb is unreachable. NASA status is separate from the CelesTrak orbital data path; check each provider status independently at `/api/data-status`.

### The UI opens but some live values look static

Check the API response directly at `/api/conjunctions` and compare `calculated_at_utc`, `data_source`, and returned object counts. A visible UI value alone does not prove it was fetched live.

### Changes to a maneuver disappear after restart

This is expected: the maneuver endpoint stores state in memory only. Add persistent storage if maneuver history needs to survive restarts.

## Security notes

- CORS is currently configured to allow all origins. Restrict allowed origins before production deployment.
- The login endpoint has demonstration defaults and no session/token authorization layer.
- Do not expose this prototype as a trusted operational control system.
- Do not store real credentials in the repository.
- Validate and rate-limit external/API inputs before exposing the service publicly.

## Possible next steps

1. Add SQLite persistence for timestamped orbital snapshots, proximity events, and data-fetch logs.
2. Record provider status, source timestamp/epoch, and whether a value came from a live request or fallback.
3. Add a true time-stepped closest-approach calculation and validate it against known reference cases.
4. Implement proper frame transformations and documented units for visualization.
5. Replace the heuristic uncertainty scalar with a scientifically justified uncertainty model before making collision-risk claims.
6. Add authenticated sessions, authorization, restricted CORS, and safer configuration for deployment.
7. Add automated tests for API responses, SGP4 propagation, provider failures, and proximity calculations.
8. Display source provenance and last successful fetch time prominently in the dashboard.

## References

- CelesTrak GP data: <https://celestrak.org/NORAD/elements/>
- CelesTrak GP API: <https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json>
- NASA SSCWeb REST services: <https://sscweb.gsfc.nasa.gov/WebServices/REST/>
- NOAA Space Weather Prediction Center: <https://www.swpc.noaa.gov/>
- NOAA F10.7 data endpoint: <https://services.swpc.noaa.gov/json/f107_cm_radio_flux.json>
- SGP4 Python package: <https://pypi.org/project/sgp4/>
- FastAPI documentation: <https://fastapi.tiangolo.com/>
- Uvicorn documentation: <https://www.uvicorn.org/>

---

**Maintainer note:** Update this README whenever endpoints, dependencies, data sources, storage behavior, or the actual risk-calculation method changes. Keep implemented functionality separate from planned functionality in project presentations and documentation.
