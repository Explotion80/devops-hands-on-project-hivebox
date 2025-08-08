import os
from flask import Flask, jsonify, Response
import httpx
from datetime import datetime, timezone, timedelta
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

app = Flask(__name__)
VERSION = "0.0.3"

# Lista ID senseBoxów, które Cię interesują
SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c"
]

@app.route("/version")
def get_version():
    return jsonify({"version": VERSION})

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/temperatur")
def get_temperatur():
    print("Starting /temperatur endpoint")
    temperatures = []
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    max_retries = 3

    for sensebox_id in SENSEBOX_IDS:
        print(f"Processing senseBox ID: {sensebox_id}")
        url = f"https://api.opensensemap.org/boxes/{sensebox_id.strip()}"
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1} for {sensebox_id}")
            try:
                resp = httpx.get(url, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                print(f"Received data for {sensebox_id}: {data}")

                sensors = data.get("sensors", [])
                for sensor in sensors:
                    title = sensor.get("title", "").lower()
                    print(f"Sensor title: {title}")
                    if title == "temperatur":
                        measurement = sensor.get("lastMeasurement")
                        print(f"Last measurement: {measurement}")
                        if not measurement:
                            continue

                        value = measurement.get("value")
                        created_at = measurement.get("createdAt")
                        if not value or not created_at:
                            continue

                        created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if created_time > one_hour_ago:
                            try:
                                val = float(value)
                                temperatures.append(val)
                                print(f"Added temperature: {val}")
                            except ValueError:
                                print(f"ValueError for value: {value}")
                                continue
                break
            except httpx.ReadTimeout:
                print(f"Timeout on {sensebox_id}, attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return jsonify({"error": f"Timeout contacting {sensebox_id}"}), 504
            except Exception as e:
                print(f"Exception on {sensebox_id}: {e}")
                return jsonify({"error": str(e)}), 500

    print(f"Collected temperatures: {temperatures}")
    if not temperatures:
        return jsonify({"message": "No recent temperature data found."}), 404

    avg_temp = sum(temperatures) / len(temperatures)
    print(f"Average temperature: {avg_temp}")

    if avg_temp < 10:
        status = "Too Cold"
    elif 10 <= avg_temp <= 36:
        status = "Good"
    else:
        status = "Too Hot"

    result = {
        "average_temperatur": round(avg_temp, 2),
        "status": status
    }
    print(f"Response: {result}")
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
