from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import OrderLineItem


@receiver(pre_save, sender=OrderLineItem)
def update_booked_slots_on_create_or_update(sender, instance, **kwargs):
    """
    Update the number of booked slots in the corresponding AvailableDate
    when an OrderLineItem is created, updated, or canceled.
    """
    if instance.pk is None:
        change_in_guests = instance.guests + 1
    else:
        old_instance = OrderLineItem.objects.get(pk=instance.pk)
        change_in_guests = (instance.guests + 1) - (old_instance.guests + 1)

        # Handle cancellation
        if old_instance.status == 'active' and instance.status == 'canceled':
            change_in_guests = -(old_instance.guests + 1)

    available_date = instance.available_date
    available_date.booked_slots = max(available_date.booked_slots + change_in_guests, 0)
    available_date.save()

    print(f"Updating booked_slots. Change in guests: {change_in_guests}")


@receiver(post_delete, sender=OrderLineItem)
def update_booked_slots_on_delete(sender, instance, **kwargs):
    """
    Update the number of booked slots in the corresponding AvailableDate
    when an OrderLineItem is deleted.
    """
    available_date = instance.available_date

    if instance.status != 'canceled':
        available_date.booked_slots = max(available_date.booked_slots - (instance.guests + 1), 0)
        available_date.save()
