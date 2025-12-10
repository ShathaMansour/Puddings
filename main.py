from flask import Flask, render_template, g, request, session, redirect
import sqlite3
import configparser
from auth import auth 
from admin import admin
from barista import barista
from database import create_order
import json

# ---------------- INITIALIZE FLASK APP ONCE ----------------
app = Flask(__name__)

print(">>> MAIN LOADED FROM:", __file__)

# ---------------- REGISTER FILTERS ----------------
@app.template_filter("loads")
def loads_filter(s):
    try:
        return json.loads(s)
    except:
        return []



# ---------------- CONFIG LOADING (LECTURER STYLE) ----------------
def init(app):
    config = configparser.ConfigParser()
    config_location = "etc/defaults.cfg"

    try:
        print("Loading config:", config_location)
        config.read(config_location)

        # Flask config
        app.config["DEBUG"] = config.getboolean("flask", "debug")
        app.secret_key = config.get("flask", "secret_key")

        # Server config
        app.config["HOST"] = config.get("server", "host")
        app.config["PORT"] = config.getint("server", "port")

        # Database config
        app.config["DATABASE"] = config.get("database", "db_path")

        app.config["UPLOAD_FOLDER"] = config.get("uploads", "image_folder")


    except Exception as e:
        print("Error reading config:", e)

# ---- Initialize Flask app ----
init(app)


app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(barista)

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
    db = get_db()

    # Fetch categories
    categories = db.execute("""
        SELECT DISTINCT category FROM menu_items
    """).fetchall()

    # Convert rows -> list of strings
    categories = [c["category"] for c in categories]

    # Pick the FIRST TWO categories (or change to random.sample)
    featured = categories[:2]

    # Load items for these two categories
    featured_data = {}
    for cat in featured:
        items = db.execute("""
            SELECT id, name, price, image
            FROM menu_items
            WHERE category = ?
            LIMIT 3
        """, (cat,)).fetchall()

        featured_data[cat] = items

    return render_template("home.html", 
                           active="home", 
                           featured=featured_data)



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
    cart = session.get("cart", {})
    cart_count = sum(cart.values())

    return render_template("menu.html", categories=categories, active="menu", cart_count=cart_count)


@app.route("/cart")
def cart():
    db = get_db()
    cart = session.get("cart", {})

    items = []

    for item_id, qty in cart.items():
        item = db.execute("SELECT * FROM menu_items WHERE id=?", (item_id,)).fetchone()
        if item:
            items.append({"item": item, "qty": qty})

    return render_template("cart.html", items=items, active="cart")


@app.route("/add-to-cart/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    cart = session.get("cart", {})

    qty = int(request.form.get("quantity", 1))
    item_id = str(item_id)

    cart[item_id] = cart.get(item_id, 0) + qty

    session["cart"] = cart
    return redirect("/menu")


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})

    if not cart:
        return redirect("/cart")

    db = get_db()

    # Convert cart items to JSON-friendly list
    order_items = []
    for item_id, qty in cart.items():
        item = db.execute("SELECT name FROM menu_items WHERE id=?", (item_id,)).fetchone()
        if item:
            order_items.append({"name": item["name"], "qty": qty})

    # Create the order in the database
    create_order("Customer", order_items)

    # Clear the cart
    session["cart"] = {}

    return render_template("order_success.html")

@app.context_processor
def inject_theme():
    from database import get_setting
    theme = get_setting("theme")
    return {"active_theme": theme}


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )


