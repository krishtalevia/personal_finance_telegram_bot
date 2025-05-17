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

@router.message(StateFilter(None), Command('login'))
async def login_handler(message: types.Message):
    telegram_id = message.from_user.id
    try:
        user = db_manager.get_user(telegram_id)
        if user is None:
            await message.answer('❌ Пользователь не найден. Для регистрации используйте /register')
            return
        
        if db_manager.is_user_authorized(telegram_id):
            await message.answer('⚠️ Вы уже авторизованы.')
        else:
            db_manager.authorize_user(telegram_id)
            await message.answer('✅ Вы успешно авторизованы.')
    
    except ValueError as ve: 
        await message.answer(f'❌ Ошибка при авторизации: {ve}')
    
    except Exception as e:
        await message.answer('❌ Произошла критическая ошибка во время авторизации. Попробуйте позже.')