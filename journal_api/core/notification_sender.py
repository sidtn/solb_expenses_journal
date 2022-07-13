from decimal import Decimal

from django.core.mail import send_mail
import pendulum
from solb_expenses_journal import settings


def send_notification_to_email(email_address, topic, message):
    subject = topic
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email_address]
    send_mail(subject, message, email_from, recipient_list)


def limit_exceeding_email_sender(expense_instance):
    from journal_api.core.services import TotalExpensesForEmail
    user = expense_instance.owner
    user_email = expense_instance.owner.email
    limits = expense_instance.owner.limits.all().order_by("type")
    month_notification_has_been_sent = False
    for limit in limits:
        currency = limit.currency.code
        if limit.type == "M":
            month_expenses = TotalExpensesForEmail(
                user=user,
                currency=currency,
                start_date=pendulum.now().start_of("month")
            ).get_report()[currency]
            if month_expenses > limit.amount:
                topic = "[Expense journal] Pay attention! Exceeding the monthly spending limit."
                message = f"Your monthly spending limit is {limit.amount} {currency}. You spent {month_expenses} {currency}."
                send_notification_to_email(user_email, topic, message)
                month_notification_has_been_sent = True
            elif month_expenses > limit.amount * limit.notification_percent * Decimal("0.01"):
                topic = f"[Expense journal] You have spent more than {limit.notification_percent}% of the monthly limit."
                message = f"Your monthly spending limit is {limit.amount} {currency}. You spent {month_expenses} {currency}."
                send_notification_to_email(user_email, topic, message)
        if limit.type == "W":
            week_expenses = TotalExpensesForEmail(
                user=user,
                currency=currency,
                start_date=pendulum.now().start_of("week")
            ).get_report()[currency]
            if week_expenses > limit.amount:
                topic = "[Expense journal] Pay attention! Exceeding the weekly spending limit."
                message = f"Your weekly spending limit is {limit.amount} {currency}. You spent {week_expenses} {currency}."
                send_notification_to_email(user_email, topic, message)
            elif week_expenses > limit.amount * limit.notification_percent * Decimal("0.01"):
                topic = f"[Expense journal] You have spent more than {limit.notification_percent}% of the weekly limit."
                message = f"Your weekly spending limit is {limit.amount} {currency}. You spent {week_expenses} {currency}."
                send_notification_to_email(user_email, topic, message)


