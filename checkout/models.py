from django.db import models
from django.db.models import Sum
from django.utils import timezone
from trip_packages.models import Trips, AvailableDate
from profiles.models import UserProfile
import uuid


class Order(models.Model):
    """
    Model to represent an order in the checkout process.
    """

    order_number = models.CharField(max_length=32, null=False, editable=False)
    date = models.DateTimeField(default=timezone.now)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='orders')
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    order_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    stripe_pid = models.CharField(max_length=254, null=True,
                                  blank=False, default='')

    def _generate_order_number(self):
        """
        Generate a random, truncated, unique order number using UUID.

        Returns:
            str: A unique, truncated order number.
        """
        return uuid.uuid4().hex[:12].upper()

    def update_total(self):
        """
        Update the grand total each time a line item is added.

        Updates both the 'order_total' and 'grand_total'
        fields and saves the model.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.grand_total = self.order_total
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    """
    Model to represent an individual line item in an order.
    """
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    trip = models.ForeignKey(Trips, null=False, blank=False,
                             on_delete=models.CASCADE)
    available_date = models.ForeignKey(AvailableDate, null=False, blank=False,
                                       on_delete=models.CASCADE)
    guests = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=10, decimal_places=2,
                                         null=False, blank=False,
                                         editable=False)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
    )

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the line item total
        and update the order total.

        Calculates the 'lineitem_total' based on 'trip.price'
        and 'guests' and saves the model.
        """
        self.lineitem_total = self.trip.price * self.guests
        super().save(*args, **kwargs)
