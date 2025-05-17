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

@router.message(StateFilter(AddExpenseStates.AddingAmount))
async def adding_expense_amount_handler(message: types.Message, state: FSMContext):
    amount_str = message.text.strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            await message.answer("⚠️ Сумма должна быть положительным числом. Повторите ввод.")
            return
        
        await state.update_data(amount=amount)
        await message.answer("🏷️ Введите категорию расхода (например, Еда, Транспорт):")
        await state.set_state(AddExpenseStates.AddingCategory)

    except ValueError:
        await message.answer("⚠️ Некорректная сумма. Введите число больше нуля. Повторите ввод.")

@router.message(StateFilter(AddExpenseStates.AddingCategory))
async def adding_expense_category_handler(message: types.Message, state: FSMContext):
    category_name = message.text.strip()
    if not category_name:
        await message.answer("⚠️ Название категории не может быть пустым. Повторите ввод.")
        return

    await state.update_data(category_name_original=category_name)
    
    telegram_id = message.from_user.id
    category_type = 'expense'
    processed_category_name = category_name

    try:
        db_manager.add_category(telegram_id, category_name, category_type)
    except ValueError as ve:
        if "уже существует" in str(ve).lower():
            existing_categories = db_manager.get_categories(telegram_id, category_type)
            for _id, name, _type in existing_categories:
                if name.lower() == category_name.lower():
                    processed_category_name = name
                    break
        else:
            await message.answer(f"❌ Ошибка при обработке категории: {ve}. Добавление расхода отменено.")
            await state.clear()
            return
        
    except Exception as e_cat:
        await message.answer(f"❌ Произошла системная ошибка с категорией: {e_cat}. Добавление расхода отменено.")
        await state.clear()
        return

    await state.update_data(category_name_processed=processed_category_name)
    
    data = await state.get_data()
    amount = data['amount']
    
    await message.answer(
        f"Подтвердите добавление расхода:\n"
        f"💸 Сумма: {amount}\n"
        f"🏷️ Категория: {processed_category_name}\n\n"
        f"Добавить эту запись? (Да/Нет)"
    )
    await state.set_state(AddExpenseStates.Confirmation)