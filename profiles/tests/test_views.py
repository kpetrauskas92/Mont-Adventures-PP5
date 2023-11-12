from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from profiles.models import UserProfile
from checkout.models import Order, OrderLineItem
from trip_packages.models import Trips, AvailableDate
from unittest.mock import patch
from datetime import datetime, timedelta


class TestViews(TestCase):
    """
    Test class for testing the views in the profiles app.

    This test class aims to validate the functionality of the
    views related to the user's profile and the cancelation of trips.
    """
    def setUp(self):
        """
        Set up the initial data for each test.

        This method sets up a mock user, user profile, trip, available dates,
        and an order object for the tests to use.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser',
                                             'test@email.com',
                                             'testpass')
        self.user_profile, _ = UserProfile.objects.get_or_create(
            user=self.user
        )
        self.trip = Trips.objects.create(
            name='Test Trip',
            price=100,
            duration=5,
            season=(1, 2),
            max_group_size=10,
            overall_rating="4.5",
            difficulty=1
        )
        future_date = datetime.now().date() + timedelta(days=31)
        self.available_date = AvailableDate.objects.create(
            trips=self.trip,
            start_date=future_date,
            end_date=future_date + timedelta(days=self.trip.duration),
            max_group_size=5,
            booked_slots=0,
            is_available=True
        )
        # Create an Order object
        self.order = Order.objects.create(
            user_profile=self.user_profile,
            first_name='Test',
            last_name='User',
            email='test@email.com',
            order_total=0,
            grand_total=0,
            stripe_pid='dummy_stripe_pid'
        )

    @patch('profiles.views.get_object_or_404')
    def test_user_profile_view(self, mock_get_object_or_404):
        """
        Test the user_profile view to ensure it returns a 200 status code.

        This test aims to check if the user profile view is rendered
        correctly and returns a status code of 200.
        """
        self.client.login(username='testuser', password='testpass')
        mock_get_object_or_404.return_value = self.user_profile

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    @patch('profiles.views.get_object_or_404')
    def test_cancel_trip_view(self, mock_get_object_or_404):
        """
        Test the cancel_trip view to ensure trip cancellation functionality.

        This test validates if a trip can be canceled by the user
        and if the status of the line item gets updated to 'canceled'.
        """
        self.client.login(username='testuser', password='testpass')

        line_item = OrderLineItem.objects.create(
            trip=self.trip,
            available_date=self.available_date,
            order=self.order
        )
        mock_get_object_or_404.return_value = line_item

        response = self.client.get(reverse('cancel-trip', args=[line_item.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'includes/cancel-trip.html')

        response = self.client.post(reverse('cancel-trip',
                                            args=[line_item.id]))
        line_item.refresh_from_db()

        self.assertEqual(line_item.status, 'canceled')
