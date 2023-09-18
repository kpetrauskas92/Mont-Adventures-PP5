from django.views import View
from django.shortcuts import render
from .models import Trips


class TripPackages(View):
    """
    TripPackages view for displaying all available travel packages.

    - Fetches all records from the Trips model.
    - Renders them in the 'trip-packages.html' template.
    """
    def get(self, request):
        trips = Trips.objects.all()

        return render(request, 'trip-packages.html', {'trips': trips})
