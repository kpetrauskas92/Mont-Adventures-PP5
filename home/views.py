import os
import requests
from django.shortcuts import render
from django.db.models import Count
from django.db.models import Q
from trip_packages.models import Trips
from trip_packages.trip_utils import display_funcs


def error_404(request, exception):
    """
    Custom handler for 404 errors (Page Not Found).
    """
    return render(request, 'includes/error_handlers/404.html', {}, status=404)


def error_500(request):
    """
    Custom handler for 500 errors (Internal Server Error).
    """
    return render(request, 'includes/error_handlers/500.html', {}, status=500)


def index(request):
    """
    View function for the homepage.
    Displays top trips and trip locations with counts.
    """

    # Retrieve top 8 trips based on the number of favorites
    top_trips = Trips.objects.annotate(
        num_favorites=Count('favorited_by')
    ).order_by('-num_favorites')[:8]

    populate_trip_attributes(top_trips)

    # Count trips per location
    locations_with_count = Trips.objects.values('location').annotate(
        num_trips=Count('id')
    )

    location_count_dict = {
        loc['location']: loc['num_trips'] for loc in locations_with_count}

    context = {
        'top_trips': top_trips,
        'location_count_dict': location_count_dict,
        'country_image_map': COUNTRY_IMAGE_MAP,
    }
    return render(request, 'index.html', context)


COUNTRY_IMAGE_MAP = {
    # Mapping of country codes to image paths
    'FR': 'web_elements/carousel/france.webp',
    'IT': 'web_elements/carousel/italy.webp',
    'ES': 'web_elements/carousel/spain.webp',
    'GB': 'web_elements/carousel/uk.webp',
    'IE': 'web_elements/carousel/ireland.webp',
    'NO': 'web_elements/carousel/norway.webp',
    'NP': 'web_elements/carousel/nepal.webp',
    'PK': 'web_elements/carousel/pakistan.webp',
}


def populate_trip_attributes(trip_list):
    # Setting string representations and icons for trip attributes
    for trip in trip_list:
        trip.duration_str = display_funcs['duration'](trip.duration)
        trip.duration_icon = (
            'web_elements/svg_icons/trip_icons/duration_icon.svg')

        trip.difficulty_str = display_funcs['difficulty'](trip.difficulty)
        trip.difficulty_icon = (
            'web_elements/svg_icons/trip_icons/difficulty_icon.svg')

        trip.location_str = display_funcs['location'](trip.location)
        trip.location_icon = (
            'web_elements/svg_icons/trip_icons/location_icon.svg')


def search_trips(request):
    """
    Search function for trips based on user query.
    """
    query = request.GET.get('q', '')
    if query:
        if len(query) >= 3:
            # Search is conducted if the query length is at least 3 characters
            results = Trips.objects.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            )
        else:
            results = Trips.objects.none()
    else:
        # Randomly select 3 trips if no query is provided
        results = Trips.objects.order_by('?')[:3]

    populate_trip_attributes(results)
    context = {
        'results': results,
        'query': query
    }
    return render(request, 'includes/search/search-results.html', context)


def subscribe_to_newsletter(request):
    """
    Handles newsletter subscription requests.
    """
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            # Handling the case where email is not provided
            context = {'alert_class': 'alert-error',
                       'message': 'Email is required'}

        # Mailchimp API integration for newsletter subscription
        api_key = os.environ.get('MAILCHIMP_API_KEY')
        region = os.environ.get('MAILCHIMP_REGION')
        list_id = os.environ.get('MAILCHIMP_AUDIENCE_ID')

        url = (f"https://{region}.api.mailchimp.com/3.0/lists/"
               f"{list_id}/members/")

        headers = {
            'Authorization': f'apikey {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'email_address': email,
            'status': 'subscribed'
        }

        response = requests.post(url, headers=headers, json=data)

        # Handling different response scenarios
        if response.status_code == 200:
            context = {'alert_class': 'alert-success',
                       'message': 'Successfully subscribed! Thank you!'}
        elif (response.status_code == 400 and
              "already a list member" in response.text):
            context = {'alert_class': 'alert-warning',
                       'message': 'This email is already subscribed.'}
        else:
            context = {'alert_class': 'alert-error',
                       'message': 'Failed to subscribe, please try again.'}

    return render(request, 'snippets/response_message.html', context)
