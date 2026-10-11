# Space Traffic Risk Engine — landing page integration

## What changed
- `static/index.html` is now the landing page.
- `static/dashboard.html` contains the previous dashboard UI unchanged.
- `static/threeui/src/shaders/neuform-isolated/sources/nexus-topology.html` contains the canonical Topology Field HTML source supplied in the ThreeUI bundle.
- The supplied `NeuformIsolatedEffects.tsx` and `threeui.css` source files are retained under `static/threeui/src/shaders/` for reference and future React/Vite integration.

## Run
From the project root, activate your virtual environment and run:

```bash
uvicorn main:app --reload --port 8000
```

Then open `http://127.0.0.1:8000/`. Use **Launch mission console** or the left-side **Sign in** tab to reach the dashboard.

## Important authentication note
The login drawer is a visual prototype. The existing FastAPI backend has no authentication endpoint, so submitting the form opens the dashboard and does not validate the entered credentials. Add server-side authentication before using this for restricted or production access.

## Source note
The landing page loads the canonical `nexus-topology.html` directly in a background iframe so its authored canvas/shader animation is used rather than approximated. The React component source is preserved but is not compiled by the current static HTML/FastAPI application because this repository does not currently include a React/Vite build setup or all of that component's imported HTML source modules.
