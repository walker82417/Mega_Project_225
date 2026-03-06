from __future__ import annotations

from datetime import datetime, timedelta, timezone
import asyncio
import random
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Industrial Monitoring API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class AuthRequest(BaseModel):
    name: str | None = None
    email: str
    password: str


def _seed_machines() -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "name": "Induction Motor",
            "status": "warning",
            "location": "Factory Floor 1",
            "lastMaintenance": "2025-03-20",
            "type": "motor",
            "temperature": 72.3,
            "vibration": 5.4,
            "current": 13.8,
            "healthScore": 68,
        },
        {
            "id": 2,
            "name": "Gear Hobbing Machine",
            "status": "normal",
            "location": "Factory Floor 1",
            "lastMaintenance": "2025-04-02",
            "type": "gear",
            "temperature": 58.9,
            "vibration": 3.0,
            "current": 10.1,
            "healthScore": 87,
        },
    ]


MACHINES: list[dict[str, Any]] = _seed_machines()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/machines")
def list_machines() -> list[dict[str, Any]]:
    return MACHINES


@app.get("/api/alerts")
def list_alerts() -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    alerts = []
    for m in MACHINES:
        if m["status"] == "normal":
            continue
        alerts.append(
            {
                "id": m["id"] * 100,
                "machine": m["name"],
                "severity": "warning" if m["healthScore"] > 50 else "critical",
                "message": f"{m['name']} needs inspection. Health score is {m['healthScore']}.",
                "timestamp": (now - timedelta(minutes=m["id"] * 4)).isoformat(),
            }
        )
    return alerts


@app.get("/api/analytics/summary")
def analytics_summary() -> dict[str, Any]:
    avg_health = round(sum(m["healthScore"] for m in MACHINES) / len(MACHINES), 1)
    warning_count = len([m for m in MACHINES if m["status"] != "normal"])
    return {
        "avgHealth": avg_health,
        "activeAlerts": warning_count,
        "predictionWindowDays": 7,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/auth/signup")
def signup(payload: AuthRequest) -> dict[str, str]:
    return {"message": f"User {payload.email} registered successfully", "token": "demo-token"}


@app.post("/api/auth/login")
def login(payload: AuthRequest) -> dict[str, str]:
    return {"message": f"Welcome {payload.email}", "token": "demo-token"}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    text = payload.message.lower()
    if "alert" in text:
        warning = [m for m in MACHINES if m["status"] != "normal"]
        return {"reply": f"There are currently {len(warning)} active machine alerts."}
    if "gear" in text or "machine 2" in text:
        m = next(x for x in MACHINES if x["id"] == 2)
        return {"reply": f"{m['name']} is {m['status']}. Temp {m['temperature']}°C, vibration {m['vibration']} mm/s."}
    if "electrical" in text or "troubleshoot" in text:
        return {
            "reply": "Start with supply voltage, contactor health, thermal relay, and bearing noise. If current rises with heat, schedule maintenance this week.",
        }
    return {
        "reply": "I can help with live status, alerts, and basic troubleshooting. Ask: 'active alerts' or 'status of gear hobbing machine'."
    }


@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            for m in MACHINES:
                m["temperature"] = round(m["temperature"] + random.uniform(-0.5, 0.8), 2)
                m["vibration"] = round(max(0.5, m["vibration"] + random.uniform(-0.2, 0.2)), 2)
                m["current"] = round(max(1.0, m["current"] + random.uniform(-0.2, 0.25)), 2)
                if m["temperature"] > 75 or m["vibration"] > 5.5:
                    m["status"] = "warning"
                    m["healthScore"] = max(45, m["healthScore"] - 1)
                else:
                    m["status"] = "normal"
                    m["healthScore"] = min(95, m["healthScore"] + 1)
            await websocket.send_json({"machines": MACHINES, "timestamp": datetime.now(timezone.utc).isoformat()})
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
