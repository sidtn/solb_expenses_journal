from decimal import Decimal

from django.db.models import signals
from django.dispatch import receiver

from journal_api.models import Expense, Limit, User
from journal_api.core.services import TotalExpensesForEmail
from journal_api.core.notification_sender import send_notification_to_email
import pendulum


@receiver(signals.post_save, sender=Expense)
def send_mail_if_over_limit(sender, instance, created, **kwargs):
    user = instance.owner
    user_email = instance.owner.email
    currency = instance.owner.limit.currency.code
    limit_per_week = instance.owner.limit.limit_per_week
    limit_per_month = instance.owner.limit.limit_per_month
    today = pendulum.now()
    week_start = today.start_of("week")
    month_start = today.start_of("month")
    month_expenses = TotalExpensesForEmail(user=user, currency=currency, start_date=month_start).get_report()[currency]
    if month_expenses > limit_per_month:
        topic = "[Expense journal] Pay attention! Exceeding the monthly spending limit."
        message = f"Your monthly spending limit is {limit_per_month} {currency}. You spent {month_expenses} {currency}."
        send_notification_to_email(user_email, topic, message)
    elif month_expenses > limit_per_month * Decimal("0.8"):
        topic = "[Expense journal] You have spent more than 80% of the monthly limit."
        message = f"Your monthly spending limit is {limit_per_month} {currency}. You spent {month_expenses} {currency}."
        send_notification_to_email(user_email, topic, message)
    else:
        week_expenses = TotalExpensesForEmail(user=user, currency=currency, start_date=week_start).get_report()[currency]
        if week_expenses > limit_per_week:
            topic = "[Expense journal] Pay attention! Exceeding the weekly spending limit."
            message = f"Your weekly spending limit is {limit_per_week} {currency}. You spent {week_expenses} {currency}."
            send_notification_to_email(user_email, topic, message)
        elif week_expenses > limit_per_week * Decimal("0.8"):
            topic = "[Expense journal] You have spent more than 80% of the weekly limit."
            message = f"Your weekly spending limit is {limit_per_week} {currency}. You spent {week_expenses} {currency}."
            send_notification_to_email(user_email, topic, message)


@receiver(signals.post_save, sender=User)
def create_limits_if_user_created(sender, instance, created, **kwargs):
    Limit.objects.create(owner=instance)
