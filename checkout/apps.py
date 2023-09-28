from django.apps import AppConfig
from importlib import import_module


class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    def ready(self):
        import_module('checkout.signals')
