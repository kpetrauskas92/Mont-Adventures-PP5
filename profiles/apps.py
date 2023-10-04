from django.apps import AppConfig
from importlib import import_module


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'
    verbose_name = 'Customers'

    def ready(self):
        import_module('profiles.signals')
