import datetime
from fastapi import FastAPI
import httpx

from datetime import datetime, timedelta

app = FastAPI()
VERSION = "0.0.2"
SENSEBOX_IDS = [
    "5e86143a6feb97001c1c9b8b",
    "62041d12bbfa4b001dff1214",
    "5e861b696feb97001c1f2fff"
]

@app.get("/")
def root():
    return {
        "message": "HiveBox API – dostępne endpointy: /version, /temperature"
    }

@app.get("/version")
def get_version():
    return {"version": VERSION}

@app.get("/temperature")
def get_temperature():
    try:
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        temperatures = []

        for box_id in SENSEBOX_IDS:
            url = f"https://api.opensensemap.org/boxes/{box_id}"
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()

            for sensor in data.get("sensors", []):
                if sensor.get("title", "").lower() == "temperature":
                    measurement = sensor.get("lastMeasurement")
                    if not measurement:
                        continue

                    value = measurement.get("value")
                    created_at = measurement.get("createdAt")

                    if not value or not created_at:
                        continue

                    created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if created_time > one_hour_ago:
                        try:
                            temperatures.append(float(value))
                        except ValueError:
                            continue

        if not temperatures:
            return {"message": "No recent temperature data found."}

        avg_temp = sum(temperatures) / len(temperatures)
        return {"average_temperature": round(avg_temp, 2)}

    except Exception as e:
        return {"error": str(e)}
