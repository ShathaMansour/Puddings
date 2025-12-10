from flask import Blueprint, render_template, session, abort, request, jsonify
from database import get_orders, update_order_status
print("BARISTA LOADED FROM:", __file__)


barista = Blueprint("barista", __name__, url_prefix="/barista")

def barista_required(func):
    def wrapper(*a, **kw):
        if session.get("role") != "barista":
            return abort(403)
        return func(*a, **kw)
    wrapper.__name__ = func.__name__
    return wrapper



@barista.route("/")
@barista_required
def dashboard():
    orders = get_orders()
    return render_template("barista/dashboard.html", orders=orders)


# UPDATE ORDER STATUS (AJAX)
@barista.route("/update", methods=["POST"])
@barista_required
def update_status():
    data = request.json
    order_id = data["order_id"]
    new_status = data["status"]

    update_order_status(order_id, new_status)
    return jsonify({"success": True})
