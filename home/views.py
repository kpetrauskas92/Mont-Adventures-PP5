from django.shortcuts import render
from django.db.models import Count
from django.db.models import Q
from trip_packages.models import Trips
from trip_packages.trip_utils import display_funcs


COUNTRY_IMAGE_MAP = {
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


def index(request):
    top_trips = Trips.objects.annotate(
        num_favorites=Count('favorited_by')
    ).order_by('-num_favorites')[:8]

    populate_trip_attributes(top_trips)

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


def search_trips(request):
    query = request.GET.get('q', '')
    results = Trips.objects.none()

    if len(query) >= 3:
        results = Trips.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    populate_trip_attributes(results)
    context = {
        'results': results,
        'query': query
    }
    return render(request, 'includes/search-results.html', context)
