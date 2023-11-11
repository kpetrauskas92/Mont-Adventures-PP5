from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.CartView.as_view(), name='cart'),
    path('add/<int:trip_id>/<int:available_date_id>/',
         views.add_to_cart_view, name='add_to_cart'),
    path('update/<int:trip_id>/<int:available_date_id>/',
         views.update_cart_view, name='update_cart_view'),
    path('remove/<int:trip_id>/<int:available_date_id>/',
         views.remove_from_cart_view, name='remove_from_cart_view'),
]
