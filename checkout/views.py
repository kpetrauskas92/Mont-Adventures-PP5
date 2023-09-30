from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse

from .checkout_utils import (
    create_stripe_payment_intent,
    initialize_order_form,
    validate_order_form,
    create_and_validate_order,
    handle_successful_checkout
)
from .models import Order
from cart.cart_utils import get_cart

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    Cache checkout data and modify Stripe PaymentIntent with metadata.

    Parameters:
        request (HttpRequest): The request object containing POST data.
    """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, ('Sorry, your payment cannot be '
                                 'processed right now. Please try '
                                 'again later.'))
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    Render the checkout page and handle the POST request to create an order.

    Parameters:
        request (HttpRequest): The request object.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    cart = get_cart(request)

    # Calculate the total price (including the initial user)
    total_price = 0
    for item in cart:
        if 'base_price' in item:
            total_price += item['base_price'] * (item['guests'] + 1)

    if request.method == 'POST':
        try:
            order, order_form = create_and_validate_order(request, cart)
            if order:
                return redirect(
                    reverse('checkout-success', args=[order.order_number]))
        except stripe.error.StripeError as e:
            messages.error(
                request, ('Sorry, your payment cannot be processed right now. '
                          'Please try again later.'))
            return HttpResponse(content=str(e), status=400)
        except Exception as e:
            messages.error(
                request, ('An error occurred. Please try again later.'))
            return HttpResponse(content=str(e), status=400)
    else:
        if not cart:
            messages.error(
                request, "There's nothing in your cart at the moment")
            return redirect(reverse('cart'))

        order_form = initialize_order_form(request.user)

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'total_price': total_price
    }

    return render(request, 'checkout/checkout.html', context)


@require_POST
def validate_form(request):
    """
    Validate the order form asynchronously and return the result as JSON.

    Parameters:
        request (HttpRequest): The request object containing POST data.
    """
    form_data = {
        'first_name': request.POST.get('first_name'),
        'last_name': request.POST.get('last_name'),
        'email': request.POST.get('email'),
    }

    is_valid, form = validate_order_form(form_data)
    if is_valid:
        return JsonResponse({'is_valid': True})
    else:
        return JsonResponse({'is_valid': False, 'errors': form.errors})


def create_payment_intent(request):
    """
    Create a Stripe PaymentIntent and return the client secret as JSON.

    Parameters:
        request (HttpRequest): The request object.
    """
    try:
        cart = get_cart(request)
        total_price = 0
        for item in cart:
            if 'base_price' in item:
                total_price += item['base_price'] * (item['guests'] + 1)

        if total_price > 0:
            stripe_total = round(total_price * 100)
            intent = create_stripe_payment_intent(
                stripe_total, settings.STRIPE_CURRENCY)
            client_secret = intent.client_secret
            return JsonResponse({'client_secret': client_secret})
        else:
            return JsonResponse({'error': 'Invalid amount.'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def checkout_success(request, order_number):
    """
    Handle successful checkout and render the success page.

    Parameters:
        request (HttpRequest): The request object.
        order_number (str): The order number for the successful order.
    """
    handle_successful_checkout(request, order_number)

    order = get_object_or_404(Order, order_number=order_number)

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout-success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
