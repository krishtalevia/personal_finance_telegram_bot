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
    telegram_id = 11111
    
    result = db_manager.register_user(telegram_id)
    assert result is True
    
    user_data = db_manager.get_user(telegram_id)
    assert user_data is not None
    assert user_data[1] == telegram_id
    assert user_data[2] == 0

# Тестовый случай 1.3: Авторизация с правильными учетными данными (зарегистрированного пользователя).
def test_authorize_registered_user(db_manager):
    telegram_id = 22222
    db_manager.register_user(telegram_id)

    result = db_manager.authorize_user(telegram_id)
    assert result is True

    assert db_manager.is_user_authorized(telegram_id) is True