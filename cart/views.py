from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views import View
from trip_packages.models import Trips, AvailableDate
from .cart_utils import (
    add_to_cart,
    remove_from_cart,
    update_cart_item,
    get_cart,
    clear_cart
)


class CartView(View):
    """
    Renders the cart page which shows all the items in the cart,
    along with the subtotal and total price.

    - Fetches the cart from the session.
    - Updates the remaining slots for each item.
    - Calculates the subtotal and total price.
    """
    template_name = 'cart.html'

    def get(self, request):
        cart = get_cart(request)
        subtotal = 0
        for item in cart:
            available_date = AvailableDate.objects.get(
                id=item['available_date_id'])
            # Deduct one slot for the user who added the trip to the cart
            item['remaining_slots'] = max(
                available_date.remaining_slots() - 1, 0)

            if 'base_price' in item:
                item['total_price'] = item['base_price'] * (item['guests'] + 1)

                subtotal += item['total_price']

        total = subtotal
        return render(request, self.template_name,
                      {'cart': cart, 'subtotal': subtotal, 'total': total})


def add_to_cart_view(request, trip_id, available_date_id):
    """
    Adds a trip to the cart and redirects back to the cart page.

    - Fetches the trip and available date using the provided IDs.
    - Adds the trip to the cart using `add_to_cart()` utility function.
    - Redirects to the cart page.
    """
    trip = get_object_or_404(Trips, id=trip_id)
    available_date = get_object_or_404(AvailableDate, id=available_date_id)
    cart, cart_total_items = add_to_cart(request, trip, available_date)

    response = HttpResponse()

    if cart is None:
        cart, cart_total_items = get_cart(request), len(get_cart(request))

        messages.warning(request, 'This date is already in your cart.')

        if 'HX-Request' in request.headers:
            response['HX-Item-Already-In-Cart'] = 'true'
            cart_html = render_to_string('includes/cart-items.html', {
                'cart': cart,
                'cart_total_items': cart_total_items,
                'messages': messages.get_messages(request)
            })
            response.content = cart_html
            return response
        else:
            return redirect('cart')

    else:
        messages.success(request, 'Trip added to cart')

        if 'HX-Request' in request.headers:
            response['HX-Item-Added'] = 'true'
            cart_html = render_to_string('includes/cart-items.html', {
                'cart': cart,
                'cart_total_items': cart_total_items,
                'messages': messages.get_messages(request)
            })
            response.content = cart_html
            return response

    return redirect('cart')


def update_cart_view(request, trip_id, available_date_id):
    """
    Updates the number of guests for a particular item in the cart.

    - Fetches the available date using the provided ID.
    - Checks if the number of guests exceeds the remaining slots.
    - Updates the cart item using `update_cart_item()` utility function.
    """
    available_date = get_object_or_404(AvailableDate, id=available_date_id)
    remove_all = request.POST.get('remove_all', None)
    guests = int(request.POST.get('guests', 1))

    if remove_all:
        guests = 0
        messages.success(request, 'All additional guests removed.')
    else:
        available_date = get_object_or_404(AvailableDate, id=available_date_id)
        if guests > available_date.remaining_slots():
            return JsonResponse(
                {'error': 'Number of guests exceeds the remaining slots'},
                status=400)
        messages.success(request, 'Additional guests added.')

    update_cart_item(request, trip_id, available_date_id, guests)

    if 'HX-Request' in request.headers:

        return JsonResponse({'status': 'success', 'guests': guests})

    return redirect('cart')


def remove_from_cart_view(request, trip_id, available_date_id):
    """
    Removes a trip from the cart.

    - Removes the trip from the cart using
    `remove_from_cart()` utility function.
    - Redirects to the cart page or returns the updated cart
    HTML if it's an HTMX request.
    """
    remove_from_cart(request, trip_id, available_date_id)
    messages.success(request, 'Trip removed from cart')

    # Check if the request is from HTMX
    if 'HX-Request' in request.headers:
        cart_html = render_to_string('includes/cart-items.html', {
            'cart': get_cart(request),
            'messages': messages.get_messages(request)
        })
        return HttpResponse(cart_html)

    return redirect('cart')


def clear_cart_view(request):
    """
    Clears all items from the cart.

    - Clears the cart using `clear_cart()` utility function.
    - Redirects to the cart page.
    """
    clear_cart(request)
    return redirect('cart')
