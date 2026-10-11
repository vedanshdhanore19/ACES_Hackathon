# Deploying to Vercel

1. Push this folder to a GitHub repository (the `.gitignore` already excludes `.env` and `__pycache__`).
2. On vercel.com choose **Add New > Project**, import the repository. Vercel detects FastAPI from `main.py` (`app = FastAPI(...)`) and `requirements.txt`; leave build and output settings empty.
3. Under **Environment Variables** add `SSA_OPERATOR_EMAIL` and `SSA_OPERATOR_PASSWORD` (see `.env.example`). The defaults in `main.py` are for local demos only.
4. Click **Deploy**, then check `/`, `/dashboard.html` and `/api/conjunctions`.

Notes
- Frontend files are in `public/` (served by Vercel's CDN). Locally, `python main.py` serves them through a StaticFiles mount at http://127.0.0.1:8000/.
- `MANEUVERED_SATELLITES` and the debris cache are in-memory, so on serverless they can reset between requests. Use a database or Redis if maneuvers must persist.
- Data fallbacks are read from `data/` using paths relative to `main.py`.
