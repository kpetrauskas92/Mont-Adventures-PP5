from django.views import View
from django.shortcuts import render
from django.db.models import Q
from .models import Trips


class TripPackages(View):
    """
    TripPackages view for displaying and filtering available travel packages.

    - Fetches all records from the Trips model.
    - Handles filtering based on query parameters.
    - Supports HTMX for partial page updates.
    """
    def get(self, request):
        """
            Handles GET requests for the TripPackages view.

            - Initializes filters and display_filters dictionaries.
            - Validates query params to ensure they match the expected types.
            - Builds a query using Q objects based on validated query params.
            - Checks for HTMX requests to return only the filtered trips.
            - Renders the appropriate template with context.
        """

        filter_names = ['price', 'duration', 'location',
                        'season', 'max_group_size',
                        'overall_rating', 'difficulty']
        filters = {}
        display_filters = {}

        # Initialize an empty Q object for complex queries
        query = Q()

        for name in filter_names:
            filters[name] = list
            (Trips.objects.values_list(name, flat=True).distinct())
            display_name = name.replace('_', ' ')
            display_filters[display_name] = filters[name]

            # Capture filters from request
            filter_values = request.GET.getlist(name)

            if filter_values:
                # Validate if the value is numeric for fields
                # that are supposed to be numeric
                if name in ['price', 'duration',
                            'max_group_size', 'difficulty']:
                    filter_values = [
                        val for val in filter_values if val.isnumeric()
                    ]

                if filter_values:
                    query &= Q(**{f"{name}__in": filter_values})

        # Apply the query filters to the Trips objects
        trips = Trips.objects.filter(query)

        if request.headers.get('HX-Request'):
            return render(request, 'includes/filter/filtered-trips.html',
                          {'trips': trips})
        else:
            return render(request, 'trip-packages.html', {
                'filters': display_filters,
                'trips': trips
            })
