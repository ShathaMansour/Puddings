import sqlite3

DB_PATH = "var/cafe.db"

connection = sqlite3.connect(DB_PATH)

with connection:

    # -------------------------
    # CREATE TABLES
    # -------------------------
    connection.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            image TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'barista'))
        )
    """)

    connection.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        items TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('pending', 'progress', 'ready')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
    connection.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
""")

# Insert default theme only if not exists
    connection.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('theme', 'default');
""")

    


    # -------------------------
    # INSERT DEFAULT USERS ONCE
    # -------------------------
    user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    if user_count == 0:
        connection.executemany("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, [
            ("testAdmin", "admin123", "admin"),
            ("testBarista", "barista123", "barista")
        ])
        print("Added default users.")

    # -------------------------
    # INSERT SAMPLE MENU ITEMS ONCE
    # -------------------------
    item_count = connection.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]

    if item_count == 0:
        connection.executemany("""
            INSERT INTO menu_items (name, price, category, description)
            VALUES (?, ?, ?, ?)
        """, [
            ("Latte", 3.50, "Drinks", "Smooth espresso with steamed milk"),
            ("Cappuccino", 3.20, "Drinks", "Classic Italian coffee with foam"),
            ("Strawberry Cake Slice", 4.00, "Cake", "Fresh, sweet strawberry cake"),
            ("Croissant", 2.40, "Cake", "Freshly baked butter croissant"),
            ("Catan Board Game", 2.00, "Board Games", "Rent for 2 hours"),
        ])
        print("Added sample menu items.")

print("Database initialised!")
