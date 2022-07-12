from django.apps import AppConfig


class JournalApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "journal_api"

    def ready(self):
        from . import signals
