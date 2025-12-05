import sqlite3

# IMPORTANT: Make sure the "var" folder exists manually.
DB_PATH = "var/cafe.db"

connection = sqlite3.connect(DB_PATH)

with connection:
    # Create table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            image TEXT
        );
    """)

    # Check if table already has items (prevents duplicates)
    count = connection.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]

    if count == 0:
        # Insert sample data
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

print("Database initialised and sample menu items added!")
