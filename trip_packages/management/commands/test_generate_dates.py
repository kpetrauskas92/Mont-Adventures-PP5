from django.core.management import call_command
from django.test import TestCase
from datetime import datetime, timedelta
from trip_packages.models import Trips, AvailableDate


class GenerateDatesCommandTest(TestCase):

    def setUp(self):
        """
        Set up the test environment.
        Create a sample Trip object.
        """
        self.trip = Trips.objects.create(
            name='Test Trip',
            season=[1, 2, 3],
            duration=5,
            max_group_size=20,
            price=100,
            difficulty=1,
        )

    def test_generate_dates_range(self):
        """
        Test if the command generates dates within the range
        of "tomorrow" to "one year later".
        """
        call_command('generate_dates')
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        one_year_later = today + timedelta(days=365)
        available_dates = AvailableDate.objects.filter(trips=self.trip)
        for date_obj in available_dates:
            self.assertTrue(tomorrow <= date_obj.start_date <= one_year_later)

    def test_generate_dates_season(self):
        """
        Test if the generated dates are in the correct season.
        """
        call_command('generate_dates')
        available_dates = AvailableDate.objects.filter(trips=self.trip)
        for date_obj in available_dates:
            self.assertIn(date_obj.start_date.month, self.trip.season)

    def test_generate_dates_weekday(self):
        """
        Test if the generated dates are on a Friday.
        """
        call_command('generate_dates')
        available_dates = AvailableDate.objects.filter(trips=self.trip)
        for date_obj in available_dates:
            self.assertEqual(date_obj.start_date.weekday(), 4)

    def test_generate_dates_duration(self):
        """
        Test if the generated dates have the correct duration.
        """
        call_command('generate_dates')
        available_dates = AvailableDate.objects.filter(trips=self.trip)
        for date_obj in available_dates:
            expected_end_date = date_obj.start_date + timedelta(
                days=self.trip.duration)
            self.assertEqual(date_obj.end_date, expected_end_date)

    def test_generate_dates_max_group_size(self):
        """
        Test if the generated dates have the correct maximum group size.
        """
        call_command('generate_dates')
        available_dates = AvailableDate.objects.filter(trips=self.trip)
        for date_obj in available_dates:
            self.assertEqual(date_obj.max_group_size, self.trip.max_group_size)
