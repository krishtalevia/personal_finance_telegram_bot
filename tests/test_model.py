import pytest
import os
from model import DatabaseManager, init_db

@pytest.fixture
def db_manager():
    if os.path.exists('test_finance_bot.db'):
        os.remove('test_finance_bot.db')