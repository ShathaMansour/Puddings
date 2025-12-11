import os
from flask import Blueprint, render_template, request, redirect, session, abort, current_app
from werkzeug.utils import secure_filename
from database import get_all_items, set_setting, delete_item, get_db


admin = Blueprint("admin", __name__)


# Admin-only access decorator:
# Ensures that only users with role "admin"
# can access routes decorated with @admin_required.
def admin_required(func):
    def wrapper(*a, **kw):
        if session.get("role") != "admin":
            return abort(403)   # Forbidden page if user is not admin
        return func(*a, **kw)

    # Preserve original function name (important for Flask routing)
    wrapper.__name__ = func.__name__
    return wrapper


# Admin dashboard route:
# Displays all menu items with optional search and category filtering.
@admin.route("/admin")
@admin_required
def admin_dashboard():

    # Fetch all menu items from the database
    items = get_all_items()

    # Extract unique categories for the filter dropdown
    categories = sorted({item["category"] for item in items})

    # Read filter values from query parameters
    search = request.args.get("search", "").strip().lower()
    category = request.args.get("category", "").strip()

    # Start with all items
    filtered_items = items

    # Filter by name if search text is provided
    if search:
        filtered_items = [
            item for item in filtered_items
            if search in item["name"].lower()
        ]

    # Filter by category if one is selected
    if category:
        filtered_items = [
            item for item in filtered_items
            if item["category"] == category
        ]

    # Render dashboard with filtered results
    return render_template(
        "admin/dashboard.html",
        items=filtered_items,
        categories=categories
    )


# Add new menu item route:
# Shows form on GET and saves new item on POST.
@admin.route("/admin/add", methods=["GET", "POST"])
@admin_required
def add_item():
    if request.method == "POST":
        # Read form data
        name = request.form["name"]
        price = request.form["price"]
        category = request.form["category"]
        description = request.form["description"]

        # Handle optional image upload
        image_file = request.files.get("image_file")
        filename = None

        if image_file and image_file.filename != "":
            # Make filename safe for filesystem
            filename = secure_filename(image_file.filename)

            # Build full upload path
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )

            # Save image file to disk
            image_file.save(file_path)

            # Store relative path for use in templates
            filename = f"uploads/{filename}"

        # Insert new item into database
        db = get_db()
        db.execute("""
            INSERT INTO menu_items (name, price, category, description, image)
            VALUES (?, ?, ?, ?, ?)
        """, (name, price, category, description, filename))
        db.commit()

        return redirect("/admin")

    # GET request so show add item form
    return render_template("admin/add_item.html")


# Edit menu item route:
# Updates text fields and optionally replaces image.
@admin.route("/admin/edit/<int:item_id>", methods=["GET", "POST"])
@admin_required
def edit_item(item_id):
    db = get_db()

    # Load existing item data
    item = db.execute(
        "SELECT * FROM menu_items WHERE id=?",
        (item_id,)
    ).fetchone()

    if request.method == "POST":
        # Read updated form values
        name = request.form["name"]
        price = request.form["price"]
        category = request.form["category"]
        description = request.form["description"]

        image_file = request.files.get("image_file")
        filename = item["image"]  # Default: keep old image

        # Replace image if a new file is uploaded
        if image_file and image_file.filename != "":
            filename_new = secure_filename(image_file.filename)
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename_new
            )
            image_file.save(file_path)

            filename = f"uploads/{filename_new}"

        # Update item in database
        db.execute("""
            UPDATE menu_items
            SET name=?, price=?, category=?, description=?, image=?
            WHERE id=?
        """, (name, price, category, description, filename, item_id))

        db.commit()
        return redirect("/admin")

    # GET request to show edit form with existing data
    return render_template("admin/edit.html", item=item)


# Delete menu item route:
# Removes item from database by ID.
@admin.route("/admin/delete/<int:item_id>")
@admin_required
def admin_delete_item(item_id):
    delete_item(item_id)
    return redirect("/admin")


# Theme change route:
# Updates the active UI theme setting.
@admin.route("/admin/theme", methods=["POST"])
@admin_required
def admin_change_theme():
    theme = request.form["theme"]
    set_setting("theme", theme)
    return redirect("/admin")


# Analytics dashboard route:
# Displays statistics such as popular items and order counts.
@admin.route("/admin/analytics")
@admin_required
def analytics_dashboard():
    db = get_db()

    # Most popular items:
    # Counts how often each item appears in orders
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

    # Orders per day:
    # Used for traffic trends over time
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
    total_orders = db.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    # Render analytics page
    return render_template(
        "admin/analytics.html",
        popular_items=popular_items,
        orders_per_day=orders_per_day,
        total_orders=total_orders
    )
