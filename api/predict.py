
import json
import os
import joblib
import pandas as pd

from http.server import BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "risk_model.pkl")

model = joblib.load(MODEL_PATH)


class handler(BaseHTTPRequestHandler):

    def respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.respond(200, {"message": "Cold Chain API is running"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))

            if length <= 0 or length > 10000:
                return self.respond(400, {"error": "Invalid request size"})

            data = json.loads(self.rfile.read(length))

            fruit = str(data.get("Fruit", "")).strip()
            if not fruit or len(fruit) > 50:
                return self.respond(400, {"error": "Invalid fruit"})

            row = {
                "Fruit": fruit,
                "Temp": float(data["Temp"]),
                "Humid": float(data["Humid"]),
                "Light": float(data["Light"]),
                "CO2": float(data["CO2"])
            }

            for name in ["Temp", "Humid", "Light", "CO2"]:
                if not pd.notna(row[name]):
                    return self.respond(400, {"error": f"Invalid {name}"})

            if not 0 <= row["Humid"] <= 100:
                return self.respond(400, {"error": "Humidity must be 0-100"})

            if row["Light"] < 0 or row["CO2"] < 0:
                return self.respond(400, {"error": "Values cannot be negative"})

            result = model.predict(pd.DataFrame([row]))[0]
            probabilities = model.predict_proba(pd.DataFrame([row]))[0]

            self.respond(200, {
                "prediction": str(result),
                "probabilities": {
                    str(label): round(float(prob) * 100, 2)
                    for label, prob in zip(model.classes_, probabilities)
                }
            })

        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.respond(400, {"error": "Please enter valid values"})
        except Exception:
            self.respond(500, {"error": "Prediction failed"})
