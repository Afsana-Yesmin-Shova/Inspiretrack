from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import psycopg2
import requests
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            latitude TEXT,
            longitude TEXT,
            address TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# Initialize DB immediately but safely
try:
    if DATABASE_URL:
        init_db()
except Exception as e:
    print("Database init error:", e)


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_location", methods=["POST"])
def get_location():
    data = request.get_json()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    address = "Unknown"

    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}",
            headers={"User-Agent": "InspireTrackApp"}
        )
        address = response.json().get("display_name", "Unknown")
    except Exception as e:
        print("Geocode error:", e)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO locations (latitude, longitude, address, timestamp) VALUES (%s, %s, %s, %s)",
        (latitude, longitude, address, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"quote": random.choice(quotes)})


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM locations ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("dashboard.html", data=data)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
