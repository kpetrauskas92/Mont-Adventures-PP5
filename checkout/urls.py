from django.urls import path
from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout-success/<order_number>',
         views.checkout_success,
         name='checkout-success'),
    path('cache_checkout_data/',
         views.cache_checkout_data,
         name='cache_checkout_data'),
    path('create_payment_intent/',
         views.create_payment_intent,
         name='create_payment_intent'),
    path('checkout/validate_form/',
         views.validate_form,
         name='validate_form'),
    path('wh/', webhook, name='webhook'),
]
