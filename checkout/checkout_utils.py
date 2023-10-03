import stripe
from django.conf import settings
from .forms import OrderForm
from .models import Order, OrderLineItem
from trip_packages.models import Trips, AvailableDate
from django.contrib import messages
from django.shortcuts import get_object_or_404
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from django.core.exceptions import ValidationError
import json


def create_stripe_payment_intent(amount, currency, metadata=None):
    print("create_stripe_payment_intent is being called")
    """
    Create a Stripe Payment Intent with a specified amount,
    currency, and metadata.

    Parameters:
        amount (int): The amount to be charged.
        currency (str): The currency type for the transaction.
        metadata (dict,): Additional metadata to attach to the PaymentIntent.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        metadata=metadata
    )
    return intent


def initialize_order_form(user):
    """
    Initialize the OrderForm with default user information if available.

    Parameters:
        user (User): The authenticated user.
    """
    if user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=user)
            return OrderForm(initial={
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'email': profile.user.email,
            })
        except UserProfile.DoesNotExist:
            return OrderForm()
    else:
        return OrderForm()


def extract_form_data(request):
    """
    Extract data from the POST request for form initialization.

    Parameters:
        request (HttpRequest): The request object.
    """
    data = {
        'first_name': request.POST.get('first_name', None),
        'last_name': request.POST.get('last_name', None),
        'email': request.POST.get('email', ''),
    }

    return data


def validate_order_form(form_data):
    """
    Validate the order form data.

    Parameters:
        form_data (dict): Data to validate using the OrderForm.
    """
    order_form = OrderForm(form_data)
    return order_form.is_valid(), order_form


def create_order(valid, order_form, request, cart, total_price):
    """
    Create an order based on form validity and incoming request data.

    Parameters:
        valid (bool): Whether the form is valid or not.
        order_form (OrderForm): Instance of the OrderForm.
        request (HttpRequest): The request object.
        cart (dict): The cart information.
    """
    if not valid:
        raise ValidationError("Invalid form data")

    order = order_form.save(commit=False)
    pid = request.POST.get('client_secret')

    if pid:
        pid = pid.split('_secret')[0]
    else:
        pid = None

    order.stripe_pid = pid
    order.original_cart = json.dumps(cart)
    order.order_total = total_price
    order.grand_total = total_price
    order.save()
    return order, None


def create_order_line_items(order, cart, request):
    """
    Create line items for the order based on the cart.

    Parameters:
        order (Order): Instance of the Order.
        cart (dict): The cart information.
        request (HttpRequest): The request object.
    """
    for item in cart:
        try:
            trip = Trips.objects.get(id=item['trip_id'])
            available_date = AvailableDate.objects.get(
                id=item['available_date_id'])
            order_line_item = OrderLineItem(
                order=order,
                trip=trip,
                available_date=available_date,
                guests=item['guests'],
            )
            order_line_item.save()
        except (Trips.DoesNotExist, AvailableDate.DoesNotExist):
            messages.error(
                request, "One of the trips in your cart wasn't found "
                "in our database. Please call us for assistance!")
            order.delete()
            return False
    return True


def create_and_validate_order(request, cart):
    """
    Extract form data, validate it, and create an order accordingly.

    Parameters:
        request (HttpRequest): The request object.
        cart (dict): The cart information.
    """
    form_data = extract_form_data(request)
    is_valid, order_form = validate_order_form(form_data)

    if not is_valid:
        messages.error(
            request, 'There was an error with your form. '
            'Please double check your information.')
        return None, order_form

    # Calculate total price here
    total_price = 0
    for item in cart:
        if 'base_price' in item:
            total_price += item['base_price'] * (item['guests'] + 1)

    # Pass the total_price to create_order function
    order, error = create_order(is_valid, order_form,
                                request, cart, total_price)

    if error:
        messages.error(
            request, 'There was an error creating your order. '
            'Please try again.')
        return None, order_form

    if not create_order_line_items(order, cart, request):
        return None, order_form

    return order, None


def handle_successful_checkout(request, order_number):
    """
    Handle the checkout process upon a successful payment.

    Parameters:
        request (HttpRequest): The request object.
        order_number (str): The generated order number.
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            user_profile_form = UserProfileForm(instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()
