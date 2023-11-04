from django.urls import path
from . import views
from .views import subscribe_to_newsletter

urlpatterns = [
    path('', views.index, name='home'),
    path('search/', views.search_trips, name='search_trips'),
    path('subscribe_to_newsletter/', subscribe_to_newsletter,
         name='subscribe_to_newsletter'),
]
