import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('heartdb.sqlite')  
    conn.row_factory = sqlite3.Row
    return conn

model = joblib.load("models/heart_model.pkl")
scaler = joblib.load("models/scaler.pkl")

FEATURE_ORDER = [
    "age", "gender", "height", "weight",
    "ap_hi", "ap_lo", "cholesterol", "gluc",
    "smoke", "alco", "active"
]

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER,
    gender INTEGER,
    height REAL,
    weight REAL,
    ap_hi INTEGER,
    ap_lo INTEGER,
    cholesterol INTEGER,
    gluc INTEGER,
    smoke INTEGER,
    alco INTEGER,
    active INTEGER,
    prediction TEXT,
    created_at TEXT
)
""")
conn.commit()
cursor.close()
conn.close()

@app.route("/")
def index():
    return "Flask API is running. Try /ping, /predict, or /history"

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "features": FEATURE_ORDER})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        
        for f in FEATURE_ORDER:
            if f not in data:
                return jsonify({"error": f"Missing field: {f}"}), 400
        
        patient = pd.DataFrame([[data[f] for f in FEATURE_ORDER]], columns=FEATURE_ORDER)
       
        patient_scaled = scaler.transform(patient)
        pred = model.predict(patient_scaled)[0]
        result = "Disease Risk" if pred == 1 else "No Disease Risk"
        
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO predictions
        (age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active,
        prediction, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
    data["age"], data["gender"], data["height"], data["weight"],
    data["ap_hi"], data["ap_lo"], data["cholesterol"], data["gluc"],
    data["smoke"], data["alco"], data["active"],
    result, datetime.datetime.utcnow().isoformat()
))
conn.commit()
cursor.close()
conn.close()

        return jsonify({"prediction": int(pred), "message": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        records = [dict(row) for row in rows]  


        return jsonify(records)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)