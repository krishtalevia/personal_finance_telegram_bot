import pytest
import os
from model import DatabaseManager, init_db

@pytest.fixture
def db_manager():
    db_file_to_use = 'database.db'
    if os.path.exists(db_file_to_use):
        os.remove(db_file_to_use)

    init_db()
    manager = DatabaseManager(db_name=db_file_to_use)

    yield manager
    
    manager.close()
    if os.path.exists(db_file_to_use):
        os.remove(db_file_to_use)

# Тестовый случай 1.1: Попытка регистрации с уже существующим в системе идентификатором пользователя.
def test_register_existing_user(db_manager):
    telegram_id = 12345
    
    db_manager.register_user(telegram_id)

    with pytest.raises(ValueError, match='Пользователь уже существует!'):
        db_manager.register_user(telegram_id)

# Тестовый случай 1.2: Успешная регистрация нового пользователя.
def test_register_new_user(db_manager):
    telegram_id = 12345
    
    result = db_manager.register_user(telegram_id)
    assert result is True
    
    user_data = db_manager.get_user(telegram_id)
    assert user_data is not None
    assert user_data[1] == telegram_id
    assert user_data[2] == 0

# Тестовый случай 1.3: Авторизация с правильными учетными данными (зарегистрированного пользователя).
def test_authorize_registered_user(db_manager):
    telegram_id = 12345
    db_manager.register_user(telegram_id)

    result = db_manager.authorize_user(telegram_id)
    assert result is True

    assert db_manager.is_user_authorized(telegram_id) is True

# Тестовый случай 1.4: Авторизация с неправильными учетными данными (незарегистрированного пользователя).
def test_authorize_non_existing_user(db_manager):
    telegram_id = 12345

    with pytest.raises(ValueError, match='Пользователь не зарегистрирован.'):
        db_manager.authorize_user(telegram_id)

# Тестовый случай 2.1: Добавление расхода с указанием всех необходимых данных.
def test_add_expense_transaction(db_manager):
    telegram_id = 12345
    db_manager.register_user(telegram_id)
    
    category_name = "Еда"
    
    result = db_manager.add_transaction(telegram_id, 'expense', 30.50, category_name)
    assert result is True

# Тестовый случай 2.3: Просмотр истории транзакций по несуществующей категории.
def test_view_transactions_non_existing_category(db_manager):
    telegram_id = 12345
    db_manager.register_user(telegram_id)

    db_manager.add_transaction(telegram_id, 'expense', 100, "Существующая Категория")

    transactions = db_manager.get_transactions(telegram_id, category_name_filter="Несуществующая Категория")
    assert isinstance(transactions, list)
    assert len(transactions) == 0

# Тестовый случай 3.1: Установка новой финансовой цели.
def test_set_new_financial_goal(db_manager):
    telegram_id = 12345
    db_manager.register_user(telegram_id)

    description = "Накопить на отпуск"
    target_amount = 100000.00
    
    result = db_manager.add_financial_goal(telegram_id, description, target_amount)
    assert result is True

    goals = db_manager.get_financial_goals(telegram_id)
    assert len(goals) == 1
    goal = goals[0]
    
    assert goal[1] == description
    assert goal[2] == target_amount
    assert goal[3] == 0.0
    assert goal[4] == 'active'
    
# Тестовый случай 3.2: Просмотр списка установленных целей.
def test_view_financial_goals(db_manager):
    telegram_id = 12345
    db_manager.register_user(telegram_id)

    db_manager.add_financial_goal(telegram_id, "Цель 1", 5000)
    db_manager.add_financial_goal(telegram_id, "Цель 2", 10000)

    goals = db_manager.get_financial_goals(telegram_id)
    assert len(goals) == 2