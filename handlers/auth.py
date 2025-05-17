from aiogram import Router, types
from aiogram.filters import Command, StateFilter

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()