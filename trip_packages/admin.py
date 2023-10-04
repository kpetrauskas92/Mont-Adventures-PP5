from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import (RangeNumericFilter,
                                          SingleNumericFilter)
from .models import Trips, TripImage, AvailableDate
from django import forms


@admin.register(Trips)
class TripsAdmin(ModelAdmin):
    """
    Admin class for the Trips model. Defines how the Trips model
    should be displayed and managed in the Django admin interface.
    """
    list_display = ['name', 'price', 'duration', 'location',
                    'season_str', 'max_group_size_str', 'display_difficulty']
    list_filter = [('price', RangeNumericFilter),
                   ('duration', SingleNumericFilter), 'location']
    search_fields = ['name', 'location']

    @display(description="Difficulty Level")
    def display_difficulty(self, obj):
        return obj.get_difficulty_display()


# For TripImage model
@admin.register(TripImage)
class TripImageAdmin(ModelAdmin):
    """
    Admin class for the TripImage model. Defines how the TripImage model
    should be displayed and managed in the Django admin interface.
    """
    list_display = ['trips', ]
    list_filter = ['trips', ]
    search_fields = ['trips__name', ]


class AvailableDateForm(forms.ModelForm):
    """
    Form class for the AvailableDate model. It customizes how the model
    form should be displayed and validates the form inputs.
    """
    class Meta:
        model = AvailableDate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['trips'].queryset = Trips.objects.filter(
                id=instance.trips_id)
            self.fields['trips'].disabled = True


@admin.register(AvailableDate)
class AvailableDateAdmin(ModelAdmin):
    """
    Admin class for the AvailableDate model. Defines how the AvailableDate
    model should be displayed and managed in the Django admin interface.
    """
    list_display = ['trip_name', 'start_date', 'end_date',
                    'max_group_size', 'booked_slots',
                    'is_available', 'is_fully_booked']
    list_filter = ['is_available', 'start_date', 'end_date', 'trips__name']
    search_fields = ['trips__name', ]
    form = AvailableDateForm

    def trip_name(self, obj):
        """
        Return the name of the trip associated with the available date.
        """
        return obj.trips.name
    trip_name.admin_order_field = 'trips__name'
    trip_name.short_description = 'Trip Name'

    @display(description="Fully Booked")
    def is_fully_booked(self, obj):
        """
        Check if the trip associated with the available date is fully booked.
        """
        return obj.booked_slots >= obj.max_group_size
