from flask import Flask, render_template, g
import sqlite3
import configparser

app = Flask(__name__)

# ---------------- CONFIG LOADING (LECTURER STYLE) ----------------
def init(app):
    config = configparser.ConfigParser()
    config_location = "etc/defaults.cfg"

    try:
        print("Loading config file:", config_location)
        config.read(config_location)

        app.config["DEBUG"] = config.getboolean("config", "debug")
        app.config["ip_address"] = config.get("config", "ip_address")
        app.config["port"] = config.getint("config", "port")
        app.config["url"] = config.get("config", "url")
        app.config["DATABASE"] = config.get("config", "db_path")

    except Exception as e:
        print("Could not read config file:", e)

init(app)   # <-- LOAD CONFIG HERE


# ---------------- DATABASE ----------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("home.html", active="home")


@app.route("/about")
def about():
    return render_template("about.html", active="about")


@app.route("/menu")
def menu():
    db = get_db()
    items = db.execute("""
        SELECT id, name, price, category, description, image
        FROM menu_items
        ORDER BY category, name
    """).fetchall()

    categories = {}
    for item in items:
        categories.setdefault(item["category"], []).append(item)

    return render_template("menu.html", categories=categories, active="menu")


@app.route("/cart")
def cart():
    return render_template("cart.html", active="cart")

@app.route("/debug/images")
def debug_images():
    db = get_db()
    rows = db.execute("SELECT id, name, image FROM menu_items").fetchall()
    return "<br>".join([f"{row['id']} – {row['name']} – {row['image']}" for row in rows])

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(port=app.config["port"])
