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
    period_end = None
    
    if period_keyword == "day":
        period_start = current_date
        period_end = current_date
    
    elif period_keyword == "week":
        period_start = current_date - datetime.timedelta(days=current_date.weekday())
        period_end = period_start + datetime.timedelta(days=6)
    
    elif period_keyword == "month":
        period_start = current_date.replace(day=1)
        next_month_start = (period_start.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        period_end = next_month_start - datetime.timedelta(days=1)
    
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
        first_day_current_month = current_period_start_date.replace(day=1)
        last_day_prev_month = first_day_current_month - datetime.timedelta(days=1)
        return last_day_prev_month
    
    elif period_keyword == "year":
        return current_period_start_date.replace(year=current_period_start_date.year - 1, month=1, day=1)
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
    
    current_transactions = []
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

    if current_transactions:
        for tr in current_transactions:
            tr_type, tr_amount, tr_category = tr[1], tr[2], tr[3]
            
            if tr_type == 'income':
                current_total_income += tr_amount
                current_incomes_by_category[tr_category] = current_incomes_by_category.get(tr_category, 0) + tr_amount
            
            elif tr_type == 'expense':
                current_total_expense += tr_amount
                current_expenses_by_category[tr_category] = current_expenses_by_category.get(tr_category, 0) + tr_amount
    
    current_net_balance = current_total_income - current_total_expense

    current_period_start_date_obj = datetime.datetime.strptime(current_period_start_str, '%Y-%m-%d').date()
    prev_period_ref_date = get_previous_period_reference_date(current_period_keyword, current_period_start_date_obj)
    
    previous_period_start_str, previous_period_end_str = None, None
    prev_transactions = []
    prev_total_income = 0.0
    prev_total_expense = 0.0
    prev_incomes_by_category = {}
    prev_expenses_by_category = {}

    if prev_period_ref_date:
        previous_period_start_str, previous_period_end_str = get_date_range_for_period(current_period_keyword, prev_period_ref_date)
        if previous_period_start_str and previous_period_end_str:
            try:
                prev_transactions = db_manager.get_transactions(
                    telegram_id,
                    period_start_str=previous_period_start_str,
                    period_end_str=previous_period_end_str
                )
                if prev_transactions:
                    for tr in prev_transactions:
                        tr_type, tr_amount, tr_category = tr[1], tr[2], tr[3]
                        
                        if tr_type == 'income':
                            prev_total_income += tr_amount
                            prev_incomes_by_category[tr_category] = prev_incomes_by_category.get(tr_category, 0) + tr_amount
                        
                        elif tr_type == 'expense':
                            prev_total_expense += tr_amount
                            prev_expenses_by_category[tr_category] = prev_expenses_by_category.get(tr_category, 0) + tr_amount
            except Exception as e:
                pass 

    response_lines = [
        f"📊 Статистика за период: {current_period_display_name} ({current_period_start_str} - {current_period_end_str})\n",
        f"🟢 Общий доход: {current_total_income:.2f}",
        f"🔴 Общий расход: {current_total_expense:.2f}",
        f"⚖️ Чистый баланс: {current_net_balance:.2f}"
    ]

    sorted_expenses, sorted_incomes = [], []
    if current_expenses_by_category:
        response_lines.append("\n📈 Структура расходов (текущий период):")
        sorted_expenses = sorted(current_expenses_by_category.items(), key=lambda item: item[1], reverse=True)
        
        for category, amount in sorted_expenses:
            percentage = (amount / current_total_expense) * 100 if current_total_expense > 0 else 0
            response_lines.append(f"  - {category}: {amount:.2f} ({percentage:.1f}%)")

    if current_incomes_by_category:
        response_lines.append("\n📉 Структура доходов (текущий период):")
        sorted_incomes = sorted(current_incomes_by_category.items(), key=lambda item: item[1], reverse=True)
        
        for category, amount in sorted_incomes:
            percentage = (amount / current_total_income) * 100 if current_total_income > 0 else 0
            response_lines.append(f"  - {category}: {amount:.2f} ({percentage:.1f}%)")

    if sorted_expenses:
        response_lines.append(f"\n🏆 Топ-{3} категории расходов:")
        for i, (category, amount) in enumerate(sorted_expenses[:3]):
            percentage = (amount / current_total_expense) * 100 if current_total_expense > 0 else 0
            response_lines.append(f"  {i+1}. {category}: {amount:.2f} ({percentage:.1f}%)")
    
    if sorted_incomes:
        response_lines.append(f"\n💰 Топ-{3} категории доходов:")
        for i, (category, amount) in enumerate(sorted_incomes[:3]):
            percentage = (amount / current_total_income) * 100 if current_total_income > 0 else 0
            response_lines.append(f"  {i+1}. {category}: {amount:.2f} ({percentage:.1f}%)")
    
    if prev_period_ref_date and previous_period_start_str:
        response_lines.append(f"\n🔄 Тренды (сравнение с предыдущим {current_period_display_name.lower()}):")
        
        income_change = current_total_income - prev_total_income
        income_change_percent_str = "-"
        
        if prev_total_income != 0:
            income_change_percent = (income_change / prev_total_income) * 100
            income_change_percent_str = f"{income_change_percent:+.1f}%"
        response_lines.append(f"  Доходы: {current_total_income:.2f} (было {prev_total_income:.2f}, изм: {income_change:+.2f}, {income_change_percent_str})")

        expense_change = current_total_expense - prev_total_expense
        expense_change_percent_str = "-"
        
        if prev_total_expense != 0:
            expense_change_percent = (expense_change / prev_total_expense) * 100
            expense_change_percent_str = f"{expense_change_percent:+.1f}%"
        response_lines.append(f"  Расходы: {current_total_expense:.2f} (было {prev_total_expense:.2f}, изм: {expense_change:+.2f}, {expense_change_percent_str})")
    
        all_expense_categories = set(current_expenses_by_category.keys()) | set(prev_expenses_by_category.keys())
        if all_expense_categories:
            response_lines.append(f"\n🔍 Сравнение категорий расходов (с предыдущим {current_period_display_name.lower()}):")
            for category in sorted(list(all_expense_categories)):
                current_amount = current_expenses_by_category.get(category, 0.0)
                prev_amount = prev_expenses_by_category.get(category, 0.0)
                change = current_amount - prev_amount
                change_percent_str = "-"
                if prev_amount != 0:
                    change_percent = (change / prev_amount) * 100
                    change_percent_str = f"{change_percent:+.1f}%"
                
                response_lines.append(f"  - {category}: {current_amount:.2f} (было {prev_amount:.2f}, изм: {change:+.2f}, {change_percent_str})")

        
        all_income_categories = set(current_incomes_by_category.keys()) | set(prev_incomes_by_category.keys())
        if all_income_categories:
            response_lines.append(f"\n🔍 Сравнение категорий доходов (с предыдущим {current_period_display_name.lower()}):")
            for category in sorted(list(all_income_categories)):
                current_amount = current_incomes_by_category.get(category, 0.0)
                prev_amount = prev_incomes_by_category.get(category, 0.0)
                change = current_amount - prev_amount
                change_percent_str = "-"
                if prev_amount != 0:
                    change_percent = (change / prev_amount) * 100
                    change_percent_str = f"{change_percent:+.1f}%"
                response_lines.append(f"  - {category}: {current_amount:.2f} (было {prev_amount:.2f}, изм: {change:+.2f}, {change_percent_str})")

    active_goals = []
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