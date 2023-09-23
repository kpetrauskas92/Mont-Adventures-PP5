from django.http import HttpRequest


def get_cart(request_or_session):
    """
    Retrieve the cart from the session. If the cart does not exist,
    an empty list is returned.
    """
    session = request_or_session.session if isinstance(
        request_or_session, HttpRequest) else request_or_session
    return session.get('cart', [])


def add_to_cart(request, trip, available_date, guests=0):
    """
    Add a trip to the cart.

    Parameters:
        request (HttpRequest): The request object.
        trip (Trips): The trip object to add to the cart.
        available_date (AvailableDate): The date object for the trip.
        guests (int, optional): The number of additional guests. Defaults to 0.

    Returns:
        bool: True if the trip was added, False otherwise.
    """
    # Decrement one slot because one is taken by the user who adds the trip
    remaining_slots = available_date.remaining_slots() - 1

    if guests > remaining_slots:
        return False

    cart = get_cart(request)

    for item in cart:
        if item['available_date_id'] == available_date.id:
            return False

    cart_item = {
        'trip_id': trip.id,
        'trip_name': trip.name,
        'trip_image': request.build_absolute_uri(trip.main_image.url),
        'available_date_id': available_date.id,
        'start_date': available_date.start_date.strftime('%Y-%m-%d'),
        'end_date': available_date.end_date.strftime('%Y-%m-%d'),
        'base_price': trip.price,
        'guests': guests,
        'total_price': trip.price * guests
    }
    cart.append(cart_item)
    request.session['cart'] = cart
    return True


def remove_from_cart(request, trip_id, available_date_id):
    """
    Remove a specific trip with a given available_date_id from the cart.

    Parameters:
        request (HttpRequest): The request object.
        trip_id (int): The ID of the trip to remove.
        available_date_id (int): The ID of the available date to remove.
    """
    cart = get_cart(request)
    updated_cart = [item for item in cart if not (
        item['trip_id'] == trip_id
        and item['available_date_id'] == available_date_id
    )]
    request.session['cart'] = updated_cart


def update_cart_item(request, trip_id, available_date_id, guests):
    """
    Update the number of guests for a specific trip in the cart.

    Parameters:
        request (HttpRequest): The request object.
        trip_id (int): The ID of the trip to update.
        available_date_id (int): The ID of the available date to update.
        guests (int): The updated number of guests.
    """
    cart = get_cart(request)
    for item in cart:
        if (
            item['trip_id'] == trip_id and
            item['available_date_id'] == available_date_id
        ):
            item['guests'] = guests
            item['total_price'] = item['base_price'] * guests
    request.session['cart'] = cart


def clear_cart(request):
    """
    Clear all items from the cart.
    """
    request.session['cart'] = []
