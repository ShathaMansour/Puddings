from flask import Blueprint, render_template, session, abort, request, jsonify 
from database import get_orders, update_order_status

# Setting up the blueprint so everything here sits under /barista
barista = Blueprint("barista", __name__, url_prefix="/barista")


# SECURITY: Barista access only
# This decorator makes sure ONLY baristas can access these routes.
# If someone tries to sneak in (customer or admin), it will show 403 page.
def barista_required(func):
    def wrapper(*a, **kw):
        if session.get("role") != "barista":
            return abort(403)   # Access forbidden
        return func(*a, **kw)
    wrapper.__name__ = func.__name__
    return wrapper



# Main barista dashboard page
@barista.route("/")
@barista_required
def dashboard():
    # Fetch all orders from the database (pending, progress, ready, collected)
    orders = get_orders()

    # Render the barista dashboard with the current orders
    return render_template("barista/dashboard.html", orders=orders)



# Update order status (AJAX)
# This is triggered when a barista drags a card into another column.
# It updates the order status in the database instantly.
@barista.route("/update", methods=["POST"])
@barista_required
def update_status():
    data = request.json  # receive the JSON sent from JS drag and drop

    order_id = data["order_id"]        # which order is being moved
    new_status = data["status"]        # where the order was dropped

    # Update the database with the new status
    update_order_status(order_id, new_status)

    # Send an "ok!" back to JavaScript
    return jsonify({"success": True})
