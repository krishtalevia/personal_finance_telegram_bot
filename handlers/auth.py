from aiogram import Router, types
from aiogram.filters import Command, StateFilter

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

@router.message(StateFilter(None), Command('register'))
async def register_handler(message: types.Message):    
    telegram_id = message.from_user.id
    try:
        if db_manager.register_user(telegram_id):
            await message.answer('✅ Вы успешно зарегистрировались. Для авторизации используйте /login')
    
    except ValueError as ve:
        if str(ve) == 'Пользователь уже существует!':
            await message.answer('⚠️ Вы уже зарегистрированы. Используйте /login для авторизации')
        else:
            await message.answer(f'❌ Ошибка: {ve}')
    
    except Exception as e:
        await message.answer('❌ Во время регистрации произошла непредвиденная ошибка.')
