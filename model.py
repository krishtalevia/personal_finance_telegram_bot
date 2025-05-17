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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'achieved', 'cancelled')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    connection.commit()
    connection.close()

if __name__ == '__main__':
    init_db()

class DatabaseManager:
    def __init__(self, db_name='database.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.connection.commit()