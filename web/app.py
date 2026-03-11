import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "anmalan.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS anmalan (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT NOT NULL,
                namn       TEXT NOT NULL,
                klass      TEXT NOT NULL,
                preferenser TEXT
            )
        """)
        try:
            conn.execute("ALTER TABLE anmalan ADD COLUMN placed BOOLEAN DEFAULT FALSE")
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
        conn.close()

init_db()

# Admin credentials from environment variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH', generate_password_hash('admin'))


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Admin login page"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error = "Invalid username or password"
    
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route("/")
@login_required
def index():
    """Main page - registration list"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT user_id, namn, username, klass, preferenser, placed FROM anmalan ORDER BY namn COLLATE NOCASE"
    ).fetchall()
    conn.close()
    return render_template("index.html", rows=rows)


@app.route("/toggle_placed/<int:user_id>", methods=["POST"])
@login_required
def toggle_placed(user_id):
    placed = request.form.get('placed') == 'true'
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE anmalan SET placed = ? WHERE user_id = ?", (placed, user_id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('index'))


@app.route("/remove/<int:user_id>", methods=["POST"])
@login_required
def remove_entry(user_id):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM anmalan WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('index'))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_entry():
    """Admin: add a registration entry manually"""
    error = None
    if request.method == 'POST':
        namn = request.form.get('namn')
        username = request.form.get('username')
        klass = request.form.get('klass')
        preferenser = request.form.get('preferenser')

        if not namn or not username:
            error = "Namn och Discord-användarnamn krävs."
        else:
            conn = sqlite3.connect(DB_PATH)
            try:
                conn.execute(
                    "INSERT INTO anmalan (namn, username, klass, preferenser) VALUES (?, ?, ?, ?)",
                    (namn, username, klass, preferenser),
                )
                conn.commit()
            finally:
                conn.close()
            return redirect(url_for('index'))

    return render_template('add_entry.html', error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5000)