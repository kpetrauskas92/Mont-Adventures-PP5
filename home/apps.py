import os
from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        if os.environ.get("RUN_GENERATE_DATES", "").lower() != "true":
            return
        from django.core import management
        from django.db.utils import OperationalError, ProgrammingError
        try:
            management.call_command("generate_dates")
        except (OperationalError, ProgrammingError):
            pass
