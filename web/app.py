import sqlite3
import os
from flask import Flask, render_template

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "anmalan.db")


@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT namn, username, klass, preferenser FROM anmalan ORDER BY namn COLLATE NOCASE"
    ).fetchall()
    conn.close()
    return render_template("index.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
