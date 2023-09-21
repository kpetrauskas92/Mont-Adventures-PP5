from django.views import View
from django.views.generic.detail import DetailView
from django.shortcuts import render
from django.db.models import Q
from ast import literal_eval
from .models import Trips
from .trip_utils import display_funcs


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


class TripDetails(DetailView):
    """
    TripDetails view for displaying detailed information
    about a single trip package.

    - Inherits from Django's built-in DetailView.
    - Utilizes the Trips model to fetch the trip details.
    - Adds extra context to the template to display
    icons and labels for trip details.
    """
    model = Trips
    template_name = 'trip-detail.html'
    context_object_name = 'trip'

    def get_context_data(self, **kwargs):
        """
        Gets the context data for rendering the template.

        - Overrides the parent method to add extra context.
        - Specifically adds the trip_details list containing icons,
        labels, and values for trip details.
        - The trip_details list is used for dynamically populating
        the trip's detailed information on the template.
        """
        context = super().get_context_data(**kwargs)
        trip = context['trip']

        # Populate the trip_details list dynamically based on the trip
        trip_details = [
            {'icon': 'web_elements/svg_icons/trip_icons/duration_icon.svg',
             'alt': 'Duration Icon', 'label': 'Duration',
             'value': display_funcs['duration'](trip.duration)},
            {'icon': 'web_elements/svg_icons/trip_icons/location_icon.svg',
             'alt': 'Location Icon', 'label': 'Location',
             'value': display_funcs['location'](trip.location)},
            {'icon': 'web_elements/svg_icons/trip_icons/season_icon.svg',
             'alt': 'Season Icon', 'label': 'Season',
             'value': display_funcs['season'](trip.season)},
            {'icon': 'web_elements/svg_icons/trip_icons/group size_icon.svg',
             'alt': 'Group Size Icon', 'label': 'Group Size',
             'value': display_funcs['max_group_size'](trip.max_group_size)},
            {'icon': 'web_elements/svg_icons/trip_icons/difficulty_icon.svg',
             'alt': 'Difficulty Icon', 'label': 'Difficulty',
             'value': display_funcs['difficulty'](trip.difficulty)}
        ]

        context['trip_details'] = trip_details
        return context
