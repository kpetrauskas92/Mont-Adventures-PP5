from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class CustomerIDCounter(models.Model):
    counter = models.IntegerField(default=0)


class UserProfile(models.Model):
    """
    UserProfile model for storing user-specific information.

    - Maintains default booking information.
    - Stores order history.
    - Generates a unique customer_id upon creation.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=5, unique=True)
    default_phone_number = models.CharField(max_length=20,
                                            null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80,
                                               null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80,
                                               null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40,
                                            null=True, blank=True)
    default_county = models.CharField(max_length=80,
                                      null=True, blank=True)
    default_postcode = models.CharField(max_length=20,
                                        null=True, blank=True)
    default_country = CountryField(blank_label='Country',
                                   null=True, blank=True)

    def __str__(self):
        return self.user.username
