from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os


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


@receiver(pre_save, sender=UserProfile)
def delete_old_image(sender, instance, **kwargs):
    # If the object is in the database and the profile_image has changed
    if instance.pk:
        try:
            old_image = UserProfile.objects.get(pk=instance.pk).profile_image
        except UserProfile.DoesNotExist:
            return

        # If the image is cleared or changed, delete it
        new_image = instance.profile_image
        if not new_image or (old_image and not old_image == new_image):
            if old_image and os.path.isfile(old_image.path):
                os.remove(old_image.path)
