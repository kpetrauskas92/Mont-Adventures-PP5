from django.core.management.base import BaseCommand
from django.db import transaction
from trip_packages.models import Trips, AvailableDate
from trip_packages.trip_utils import generate_available_dates
from datetime import timedelta


class Command(BaseCommand):
    help = 'Generate available dates for Trip Packages'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            for trip in Trips.objects.all():
                AvailableDate.objects.filter(trips=trip).delete()

                available_dates = generate_available_dates(
                    trip.season, trip.duration, include_departure_day=False)
                for date in available_dates:
                    end_date = date + timedelta(days=trip.duration)
                    AvailableDate.objects.create(
                        trips=trip,
                        start_date=date,
                        end_date=end_date,
                        max_group_size=trip.max_group_size
                    )
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully generated dates for product {trip.name}'))
