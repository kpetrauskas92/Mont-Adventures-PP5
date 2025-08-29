import os
from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        if os.environ.get("AUTO_CREATE_SUPERUSER", "").lower() != "true":
            return
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError, ProgrammingError, IntegrityError
        try:
            User = get_user_model()
            username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or ""
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
            if not username or not password:
                return
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
        except (OperationalError, ProgrammingError, IntegrityError):
            pass
