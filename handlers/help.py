from aiogram import Router, types
from aiogram.filters import Command, CommandObject

router = Router()

@router.message(Command('help'))
async def help_handler(message: types.Message, command: CommandObject):
    args = command.args
    
    if not args:
        help_text = (
            "📋 Список доступных команд:\n\n"
            "/start - Начало работы и информация о боте.\n"
            "/register - Регистрация нового пользователя.\n\n"
            "💸 Управление финансами:\n"
            "/add_income - Добавить запись о доходе.\n"
            "/add_expense - Добавить запись о расходе.\n"
            "/view_transactions - Просмотр истории транзакций.\n\n"
            "🎯 Финансовые цели:\n"
            "/set_goal - Установить новую финансовую цель.\n\n"
            "📊 Аналитика:\n"
            "/statistics - Просмотр статистики по финансам и целям.\n\n"
            "ℹ️ Для получения подробной информации по конкретной команде, введите /help [имя_команды]."
        )
        await message.answer(help_text)