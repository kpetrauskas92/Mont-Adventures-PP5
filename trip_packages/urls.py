from django.urls import path
from .views import TripPackages, TripDetails, BookingDrawer


urlpatterns = [
    path('trip_packages/', TripPackages.as_view(), name='trip_packages'),
    path('trip_details/<int:pk>/', TripDetails.as_view(), name='trip_details'),
    path('booking_drawer/<int:trip_id>/', BookingDrawer.as_view(),
         name='booking_drawer'),
]
