from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DB_NAME = "database.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            room TEXT NOT NULL,
            slot TEXT NOT NULL,
            date TEXT NOT NULL,
            weight INTEGER NOT NULL,
            payment TEXT NOT NULL,
            total INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/book", methods=["POST"])
def book():
    data = request.get_json(force=True)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings (name, room, slot, date, weight, payment, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["room"],
        data["slot"],
        data["date"],
        int(data["weight"]),
        data["payment"],
        int(data["total"]),
        "pending"
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Booking saved"})


@app.route("/bookings", methods=["GET"])
def get_bookings():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM bookings ORDER BY id DESC").fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/update-status/<int:booking_id>", methods=["POST"])
def update_status(booking_id):
    data = request.get_json(force=True)
    new_status = data.get("status", "pending")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "UPDATE bookings SET status=? WHERE id=?",
        (new_status, booking_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Status updated"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)