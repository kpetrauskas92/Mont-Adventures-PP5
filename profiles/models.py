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
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=5, unique=True)
    default_country = CountryField(blank_label='Country',
                                   null=True, blank=True)

    def __str__(self):
        return self.user.username
