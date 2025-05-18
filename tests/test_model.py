import pytest
import os
from model import DatabaseManager, init_db

@pytest.fixture
def db_manager():
    db_file_to_use = 'database.db'
    if os.path.exists(db_file_to_use):
        os.remove(db_file_to_use)