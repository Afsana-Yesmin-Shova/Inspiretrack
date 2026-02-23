from flask import Flask, render_template, request, jsonify, redirect, session
import requests
import sqlite3
import secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # change this in production

# -------------------------
# Quotes List (Dynamic)
# -------------------------
quotes = [
    "Success is built wherever you stand.",
    "Greatness begins from where you are.",
    "You are exactly where you need to be.",
    "Dream big, no matter your location.",
    "Your journey starts at this very place.",
    "Push yourself, because no one else will.",
    "Small steps today create big results tomorrow.",
    "Stay focused. Stay unstoppable.",
    "Your destiny is bigger than your doubts.",
    "Make today powerful.",
    "Turn your pain into power.",
    "You are stronger than you think.",
    "Rise above limitations.",
    "Work in silence, let success speak.",
    "Every click is a new beginning."
]

# -------------------------
# Database Initialization
# -------------------------
def init_db():
    conn = sqlite3.connect("database.db")
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

# -------------------------
# User Homepage
# -------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------
# Get Location Route
# -------------------------
@app.route('/get_location', methods=['POST'])
def get_location():
    data = request.json
    lat = data['latitude']
    lon = data['longitude']

    # Reverse Geocoding using OpenStreetMap
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    headers = {"User-Agent": "InspireTrackApp"}

    response = requests.get(url, headers=headers)
    location_data = response.json()

    address = location_data.get("display_name", "Address not found")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to Database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO locations (latitude, longitude, address, timestamp)
        VALUES (?, ?, ?, ?)
    """, (lat, lon, address, timestamp))
    conn.commit()
    conn.close()

    # Generate random quote
    quote = secrets.choice(quotes)

    return jsonify({"quote": quote})

# -------------------------
# Admin Login
# -------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/dashboard')

    return render_template("admin_login.html")

# -------------------------
# Dashboard (Protected)
# -------------------------
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM locations ORDER BY id DESC")
    locations = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM locations")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        locations=locations,
        total=total
    )

# -------------------------
# Logout
# -------------------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/admin')

# -------------------------
# Run App
# -------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
