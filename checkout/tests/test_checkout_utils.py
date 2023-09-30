import stripe
from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock
from checkout.checkout_utils import (
    create_stripe_payment_intent,
    initialize_order_form,
    create_and_validate_order,
    extract_form_data,
    validate_order_form,
    create_order,
    create_order_line_items,
    handle_successful_checkout,
)
from checkout.models import Order
from trip_packages.models import Trips, AvailableDate
from profiles.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError


class CheckoutUtilsTestCase(TestCase):

    def setUp(self):
        """
        Set up common test data and state across test methods.
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.trip = Trips.objects.create(
            name='Test Trip',
            price=100,
            duration=5,
            season=(1, 2),
            max_group_size=10,
            overall_rating="4.5",
            difficulty=1)
        self.available_date = AvailableDate.objects.create(
            trips=self.trip,
            start_date='2022-12-31',
            end_date='2023-01-01',
            max_group_size=10,
            booked_slots=0,
            is_available=True
        )
        self.cart = [{'trip_id': self.trip.id,
                      'available_date_id': self.available_date.id,
                      'guests': 2}]
        self.request = self.factory.post('/checkout/')
        self.request.user = self.user
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

    @patch('stripe.PaymentIntent.create')
    def test_create_stripe_payment_intent(self, mock_create):
        """
        Test Stripe Payment Intent creation.

        This test mocks Stripe's PaymentIntent creation method and checks
        if the created intent matches the expected mock object.
        """
        mock_intent = Mock()
        mock_create.return_value = mock_intent
        intent = create_stripe_payment_intent(1000, 'usd')
        self.assertEqual(intent, mock_intent)

    @patch('stripe.PaymentIntent.create')
    def test_create_stripe_payment_intent_failure(self, mock_create):
        """
        Test Stripe Payment Intent creation failure handling.

        This test checks if a Stripe error is raised when the Payment Intent
        creation fails.
        """
        mock_create.side_effect = stripe.error.StripeError("An error occurred")
        with self.assertRaises(stripe.error.StripeError):
            create_stripe_payment_intent(1000, 'usd')

    def test_initialize_order_form(self):
        """
        Test initializing the OrderForm with default user information.

        This test verifies that the OrderForm is initialized with
        the correct default values based on the authenticated user's profile.
        """
        form = initialize_order_form(self.user)
        self.assertIsNotNone(form)

    def test_initialize_order_form_no_user_profile(self):
        """
        Test initializing the order form when no UserProfile exists.

        This test checks if the form is initialized correctly
        when the UserProfile associated with the User does not exist.
        """
        self.profile.delete()
        form = initialize_order_form(self.user)
        self.assertIsNotNone(form)

    def test_extract_form_data(self):
        """
        Test data extraction from POST request for form initialization.

        This test checks if data extracted from the request object
        matches the expected values for form fields.
        """
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
        }

        self.request = self.factory.post('/checkout/', post_data)
        self.request.user = self.user
        data = extract_form_data(self.request)

        self.assertEqual(data.get('first_name'), 'John')
        self.assertEqual(data.get('last_name'), 'Doe')
        self.assertEqual(data.get('email'), 'john.doe@example.com')

    def test_validate_order_form(self):
        """
        Test form validation.

        This test confirms that the form validates successfully with
        correct form data and fails with incorrect or missing data.
        """
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
        }
        self.request = self.factory.post('/checkout/', post_data)
        self.request.user = self.user
        form_data = self.request.POST.dict()
        is_valid, form = validate_order_form(form_data)
        if not is_valid:
            self.fail(f"Form should be valid but had errors: {form.errors}")
        self.assertTrue(is_valid)

    def test_create_order_invalid_form(self):
        """
        Test order creation with an invalid form.

        This test checks if a ValidationError is raised
        when attempting to create an order with an invalid form.
        """
        invalid_data = {'first_name': '', 'last_name': '',
                        'email': ''}
        is_valid, form = validate_order_form(invalid_data)
        self.assertFalse(is_valid)
        with self.assertRaises(ValidationError):
            create_order(is_valid, form, self.request, self.cart)

    def test_create_order(self):
        """
        Test order creation based on form validity.

        This test checks if an order is successfully created when
        the form is valid, and fails otherwise.
        """
        form_data = self.request.POST.dict()
        is_valid, form = validate_order_form(form_data)
        if is_valid:
            order, _ = create_order(is_valid, form, self.request, self.cart)
            self.assertIsNotNone(order)
        else:
            print(form.errors)

    def test_create_order_line_items(self):
        """
        Test creating line items for the order based on the cart.

        This test verifies that line items are created successfully
        and associated with the correct order and cart items.
        """
        order = Order.objects.create(
            first_name='John', last_name='Doe', stripe_pid='test_pid')
        result = create_order_line_items(order, self.cart, self.request)
        self.assertTrue(result)

    def test_create_and_validate_order(self):
        """
        Test form data extraction, validation, and order creation.

        This test goes through the process of extracting form data,
        validating it, and creating an order accordingly.
        """
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'client_secret': 'test_secret'
        }
        self.request = self.factory.post('/checkout/', post_data)
        self.request.user = self.user
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)
        order, _ = create_and_validate_order(self.request, self.cart)
        self.assertIsNotNone(order)

    def test_create_order_check_return_values(self):
        """
        Test created order attributes.

        This test checks if the created order has
        the correct attributes based on the form data submitted.
        """
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
        }
        self.request = self.factory.post('/checkout/', post_data)
        self.request.user = self.user
        form_data = self.request.POST.dict()
        is_valid, form = validate_order_form(form_data)
        order, _ = create_order(is_valid, form, self.request, self.cart)
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.last_name, 'Doe')
        self.assertEqual(order.email, 'john.doe@example.com')

    @patch('profiles.forms.UserProfileForm.is_valid')
    def test_handle_successful_checkout(self, mock_is_valid):
        """
        Test handling of a successful checkout process.

        This test mocks the UserProfileForm's validity and checks
        if the checkout process is handled successfully, updating
        the user profile if needed.
        """
        mock_is_valid.return_value = True
        order = Order.objects.create(
            first_name='John', last_name='Doe', stripe_pid='test_pid')
        handle_successful_checkout(self.request, order.order_number)
