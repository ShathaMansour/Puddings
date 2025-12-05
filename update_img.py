import sqlite3

db = sqlite3.connect("var/cafe.db")

db.execute("""
    UPDATE menu_items
    SET image = ?
    WHERE id = ?
""", ("img/test.png", 2))

db.commit()
db.close()

print("Updated image for item 2!")
