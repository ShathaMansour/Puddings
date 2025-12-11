import os
from flask import Blueprint, render_template, request, redirect, session, abort, current_app
from werkzeug.utils import secure_filename
from database import get_all_items, set_setting, delete_item, get_db


admin = Blueprint("admin", __name__)

def admin_required(func):
    def wrapper(*a, **kw):
        if session.get("role") != "admin":
            return abort(403)
        return func(*a, **kw)
    wrapper.__name__ = func.__name__
    return wrapper


@admin.route("/admin")
@admin_required
def admin_dashboard():

    # Get all items from DB
    items = get_all_items()

    # Extract unique categories
    categories = sorted({item["category"] for item in items})

    # Get filters from query string
    search = request.args.get("search", "").strip().lower()
    category = request.args.get("category", "").strip()

    # Filter items
    filtered_items = items

    if search:
        filtered_items = [
            item for item in filtered_items
            if search in item["name"].lower()
        ]

    if category:
        filtered_items = [
            item for item in filtered_items
            if item["category"] == category
        ]

    return render_template(
        "admin/dashboard.html",
        items=filtered_items,
        categories=categories
    )


@admin.route("/admin/add", methods=["GET", "POST"])
@admin_required
def add_item():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        category = request.form["category"]
        description = request.form["description"]

        # Handle image upload
        image_file = request.files.get("image_file")
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image_file.save(file_path)   # Saved permenantly 

            # Store path relative to /static
            filename = f"uploads/{filename}"

        db = get_db()
        db.execute("""
            INSERT INTO menu_items (name, price, category, description, image)
            VALUES (?, ?, ?, ?, ?)
        """, (name, price, category, description, filename))
        db.commit()

        return redirect("/admin")

    return render_template("admin/add_item.html")




# ------------------------------
# EDIT ITEM
# ------------------------------
@admin.route("/admin/edit/<int:item_id>", methods=["GET", "POST"])
@admin_required
def edit_item(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM menu_items WHERE id=?", (item_id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        category = request.form["category"]
        description = request.form["description"]

        image_file = request.files.get("image_file")
        filename = item["image"]  # keep old image by default

        if image_file and image_file.filename != "":
            filename_new = secure_filename(image_file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename_new)
            image_file.save(file_path)

            filename = f"uploads/{filename_new}"

        db.execute("""
            UPDATE menu_items
            SET name=?, price=?, category=?, description=?, image=?
            WHERE id=?
        """, (name, price, category, description, filename, item_id))

        db.commit()
        return redirect("/admin")

    return render_template("admin/edit.html", item=item)



# ------------------------------
# DELETE ITEM
# ------------------------------
@admin.route("/admin/delete/<int:item_id>")
@admin_required
def admin_delete_item(item_id):
    delete_item(item_id)
    return redirect("/admin")

@admin.route("/admin/theme", methods=["POST"])
@admin_required
def admin_change_theme():
    theme = request.form["theme"]
    set_setting("theme", theme)
    return redirect("/admin")

@admin.route("/admin/analytics")
@admin_required
def analytics_dashboard():
    db = get_db()

    # Most popular menu items (count how many times they appear in orders)
    popular_items = [
    (row[0], row[1])
    for row in db.execute("""
        SELECT json_extract(value, '$.name') AS name,
               COUNT(*) AS count
        FROM orders, json_each(orders.items)
        GROUP BY name
        ORDER BY count DESC
    """).fetchall()
]


    # Orders per day
    orders_per_day = [
    (row[0], row[1])
    for row in db.execute("""
        SELECT DATE(created_at) AS day,
               COUNT(*) AS count
        FROM orders
        GROUP BY day
        ORDER BY day
    """).fetchall()
]


    # Total number of orders
    total_orders = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    return render_template(
    "admin/analytics.html",
    popular_items=popular_items,
    orders_per_day=orders_per_day,
    total_orders=total_orders
)


