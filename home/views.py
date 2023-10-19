from django.shortcuts import render
from django.db.models import Q
from trip_packages.models import Trips


def index(request):
    """ A view to return the index page """
    return render(request, 'index.html')


def search_trips(request):
    query = request.GET.get('q', '')

    results = Trips.objects.none()

    if len(query) >= 3:
        results = Trips.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    context = {
        'results': results,
        'query': query
    }
    return render(request, 'includes/search-results.html', context)
