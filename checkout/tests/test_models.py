from django.test import TestCase
from django.contrib.auth.models import User
from django_countries.fields import Country
from checkout.models import Order, OrderLineItem
from profiles.models import UserProfile
from trip_packages.models import Trips, AvailableDate
from datetime import date


class CheckoutModelTests(TestCase):

    def setUp(self):
        """
        Set up common test data and state across test methods.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.trip = Trips.objects.create(
            name="Trip 1",
            price=100,
            duration=3,
            location="Location 1",
            season=[1, 2],
            max_group_size=5,
            overall_rating=4.5,
            difficulty=2
        )

        self.available_date = AvailableDate.objects.create(
            trips=self.trip,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 10),
            max_group_size=5,
            booked_slots=0,
            is_available=True
        )

        self.order = Order.objects.create(
            user_profile=self.user_profile,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            country='US',
            stripe_pid='test_stripe_pid'
        )

        self.order_line_item = OrderLineItem.objects.create(
            order=self.order,
            trip=self.trip,
            available_date=self.available_date,
            guests=2
        )

    def test_order_model(self):
        """
        Test the Order model for correct data types and field values.

        This test checks that an Order instance is correctly created and that
        its fields contain the expected data types and values.
        """
        self.assertIsInstance(self.order, Order)
        self.assertIsInstance(self.order.order_number, str)
        self.assertIsNotNone(self.order.order_number)
        self.assertNotEqual(self.order.order_number, "")

        self.assertEqual(self.order.user_profile, self.user_profile)
        self.assertEqual(self.order.first_name, 'John')
        self.assertEqual(self.order.last_name, 'Doe')
        self.assertEqual(self.order.email, 'john@example.com')
        self.assertEqual(self.order.country, Country('US'))
        self.assertEqual(self.order.stripe_pid, 'test_stripe_pid')

    def test_unique_order_number(self):
        """
        Test that each Order instance has a unique order number.
        """
        another_order = Order.objects.create(
            user_profile=self.user_profile,
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            country='US',
            stripe_pid='another_test_stripe_pid'
        )
        self.assertNotEqual(
            self.order.order_number, another_order.order_number)

    def test_update_total(self):
        """
        Test the update_total method to ensure it correctly updates
        order_total and grand_total.
        """
        self.order.update_total()
        self.assertEqual(self.order.order_total, 200)
        self.assertEqual(self.order.grand_total, 200)

    def test_order_line_item_model(self):
        """
        Test the OrderLineItem model for correct data types and field values.

        This test checks that an OrderLineItem instance is correctly created
        and that its fields contain the expected data types and values.
        It also checks if the 'lineitem_total' is calculated correctly.
        """
        self.assertEqual(self.order_line_item.order, self.order)
        self.assertEqual(self.order_line_item.trip, self.trip)
        self.assertEqual(
            self.order_line_item.available_date, self.available_date)
        self.assertEqual(self.order_line_item.guests, 2)
        self.assertEqual(self.order_line_item.lineitem_total, 200)

    def test_automatic_lineitem_total_calculation(self):
        """
        Test that lineitem_total is automatically calculated upon saving.
        """
        self.assertEqual(self.order_line_item.lineitem_total, 200)

    def test_order_total_after_deleting_lineitem(self):
        """
        Test if the order totals get updated when an OrderLineItem is deleted.
        """
        self.order_line_item.delete()
        self.order.update_total()
        self.assertEqual(self.order.order_total, 0)
        self.assertEqual(self.order.grand_total, 0)
