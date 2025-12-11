import sqlite3
from flask import g, current_app

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def get_all_items():
    return get_db().execute("SELECT * FROM menu_items").fetchall()

def get_item(id):
    return get_db().execute("SELECT * FROM menu_items WHERE id=?", (id,)).fetchone()

def add_item(name, price, category, description, image):
    db = get_db()
    db.execute("""
        INSERT INTO menu_items (name, price, category, description, image)
        VALUES (?, ?, ?, ?, ?)
    """, (name, price, category, description, image))
    db.commit()

def update_item(id, name, price, category, description, image):
    db = get_db()
    db.execute("""
        UPDATE menu_items
        SET name=?, price=?, category=?, description=?, image=?
        WHERE id=?
    """, (name, price, category, description, image, id))
    db.commit()

def delete_item(id):
    db = get_db()
    db.execute("DELETE FROM menu_items WHERE id=?", (id,))
    db.commit()

import json

def create_order(customer_name, items):
    db = get_db()

    import json
    items_json = json.dumps(items)

    cursor = db.execute("""
        INSERT INTO orders (customer_name, items, status)
        VALUES (?, ?, 'pending')
    """, (customer_name, items_json))

    db.commit()

    return cursor.lastrowid   


def get_orders():
    db = get_db()
    return db.execute("SELECT * FROM orders ORDER BY created_at").fetchall()

def update_order_status(order_id, status):
    db = get_db()
    db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    db.commit()
def get_setting(key):
    db = get_db()
    row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None

def set_setting(key, value):
    db = get_db()
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    db.commit()
