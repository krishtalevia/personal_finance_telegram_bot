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