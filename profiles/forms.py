import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UserProfile
from allauth.account.forms import SignupForm, LoginForm
from django import forms


class CustomLoginForm(LoginForm):

    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least "
                                        "8 characters long.")
        return password


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
            raise forms.ValidationError("First name must be at least 3 "
                                        "characters long.")

        if re.search('[^a-zA-Z]', first_name):
            raise forms.ValidationError("First name should only "
                                        "contain alphabets.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 3:
            raise forms.ValidationError("Last name must be at least 3 "
                                        "characters long.")

        if re.search('[^a-zA-Z]', last_name):
            raise forms.ValidationError("Last name should only "
                                        "contain alphabets.")

        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email "
                                        "already exists.")
        return email

    def save(self, request=None):
        user = super(CustomSignupForm, self).save(request)
        if user:
            user.first_name = self.cleaned_data['first_name'].capitalize()
            user.last_name = self.cleaned_data['last_name'].capitalize()
            user.save()

        return user


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'custom_widgets/custom_clearable_file_input.html'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'country', 'city', 'phone_number',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'profile_image': CustomClearableFileInput
        }

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)

        custom_classes = 'border-black rounded-0 profile-form-input'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = custom_classes

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Validate file size
            if hasattr(image, 'size') and image.size > 5 * 1024 * 1024:
                raise ValidationError("Image size should not exceed 5MB.")

            # Validate file format only for UploadedFile objects
            if hasattr(image, 'content_type'):
                content_type = image.content_type
                if content_type not in ['image/jpeg', 'image/png']:
                    raise ValidationError("Accepted file formats are: "
                                          "JPEG, PNG.")

        return image

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country:
            raise ValidationError("Please select a country.")
        return country

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city is None:
            raise ValidationError("City cannot be empty.")
        if re.search('[^a-zA-Z]', city):
            raise ValidationError("City name should only contain alphabets.")
        return city.capitalize()

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number is None:
            raise ValidationError("Phone number cannot be empty.")
        if re.search('[^0-9]', phone_number):
            raise ValidationError("Phone number should only contain numbers.")
        return phone_number

    def clean_emergency_contact_name(self):
        name = self.cleaned_data.get('emergency_contact_name')
        if name is None:
            raise ValidationError("Emergency contact name cannot be empty.")
        if re.search('[^a-zA-Z ]', name):
            raise ValidationError("Name should only contain alphabets.")
        return name

    def clean_emergency_contact_phone(self):
        phone_number = self.cleaned_data.get('emergency_contact_phone')
        if phone_number is None:
            raise ValidationError("Emergency contact phone cannot be empty.")
        if re.search('[^0-9]', phone_number):
            raise ValidationError("Phone number should only contain numbers.")
        return phone_number
