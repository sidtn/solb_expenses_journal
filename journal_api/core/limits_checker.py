import datetime
from decimal import Decimal

import pendulum
from django.db.utils import IntegrityError

from journal_api.core.currency_converter import currency_converter
from journal_api.models import NotificationOfExceeding


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


def check_exceeded_limits(expense_instance):
    user = expense_instance.owner
    limits = expense_instance.owner.limits.all().order_by("type")
    now = pendulum.now()
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
            if (
                custom_period_expenses
                > limit.amount * limit.notification_percent * Decimal("0.01")
            ):
                try:
                    NotificationOfExceeding.objects.create(
                        limit=limit, exceeding=custom_period_expenses
                    )
                except IntegrityError:
                    pass
        if limit.type == "M":
            month_expenses = total_expenses_by_user_and_period(
                user=user,
                currency=currency,
                start_date=now.start_of("month"),
                end_date=now.end_of("month"),
            )
            if (
                month_expenses
                > limit.amount * limit.notification_percent * Decimal("0.01")
            ):
                try:
                    NotificationOfExceeding.objects.create(
                        limit=limit, exceeding=month_expenses
                    )
                except IntegrityError:
                    pass
        if limit.type == "W":
            week_expenses = total_expenses_by_user_and_period(
                user=user,
                currency=currency,
                start_date=now.start_of("week"),
                end_date=now.end_of("week"),
            )
            if (
                week_expenses
                > limit.amount * limit.notification_percent * Decimal("0.01")
            ):
                try:
                    NotificationOfExceeding.objects.create(
                        limit=limit, exceeding=week_expenses
                    )
                except IntegrityError:
                    pass


def message_generator(notification_instance):
    currency = notification_instance.limit.currency.code
    limit_expenses = notification_instance.limit.amount
    current_expenses = notification_instance.exceeding
    if notification_instance.limit.type == "C":
        start_date = notification_instance.limit.custom_start_date
        end_date = notification_instance.limit.custom_end_date
        message = (
            f"Your spending limit from {start_date} to {end_date} is {limit_expenses} {currency}."
            f" You spent {current_expenses} {currency}."
        )
        if current_expenses > limit_expenses:
            topic = "[Expense journal] Pay attention! Exceeding your spending limit."
        else:
            topic = (
                f"[Expense journal] You have spent more than "
                f"{notification_instance.limit.notification_percent}% of your period limit."
            )
        return topic, message
    elif notification_instance.limit.type == "M":
        message = (
            f"Your monthly spending limit is {limit_expenses} {currency}."
            f" You spent {current_expenses} {currency}."
        )
        if current_expenses > limit_expenses:
            topic = "[Expense journal] Pay attention! Exceeding the monthly spending limit."
        else:
            topic = (
                f"[Expense journal] You have spent more than"
                f" {notification_instance.limit.notification_percent}% of the monthly limit."
            )
        return topic, message
    elif notification_instance.limit.type == "W":
        message = f"Your weekly spending limit is {limit_expenses} {currency}. You spent {current_expenses} {currency}."
        if current_expenses > limit_expenses:
            topic = "[Expense journal] Pay attention! Exceeding the weekly spending limit."
        else:
            topic = (
                f"[Expense journal] You have spent more than"
                f" {notification_instance.limit.notification_percent}% of the weekly limit."
            )
        return topic, message
