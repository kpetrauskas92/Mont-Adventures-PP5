from django.test import TestCase, Client
from django.urls import reverse
from trip_packages.models import Trips, AvailableDate
from cart.cart_utils import get_cart


class CartViewTests(TestCase):

    def setUp(self):
        """
        Setup test environment.
        """
        self.client = Client()
        self.cart_url = reverse('cart')

        session = self.client.session
        session['some_key'] = 'some_value'
        session.save()

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
            start_date='2023-01-01',
            end_date='2023-01-10',
            max_group_size=5,
            booked_slots=0,
            is_available=True
        )

        self.date2 = AvailableDate.objects.create(
            id=2,
            trips=self.trip2,
            start_date='2023-02-01',
            end_date='2023-02-10',
            max_group_size=6,
            booked_slots=1,
            is_available=True
        )

    def test_CartView_GET(self):
        """
        Tests that the CartView returns a 200 OK status code
        and uses the 'cart.html' template.
        """
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_add_to_cart_view(self):
        """
        Tests that adding an item to the cart redirects to the cart page,
        and that the cart is no longer empty.
        """
        add_cart_url = reverse(
            'add_to_cart', args=[self.trip1.id, self.date1.id])
        response = self.client.get(add_cart_url)
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(get_cart(self.client.session), [])

    def test_update_cart_view(self):
        """
        Tests that updating the cart successfully redirects to the cart page.
        """
        update_cart_url = reverse(
            'update_cart_view', args=[self.trip1.id, self.date1.id])
        response = self.client.post(update_cart_url, {'guests': 2})
        self.assertEqual(response.status_code, 302)

    def test_remove_from_cart_view(self):
        """
        Tests that removing an item from the cart redirects to the cart page,
        and that the cart is empty afterward.
        """
        remove_cart_url = reverse(
            'remove_from_cart_view', args=[self.trip1.id, self.date1.id])
        response = self.client.get(remove_cart_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_cart(self.client.session), [])

    def test_clear_cart_view(self):
        """
        Tests that clearing the cart redirects to the cart page,
        and that the cart is empty afterward.
        """
        clear_cart_url = reverse('clear_cart_view')
        response = self.client.get(clear_cart_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_cart(self.client.session), [])
