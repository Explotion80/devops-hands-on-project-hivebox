from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
VERSION = "0.0.1"

# Lista ID senseBoxów, które Cię interesują
SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c"
]

@app.route("/version")
def get_version():
    return jsonify({"version": VERSION})

@app.route("/temperature-debug")
def temperature_debug():
    try:
        result = []
        for sensebox_id in SENSEBOX_IDS:
            url = f"https://api.opensensemap.org/boxes/{sensebox_id}"
            response = requests.get(url)
            response.raise_for_status()
            box = response.json()

            sensors_data = []
            for sensor in box.get("sensors", []):
                if sensor.get("title", "").lower() == "temperatur":
                    measurement = sensor.get("lastMeasurement")
                    sensors_data.append({
                        "title": sensor.get("title"),
                        "lastMeasurement": measurement
                    })

            result.append({
                "senseBoxId": sensebox_id,
                "sensors": sensors_data
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/temperatur")
def get_temperature():
    """
    Zwraca średnią temperaturę z ostatniej godziny z wszystkich senseBoxów.
    """
    try:
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        temperatures = []

        for sensebox_id in SENSEBOX_IDS:
            url = f"https://api.opensensemap.org/boxes/{sensebox_id}"
            response = requests.get(url)
            response.raise_for_status()
            box = response.json()

            for sensor in box.get("sensors", []):
                if sensor.get("title", "").lower() == "temperatur":
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
            return jsonify({"message": "No recent temperature data found."})

        avg_temp = sum(temperatures) / len(temperatures)
        return jsonify({"average_temperature": round(avg_temp, 2)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)