import datetime
from aiogram import Router, types
from aiogram.filters import Command, StateFilter

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

@router.message(Command('set_goal'))
async def set_financial_goal_handler(message: types.Message):
    telegram_id = message.from_user.id

    user = db_manager.get_user(telegram_id)
    if not user:
        await message.answer('❌ Вы не зарегистрированы. Используйте команду /register для регистрации.')
        return
    
    if not db_manager.is_user_authorized(telegram_id):
        await message.answer('❌ Вы не авторизованы. Используйте команду /login для авторизации.')
        return
    
    args_str = message.get_args()
    if not args_str:
        await message.answer(
            "⚠️ Неверный формат команды.\n"
            "Используйте: /set_goal [сумма] [описание]\n"
            "Пример: /set_goal 100000 Скопить на отпуск"
        )
        return

    args_list = args_str.split(maxsplit=1)

    if len(args_list) < 2:
        await message.answer(
            "⚠️ Не указана сумма или описание цели.\n"
            "Используйте: /set_goal [сумма] [описание]\n"
            "Пример: /set_goal 100000 Скопить на отпуск"
        )
        return

    amount_str = args_list[0]
    description = args_list[1].strip()
