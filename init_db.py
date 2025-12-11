import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "var/cafe.db"
connection = sqlite3.connect(DB_PATH)

with connection:

    # Menu items table:
    # Stores all items shown on the menu. 
    # Admin dashboard adds/edits/deletes from here.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            image TEXT   -- just storing a path to the uploaded image
        )
    """)

    # Users table:
    # Stores admin + barista accounts.
    # Passwords are hashed for security.
    # Role controls what dashboard they see.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,  -- hashed password
            role TEXT NOT NULL CHECK(role IN ('admin', 'barista'))
        )
    """)

    # Orders table:
    # Stores every order created when a customer checks out.
    # Status is used by the barista dashboard (pending → progress → ready → collected).
    # created_at is for analytics + timestamps.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items TEXT NOT NULL,  -- stored as JSON string
            status TEXT NOT NULL CHECK(status IN ('pending', 'progress', 'ready', 'collected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Settings table
    # Used to store things like the active theme (default, Halloween, future: Christmas…)
    # Can be expanded in the future without changing the schema.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Insert default theme ONLY if nothing exists yet
    connection.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('theme', 'default')
    """)

    # Insert test users:
    # Adds one admin + one barista for testing.
    # Passwords are securely hashed here.
    user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    if user_count == 0:

        connection.executemany("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, [
            ("testAdmin", generate_password_hash("admin123"), "admin"),
            ("testBarista", generate_password_hash("barista123"), "barista")
        ])

    # Insert sample menu items:
    # These are placeholders so the site has content immediately.
    # Admin can change/remove everything later.
    item_count = connection.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]

    if item_count == 0:
        connection.executemany("""
            INSERT INTO menu_items (name, price, category, description, image)
            VALUES (?, ?, ?, ?, ?)
        """, [

            # Drinks
            ("Vanilla Latte", 3.80, "Drinks", "Smooth espresso blended with steamed milk and vanilla syrup.", "img/slideshow4.png"),
            ("Iced Caramel Macchiato", 4.20, "Drinks", "Espresso over milk with sweet caramel drizzle served on ice.", "img/slideshow5.png"),
            ("Mocha Deluxe", 4.50, "Drinks", "Rich espresso mixed with chocolate and topped with whipped cream.", "img/slideshow4.png"),
            ("Matcha Green Tea Latte", 4.00, "Drinks", "Creamy ceremonial-grade matcha blended with milk.", "img/slideshow5.png"),
            ("Chai Spice Latte", 3.90, "Drinks", "Aromatic chai infused with cinnamon, cardamom, and warm spices.", "img/slideshow4.png"),

            # Cake
            ("Triple Chocolate Cake Slice", 4.50, "Cake", "Dark, milk, and white chocolate layers topped with ganache.", "img/slideshow2.png"),
            ("Victoria Sponge Slice", 4.20, "Cake", "Classic vanilla sponge filled with raspberry jam and cream.", "img/slideshow3.png"),
            ("Carrot Walnut Cake", 4.30, "Cake", "Moist carrot cake with walnuts and cream cheese frosting.", "img/slideshow2.png"),
            ("Red Velvet Slice", 4.40, "Cake", "Smooth cocoa sponge with velvety cream cheese icing.", "img/slideshow3.png"),
            ("Lemon Drizzle Slice", 3.90, "Cake", "Zesty lemon sponge soaked in sweet citrus glaze.", "img/slideshow3.png"),

            # Board games
            ("Uno Deck", 1.50, "Board Games", "Fast-paced card game fun for all ages.", "img/shess.png"),
            ("Jenga Tower", 2.00, "Board Games", "Stack wooden blocks and try not to let the tower fall!", "img/shess.png"),
            ("Chess Set", 2.50, "Board Games", "Classic strategy board game for two players.", "img/shess.png"),
            ("Dobble", 1.80, "Board Games", "Find and match symbols quickly before your opponents!", "img/shess.png"),
            ("Exploding Kittens", 2.20, "Board Games", "Chaotic and fun card game filled with surprises.", "img/shess.png")
        ])

        print("Added sample menu items.")

print("Database initialised!")
