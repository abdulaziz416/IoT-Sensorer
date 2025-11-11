from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional


class MongoDBManager:
    def __init__(self):
        # Använd MongoDB Atlas eller lokal MongoDB
        self.connection_string = os.getenv(
            "MONGODB_URI", "mongodb://localhost:27017/weatherstation"
        )
        self.client = MongoClient(self.connection_string)
        self.db = self.client.weatherstation
        self.collection = self.db.sensor_data

        # Skapa index för timestamp
        self.collection.create_index("timestamp")

    def insert_data(self, data: Dict) -> str:
        """Infoga sensordata i databasen"""
        result = self.collection.insert_one(data)
        return result.inserted_id

    def get_latest_data(self) -> Optional[Dict]:
        """Hämta senaste datapunkt"""
        return self.collection.find_one(sort=[("timestamp", -1)])

    def get_recent_data(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Hämta data från senaste timmarna"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_timestamp = cutoff_time.timestamp()

        cursor = self.collection.find(
            {"timestamp": {"$gte": cutoff_timestamp}}, sort=[("timestamp", 1)]
        ).limit(limit)

        return list(cursor)

    def get_daily_stats(self) -> Dict:
        """Beräkna statistik för senaste dygnet"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        cutoff_timestamp = cutoff_time.timestamp()

        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_timestamp}}},
            {
                "$group": {
                    "_id": None,
                    "avg_temperature": {"$avg": "$temperature"},
                    "max_temperature": {"$max": "$temperature"},
                    "min_temperature": {"$min": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "avg_light": {"$avg": "$light_level"},
                    "data_points": {"$sum": 1},
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))
        if result:
            return result[0]
        return {}
