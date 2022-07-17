import datetime

from celery import shared_task
from django.core.mail import send_mail

from journal_api.core.limits_checker import (
    check_exceeded_limits,
    message_generator,
)
from journal_api.models import Expense, NotificationOfExceeding
from solb_expenses_journal import settings


@shared_task
def send_notification_to_email():
    notifications = NotificationOfExceeding.objects.filter(is_sent=False)
    for notification in notifications:
        subject = message_generator(notification)[0]
        message = message_generator(notification)[1]
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [notification.limit.owner.email]
        send_mail(
            subject, message, email_from, recipient_list, fail_silently=False
        )
        notification.is_sent = True
        notification.save()


@shared_task
def record_notification_to_base():
    expenses = Expense.objects.filter(
        created_at__gte=datetime.datetime.now()
        - datetime.timedelta(minutes=10)
    ).distinct("owner")
    for expense in expenses:
        check_exceeded_limits(expense)
