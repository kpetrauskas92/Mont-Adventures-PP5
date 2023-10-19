from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class CustomerIDCounter(models.Model):
    """
    CustomerIDCounter model for generating unique customer IDs.

    - Holds a counter field that is used to create unique customer IDs.
    """
    counter = models.IntegerField(default=0)


class UserProfile(models.Model):
    """
    UserProfile model for storing user-specific information.

    - Maintains default booking information.
    - Stores order history.
    - Generates a unique customer_id upon creation.
    """
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=5, unique=True)
    profile_image = models.ImageField(upload_to='profiles/users/avatars',
                                      null=True, blank=True)

    country = CountryField(blank_label='Country',
                           null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=40,
                                              null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=15,
                                               null=True, blank=True)

    def __str__(self):
        return self.user.username
