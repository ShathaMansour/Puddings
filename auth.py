from flask import Blueprint, render_template, request, redirect, session
from database import get_db
from werkzeug.security import check_password_hash


auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        # Get user by username ONLY
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        # Check hash securely
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/barista")

        error = "Invalid username or password"

    return render_template("login.html", error=error)
    


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
