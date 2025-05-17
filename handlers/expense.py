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

@router.message(StateFilter(None), Command('add_expense'))
async def add_expense_start_handler(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id

    user = db_manager.get_user(telegram_id)
    if not user:
        await message.answer('❌ Вы не зарегистрированы. Используйте команду /register для регистрации.')
        return
    
    if not db_manager.is_user_authorized(telegram_id):
        await message.answer('❌ Вы не авторизованы. Используйте команду /login для авторизации.')
        return
    
    await message.answer("💸 Введите сумму расхода:")
    await state.set_state(AddExpenseStates.AddingAmount)