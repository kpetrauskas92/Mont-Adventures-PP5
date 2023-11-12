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

    def test_name_fields(self):
        """
        Test validation for name fields: first_name and last_name.
        """
        name_fields = ['first_name', 'last_name']

        for field in name_fields:
            # Test valid name
            form_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
            }
            form_data[field] = 'John'
            form = OrderForm(form_data)
            self.assertTrue(form.is_valid())

            # Test short name
            form_data[field] = 'Jo'
            form = OrderForm(form_data)
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors[field],
                [f'{field.replace("_", " ").capitalize()} '
                 'must be at least 3 characters long.']
            )

            # Test non-alphabetic name
            form_data[field] = 'John123'
            form = OrderForm(form_data)
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors[field],
                [f'{field.replace("_", " ").capitalize()} '
                 'should only contain letters.']
            )

    def test_invalid_email(self):
        """
        Test that the form is invalid with an incorrect email format.
        """
        form = OrderForm({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid_email',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['email'], ['Enter a valid email address.'])

    def test_multiple_errors(self):
        """
        Test that the form captures multiple errors.
        """
        form = OrderForm({
            'first_name': 'Jo',
            'last_name': 'D',
            'email': 'invalid_email',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
