import sqlite3

conn = sqlite3.connect("heart.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER,
    gender INTEGER,
    height REAL,
    weight REAL,
    ap_hi REAL,
    ap_lo REAL,
    cholesterol INTEGER,
    gluc INTEGER,
    smoke INTEGER,
    alco INTEGER,
    active INTEGER,
    prediction TEXT,
    created_at TEXT,
    user_id INTEGER
)
""")

conn.commit()
conn.close()

print("SQLite database initialized")
