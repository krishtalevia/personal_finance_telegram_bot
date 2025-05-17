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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            amount REAL NOT NULL,
            category_name TEXT NOT NULL, 
            transaction_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    connection.commit()
    connection.close()