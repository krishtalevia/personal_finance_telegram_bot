import sqlite3
from datetime import datetime

def init_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id     INTEGER UNIQUE NOT NULL,
            username        TEXT,
            is_authorized   BOOLEAN DEFAULT 0
        );
    ''')
    connection.commit()
    connection.close()