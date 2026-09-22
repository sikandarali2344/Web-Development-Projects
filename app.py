import sqlite3
import os
import json
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, g, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "store.db")

app = Flask(__name__)
app.secret_key = "sikandar-furniture-dev-secret-change-me"  # change this before real deployment

# ---------------------------------------------------------------------------
# Product catalog (in a real store this would live in the database too)
# ---------------------------------------------------------------------------
PRODUCTS = [
    {"id": 1, "name": "Milano Chesterfield Sofa", "cat": "sofa", "price": 184999, "old": 219999,
     "rating": 4.8, "reviews": 212, "badge": "Bestseller",
     "img": "https://loremflickr.com/600/450/chesterfield,sofa?lock=1",
     "colors": ["#5c4632", "#2c2c2c", "#8a6d4b"]},
    {"id": 2, "name": "Nordic Wingback Chair", "cat": "chair", "price": 42999, "old": None,
     "rating": 4.6, "reviews": 96, "badge": "New",
     "img": "https://loremflickr.com/600/450/wingback,armchair?lock=2",
     "colors": ["#6f7d5f", "#1c1a17", "#c99a6e"]},
    {"id": 3, "name": "Kashmir Solid Oak Dining Table", "cat": "table", "price": 96999, "old": 112999,
     "rating": 4.9, "reviews": 154, "badge": "Top Rated",
     "img": "https://loremflickr.com/600/450/dining,table,wood?lock=3",
     "colors": ["#a9764c", "#3c2f22"]},
    {"id": 4, "name": "Hessa Upholstered Bed Frame", "cat": "bed", "price": 78999, "old": None,
     "rating": 4.5, "reviews": 68, "badge": None,
     "img": "https://loremflickr.com/600/450/bed,frame,bedroom?lock=4",
     "colors": ["#d9d3c3", "#8a6d4b", "#2c2c2c"]},
    {"id": 5, "name": "Lahore Rattan Accent Chair", "cat": "chair", "price": 28999, "old": 34999,
     "rating": 4.4, "reviews": 41, "badge": "Sale",
     "img": "https://loremflickr.com/600/450/rattan,chair?lock=5",
     "colors": ["#c99a6e", "#5c4632"]},
    {"id": 6, "name": "Walnut Coffee Table", "cat": "table", "price": 31999, "old": None,
     "rating": 4.7, "reviews": 87, "badge": None,
     "img": "https://loremflickr.com/600/450/walnut,coffee,table?lock=6",
     "colors": ["#3c2f22", "#a9764c"]},
    {"id": 7, "name": "Studio 3-Seater Fabric Sofa", "cat": "sofa", "price": 139999, "old": 159999,
     "rating": 4.6, "reviews": 133, "badge": "Sale",
     "img": "https://loremflickr.com/600/450/fabric,sofa,living?lock=7",
     "colors": ["#6f7d5f", "#8a6d4b", "#1c1a17", "#d9d3c3"]},
    {"id": 8, "name": "Oak Bookshelf Unit", "cat": "storage", "price": 54999, "old": None,
     "rating": 4.8, "reviews": 59, "badge": "New",
     "img": "https://loremflickr.com/600/450/bookshelf,wood?lock=8",
     "colors": ["#a9764c", "#3c2f22"]},
    {"id": 9, "name": "Sialkot Solid Wood Wardrobe", "cat": "storage", "price": 89999, "old": 99999,
     "rating": 4.5, "reviews": 74, "badge": None,
     "img": "https://loremflickr.com/600/450/wardrobe,closet,wood?lock=9",
     "colors": ["#3c2f22", "#5c4632", "#1c1a17"]},
    {"id": 10, "name": "Riverside King Bed", "cat": "bed", "price": 112999, "old": 129999,
     "rating": 4.9, "reviews": 188, "badge": "Bestseller",
     "img": "https://loremflickr.com/600/450/king,bed,wooden?lock=10",
     "colors": ["#a9764c", "#2c2c2c"]},
    {"id": 11, "name": "Islamabad Recliner Chair", "cat": "chair", "price": 64999, "old": None,
     "rating": 4.3, "reviews": 45, "badge": None,
     "img": "https://loremflickr.com/600/450/recliner,chair,leather?lock=11",
     "colors": ["#2c2c2c", "#5c4632"]},
    {"id": 12, "name": "Marble-Top Console Table", "cat": "table", "price": 47999, "old": None,
     "rating": 4.6, "reviews": 38, "badge": "New",
     "img": "https://loremflickr.com/600/450/console,table,marble?lock=12",
     "colors": ["#d9d3c3", "#a9764c"]},
]
PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            items_json TEXT NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return {"user": current_user(), "cart_count": cart_count()}


# ---------------------------------------------------------------------------
# Cart helpers (session based; a guest cart survives across pages via cookie)
# ---------------------------------------------------------------------------
def get_cart():
    return session.setdefault("cart", {})  # key: "id_color" -> {id, color, qty}


def cart_count():
    return sum(item["qty"] for item in session.get("cart", {}).values())


def cart_lines():
    lines, total = [], 0
    for key, item in session.get("cart", {}).items():
        p = PRODUCTS_BY_ID.get(item["id"])
        if not p:
            continue
        line_total = p["price"] * item["qty"]
        total += line_total
        lines.append({
            "key": key, "product": p, "color": item["color"],
            "qty": item["qty"], "line_total": line_total,
        })
    return lines, total


# ---------------------------------------------------------------------------
# Routes: storefront
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


# ---------------------------------------------------------------------------
# Routes: auth
# ---------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = None
        if not name or not email or not password:
            error = "Please fill in every field."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."

        db = get_db()
        if error is None:
            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                error = "An account with that email already exists."

        if error:
            flash(error, "error")
            return render_template("register.html", name=name, email=email)

        db.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        session["user_id"] = user["id"]
        flash(f"Welcome, {name}! Your account has been created.", "success")
        return redirect(url_for("index"))

    return render_template("register.html", name="", email="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Incorrect email or password.", "error")
            return render_template("login.html", email=email)

        session["user_id"] = user["id"]
        flash(f"Welcome back, {user['name']}!", "success")
        next_url = request.args.get("next") or url_for("index")
        return redirect(next_url)

    return render_template("login.html", email="")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/account")
@login_required
def account():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],),
    ).fetchall()
    orders = []
    for row in rows:
        orders.append({
            "id": row["id"],
            "total": row["total"],
            "created_at": row["created_at"],
            "lines": json.loads(row["items_json"]),
        })
    return render_template("account.html", orders=orders)


# ---------------------------------------------------------------------------
# Routes: cart API (used by static/script.js via fetch)
# ---------------------------------------------------------------------------
@app.route("/api/cart", methods=["GET"])
def api_cart_get():
    lines, total = cart_lines()
    return jsonify({
        "count": cart_count(),
        "total": total,
        "items": [
            {
                "key": l["key"], "id": l["product"]["id"], "name": l["product"]["name"],
                "img": l["product"]["img"], "price": l["product"]["price"],
                "color": l["color"], "qty": l["qty"], "line_total": l["line_total"],
            } for l in lines
        ],
    })


@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json(force=True)
    pid = int(data.get("id"))
    color = data.get("color") or "#000000"
    if pid not in PRODUCTS_BY_ID:
        return jsonify({"error": "Unknown product"}), 400

    cart = get_cart()
    key = f"{pid}_{color}"
    if key in cart:
        cart[key]["qty"] += 1
    else:
        cart[key] = {"id": pid, "color": color, "qty": 1}
    session.modified = True
    return jsonify({"ok": True, "count": cart_count()})


@app.route("/api/cart/update", methods=["POST"])
def api_cart_update():
    data = request.get_json(force=True)
    key = data.get("key")
    delta = int(data.get("delta", 0))
    cart = get_cart()
    if key in cart:
        cart[key]["qty"] += delta
        if cart[key]["qty"] <= 0:
            del cart[key]
        session.modified = True
    lines, total = cart_lines()
    return jsonify({"ok": True, "count": cart_count(), "total": total})


@app.route("/api/cart/remove", methods=["POST"])
def api_cart_remove():
    data = request.get_json(force=True)
    key = data.get("key")
    cart = get_cart()
    if key in cart:
        del cart[key]
        session.modified = True
    return jsonify({"ok": True, "count": cart_count()})


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    if not session.get("user_id"):
        return jsonify({"error": "login_required", "redirect": url_for("login")}), 401

    lines, total = cart_lines()
    if not lines:
        return jsonify({"error": "empty_cart"}), 400

    items = [
        {"name": l["product"]["name"], "color": l["color"], "qty": l["qty"],
         "price": l["product"]["price"], "line_total": l["line_total"]}
        for l in lines
    ]
    db = get_db()
    db.execute(
        "INSERT INTO orders (user_id, items_json, total, created_at) VALUES (?, ?, ?, ?)",
        (session["user_id"], json.dumps(items), total, datetime.utcnow().isoformat()),
    )
    db.commit()
    session["cart"] = {}
    session.modified = True
    return jsonify({"ok": True, "redirect": url_for("account")})


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        init_db()  # safe: CREATE TABLE IF NOT EXISTS
    app.run(debug=True, host="127.0.0.1", port=5000)
