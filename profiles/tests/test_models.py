from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import UserProfile, CustomerIDCounter


class UserProfileModelTest(TestCase):
    """
    Test cases for the UserProfile model.

    - Validates profile creation upon User creation.
    - Checks the generation of unique customer IDs.
    - Verifies the string representation of the UserProfile.
    - Ensures that the default phone number is None.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='12345')
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_creation(self):
        self.assertTrue(isinstance(self.profile, UserProfile))

    def test_customer_id_generation(self):
        counter_obj = CustomerIDCounter.objects.first()
        expected_customer_id = f"CUST{counter_obj.counter:05}"
        self.assertEqual(self.profile.customer_id, expected_customer_id)

    def test_string_representation(self):
        self.assertEqual(str(self.profile), self.user.username)

    def test_default_phone_number(self):
        self.assertIsNone(self.profile.default_phone_number)
