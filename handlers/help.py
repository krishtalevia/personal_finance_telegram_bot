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

    elif args == 'add_income':
        help_text = (
            "💸 Команда /add_income:\n\n"
            "Предназначена для добавления новой записи о доходе.\n"
            "Бот пошагово запросит у вас:\n"
            "1. Сумму дохода (например, 50000).\n"
            "2. Категорию дохода (например, Зарплата).\n\n"
            "Пример вызова: /add_income\n"
            "(Далее следуйте инструкциям бота)"
        )
        await message.answer(help_text)

    elif args == 'add_expense':
        help_text = (
            "💸 Команда /add_expense:\n\n"
            "Предназначена для добавления новой записи о расходе.\n"
            "Бот пошагово запросит у вас:\n"
            "1. Сумму расхода (например, 2500).\n"
            "2. Категорию расхода (например, Еда, Транспорт).\n\n"
            "Пример вызова: /add_expense\n"
            "(Далее следуйте инструкциям бота)"
        )
        await message.answer(help_text)

    elif args == 'view_transactions':
        help_text = (
            "📜 Команда /view_transactions [период] [категория]:\n\n"
            "Позволяет просматривать историю ваших транзакций.\n"
            "Аргументы (период и категория) не обязательны.\n\n"
            "Параметры:\n"
            "  [период] - Укажите период (день, неделя, месяц, год). По умолчанию 'месяц'.\n"
            "  [категория] - Название категории для фильтрации (например, Еда).\n\n"
            "Примеры использования:\n"
            "/view_transactions - транзакции за текущий месяц.\n"
            "/view_transactions неделя - транзакции за текущую неделю.\n"
            "/view_transactions год Еда - транзакции по категории 'Еда' за текущий год.\n"
            "/view_transactions Транспорт - транзакции по категории 'Транспорт' за текущий месяц."
        )
        await message.answer(help_text)