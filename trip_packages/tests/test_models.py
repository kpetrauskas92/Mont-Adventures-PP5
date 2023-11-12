from django.test import TestCase
from trip_packages.models import Trips, AvailableDate
from datetime import date


class TripsModelTest(TestCase):
    """
    Test cases for the Trips model.

    - Validates Trip object creation and attribute assignment.
    - Checks the functionality of the difficulty_value property.
    """

    def setUp(self):
        """
        Setup a sample Trips object for testing purposes.
        """
        self.trip = Trips.objects.create(
            name="Sample Trip",
            price=100,
            duration=3,
            location="Sample Location",
            season=[1, 2, 12],  # January, February, December
            max_group_size=5,
            difficulty=2,
            overall_rating=4.5
        )

    def test_trip_creation(self):
        """
        Test if the Trip object is created
        and attributes are assigned correctly.
        """
        self.assertEqual(self.trip.name, "Sample Trip")
        self.assertEqual(self.trip.price, 100)
        self.assertEqual(self.trip.duration, 3)
        self.assertEqual(self.trip.location, "Sample Location")
        self.assertEqual(self.trip.season, [1, 2, 12])
        self.assertEqual(self.trip.max_group_size, 5)
        self.assertEqual(self.trip.difficulty, 2)
        self.assertEqual(self.trip.overall_rating, 4.5)

    def test_difficulty_value_property(self):
        """
        Test if the difficulty_value property returns the correct value.
        """
        self.assertEqual(self.trip.difficulty_str(), 'Moderate')


class AvailableDateModelTest(TestCase):
    """
    Test cases for the AvailableDate model.

    - Validates AvailableDate object creation and attribute assignment.
    - Checks the functionality of the remaining_slots method.
    """

    def setUp(self):
        """
        Setup a sample Trips object and an AvailableDate
        object for testing purposes.
        """
        self.trip = Trips.objects.create(
            name="Sample Trip",
            price=100,
            duration=3,
            location="Sample Location",
            season=[1, 2, 12],
            max_group_size=5,
            difficulty=2,
            overall_rating=4.5
        )
        self.available_date = AvailableDate.objects.create(
            trips=self.trip,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 3),
            max_group_size=10,
            booked_slots=3,
            is_available=True
        )

    def test_available_date_creation(self):
        """
        Test if the AvailableDate object is created
        and attributes are assigned correctly.
        """
        self.assertEqual(self.available_date.trips, self.trip)
        self.assertEqual(self.available_date.start_date.strftime('%Y-%m-%d'),
                         "2023-01-01")
        self.assertEqual(self.available_date.end_date.strftime('%Y-%m-%d'),
                         "2023-01-03")
        self.assertEqual(self.available_date.max_group_size, 10)
        self.assertEqual(self.available_date.booked_slots, 3)
        self.assertEqual(self.available_date.is_available, True)

    def test_remaining_slots_method(self):
        """
        Test if the remaining_slots method returns the correct value.
        """
        self.assertEqual(self.available_date.remaining_slots(), 7)
