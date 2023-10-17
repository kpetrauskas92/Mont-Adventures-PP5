from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from trip_packages.models import Trips


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


def review_image_path(instance, filename):
    """
    Function to determine the upload path for review images.

    - Constructs the path where the review images will be stored.
    """
    return f'profiles/users/reviews/trip-{instance.trip.id}/{filename}'


class Reviews(models.Model):
    """
    Reviews model for storing user reviews of trips.

    - Stores the user who made the review.
    - Associates the review with a trip.
    - Holds the rating, comment, and approval status of the review.
    """
    user = models.ForeignKey(User, related_name='reviews',
                             on_delete=models.CASCADE)
    trip = models.ForeignKey(Trips, related_name='reviews',
                             on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to=review_image_path,
                              null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.trip.name} - {self.rating}"
