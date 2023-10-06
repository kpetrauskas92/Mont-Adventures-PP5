from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import (UserProfile,
                             FavoriteTrip,
                             Reviews,
                             CustomerIDCounter)
from trip_packages.models import Trips, AvailableDate
from datetime import date


class UserProfileModelTest(TestCase):
    """
    Test cases for the UserProfile, FavoriteTrip, and Reviews models.

    - Validates profile creation upon User creation.
    - Checks the generation of unique customer IDs.
    - Verifies the string representation of the UserProfile.
    - Tests the creation and string representation of the FavoriteTrip model.
    - Tests the creation, string representation,
    and default settings of the Reviews model.
    - Tests the default and additional fields in the UserProfile model.
    """
    def setUp(self):
        """
        Set up test environment.
        """
        self.user = User.objects.create_user(username='testuser',
                                             password='12345')
        self.profile = UserProfile.objects.get(user=self.user)
        self.trip = Trips.objects.create(
            name='Test Trip',
            price=100,
            duration=5,
            season=(1, 2),
            max_group_size=10,
            overall_rating="4.5",
            difficulty=1
        )
        self.available_date = AvailableDate.objects.create(
            trips=self.trip,
            start_date=date(2023, 12, 1),
            end_date=date(2023, 12, 10),
            max_group_size=5,
            booked_slots=0,
            is_available=True
        )

    def test_profile_creation(self):
        """
        Validate profile creation upon User creation.
        """
        self.assertTrue(isinstance(self.profile, UserProfile))

    def test_customer_id_generation(self):
        """
        Check the generation of unique customer IDs.
        """
        counter_obj = CustomerIDCounter.objects.first()
        expected_customer_id = f"{counter_obj.counter:05}"
        self.assertEqual(self.profile.customer_id, expected_customer_id)

    def test_string_representation(self):
        """
        Verify the string representation of the UserProfile.
        """
        self.assertEqual(str(self.profile), self.user.username)

    def test_favorite_trip_creation(self):
        """
        Test the creation of FavoriteTrip model.
        """
        favorite_trip = FavoriteTrip.objects.create(user=self.user,
                                                    trip=self.trip)
        self.assertTrue(isinstance(favorite_trip, FavoriteTrip))

    def test_reviews_creation(self):
        """
        Test the creation of Reviews model.
        """
        review = Reviews.objects.create(
            user=self.user,
            trip=self.trip,
            rating=5,
            comment="Great trip!",
            is_approved=False
        )
        self.assertTrue(isinstance(review, Reviews))

    def test_favorite_trip_str(self):
        """
        Test the string representation of the FavoriteTrip model.
        """
        favorite_trip = FavoriteTrip.objects.create(user=self.user,
                                                    trip=self.trip)
        self.assertEqual(str(favorite_trip),
                         f"{self.user.username} - {self.trip.name}")

    def test_reviews_str(self):
        """
        Test the string representation of the Reviews model.
        """
        review = Reviews.objects.create(
            user=self.user,
            trip=self.trip,
            rating=5,
            comment="Great trip!",
            is_approved=False
        )
        self.assertEqual(str(review),
                         f"{self.user.username} - {self.trip.name} - 5")

    def test_reviews_default_settings(self):
        """
        Test the default settings of the Reviews model.
        """
        review = Reviews.objects.create(
            user=self.user,
            trip=self.trip,
            rating=5,
            comment="Great trip!"
        )
        self.assertFalse(review.is_approved)

    def test_user_profile_additional_fields(self):
        """
        Test the additional fields in the UserProfile model.
        """
        self.profile.country = 'US'
        self.profile.city = 'New York'
        self.profile.phone_number = '1234567890'
        self.profile.emergency_contact_name = 'John Doe'
        self.profile.emergency_contact_phone = '9876543210'
        self.profile.save()

        updated_profile = UserProfile.objects.get(id=self.profile.id)
        self.assertEqual(updated_profile.country, 'US')
        self.assertEqual(updated_profile.city, 'New York')
        self.assertEqual(updated_profile.phone_number, '1234567890')
        self.assertEqual(updated_profile.emergency_contact_name, 'John Doe')
        self.assertEqual(updated_profile.emergency_contact_phone, '9876543210')

    def test_user_profile_default_fields(self):
        """
        Test the default fields in the UserProfile model.
        """
        self.assertIsNone(self.profile.phone_number)
        self.assertIsNone(self.profile.emergency_contact_name)
        self.assertIsNone(self.profile.emergency_contact_phone)
