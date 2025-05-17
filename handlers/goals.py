import datetime
from aiogram import Router, types
from aiogram.filters import Command, StateFilter

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

@router.message(Command('set_goal'))
async def set_financial_goal_handler(message: types.Message):
    pass