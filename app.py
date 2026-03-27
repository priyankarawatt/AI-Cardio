import joblib
import sqlite3
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # Set True in production (HTTPS)
    SESSION_COOKIE_SAMESITE="Lax"
)

def get_db():
    conn = sqlite3.connect("heart.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# LOAD MODELS (Connecting the brains)
# ==========================================
model = joblib.load("models/heart_model.pkl")
scaler = joblib.load("models/scaler.pkl")
# Loading the chatbot brain you just trained in Jupyter!
chat_model = joblib.load("models/chat_model.pkl") 

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("register.html", error="All fields are required")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone():
            conn.close()
            return render_template("register.html", error="Username already exists")
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template("login.html", error="All fields are required.")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid credentials")

        session.clear()  # Prevent session fixation
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect(url_for("welcome"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("welcome"))
    return redirect(url_for("login"))

@app.route("/analysis")
@login_required
def index():
    return render_template("index.html", username=session["username"])

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    # Fetching the full latest record so the dashboard UI stays updated
    cur.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY id DESC LIMIT 1", (session["user_id"],))
    last_record = cur.fetchone()
    conn.close()
    return render_template("dashboard.html", username=session["username"], last_record=last_record)

# ==========================================
# THE CHATBOT FIX: Smart Intent Logic
# ==========================================
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").lower()
    
    # 1. AI Predicts what the user is asking about
    intent = chat_model.predict([user_msg])[0] 
    
    # 2. Fetch real data for this specific user to give smart answers
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT prediction, created_at, ap_hi, ap_lo FROM predictions WHERE user_id=? ORDER BY id DESC LIMIT 1", (session["user_id"],))
    last = cur.fetchone()
    conn.close()
    
    reply = ""
    
    # 3. Dynamic logic to build the "so and soo" response
    if intent == "ask_score":
        if last:
            reply = f"Based on your latest assessment from **{last['created_at']}**, your result was: **{last['prediction']}**. Keep monitoring your vitals!"
        else:
            reply = "I don't see any previous assessments for you. Let's head to the 'Risk Analysis' page to find out your score!"
            
    elif intent == "ask_bp":
        if last:
            reply = f"Your last recorded blood pressure was **{last['ap_hi']}/{last['ap_lo']} mmHg**. This was captured during your session on {last['created_at']}."
        else:
            reply = "I don't have your blood pressure data yet. Try running an analysis!"

    elif intent == "emergency":
        reply = "🚨 **EMERGENCY WARNING:** If you are feeling chest pain, shortness of breath, or dizziness, please call emergency services immediately. Don't wait!"

    elif intent == "greeting":
        reply = f"Hello {session['username']}! I'm your AI Heart Assistant. How can I help you with your data today?"

    elif intent == "ask_advice" or intent == "diet_exercise":
        reply = "For a healthy heart, I recommend 30 minutes of walking daily and a diet low in salts and fats. Would you like more tips?"

    else:
        reply = "I'm not quite sure I understand. Are you asking about your test score or looking for advice?"

    return jsonify({"reply": reply})

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    data = request.get_json()
    try:
        errors = []

        age = int(data["age"])
        height = float(data["height"])
        weight = float(data["weight"])
        systolic_bp = float(data["systolic_bp"])
        diastolic_bp = float(data["diastolic_bp"])


        if age <= 0 or age > 120:
            errors.append("Age must be between 1 and 120.")

        if height <= 50 or height > 300:
            errors.append("Height appears unrealistic.")

        if weight <= 10 or weight > 500:
            errors.append("Weight appears unrealistic.")

        if systolic_bp <= 0:
            errors.append("Systolic BP must be positive.")

        if systolic_bp < 50 or systolic_bp > 300:
            errors.append("Systolic BP value appears biologically unrealistic.")

        if diastolic_bp <= 0:
            errors.append("Diastolic BP must be positive.")

        if diastolic_bp < 30 or diastolic_bp > 200:
            errors.append("Diastolic BP value appears biologically unrealistic.")

        if systolic_bp <= diastolic_bp:
            errors.append("Systolic BP must be greater than Diastolic BP.")

        if errors:
            return jsonify({"error": errors})


        values = [
            age,
            1 if data["gender"].lower() == "male" else 0,
            height,
            weight,
            systolic_bp,
            diastolic_bp,
            ["Normal", "Above Normal", "Well Above Normal"].index(data["cholesterol"]) + 1,
            ["Normal", "Above Normal", "Well Above Normal"].index(data["gluc"]) + 1,
            1 if data["smoke"].lower() == "yes" else 0,
            1 if data["alco"].lower() == "yes" else 0,
            1 if data["active"].lower() == "yes" else 0
        ]

        scaled_data = scaler.transform([values])
        prediction = model.predict(scaled_data)[0]
        result = "Risk of Heart Disease" if prediction == 1 else "No Risk Detected"


        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO predictions 
            (age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, prediction, created_at, user_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (*values, result, datetime.datetime.now().strftime("%d %b"), session["user_id"]))

        conn.commit()
        conn.close()

        return jsonify({
            "prediction": result
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": "An unexpected error occurred."})

@app.route("/history")
@login_required
def history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY id DESC", (session["user_id"],))
    records = [dict(row) for row in cur.fetchall()]
    conn.close()
    return render_template("history.html", records=records, username=session["username"])
@app.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html", username=session["username"])

@app.route("/graph")
@login_required
def graph():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT created_at, prediction
        FROM predictions
        WHERE user_id=?
        ORDER BY id ASC
    """, (session["user_id"],))

    records = cur.fetchall()
    conn.close()

    dates = [row["created_at"] for row in records]
    results = [1 if row["prediction"] == "Risk of Heart Disease" else 0 for row in records]

    if not dates:
        dates = ["No Data"]

    if not results:
        results = [0]

    return render_template("graph.html", dates=dates, results=results)


if __name__ == "__main__":
    app.run(debug=True)