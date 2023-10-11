from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .forms import UserProfileForm
from .models import UserProfile, FavoriteTrip, Reviews
from checkout.models import Order, OrderLineItem
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse


def login_success_view(request):
    response = render(request, 'account/login_success.html')
    return response


@login_required
def user_profile(request):
    """Display the user's profile.

    This view fetches the logged-in user's profile and orders, and renders them
    on the profile page.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.filter(
        user_profile=request.user.userprofile).order_by('-id')
    for order in orders:
        order.non_canceled_lineitems = order.lineitems.exclude(
            status='canceled')
    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'profile.html', context)


@login_required
def user_bookings(request):
    """Display the user's bookings.

    This view fetches the logged-in user's orders and displays them
    on the bookings page.
    """
    orders = Order.objects.filter(
        user_profile=request.user.userprofile).order_by('-id')
    for order in orders:
        order.non_canceled_lineitems = order.lineitems.exclude(
            status='canceled')
    context = {
        'orders': orders
    }
    return render(request, 'includes/user-bookings.html', context)


@login_required
def cancel_trip(request, lineitem_id):
    """Cancel a booked trip."""
    lineitem = get_object_or_404(OrderLineItem, id=lineitem_id)

    start_date = lineitem.available_date.start_date
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    can_cancel = (
        (lineitem.available_date.start_date - timezone.now().date()) >
        timedelta(days=14)
    )

    if request.method == 'POST' and can_cancel:
        # Update the line item status to 'canceled'
        lineitem.status = 'canceled'
        lineitem.save()

        # Update the total amount for the Order
        order = lineitem.order
        order.grand_total -= lineitem.lineitem_total
        order.save()

        # Update the booked slots for the trip
        available_date = lineitem.available_date
        available_date.booked_slots -= lineitem.guests
        available_date.save()

        messages.success(request, 'Trip canceled successfully.')

        return redirect('profile')

    return render(
        request, 'includes/cancel-trip.html',
        {'lineitem': lineitem, 'can_cancel': can_cancel})


@login_required
def user_favorites(request):
    """Display the user's favorite trips.

    This view fetches the logged-in user's favorite trips and renders them
    on the favorites page.
    """
    favorite_trips = FavoriteTrip.objects.filter(
        user=request.user).select_related('trip')
    context = {
        'favorite_trips': favorite_trips
    }
    return render(request, 'includes/user-favorites.html', context)


@login_required
def user_reviews(request):
    """Display the user's reviews.

    This view fetches the logged-in user's reviews and renders them
    on the reviews page.
    """
    reviews = Reviews.objects.filter(user=request.user).select_related('trip')
    context = {
        'reviews': reviews
    }
    return render(request, 'includes/user-reviews.html', context)


@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(UpdateView):
    """Class-based view for updating user profile.

    This class provides methods for rendering the edit-profile page and
    updating the user's profile.

    Attributes:
        model: UserProfile model.
        form_class: The form class to use for validation.
        template_name: The template to render.
        success_url: URL to redirect after successful update.
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'edit-profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        """
        Get the current user's profile to edit.
        """
        return UserProfile.objects.get(user=self.request.user)

    def form_valid(self, form):
        """
        Perform actions on a valid form submission.
        """
        form.instance.user = self.request.user
        form.save()
        if self.request.headers.get('HX-Request') == 'true':
            return JsonResponse({'form_valid': True}, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Perform actions on an invalid form submission.
        """
        return super().form_invalid(form)
