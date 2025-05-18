from aiogram import Router, types
from aiogram.filters import Command

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

@router.message(Command('start'))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    
    registration_status = "❌ Не зарегистрирован"
    authorization_status = "❌ Не авторизован"

    try:
        user = db_manager.get_user(telegram_id)
        if user:
            registration_status = "✅ Зарегистрирован"
            if db_manager.is_user_authorized(telegram_id):
                authorization_status = "✅ Авторизован"

    except Exception as e:
        pass

    welcome_message = (
        f"👋 Добро пожаловать в бот для управления личными финансами!\n\n"
        f"💸 Этот бот поможет вам:\n"
        f"  • Отслеживать расходы и доходы 📊\n"
        f"  • Категоризировать финансовые операции 🏷️\n"
        f"  • Анализировать личный бюджет 📈\n"
        f"  • Устанавливать и отслеживать финансовые цели 🎯\n\n"
        f"🔒 Для полноценной работы с вашими данными требуется регистрация и авторизация.\n\n"
        f"👤 Ваш текущий статус:\n"
        f"  Регистрация: {registration_status}\n"
        f"  Авторизация: {authorization_status}\n\n"
        f"➡️ Для начала работы:\n"
        f"  • Если вы здесь впервые, используйте /register для создания аккаунта.\n"
        f"  • Если у вас уже есть аккаунт, используйте /login для входа.\n\n"
        f"ℹ️ Список всех доступных команд можно посмотреть с помощью /help."
    )
    
    await message.answer(welcome_message)