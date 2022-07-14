import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "solb_expenses_journal.settings"
)

app = Celery("solb_expenses_journal")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
