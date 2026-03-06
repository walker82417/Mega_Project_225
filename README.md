# Mega Project 2025-26

This repository now contains:
- Existing frontend HTML pages (style unchanged)
- A new FastAPI backend for live/mock machine data, alerts, auth, and chatbot
- A baseline AI training script for predictive maintenance anomaly detection

## Quick Start

### 1) Run backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Run frontend
Serve this folder with any static file server:
```bash
python -m http.server 5500
```
Then open `http://127.0.0.1:5500/dashboard.html`.

> `api-config.js` points frontend to `http://127.0.0.1:8000` by default.

## Functional Endpoints
- `GET /api/health`
- `GET /api/machines`
- `GET /api/alerts`
- `GET /api/analytics/summary`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/chat`
- `WS /ws/live` (live stream every 2 seconds)

## AI Model Training (baseline)
Train anomaly model from CSV:
```bash
python backend/ai/train_predictive_model.py --data data/machine_data.csv
```

The script auto-picks available features from:
`temperature, vibration, current, pressure, humidity, rpm`.

## Notes
- Frontend visual style was not changed.
- Current data is simulated for now (until hardware + MQTT arrives).
- You can replace mock update logic with MQTT ingestion later without changing frontend structure.
