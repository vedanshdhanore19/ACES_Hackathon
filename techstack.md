# Comprehensive Technology Stack & Tooling Specification

## 1. Programming Languages & Runtimes
- **Python 3.11+**: Primary language for server-side processing, mathematical transformations, data pipelines, and API handling. Chosen for native C-extensions support (`numpy`, `scipy`) required in high-throughput astrodynamics calculations.
- **Modern JavaScript (ES6+)**: Browser-side execution engine for rendering 3D graphics, handling asynchronous UI events, and driving real-time WebSockets/REST updates without heavy frontend frameworks.
- **HTML5 & CSS3**: Native markup and styling for a lightweight, single-page tactical operations dashboard.

---

## 2. Backend & API Framework
- **FastAPI**: Asynchronous Python web framework used to expose high-performance endpoints (`/api/conjunctions`). Native support for Pydantic schema validation and low latency overhead.
- **Uvicorn**: High-performance ASGI web server engine driving the FastAPI application.

---

## 3. Astrodynamics, Math & Data Physics Libraries
- **`sgp4` (Python Package)**: Standard implementation of Simplified General Perturbations Satellite Orbit Model #4 (SGP4/SDP4). Converts raw Two-Line Element (TLE) orbital sets into accurate 3D Earth-Centered Inertial (ECI) coordinate vectors ($X, Y, Z$) and velocity state vectors ($V_x, V_y, V_z$).
- **`NumPy`**: Fast vectorized matrix operations for 3D Euclidean pairwise distance calculations across large satellite arrays.
- **`SciPy`**: Statistical algorithms and covariance matrix math used to derive multi-variable probability of collision ($P_c$) Gaussian overlap integrals.
- **`Requests` / `httpx`**: Asynchronous HTTP client library to pull live data streams from external space situational awareness APIs.

---

## 4. Frontend & 3D Visualization Engine
- **CesiumJS (v1.104+ via CDN)**: WebGL-powered 3D Earth globe visualization library. Renders satellites in high-precision Earth-Centered Fixed (ECEF) space, draws animated orbit trajectories, and displays high-risk collision vectors in real time.
- **Vanilla CSS3 Flexbox/Grid**: Custom dark-mode tactical HUD overlay with responsive sliders for live solar flare parameter adjustments.

---

## 5. Live Production External Data Feeds (APIs)
- **CelesTrak General Perturbations (GP) API**
  - **Endpoint:** `https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json`
  - **Role:** Fetches live orbital catalog data (NORAD IDs, TLE Line 1 & Line 2, object classifications, epoch timestamps) in structured JSON.
- **NOAA Space Weather Prediction Center (SWPC) API**
  - **Endpoint:** `https://services.swpc.noaa.gov/json/f107_cm_radio_flux.json`
  - **Role:** Provides real-time solar flare radio flux data ($F10.7$ index) used as a dynamic scalar to calculate atmospheric heating and upper-atmosphere drag decay uncertainties.

---

## 6. AI Agent Engineering Tools & Workflow Setup
- **Coding Assistant Engines**: Claude 3.5 Sonnet / Cursor AI / GitHub Copilot
- **Agent Instruction System**: Contextual file-based guidance system using 5 core workspace Markdown files:
  1. `prd.md`: Product vision and feature boundaries.
  2. `architecture.md`: System topology, endpoints, and file structures.
  3. `rules.md`: Technical constraints and non-negotiables.
  4. `memory.md`: State management and task tracking across agent prompts.
  5. `techstack.md`: Explicit tool choices, versioning, and API specifications.

---

## 7. Developer Tooling & Environment
- **Environment Management**: Python Virtual Environment (`venv` / `conda`)
- **Version Control**: Git & GitHub for rapid deployment
- **HTTP/API Testing**: FastAPI Swagger UI (`/docs`) and cURL