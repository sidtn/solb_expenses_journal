import datetime
from decimal import Decimal

import pendulum

from journal_api.core.currency_converter import currency_converter


def total_expenses_by_user_and_period(user, currency, start_date, end_date):
    amount = 0
    expenses = user.expenses.filter(created_at__range=[start_date, end_date])
    for expense in expenses:
        amount_in_currency = round(
            currency_converter(expense.currency.code, currency)
            * expense.amount,
            2,
        )
        amount += amount_in_currency
    return amount


def limits_checker(expense_instance):
    user = expense_instance.owner
    user_email = expense_instance.owner.email
    limits = expense_instance.owner.limits.all().order_by("type")
    for limit in limits:
        currency = limit.currency.code
        if (
            limit.type == "C"
            and limit.custom_end_date >= datetime.date.today()
        ):
            custom_period_expenses = total_expenses_by_user_and_period(
                user=user,
                currency=currency,
                start_date=limit.custom_start_date,
                end_date=limit.custom_end_date,
            )
            if custom_period_expenses > limit.amount:
                topic = "[Expense journal] Pay attention! Exceeding your spending limit."
                message = (
                    f"Your spending limit from {limit.custom_start_date} to {limit.custom_end_date} is "
                    f"{limit.amount} {currency}. You spent {custom_period_expenses} {currency}."
                )
                return {
                    "user_email": user_email,
                    "topic": topic,
                    "message": message,
                }
            elif (
                custom_period_expenses
                > limit.amount * limit.notification_percent * Decimal("0.01")
            ):
                topic = f"[Expense journal] You have spent more than {limit.notification_percent}% of your period limit."
                message = (
                    f"Your spending limit from {limit.custom_start_date} to {limit.custom_end_date} is "
                    f"{limit.amount} {currency}. You spent {custom_period_expenses} {currency}."
                )
                return {
                    "user_email": user_email,
                    "topic": topic,
                    "message": message,
                }
        if limit.type == "M":
            month_expenses = total_expenses_by_user_and_period(
                user=user,
                currency=currency,
                start_date=pendulum.now().start_of("month"),
                end_date=pendulum.now().end_of("month"),
            )
            if month_expenses > limit.amount:
                topic = "[Expense journal] Pay attention! Exceeding the monthly spending limit."
                message = f"Your monthly spending limit is {limit.amount} {currency}. You spent {month_expenses} {currency}."
                return {
                    "user_email": user_email,
                    "topic": topic,
                    "message": message,
                }
            elif (
                month_expenses
                > limit.amount * limit.notification_percent * Decimal("0.01")
            ):
                topic = f"[Expense journal] You have spent more than {limit.notification_percent}% of the monthly limit."
                message = f"Your monthly spending limit is {limit.amount} {currency}. You spent {month_expenses} {currency}."
                return {
                    "user_email": user_email,
                    "topic": topic,
                    "message": message,
                }
        if limit.type == "W":
            week_expenses = total_expenses_by_user_and_period(
                user=user,
                currency=currency,
                start_date=pendulum.now().start_of("week"),
                end_date=pendulum.now().end_of("week"),
            )
            if week_expenses > limit.amount:
                topic = "[Expense journal] Pay attention! Exceeding the weekly spending limit."
                message = f"Your weekly spending limit is {limit.amount} {currency}. You spent {week_expenses} {currency}."
                return {
                    "user_email": user_email,
                    "topic": topic,
                    "message": message,
                }
            elif (
                week_expenses
                > limit.amount * limit.notification_percent * Decimal("0.01")
            ):
                topic = f"[Expense journal] You have spent more than {limit.notification_percent}% of the weekly limit."
                message = f"Your weekly spending limit is {limit.amount} {currency}. You spent {week_expenses} {currency}."
                return {
                    "user_email": user_email,
                    "topic": topic,
                    "message": message,
                }
