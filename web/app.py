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
        "SELECT namn, username, klass, preferenser FROM anmalan ORDER BY namn COLLATE NOCASE"
    ).fetchall()
    conn.close()
    return render_template("index.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)