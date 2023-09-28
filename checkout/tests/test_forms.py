from django.test import TestCase
from checkout.forms import OrderForm


class TestOrderForm(TestCase):

    def test_form_is_valid(self):
        """
        Test if the OrderForm is valid with the required data.

        This test checks that the OrderForm is valid when
        all required fields are filled out correctly.
        """
        form = OrderForm({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'country': 'US',
        })
        self.assertTrue(form.is_valid())

    def test_form_is_invalid(self):
        """
        Test if the OrderForm is invalid when fields are missing.

        This test checks that the OrderForm is invalid when
        required fields are not filled out.
        It also checks if the number of errors matches
        the number of required fields.
        """
        form = OrderForm({})
        self.assertFalse(form.is_valid())
        required_fields = sum(
            1 for field, value in form.fields.items() if value.required)
        self.assertEqual(len(form.errors), required_fields)
