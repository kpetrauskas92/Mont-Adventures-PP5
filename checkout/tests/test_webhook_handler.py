from django.test import TestCase
from unittest.mock import patch
from checkout.models import Order
from checkout.webhook_handler import StripeWH_Handler


class TestStripeWHHandler(TestCase):

    def setUp(self):
        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            grand_total=100.00,
            stripe_pid="test_stripe_pid"
        )
        self.handler = StripeWH_Handler(None)

    @patch('checkout.webhook_handler.send_mail')
    def test_send_confirmation_email(self, mock_send_mail):
        # Call the _send_confirmation_email method
        self.handler._send_confirmation_email(self.order)

        # Assert that send_mail was called once
        mock_send_mail.assert_called_once()

        # Get the arguments with which send_mail was called
        args, kwargs = mock_send_mail.call_args

        # Check the email subject contains 'Booking Number'
        self.assertIn('Booking Number', args[0])
        self.assertIn(self.order.email, args[3])
