# AI Agent Operating Rules & Constraints

## Strict Guidelines
1. NO Machine Learning Models: Do NOT attempt to build neural networks or heavy ML pipelines from scratch. Stick to analytical SGP4 physics and 3D Euclidean geometry.
2. Single-File Frontend: Keep all visual UI elements inside `static/index.html` using CDN links for Three.js. Do NOT introduce Node.js, Webpack, or complex React build setups.
3. Fast Execution Limits: Limit pairwise initial filtering to 50–100 satellites during testing to ensure sub-second API execution.
4. Resilient Fallbacks: Always wrap external API calls in try-except blocks with hardcoded fallbacks (e.g., default `F10.7 = 150.0`) in case CelesTrak or NOAA times out.
5. Strict CORS Policy: Ensure FastAPI includes `CORSMiddleware` with `allow_origins=["*"]` so external or AI-generated frontends never encounter cross-origin errors.

## Code Style
- Write clean, modular Python functions with explicit type hints (`float`, `dict`, `list`).
- Do NOT rewrite or delete working code unless explicitly instructed in `memory.md`.