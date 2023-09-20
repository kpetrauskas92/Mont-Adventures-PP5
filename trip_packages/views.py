from django.views import View
from django.shortcuts import render
from django.db.models import Q
from ast import literal_eval
from .models import Trips

MONTHS = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]


def generate_filter_options(model, field_name, display_func=None):
    """
    Generate a list of unique filter options for a given field in a model.
    """
    values = list(model.objects.values_list(field_name, flat=True).distinct())
    if display_func:
        return [{'value': v, 'display': display_func(v)} for v in values]
    else:
        return values


class TripPackages(View):
    """
    TripPackages view for displaying and filtering available travel packages.

    - Fetches all records from the Trips model.
    - Handles filtering based on query parameters.
    - Supports HTMX for partial page updates.
    """
    def get_filter_values(self, request, display_name, model_name):
        """
        Extracts and validates filter values from the request
        for a given filter name.
        """
        filter_values = request.GET.getlist(display_name)
        if filter_values:
            if model_name == "season":
                filter_values = [literal_eval(val) for val in filter_values]
            if model_name in ['price', 'duration',
                              'max_group_size', 'difficulty']:
                filter_values = [
                    val for val in filter_values if val.isnumeric()]
        return filter_values

    def get(self, request):
        """
        Handles GET requests for the TripPackages view.

        - Initializes filters and display_filters dictionaries.
        - Validates query params to ensure they match the expected types.
        - Builds a query using Q objects based on validated query params.
        - Checks for HTMX requests to return only the filtered trips.
        - Renders the appropriate template with context.
        """
        filter_names = ['price', 'duration', 'location', 'season',
                        'max_group_size', 'overall_rating', 'difficulty']
        custom_display_names = {'overall_rating': 'Rating',
                                'max_group_size': 'Group Size'}
        reverse_custom_display_names = {
            v: k for k, v in custom_display_names.items()}

        filters = {}
        display_filters = {}
        query = Q()

        display_funcs = {
            'price': lambda x: x,
            'difficulty': lambda x: Trips(difficulty=x).difficulty_str(),
            'duration': lambda x: f"{x} day{'s' if x > 1 else ''}",
            'season': lambda x: ', '.join([MONTHS[month] for month in x]),
            'max_group_size': lambda x: f"Up to {x}",
            'overall_rating': lambda x: f"{x} Stars",
            'location': lambda x: x
        }

        for name in filter_names:
            display_func = display_funcs.get(name, None)
            filters[name] = generate_filter_options(Trips, name, display_func)
            display_name = custom_display_names.get(
                name, name.replace('_', ' '))
            display_filters[display_name] = filters[name]

            model_name = reverse_custom_display_names.get(display_name, name)
            filter_values = self.get_filter_values(request,
                                                   display_name, model_name)

            if filter_values:
                query &= Q(**{f"{model_name}__in": filter_values})

        trips = Trips.objects.filter(query)

        if request.headers.get('HX-Request'):
            return render(request, 'includes/filter/filtered-trips.html',
                          {'trips': trips})
        else:
            return render(request, 'trip-packages.html',
                          {'filters': display_filters, 'trips': trips})
