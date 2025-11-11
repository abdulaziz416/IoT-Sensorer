from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from typing import List
import os
import time

from models import SensorData, SensorDataIn
from database import MongoDBManager

app = FastAPI(title="Smart Väderstation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initiera databasanslutning
db = MongoDBManager()


@app.post("/data", response_model=SensorData)
async def receive_sensor_data(data: SensorDataIn):
    """Ta emot sensordata från microcontroller"""
    try:
        data_dict = data.dict()
        if not data_dict.get("timestamp"):
            data_dict["timestamp"] = time.time()
        inserted_id = db.insert_data(data_dict)  # din databas-funktion
        if not inserted_id:
            raise HTTPException(status_code=500, detail="Kunde inte spara data")
        return {**data_dict, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fel vid datalagring: {str(e)}")


@app.get("/data/latest", response_model=SensorData)
async def get_latest_data():
    """Hämta senaste datapunkt"""
    data = db.get_latest_data()
    if not data:
        raise HTTPException(status_code=404, detail="Ingen data tillgänglig")
    return data


@app.get("/data/history", response_model=List[SensorData])
async def get_history(hours: int = 24, limit: int = 100):
    """Hämta historisk data"""
    data = db.get_recent_data(hours=hours, limit=limit)
    return data


@app.get("/data/stats")
async def get_statistics():
    """Hämta statistik för senaste dygnet"""
    stats = db.get_daily_stats()
    return stats


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
