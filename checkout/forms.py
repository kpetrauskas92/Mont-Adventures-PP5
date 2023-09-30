from django import forms
from django.core.exceptions import ValidationError
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Form class for handling Order creation and validation.

    This form is built on top of the Order model and adds additional validation
    and formatting logic.
    """
    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'email',
        )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and set field attributes.

        This method sets placeholders, classes, and other
        attributes for the form fields.
        """
        super(OrderForm, self).__init__(*args, **kwargs)

        placeholders = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
        }

        self.fields['first_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False

    def clean_first_name(self):
        """
        Validate the 'first_name' field.

        This method ensures that 'first_name' is at least 3 characters
        long and contains only alphabetic characters.

        Returns:
            str: The cleaned first name if validation succeeds.
        """
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 3:
            raise ValidationError("First name must be at least 3 "
                                  "characters long.")
        if not first_name.isalpha():
            raise ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        """
        Validate the 'last_name' field.

        This method ensures that 'last_name' is at least 3 characters
        long and contains only alphabetic characters.

        Returns:
            str: The cleaned last name if validation succeeds.
        """
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 3:
            raise ValidationError("Last name must be at least 3 "
                                  "characters long.")
        if not last_name.isalpha():
            raise ValidationError("Last name should only contain letters.")
        return last_name
