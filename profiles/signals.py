from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from checkout.models import Order
from .models import UserProfile, CustomerIDCounter


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Handle post-save operations for User model.

    If a new User is created:
    - Atomically generates and assigns a unique customer_id.

    If an existing User is updated:
    - Saves the associated UserProfile.
    """
    if created:
        with transaction.atomic():
            counter_obj = CustomerIDCounter.objects.select_for_update().first()
            if counter_obj is None:
                counter_obj = CustomerIDCounter.objects.create(counter=1)
            else:
                counter_obj.counter += 1
                counter_obj.save()

            customer_id = f"{counter_obj.counter:05}"
            user_profile = UserProfile.objects.create(user=instance,
                                                      customer_id=customer_id)

            # Associate past orders with this user profile
            past_orders = Order.objects.filter(email=instance.email,
                                               user_profile__isnull=True)

            for order in past_orders:
                order.user_profile = user_profile
                order.save()

    else:
        instance.userprofile.save()
