from django.urls import path
from .views import (TripPackages,
                    TripDetails,
                    trip_overview,
                    BookingDrawer,
                    TripReviews,
                    trip_review_form)


urlpatterns = [
    path('explore/', TripPackages.as_view(), name='trip_packages'),
    path('trip_packages/<int:trip_id>/', TripPackages.as_view(),
         name='trip_with_id'),
    path('trip/<int:pk>/', TripDetails.as_view(), name='trip_details'),
    path('trip_packages/trip_overview/<int:trip_id>/', trip_overview,
         name='trip_overview'),
    path('booking_drawer/<int:trip_id>/', BookingDrawer.as_view(),
         name='booking_drawer'),
    path('trip_packages/trip_reviews/<int:trip_id>/', TripReviews.as_view(),
         name='trip_reviews'),
    path('trip_reviews/<int:trip_id>/<int:review_id>/',
         trip_review_form, name='trip_review_form_with_id'),
    path('trip_review_form/<int:trip_id>/', trip_review_form,
         name='trip_review_form'),
]
