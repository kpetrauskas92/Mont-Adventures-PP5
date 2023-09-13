from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from profiles.forms import CustomSignupForm


class CustomSignupFormTest(TestCase):

    def test_clean_first_name_valid(self):
        """
        Test if the clean_first_name method works for valid input.
        """
        form = CustomSignupForm(data={'first_name': 'John'})
        form.is_valid()
        self.assertEqual(form.cleaned_data['first_name'], 'John')

    def test_clean_first_name_invalid(self):
        """
        Test if the clean_first_name method raises ValidationError
        for invalid input.
        """
        form = CustomSignupForm(data={'first_name': 'Jo'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'],
                         ['First name must be at least 3 characters long.'])

    def test_clean_last_name_valid(self):
        """
        Test if the clean_last_name method works for valid input.
        """
        form = CustomSignupForm(data={'last_name': 'Doe'})
        form.is_valid()
        self.assertEqual(form.cleaned_data['last_name'], 'Doe')

    def test_clean_last_name_invalid(self):
        """
        Test if the clean_last_name method raises ValidationError
        for invalid input.
        """
        form = CustomSignupForm(data={'last_name': 'Do'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['last_name'],
                         ['Last name must be at least 3 characters long.'])

    def setUp(self):
        self.factory = RequestFactory()

    def mock_get_response(self, request):
        # Mock get_response method for middleware
        return None

    def test_clean_email_unique(self):
        """
        Test if the clean_email method validates unique emails.
        """
        request = self.factory.get('/accounts/signup/')

        # Add session to the request
        middleware = SessionMiddleware(self.mock_get_response)
        middleware.process_request(request)
        request.session.save()

        # Create a user with an email, first name, last name, and password
        form_data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'testpassword'
        }
        form = CustomSignupForm(data=form_data)
        form.is_valid()
        form.save(request)

        # Try to create another user with the same email
        form2 = CustomSignupForm(data={'email': 'test@example.com',
                                       'first_name': 'Jane',
                                       'last_name': 'Doe',
                                       'password1': 'testpassword'})
        self.assertFalse(form2.is_valid())
        self.assertEqual(form2.errors['email'],
                         ['An account with this email already exists.'])
