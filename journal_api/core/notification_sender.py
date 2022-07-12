from django.core.mail import send_mail

from solb_expenses_journal import settings


def send_notification_to_email(email_address, topic, message):
    subject = topic
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email_address]
    send_mail(subject, message, email_from, recipient_list)
