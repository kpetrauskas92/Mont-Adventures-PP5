from django.test import TestCase
from django_countries.fields import Country
from trip_packages.models import Trips, AvailableDate
from profiles.models import UserProfile, User
from checkout.models import Order, OrderLineItem


class CheckoutSignalsTest(TestCase):

    def setUp(self):
        """
        Set up common test data and state across test methods.
        """
        self.user = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='password'
        )

        self.user_profile = UserProfile.objects.get(user=self.user)

        self.trip = Trips.objects.create(
            name='Test Trip',
            price=1000,
            duration=3,
            location='Test Location',
            season=[1, 2],
            max_group_size=5,
            difficulty=1
        )

        self.available_date = AvailableDate.objects.create(
            trips=self.trip,
            start_date='2023-10-01',
            end_date='2023-10-03',
            max_group_size=5,
            booked_slots=0,
            is_available=True
        )

        self.order = Order.objects.create(
            user_profile=self.user_profile,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            country=Country('US'),
            stripe_pid='test_stripe_pid'
        )

    def test_update_booked_slots_on_create(self):
        """
        Test that the 'booked_slots' attribute is updated when
        an OrderLineItem is created.

        This test verifies that creating an OrderLineItem instance
        properly updates the 'booked_slots' on the associated
        AvailableDate instance.
        """
        OrderLineItem.objects.create(
            order=self.order,
            trip=self.trip,
            available_date=self.available_date,
            guests=2,
        )
        self.available_date.refresh_from_db()
        self.assertEqual(self.available_date.booked_slots, 3)

    def test_update_booked_slots_on_update(self):
        """
        Test that the 'booked_slots' attribute is updated when
        an OrderLineItem is updated.

        This test verifies that updating the 'guests' field
        on an OrderLineItem instance properly updates the 'booked_slots'
        on the associated AvailableDate instance.
        """
        order_line_item = OrderLineItem.objects.create(
            order=self.order,
            trip=self.trip,
            available_date=self.available_date,
            guests=2,
        )
        order_line_item.guests = 3
        order_line_item.save()
        self.available_date.refresh_from_db()
        self.assertEqual(self.available_date.booked_slots, 4)

    def test_update_booked_slots_on_delete(self):
        """
        Test that the 'booked_slots' attribute is updated when
        an OrderLineItem is deleted.

        This test verifies that deleting an OrderLineItem instance
        properly updates the 'booked_slots' on the associated AvailableDate
        instance back to its original value.
        """
        order_line_item = OrderLineItem.objects.create(
            order=self.order,
            trip=self.trip,
            available_date=self.available_date,
            guests=2,
        )
        order_line_item.delete()
        self.available_date.refresh_from_db()
        self.assertEqual(self.available_date.booked_slots, 0)
