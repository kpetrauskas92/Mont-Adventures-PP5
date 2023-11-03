import uuid
from django.templatetags.static import static
from django.db import models
from django.db.models import JSONField, Avg
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


MONTHS = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]


class DifficultyLevel(models.IntegerChoices):
    EASY = 1, 'Easy'
    MODERATE = 2, 'Moderate'
    CHALLENGING = 3, 'Challenging'
    HARD = 4, 'Hard'


class Trips(models.Model):
    """
    Trips model for storing information about different travel packages.

    - Stores the main image of the trip.
    - Contains details like name, price, duration, and location.
    - Maintains seasonal availability as an array of integers.
    - Keeps track of the maximum group size and overall rating.
    - Holds an integer value for the trip's difficulty level.
    """
    main_image = models.ImageField(
        upload_to='trip_packages/main_images/',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    price = models.IntegerField(db_index=True)
    duration = models.IntegerField(db_index=True)
    location = CountryField()
    season = JSONField(db_index=True)
    max_group_size = models.IntegerField(db_index=True)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1,
                                         default=0.0, db_index=True)
    difficulty = models.IntegerField(db_index=True,
                                     choices=DifficultyLevel.choices)

    def get_image_url(self):
        if self.main_image:
            return self.main_image.url
        return static('web_elements/default-trip-img.webp')

    def duration_str(self):
        return f"{self.duration} day{'s' if self.duration > 1 else ''}"

    def season_str(self):
        return ', '.join([MONTHS[month] for month in self.season])

    def max_group_size_str(self):
        return f"Up to {self.max_group_size}"

    def difficulty_str(self):
        return DifficultyLevel(self.difficulty).label

    def __str__(self):
        return self.name


class TripOverview(models.Model):
    """
    TripOverview model for storing detailed information about a specific trip.

    - Links to the associated trip in the Trips model through a ForeignKey.
    - Contains a textual overview of the trip.
    - Specifies what is included and not included in the trip package.
    - Provides a list of equipment needed for the trip.
    - Indicates the skill level required for the trip.
    - Describes the expected weather conditions during the trip.
    - Outlines the cancellation policy for the trip.
    - Includes any other important notes or details about the trip.
    """
    trip = models.ForeignKey(Trips, related_name='overviews',
                             on_delete=models.CASCADE)
    trip_overview = models.TextField()
    included = models.TextField()
    not_included = models.TextField()
    equipment_list = models.TextField()
    skill_level = models.TextField()
    weather_conditions = models.TextField()
    cancellation_policy = models.TextField()
    important_notes = models.TextField()


class TripImage(models.Model):
    """
    TripImage model for storing additional images related to a trip.

    - Holds a ForeignKey to the associated Trips model.
    - Stores additional images in a specified upload directory.
    """
    trips = models.ForeignKey(Trips,
                              related_name='images',
                              on_delete=models.CASCADE)
    image = models.ImageField(upload_to='trip_packages/additional_images/')


class AvailableDate(models.Model):
    """
    AvailableDate model for storing available dates for a trip.

    - Holds a ForeignKey to the associated Trips model.
    - Stores the start and end date for the trip's availability.
    - Maintains the maximum group size and the number of booked slots.
    - Contains a Boolean field to indicate if the trip is available.
    """
    trips = models.ForeignKey(Trips, related_name='available_dates',
                              on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    max_group_size = models.IntegerField()
    booked_slots = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def remaining_slots(self):
        return self.max_group_size - self.booked_slots

    def __str__(self):
        return f"{self.trips.name} - {self.start_date} to {self.end_date}"


class FavoriteTrip(models.Model):
    user = models.ForeignKey(get_user_model(),
                             related_name='favorite_trips',
                             on_delete=models.CASCADE)
    trip = models.ForeignKey(Trips,
                             related_name='favorited_by',
                             on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'trip')

    def __str__(self):
        return f"{self.user.username} - {self.trip.name}"

    @classmethod
    def add_favorite(cls, user, trip):
        # REVIEW
        obj, created = cls.objects.get_or_create(user=user, trip=trip)

    @classmethod
    def remove_favorite(cls, user, trip):
        # Delete the favorite if it exists
        cls.objects.filter(user=user, trip=trip).delete()


def review_image_path(instance, filename):
    """
    Function to determine the upload path for review images.

    - Constructs the path where the review images will be stored.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'trip_packages/reviews/trip-{instance.trip.id}/{filename}'


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
    title = models.CharField(max_length=25, null=True, blank=True)
    comment = models.TextField(max_length=300)
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to=review_image_path,
                              null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.trip.name} - {self.rating}"


# Signal to update overall_rating when a review is saved or deleted
@receiver([post_save, post_delete], sender=Reviews)
def update_overall_rating(sender, instance, **kwargs):
    trip = instance.trip
    approved_reviews = Reviews.objects.filter(trip=trip, is_approved=True)
    new_rating = approved_reviews.aggregate(Avg('rating'))['rating__avg']
    trip.overall_rating = round(new_rating, 1) if new_rating else 0.0
    trip.save()
