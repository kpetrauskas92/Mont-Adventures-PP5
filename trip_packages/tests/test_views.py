from django.test import TestCase, Client
from django.urls import reverse
from trip_packages.models import Trips


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
        response = self.client.get(self.url, {'price': '9999'})
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

    def test_html_elements(self):
        """
        Test the presence of key HTML elements in the rendered template.
        """
        response = self.client.get(self.url)

        # Test for Trip Name
        self.assertContains(
            response,
            '<h1 class="text-white uppercase text-6xl font-bold p-4">'
        )

        # Test for Trip Details Grid
        self.assertContains(
            response,
            '<div class="flex gap-6 md:gap-10 lg:gap-14 justify-center mt-4">'
        )

        # Test for Trip Price
        self.assertContains(
            response,
            '<p class="text-4xl font-bold text-center text-black my-4">'
        )

        # Test for Book Now Button
        self.assertContains(
            response,
            '<label for="my-drawer-4"'
        )

        # Test for Tabs
        self.assertContains(
            response,
            '<div class="tabs pt-4 flex justify-center">'
        )
