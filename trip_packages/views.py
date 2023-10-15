from django.views import View
from django.views.generic.detail import DetailView
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from ast import literal_eval
from .models import Trips, AvailableDate
from .trip_utils import display_funcs, MONTHS


def generate_filter_options(model, field_name, display_func=None):
    """
    Generate a list of unique filter options for a given field in a model.
    """
    if field_name == 'season':
        seasons = {
            'Winter': [12, 1, 2],
            'Spring': [3, 4, 5],
            'Summer': [6, 7, 8],
            'Autumn': [9, 10, 11]
        }

        season_filters = {}
        for season, months in seasons.items():
            season_filters[season] = [{'value': m,
                                       'display': MONTHS[m]} for m in months]

        return season_filters

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
        min_price = Trips.objects.aggregate(Min('price'))['price__min']
        max_price = Trips.objects.aggregate(Max('price'))['price__max']
        price_range = {'min_price': min_price, 'max_price': max_price}

        filter_names = ['price', 'duration', 'location', 'season',
                        'max_group_size', 'overall_rating', 'difficulty']
        custom_display_names = {'overall_rating': 'Rating',
                                'max_group_size': 'Group Size'}
        reverse_custom_display_names = {
            v: k for k, v in custom_display_names.items()}

        filters = {}
        display_filters = {}
        query = Q()

        all_trips = Trips.objects.all()
        filtered_trips = []

        for name in filter_names:
            display_func = display_funcs.get(name, None)
            filters[name] = generate_filter_options(Trips, name, display_func)
            display_name = custom_display_names.get(name,
                                                    name.replace('_', ' '))
            display_filters[display_name] = filters[name]

            model_name = reverse_custom_display_names.get(display_name, name)
            filter_values = self.get_filter_values(request,
                                                   display_name,
                                                   model_name)

            if filter_values:
                if model_name == "price":
                    max_price = int(filter_values[0])
                    if max_price != 0:
                        query &= Q(price__lte=max_price)
                elif model_name == "season":
                    filtered_trips = [
                        trip for trip in all_trips
                        if any(month in trip.season for month in filter_values)
                    ]
                    all_trips = filtered_trips
                else:
                    query &= Q(**{f"{model_name}__in": filter_values})
                    filtered_trips = all_trips.filter(query)
                    all_trips = filtered_trips

            if 'price' in request.GET:
                max_price = int(request.GET['price'])
                if max_price != 0:
                    query &= Q(price__lte=max_price)

            filtered_trips = Trips.objects.filter(query)

        if not filtered_trips:
            filtered_trips = all_trips

        if request.headers.get('HX-Request'):
            return render(request, 'includes/filter/filtered-trips.html',
                          {'trips': filtered_trips})
        else:
            return render(request, 'trip-packages.html',
                          {'filters': display_filters,
                           'trips': filtered_trips,
                           'price_range': price_range})


# Utility function to convert month list to season list
def months_to_seasons(months):
    seasons = []
    if any(month in months for month in [12, 1, 2]):
        seasons.append('Winter')
    if any(month in months for month in [3, 4, 5]):
        seasons.append('Spring')
    if any(month in months for month in [6, 7, 8]):
        seasons.append('Summer')
    if any(month in months for month in [9, 10, 11]):
        seasons.append('Autumn')
    return ', '.join(seasons)


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

        seasons = months_to_seasons(trip.season)

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
             'value': seasons},
            {'icon': 'web_elements/svg_icons/trip_icons/group size_icon.svg',
             'alt': 'Group Size Icon', 'label': 'Group Size',
             'value': display_funcs['max_group_size'](trip.max_group_size)},
            {'icon': 'web_elements/svg_icons/trip_icons/difficulty_icon.svg',
             'alt': 'Difficulty Icon', 'label': 'Difficulty',
             'value': display_funcs['difficulty'](trip.difficulty)}
        ]

        context['trip_details'] = trip_details
        return context


class BookingDrawer(View):
    """
    BookingDrawer view for displaying available dates for a specific trip.

    - Fetches the relevant trip record based on the trip_id parameter.
    - Retrieves available dates for the trip.
    - Renders different templates based on whether
    the request is an HTMX request or not.
    """
    template_name = 'includes/booking/booking-drawer.html'

    def get(self, request, trip_id):
        """
        Handles GET requests for the BookingDrawer view.

        - Fetches the Trip object and available dates for that trip.
        - Checks if the request is an HTMX request.
        - Renders the appropriate template with context.
        """
        trip = get_object_or_404(Trips, id=trip_id)
        available_dates = AvailableDate.objects.filter(trips=trip,
                                                       is_available=True)

        if 'HX-Request' in request.headers:
            return render(request,
                          'includes/booking/available-dates.html',
                          {'trip': trip, 'available_dates': available_dates})
        else:
            return render(request, self.template_name,
                          {'trip': trip,
                           'available_dates': available_dates})
