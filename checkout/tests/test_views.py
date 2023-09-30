from stripe.error import StripeError
from django.test import TestCase, Client
from unittest.mock import patch, Mock
from django.urls import reverse
from profiles.models import UserProfile
from checkout.models import Order
from trip_packages.models import Trips
from django.contrib.auth.models import User


class CheckoutViewsTestCase(TestCase):

    def setUp(self):
        """
        Set up common test data and state across test methods.
        """
        self.client = Client()
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
            difficulty=1
        )
        self.cart = [{'trip_id': self.trip.id, 'guests': 2}]
        self.client.login(username='testuser', password='testpass')

    @patch('stripe.PaymentIntent.create')
    @patch('stripe.PaymentIntent.modify')
    def test_checkout(self, mock_modify, mock_create):
        """
        Test the checkout view for successful order creation and redirection.

        This test mocks Stripe's PaymentIntent methods and tests
        if the checkout view redirects to the 'checkout-success' page
        upon successful order creation.
        """
        mock_intent = Mock()
        mock_create.return_value = mock_intent
        mock_modify.return_value = mock_intent

        order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            stripe_pid='test_pid'
        )

        response = self.client.post(
            reverse('checkout'),
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'country': 'US',
                'client_secret': 'test_secret_secret123',
            }
        )

        order = Order.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('checkout-success', args=[order.order_number]))

    @patch('stripe.PaymentIntent.modify')
    def test_cache_checkout_data(self, mock_modify):
        """
        Test caching checkout data and modifying Stripe PaymentIntent.

        This test mocks Stripe's PaymentIntent 'modify' method and tests if the
        view correctly modifies the PaymentIntent
        and returns a 200 status code.
        """
        mock_intent = Mock()
        mock_modify.return_value = mock_intent

        response = self.client.post(
            reverse('cache_checkout_data'),
            {'client_secret': 'test_secret_secret123'}
        )

        self.assertEqual(response.status_code, 200)

    def test_checkout_success(self):
        """
        Test the 'checkout_success' view for successful rendering.

        This test checks if the 'checkout_success' view renders
        the correct template and returns a 200 status code.
        """
        order = Order.objects.create(
            first_name='John', last_name='Doe', stripe_pid='test_pid')
        response = self.client.get(
            reverse('checkout-success', args=[order.order_number]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout-success.html')

    def test_checkout_unauthenticated_user(self):
        """
        Test the 'checkout' view for unauthenticated users.

        This test checks if the 'checkout' view redirects unauthenticated users
        and returns a 302 status code.
        """
        self.client.logout()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_empty_cart(self):
        """
        Test the 'checkout' view with an empty cart.

        This test checks if the 'checkout' view redirects users
        with an empty cart and returns a 302 status code.
        """
        self.client.session['cart'] = []
        self.client.session.save()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_invalid_form(self):
        """
        Test the 'checkout' view with an invalid form submission.

        This test checks if the 'checkout' view returns a 200 status code when
        submitted with an invalid form.
        """
        response = self.client.post(
            reverse('checkout'),
            {'first_name': '', 'last_name': '', 'email': '', 'country': ''}
        )
        self.assertEqual(response.status_code, 200)

    @patch('stripe.PaymentIntent.create')
    @patch('checkout.views.create_and_validate_order')
    def test_checkout_stripe_payment_failed(self,
                                            mock_create_and_validate_order,
                                            mock_create):
        """
        Test the checkout view when stripe payment fails.

        This test mocks Stripe's PaymentIntent methods and the
        create_and_validate_order function to simulate a Stripe error.
        """
        mock_intent = Mock()
        mock_create.return_value = mock_intent

        # Mocking create_and_validate_order to raise a StripeError
        mock_create_and_validate_order.side_effect = StripeError(
            "Payment Failed")

        response = self.client.post(
            reverse('checkout'),
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'country': 'US',
                'client_secret': 'test_secret_secret123',
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_validate_form(self):
        """
        Test the 'validate_form' view with a valid form submission.

        This test checks if the 'validate_form' view returns a 200 status code
        and a JSON response indicating that the form is valid when submitted
        with valid data.
        """
        response = self.client.post(
            reverse('validate_form'),
            {'first_name': 'John', 'last_name': 'Doe',
             'email': 'john.doe@example.com', 'country': 'US'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'is_valid': True})
