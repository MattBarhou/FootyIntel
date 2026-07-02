# FootyIntel

Monorepo for the FootyIntel application — a Premier League match prediction and team comparison platform.

## Structure

- `frontend/` — Next.js web app (DaisyUI + Tailwind CSS)
- `backend/` — FastAPI API server with ML prediction

## Getting started

### Backend

From the `backend` directory, install dependencies and start the API:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API must have match data in `backend/data/raw/` and a trained model in `backend/data/models/` for predictions to work. See `backend/scripts/train_model.py` to train the model.

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Set `API_URL` in `.env.local` to your backend URL (default: `http://127.0.0.1:8000`).

### Features

- **Teams sidebar** — Browse all teams with cached list; select a team to view last-5 form
- **Predict** (`/predict`) — ML match outcome probabilities
- **Compare** (`/compare`) — Side-by-side season stat comparison

## Development

Run both servers concurrently:

1. Backend on port `8000`
2. Frontend on port `3000`

The frontend uses Server Actions and server-side fetching — no CORS configuration is required for the default setup.
