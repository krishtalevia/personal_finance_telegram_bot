import datetime
from aiogram import Router, types
from aiogram.filters import Command, StateFilter

from model import DatabaseManager

router = Router()
db_manager = DatabaseManager()

PERIODS = {
    "день": "day",
    "неделя": "week",
    "месяц": "month",
    "год": "year",
}

def get_date_range_for_period(period_keyword, reference_date=None):
    if reference_date is None:
        current_date = datetime.date.today()
    else:
        current_date = reference_date
        
    period_start = None
    
    if period_keyword == "day":
        period_start = current_date
        period_end = current_date
    
    elif period_keyword == "week":
        period_start = current_date - datetime.timedelta(days=current_date.weekday())
        period_end = period_start + datetime.timedelta(days=6)
    
    elif period_keyword == "month":
        period_start = current_date.replace(day=1)
        next_month = period_start.replace(day=28) + datetime.timedelta(days=4)
        period_end = next_month - datetime.timedelta(days=next_month.day)
    
    elif period_keyword == "year":
        period_start = current_date.replace(month=1, day=1)
        period_end = current_date.replace(month=12, day=31)
    
    if period_start and period_end:
        return period_start.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d')
    return None, None

def get_previous_period_reference_date(period_keyword, current_period_start_date):
    if period_keyword == "day":
        return current_period_start_date - datetime.timedelta(days=1)
    
    elif period_keyword == "week":
        return current_period_start_date - datetime.timedelta(weeks=1)
    
    elif period_keyword == "month":

        prev_month_approx = current_period_start_date - datetime.timedelta(days=5) # مثلا
        return prev_month_approx.replace(day=1)
    
    elif period_keyword == "year":
        return current_period_start_date.replace(year=current_period_start_date.year - 1)
    return None

@router.message(Command('statistics'))
async def statistics_handler(message: types.Message):
    telegram_id = message.from_user.id

    user = db_manager.get_user(telegram_id)
    if not user:
        await message.answer('❌ Вы не зарегистрированы. Используйте команду /register для регистрации.')
        return
    
    if not db_manager.is_user_authorized(telegram_id):
        await message.answer('❌ Вы не авторизованы. Используйте команду /login для авторизации.')
        return
    
    args_str = message.get_args()
    args_list = args_str.split() if args_str else []

    current_period_keyword = "month" 
    current_period_display_name = "Текущий месяц" 
    today_date = datetime.date.today()

    if args_list:
        potential_period_arg = args_list[0].lower()
        if potential_period_arg in PERIODS:
            current_period_keyword = PERIODS[potential_period_arg]
            for display, keyword_val in PERIODS.items():
                if keyword_val == current_period_keyword:
                    current_period_display_name = display.capitalize()
                    break

    current_period_start_str, current_period_end_str = get_date_range_for_period(current_period_keyword, today_date)

    if not current_period_start_str or not current_period_end_str:
        await message.answer("⚠️ Не удалось определить текущий период для статистики.")
        return
    
    try:
        current_transactions = db_manager.get_transactions(
            telegram_id, 
            period_start_str=current_period_start_str, 
            period_end_str=current_period_end_str
        )
    except Exception as e:
        await message.answer("❌ Произошла ошибка при получении транзакций (текущий период).")
        return
    
    current_total_income = 0.0
    current_total_expense = 0.0
    current_incomes_by_category = {} 
    current_expenses_by_category = {} 

    if transactions:
        for tr in transactions:
            tr_type = tr[1] 
            tr_amount = tr[2]
            tr_category = tr[3]
            
            if tr_type == 'income':
                total_income += tr_amount
                incomes_by_category[tr_category] = incomes_by_category.get(tr_category, 0) + tr_amount
            elif tr_type == 'expense':
                total_expense += tr_amount
                expenses_by_category[tr_category] = expenses_by_category.get(tr_category, 0) + tr_amount
    
    net_balance = total_income - total_expense

    response_lines = [
        f"📊 Статистика за период: {period_display_name} ({period_start_str} - {period_end_str})\n",
        f"🟢 Общий доход: {total_income:.2f}",
        f"🔴 Общий расход: {total_expense:.2f}",
        f"⚖️ Чистый баланс: {net_balance:.2f}"
    ]

    if expenses_by_category:
        response_lines.append("\n📈 Структура расходов:")
        
        sorted_expenses = sorted(expenses_by_category.items(), key=lambda item: item[1], reverse=True)
        for category, amount in sorted_expenses:
            percentage = (amount / total_expense) * 100 if total_expense > 0 else 0
            response_lines.append(f"  - {category}: {amount:.2f} ({percentage:.1f}%)")
    else:
        if total_expense == 0 and transactions:
             response_lines.append("\n📈 Расходов за период не было.")

    if incomes_by_category:
        response_lines.append("\n📉 Структура доходов:")
        
        sorted_incomes = sorted(incomes_by_category.items(), key=lambda item: item[1], reverse=True)
        for category, amount in sorted_incomes:
            percentage = (amount / total_income) * 100 if total_income > 0 else 0
            response_lines.append(f"  - {category}: {amount:.2f} ({percentage:.1f}%)")
    else:
        if total_income == 0 and transactions:
            response_lines.append("\n📉 Доходов за период не было.")

    if not transactions:
        response_lines.append("\n🤷 Транзакций за указанный период не найдено.")
        response_lines = [
            f"📊 Статистика за период: {period_display_name} ({period_start_str} - {period_end_str})\n",
            "🤷 Транзакций за указанный период не найдено."
        ]

    try:
        active_goals = db_manager.get_financial_goals(telegram_id, status='active')
        if active_goals:
            response_lines.append("\n🎯 Прогресс по активным финансовым целям:")
            for goal in active_goals:
        
                goal_desc = goal[1]
                goal_target = goal[2]
                goal_current = goal[3]

                progress_percent = 0.0
                if goal_target > 0:
                    progress_percent = (goal_current / goal_target) * 100.0
                
                progress_percent = min(progress_percent, 100.0) 

                line = f"  - {goal_desc}: {goal_current:.2f} / {goal_target:.2f} ({progress_percent:.1f}%)"
                if goal_current >= goal_target:
                    line += " ✅ Цель достигнута!"
                response_lines.append(line)
            else: 
                response_lines.append("\n🎯 Активных финансовых целей нет.")

    except Exception as e_goals:
        response_lines.append("\n⚠️ Не удалось загрузить информацию о финансовых целях.")

    
    await message.answer("\n".join(response_lines))