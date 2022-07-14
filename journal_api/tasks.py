from celery import shared_task
from django.core.mail import send_mail

from solb_expenses_journal import settings


@shared_task
def send_notification_to_email(data_dict):
    subject = data_dict["topic"]
    message = data_dict["message"]
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [data_dict["user_email"]]
    send_mail(
        subject, message, email_from, recipient_list, fail_silently=False
    )
