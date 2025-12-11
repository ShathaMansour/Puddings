from flask import Blueprint, render_template, request, redirect, session
from database import get_db
from werkzeug.security import check_password_hash


auth = Blueprint('auth', __name__)


# Login route:
# Handles both the login form display (GET)
# and the actual login authentication (POST).
@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        # Try to find a user with that username
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        # If user exists AND the hashed password matches then log them in
        if user and check_password_hash(user["password"], password):

            # Store who is logged in + their role
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            # Redirect depending on their role
            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/barista")

        # If username doesn't exist or wrong password 
        error = "Invalid username or password"

    # If GET or login failed, show login page
    return render_template("login.html", error=error)



# Logour route:
# Clears the session completely and sends user back to login.
@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
