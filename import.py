import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from app import app, db, Item  # Replace 'your_flask_app' with the name of your Flask app file

def get_sqlite_data():
    conn = sqlite3.connect('my_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT description as name, total, day, month FROM tb_event")  # Replace with your SQLite table name
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def migrate_to_postgres(data):
    with app.app_context():
        for name, total, day, month in data:
            new_item = Item(name=name, total=total, day=int(day), month=int(month))
            db.session.add(new_item)
        db.session.commit()

if __name__ == "__main__":
    sqlite_data = get_sqlite_data()
    migrate_to_postgres(sqlite_data)
