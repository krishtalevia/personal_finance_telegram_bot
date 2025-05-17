import sqlite3
from datetime import datetime

def init_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id     INTEGER UNIQUE NOT NULL,
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

    def get_user(self, telegram_id):
        self.cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return self.cursor.fetchone()
    
    def register_user(self, telegram_id):
        if self.get_user(telegram_id):
            raise ValueError('Пользователь уже существует!')
        self.cursor.execute('INSERT INTO users (telegram_id, is_authorized) VALUES (?, ?)', (telegram_id, 0))
        self.connection.commit()
        return True
    
    def authorize_user(self, telegram_id):
        self.cursor.execute('SELECT is_authorized FROM users WHERE telegram_id = ?', (telegram_id,))
        result = self.cursor.fetchone()

        if result is None:
            raise ValueError('Пользователь не зарегистрирован.')
        
        if result[0] == 1:
            raise ValueError('Пользователь уже авторизован.')

        self.cursor.execute('UPDATE users SET is_authorized = 1 WHERE telegram_id = ?', (telegram_id,))
        self.connection.commit()
        return True

    def is_user_authorized(self, telegram_id):
        self.cursor.execute('SELECT is_authorized FROM users WHERE telegram_id = ?', (telegram_id,))
        result = self.cursor.fetchone()
        if result is None:
            raise ValueError('Пользователь не найден.')
        return result[0] == 1
    
    def logout_user(self, telegram_id):
        if self.is_user_authorized(telegram_id):
            self.cursor.execute('UPDATE users SET is_authorized = 0 WHERE telegram_id = ?', (telegram_id,))
            self.connection.commit()
            return True
        else:
            raise ValueError('Пользователь не авторизован.')
        
    def get_user_id_by_telegram_id(self, telegram_id):
        self.cursor.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,))
        user_id = self.cursor.fetchone()
        if user_id:
            return user_id[0]
        return None
    
    def add_category(self, telegram_id, name, type):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            raise ValueError("Пользователь для добавления категории не найден.")

        self.cursor.execute(
            "SELECT id FROM categories WHERE user_id = ? AND name = ? AND type = ?",
            (user_id, name, type)
        )
        if self.cursor.fetchone():
            raise ValueError(f"Категория '{name}' ({type}) уже существует для этого пользователя.")

        self.cursor.execute(
            "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
            (user_id, name, type)
        )
        self.connection.commit()
        return True
    
    def get_categories(self, telegram_id, category_type=None):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return []

        params = [user_id]

        if category_type:
            "SELECT id, name, type FROM categories WHERE user_id = ?" += " AND type = ?"
            params.append(category_type)
        
        self.cursor.execute("SELECT id, name, type FROM categories WHERE user_id = ?", params) 
        return self.cursor.fetchall()
    
    def add_transaction(self, telegram_id, type, amount, category_name):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            raise ValueError("Пользователь для добавления транзакции не найден.")

        transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute(
            "INSERT INTO transactions (user_id, type, amount, category_name, transaction_date) VALUES (?, ?, ?, ?, ?)",
            [user_id, type, amount, category_name, transaction_date]
        )
        self.connection.commit()
        return True 
    
    def get_transactions(self, telegram_id, period_start_str=None, period_end_str=None, category_name_filter=None, transaction_type_filter=None):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return []

        query = "SELECT id, type, amount, category_name, transaction_date FROM transactions WHERE user_id = ?"
        params = [user_id]

        if period_start_str:
            start_dt = period_start_str
            if len(period_start_str) == 10:
                start_dt += " 00:00:00"
            query += " AND transaction_date >= ?"
            params.append(start_dt)
        
        if period_end_str:
            end_dt = period_end_str
            if len(period_end_str) == 10:
                end_dt += " 23:59:59"
            query += " AND transaction_date <= ?"
            params.append(end_dt)

        if category_name_filter:
            query += " AND category_name = ?"
            params.append(category_name_filter)
        
        if transaction_type_filter:
            query += " AND type = ?"
            params.append(transaction_type_filter)
            
        query += " ORDER BY transaction_date DESC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def add_financial_goal(self, telegram_id, description, target_amount):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            raise ValueError("Пользователь для добавления финансовой цели не найден.")

        self.cursor.execute(
            "INSERT INTO financial_goals (user_id, description, target_amount) VALUES (?, ?, ?)",
            [user_id, description, target_amount]
        )
        self.connection.commit()
        return True
    
    def get_financial_goals(self, telegram_id, status_filter=None):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return []

        query = "SELECT id, description, target_amount, current_amount, status FROM financial_goals WHERE user_id = ?"
        params = [user_id]

        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)

        query += " ORDER BY id DESC"

        self.cursor.execute(query, params) 
        return self.cursor.fetchall()
    
    def get_financial_goal_by_id(self, goal_id, telegram_id):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return None 
        
        self.cursor.execute(
            "SELECT id, description, target_amount, current_amount, status FROM financial_goals WHERE id = ? AND user_id = ?",
            [goal_id, user_id]
        )
        return self.cursor.fetchone()
    
    def update_goal_parameter(self, goal_id, telegram_id, parameter_name, new_value):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            raise ValueError("Пользователь для обновления цели не найден.")

        allowed_parameters = ['description', 'target_amount', 'current_amount', 'status']
        if parameter_name not in allowed_parameters:
            raise ValueError(f"Параметр '{parameter_name}' не может быть обновлен.")

        self.cursor.execute(
            f"UPDATE financial_goals SET {parameter_name} = ? WHERE id = ? AND user_id = ?",
            [new_value, goal_id, user_id]
        )
        self.connection.commit()
        return True
    
    def delete_financial_goal(self, goal_id, telegram_id):
        user_id = self.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            raise ValueError("Пользователь для удаления цели не найден.")
        
        self.cursor.execute(
            "DELETE FROM financial_goals WHERE id = ? AND user_id = ?",
            [goal_id, user_id]
        )
        self.connection.commit()
        return True