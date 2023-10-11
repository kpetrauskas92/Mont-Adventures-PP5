from django.urls import path
from .views import (login_success_view,
                    user_profile,
                    user_bookings,
                    cancel_trip,
                    user_favorites,
                    user_reviews,
                    UserProfileUpdateView)

urlpatterns = [
    path('login_success/', login_success_view, name='login_success'),
    path('profile/', user_profile, name='profile'),
    path('profile/bookings/', user_bookings, name='user_bookings'),
    path('cancel-trip/<int:lineitem_id>/', cancel_trip, name='cancel-trip'),
    path('profile/favorites/', user_favorites, name='user_favorites'),
    path('profile/reviews/', user_reviews, name='user_reviews'),
    path('profile/edit/', UserProfileUpdateView.as_view(),
         name='edit-profile'),
]
