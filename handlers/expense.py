from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

class AddExpenseStates(StatesGroup):
    AddingAmount = State()
    AddingCategory = State()
    Confirmation = State()