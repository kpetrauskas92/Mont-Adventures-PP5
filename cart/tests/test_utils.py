from django.test import TestCase
from django.urls import reverse
from trip_packages.models import Trips, AvailableDate
from django.test.client import RequestFactory
from datetime import date
from cart.cart_utils import (
    get_cart,
    add_to_cart,
    remove_from_cart,
    update_cart_item,
    clear_cart)


class CartUtilsTests(TestCase):
    """
    Test cases for cart utilities in cart_utils.py.

    - Tests getting an empty cart.
    - Tests adding to the cart.
    - Tests removing from the cart.
    - Tests updating cart items.
    - Tests clearing the cart.
    """
    def setUp(self):
        """
        Setup test environment.
        """
        self.factory = RequestFactory()

        # Create mock data for Trips and AvailableDate models
        self.trip1 = Trips.objects.create(
            id=1,
            name="Trip 1",
            price=100,
            duration=3,
            location="Location 1",
            season=[1, 2],
            max_group_size=5,
            overall_rating=4.5,
            difficulty=2
        )
        self.trip2 = Trips.objects.create(
            id=2,
            name="Trip 2",
            price=200,
            duration=4,
            location="Location 2",
            season=[3, 4],
            max_group_size=6,
            overall_rating=4.0,
            difficulty=3
        )

        self.date1 = AvailableDate.objects.create(
            id=1,
            trips=self.trip1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
            max_group_size=5,
            booked_slots=0,
            is_available=True
        )
        self.date2 = AvailableDate.objects.create(
            id=2,
            trips=self.trip2,
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 10),
            max_group_size=6,
            booked_slots=1,
            is_available=True
        )

    def create_request_with_session(self):
        """
        Utility function to create a request object with an empty session.
        """
        request = self.factory.get(reverse('cart'))
        request.session = {}
        return request

    def test_get_empty_cart(self):
        """
        Tests that an empty cart is correctly retrieved from the session.
        """
        request = self.create_request_with_session()
        self.assertEqual(get_cart(request), [])

    def test_add_to_cart(self):
        """
        Tests that an item can be successfully added to the cart,
        and that the cart is no longer empty afterward.
        """
        request = self.create_request_with_session()
        result = add_to_cart(request, self.trip1, self.date1, guests=2)
        self.assertTrue(result)
        self.assertNotEqual(get_cart(request), [])

    def test_remove_from_cart(self):
        """
        Tests that an item can be successfully removed from the cart,
        and that the cart is empty afterward.
        """
        request = self.create_request_with_session()
        add_to_cart(request, self.trip1, self.date1, guests=2)
        remove_from_cart(request, self.trip1.id, self.date1.id)
        self.assertEqual(get_cart(request), [])

    def test_update_cart_item(self):
        """
        Tests that the number of guests for an item in the cart
        can be successfully updated.
        """
        request = self.create_request_with_session()
        add_to_cart(request, self.trip1, self.date1, guests=2)
        update_cart_item(request, self.trip1.id, self.date1.id, guests=3)
        cart = get_cart(request)
        self.assertEqual(cart[0]['guests'], 3)

    def test_clear_cart(self):
        """
        Tests that all items can be successfully removed from the cart,
        and that the cart is empty afterward.
        """
        request = self.create_request_with_session()
        add_to_cart(request, self.trip1, self.date1, guests=2)
        add_to_cart(request, self.trip2, self.date2, guests=2)
        clear_cart(request)
        self.assertEqual(get_cart(request), [])
