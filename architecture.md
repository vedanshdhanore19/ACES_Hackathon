# System Architecture & Tech Stack Specification

## Operational Strategy
- **API-First Contract:** The backend exposes a strictly defined REST API schema with CORS enabled (`allow_origins=["*"]`).
- **Decoupled Frontend:** The UI is assembled using pre-built 3D WebGL components from ThreeUI (`threeui.com/browse`), wired to the FastAPI endpoint using AI prompts (Claude / Gemini / ChatGPT).

## System Data Flow
[ CelesTrak API ] ──> [ FastAPI Backend ] <── [ NOAA Space Weather API ]
                             │
          ┌──────────────────┴──────────────────┐
          │ 1. Ingest TLEs / OMMs               │
          │ 2. Propagate Orbit via SGP4         │
          │ 3. Euclidean Pairwise Distance      │
          │ 4. Compute Drag Uncertainty (F10.7) │
          │ 5. Calculate Collision Risk Score   │
          └──────────────────┬──────────────────┘
                             │
                 Strict JSON Payload (CORS Enabled)
                             │
                             ▼
             [ ThreeUI WebGL Frontend / Index.html ]
             • 3D Earth / Particle Mesh Canvas
             • Green points: Normal Satellites
             • Red Pulsing Lines: Conjunction Alerts
             • Slider: Interactive Solar Flux Multiplier

## Directory Structure
space-traffic-engine/
├── prd.md
├── architecture.md
├── rules.md
├── memory.md
├── techstack.md
├── main.py              # FastAPI Server, Data Fetching & SGP4 Calculations
└── static/
    └── index.html       # ThreeUI + Vanilla JS Dashboard# System Architecture & Tech Stack Specification

## Operational Strategy
- **API-First Contract:** The backend exposes a strictly defined REST API schema with CORS enabled (`allow_origins=["*"]`).
- **Decoupled Frontend:** The UI is assembled using pre-built 3D WebGL components from ThreeUI (`threeui.com/browse`), wired to the FastAPI endpoint using AI prompts (Claude / Gemini / ChatGPT).

## System Data Flow
[ CelesTrak API ] ──> [ FastAPI Backend ] <── [ NOAA Space Weather API ]
                             │
          ┌──────────────────┴──────────────────┐
          │ 1. Ingest TLEs / OMMs               │
          │ 2. Propagate Orbit via SGP4         │
          │ 3. Euclidean Pairwise Distance      │
          │ 4. Compute Drag Uncertainty (F10.7) │
          │ 5. Calculate Collision Risk Score   │
          └──────────────────┬──────────────────┘
                             │
                 Strict JSON Payload (CORS Enabled)
                             │
                             ▼
             [ ThreeUI WebGL Frontend / Index.html ]
             • 3D Earth / Particle Mesh Canvas
             • Green points: Normal Satellites
             • Red Pulsing Lines: Conjunction Alerts
             • Slider: Interactive Solar Flux Multiplier

## Directory Structure
space-traffic-engine/
├── prd.md
├── architecture.md
├── rules.md
├── memory.md
├── techstack.md
├── main.py              # FastAPI Server, Data Fetching & SGP4 Calculations
└── static/
    └── index.html       # ThreeUI + Vanilla JS Dashboard