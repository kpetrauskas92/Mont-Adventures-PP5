from django.contrib.auth.models import User
from .models import UserProfile
from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    """
    Custom signup form inheriting from allauth's SignupForm.

    - Includes additional fields for first_name and last_name.
    - Validates the length of first_name and last_name.
    - Ensures email uniqueness across User instances.
    """
    first_name = forms.CharField(
        max_length=25,
        label='First Name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=25,
        label='Last Name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    field_order = ['first_name', 'last_name',
                   'email', 'password1']

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) < 3:
            raise forms.ValidationError("First name must be at least "
                                        "3 characters long.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 3:
            raise forms.ValidationError("Last name must be at least "
                                        "3 characters long.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email "
                                        "already exists.")
        return email

    def save(self, request=None):
        user = super(CustomSignupForm, self).save(request)
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'country', 'city', 'phone_number',
            'emergency_contact_name', 'emergency_contact_phone'
        ]

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)

        custom_classes = 'border-black rounded-0 profile-form-input'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = custom_classes
