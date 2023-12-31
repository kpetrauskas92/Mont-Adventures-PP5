from django.urls import path
from .views import (login_success_view,
                    user_profile,
                    delete_user_profile,
                    user_bookings,
                    cancel_trip,
                    user_favorites,
                    user_reviews,
                    edit_review,
                    delete_review,
                    UserProfileUpdateView
                    )

urlpatterns = [
    path('login_success/', login_success_view, name='login_success'),
    path('profile/', user_profile, name='profile'),
    path('profile/delete', delete_user_profile, name='delete_user_profile'),
    path('profile/bookings/', user_bookings, name='user_bookings'),
    path('cancel-trip/<int:lineitem_id>/', cancel_trip, name='cancel-trip'),
    path('profile/favorites/', user_favorites, name='user_favorites'),
    path('profile/reviews/', user_reviews, name='user_reviews'),
    path('edit_review/<int:review_id>/', edit_review, name='edit_review'),
    path('delete_review/<int:review_id>/', delete_review,
         name='delete_review'),
    path('profile/edit/', UserProfileUpdateView.as_view(),
         name='edit-profile'),
]
