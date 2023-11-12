from django.test import TestCase, Client
from django.urls import reverse
from trip_packages.models import Trips, AvailableDate
from datetime import date


class TripPackagesViewTest(TestCase):
    """
    Test cases for the TripPackages view.

    - Validates status code for GET requests.
    - Checks the context data for trips and filters.
    - Verifies filtering based on query parameters.
    - Tests HTMX partial updates.
    - Tests multiple filter combinations.
    - Tests negative cases where filters yield no results.
    - Tests scenarios with invalid or missing filter values.
    """

    def setUp(self):
        """
        Setup test environment.
        """
        self.client = Client()
        self.url = reverse('trip_packages')
        self.trip1 = Trips.objects.create(
            name="Test Trip 1",
            price=1000,
            duration=5,
            location="Test Location 1",
            season=[1, 2],
            max_group_size=5,
            difficulty=2,
            overall_rating="4.5"
        )
        self.trip2 = Trips.objects.create(
            name="Test Trip 2",
            price=2000,
            duration=7,
            location="Test Location 2",
            season=[3, 4],
            max_group_size=10,
            difficulty=3,
            overall_rating="4.0"
        )

    def test_get_request(self):
        """
        Test GET request and status code.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        """
        Test context data for trips and filters.
        """
        response = self.client.get(self.url)
        self.assertTrue('trips' in response.context)
        self.assertTrue('filters' in response.context)

    def test_filtering(self):
        """
        Test filtering based on query parameters.
        """
        response = self.client.get(self.url, {'price': '1000'})
        self.assertTrue(all(trip.price == 1000
                            for trip in response.context['trips']))

    def test_htmx_partial_update(self):
        """
        Test HTMX partial updates.
        """
        response = self.client.get(self.url, HTTP_HX_REQUEST='true')
        self.assertTemplateUsed(response,
                                'includes/filter/filtered-trips.html')

    def test_multiple_filters(self):
        """
        Test applying multiple filters.
        """
        response = self.client.get(self.url,
                                   {'price': '1000', 'duration': '5'})
        self.assertTrue(all(trip.price == 1000 and trip.duration == 5
                            for trip in response.context['trips']))

    def test_negative_case(self):
        """
        Test filtering that yields no results.
        """
        response = self.client.get(self.url, {'price': '1'})
        self.assertEqual(len(response.context['trips']), 0)

    def test_invalid_filter_value(self):
        """
        Test invalid filter values.
        """
        response = self.client.get(self.url, {'price': 'abc'})
        self.assertEqual(response.status_code, 200)

    def test_missing_filter_value(self):
        """
        Test missing filter value.
        """
        response = self.client.get(self.url, {'price': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all
                        (trip.price == 1000 for trip in response.context
                         ['trips']))


class TripDetailsViewTest(TestCase):
    """
    Test cases for the TripDetails view.

    - Validates status code for GET requests.
    - Checks the context data for trip and trip details.
    - Verifies the format of trip details.
    - Tests the presence of HTML elements in the rendered template.
    """

    def setUp(self):
        """
        Setup test environment.
        """
        self.client = Client()
        self.trip = Trips.objects.create(
            name="Test Trip",
            price=1000,
            duration=5,
            location="Test Location",
            season=[1, 2],
            max_group_size=5,
            difficulty=2
        )
        self.url = reverse('trip_details', args=[self.trip.id])

    def test_get_request(self):
        """
        Test GET request and status code.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        """
        Test context data for trip and trip details.
        """
        response = self.client.get(self.url)
        self.assertTrue('trip' in response.context)
        self.assertTrue('trip_details' in response.context)

    def test_trip_details_format(self):
        """
        Test if the trip details are formatted as expected.
        """
        response = self.client.get(self.url)
        trip_details = response.context['trip_details']
        for detail in trip_details:
            self.assertTrue('icon' in detail)
            self.assertTrue('alt' in detail)
            self.assertTrue('label' in detail)
            self.assertTrue('value' in detail)


class BookingDrawerViewTest(TestCase):
    """
    Tests for the BookingDrawer view.
    """

    def setUp(self):
        """
        Sets up the test environment.

        - Creates a trip object with dummy data.
        - Creates available date objects for the trip.
        """
        self.trip = Trips.objects.create(
            name='Test Trip',
            season=[1, 2, 3],
            duration=5,
            max_group_size=20,
            price=100,
            difficulty=1  # Add other required fields as necessary
        )
        AvailableDate.objects.create(
            trips=self.trip,
            start_date=date.today(),
            end_date=date.today(),
            max_group_size=20,
            is_available=True
        )

    def test_view_exists_at_desired_location(self):
        """
        Tests that the BookingDrawer view is accessible
        and returns a 200 status.
        """
        response = self.client.get(
            reverse('booking_drawer', args=[self.trip.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_with_invalid_trip(self):
        """
        Tests that the BookingDrawer view returns a 404
        status when accessed with an invalid trip_id.
        """
        response = self.client.get(reverse('booking_drawer', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_view_uses_correct_template(self):
        """
        Tests that the BookingDrawer view renders the correct template.
        """
        response = self.client.get(
            reverse('booking_drawer', args=[self.trip.id]))
        self.assertTemplateUsed(
            response, 'includes/booking/booking-drawer.html')

    def test_view_with_htmx_request(self):
        """
        Tests that the BookingDrawer view returns the
        'available-dates.html' template when accessed via an HTMX request.
        """
        response = self.client.get(
            reverse('booking_drawer',
                    args=[self.trip.id]), HTTP_HX_REQUEST='true')
        self.assertTemplateUsed(
            response, 'includes/booking/available-dates.html')
