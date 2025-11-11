from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorDataIn(BaseModel):
    temperature: float = Field(..., description="Temperatur i Celsius")
    humidity: float = Field(..., description="Relativ fuktighet i %")
    light_level: float = Field(..., description="Ljusnivå i %")
    timestamp: Optional[float] = Field(None, description="Unix timestamp")


class SensorData(SensorDataIn):
    id: str = Field(..., description="Unikt ID för datapunkt")

    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "temperature": 23.5,
                "humidity": 45.2,
                "light_level": 75.8,
                "timestamp": 1635789200.0,
            }
        }
