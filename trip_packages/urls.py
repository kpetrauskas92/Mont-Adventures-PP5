from django.urls import path
from .views import TripPackages


urlpatterns = [
    path('trip_packages/', TripPackages.as_view(), name='trip_packages'),
]
