from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Q, Min, Max
from ast import literal_eval
from .models import Trips, TripOverview, AvailableDate, FavoriteTrip, Reviews
from profiles.models import UserProfile
from .trip_utils import display_funcs, MONTHS, populate_filled_stars
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from .forms import ReviewForm
from django.db.models import Prefetch
from django.utils import timezone


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

    if field_name == 'overall_rating':
        return [{'value': '0', 'display': "New"}] + \
            [{'value': str(i),
              'display': f"{i} star{'s' if i > 1 else ''}"}
                for i in range(1, 6)]

    values = list(
        model.objects.values_list(
            field_name, flat=True).distinct().order_by(field_name))
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

        filtered_trips = all_trips.order_by('-price')

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

            local_query = Q()

            if filter_values:
                if model_name == "price":
                    max_price = int(filter_values[0])
                    if max_price != 0:
                        local_query &= Q(price__lte=max_price)

                elif model_name == "season":
                    season_filtered_trip_pks = []
                    for trip in filtered_trips:
                        if any(month in trip.season
                               for month in filter_values):
                            season_filtered_trip_pks.append(trip.pk)
                    filtered_trips = Trips.objects.filter(
                        pk__in=season_filtered_trip_pks)

                else:
                    local_query &= Q(**{f"{model_name}__in": filter_values})

                if model_name != "season":
                    filtered_trips = filtered_trips.filter(local_query)

                if 'price' in request.GET:
                    max_price = int(request.GET['price'])
                    if max_price != 0:
                        query &= Q(price__lte=max_price)

                if model_name == "overall_rating":
                    star_queries = Q()
                    for value in filter_values:
                        if value == '0':
                            star_queries |= Q(overall_rating=0.0)
                        else:
                            star_rating = int(value)
                            if star_rating == 1:
                                lower_bound = 0.0
                            else:
                                lower_bound = (star_rating - 1) + 0.05
                            upper_bound = star_rating + 0.95
                            star_queries |= Q(
                                overall_rating__gte=lower_bound,
                                overall_rating__lt=upper_bound)

                    filtered_trips = filtered_trips.filter(star_queries)

        if request.user.is_authenticated:
            user_favorites = FavoriteTrip.objects.filter(
                user=request.user).values_list('trip', flat=True)
        else:
            user_favorites = []

        for trip in filtered_trips:
            filtered_trips = populate_filled_stars(filtered_trips)
            trip.review_count = trip.reviews.filter(is_approved=True).count()
            trip.duration_str = display_funcs['duration'](trip.duration)
            trip.duration_icon = (
                'web_elements/svg_icons/trip_icons/duration_icon.svg')

            trip.difficulty_str = display_funcs['difficulty'](trip.difficulty)
            trip.difficulty_icon = (
                'web_elements/svg_icons/trip_icons/difficulty_icon.svg')

            trip.location_str = display_funcs['location'](trip.location)
            trip.location_icon = (
                'web_elements/svg_icons/trip_icons/location_icon.svg')

        if request.headers.get('HX-Request'):
            return render(request,
                          'includes/filter/filtered-trips.html',
                          {'trips': filtered_trips,
                           'user_favorites': user_favorites})
        else:
            return render(request, 'trip-packages.html',
                          {'filters': display_filters,
                           'trips': filtered_trips,
                           'price_range': price_range,
                           'user_favorites': user_favorites})

    def post(self, request, *args, **kwargs):
        trip_id = self.kwargs.get('trip_id', None)
        if trip_id is None:
            return HttpResponseBadRequest("Missing trip_id")

        if not request.user.is_authenticated:
            return HttpResponse("User not authenticated", status=403)

        try:
            trip = Trips.objects.get(id=trip_id)
        except Trips.DoesNotExist:
            return HttpResponse("Trip does not exist", status=404)

        is_favorited = FavoriteTrip.objects.filter(user=request.user,
                                                   trip=trip).exists()

        if is_favorited:
            FavoriteTrip.remove_favorite(request.user, trip)
        else:
            FavoriteTrip.add_favorite(request.user, trip)

        new_status = not is_favorited

        return JsonResponse({'status': 'success',
                             'is_favorited': new_status}, status=200)


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

        # Fetch reviews for this trip
        reviews = Reviews.objects.filter(trip=trip, is_approved=True)
        review_count = reviews.count()

        filled_stars = 0 if trip.overall_rating is None else round(
            trip.overall_rating)

        all_trips = Trips.objects.all()

        for each_trip in all_trips:
            each_trip.filled_stars = round(each_trip.overall_rating)

        context['reviews'] = reviews
        context['filled_stars'] = filled_stars
        context['review_count'] = review_count

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
             'value': display_funcs['difficulty'](trip.difficulty)},
            {'icon': 'web_elements/svg_icons/trip_icons/rating_icon.svg',
             'alt': 'Rating Icon', 'label': 'Rating',
             'value': display_funcs['overall_rating'](trip.overall_rating)},
        ]

        is_favorite = False
        if self.request.user.is_authenticated:
            is_favorite = FavoriteTrip.objects.filter(
                user=self.request.user, trip=self.object
            ).exists()

        context['is_favorite'] = is_favorite
        context['trip_details'] = trip_details

        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()

        try:
            trip_overview = TripOverview.objects.get(trip=self.object)
        except TripOverview.DoesNotExist:
            trip_overview = None
        context['trip_overview'] = trip_overview

        return context


def trip_overview(request, trip_id):
    trip = get_object_or_404(Trips, pk=trip_id)
    try:
        trip_overview = TripOverview.objects.get(trip=trip)
    except TripOverview.DoesNotExist:
        trip_overview = None

    return render(request, 'includes/overview/trip-overview.html', {
        'trip_overview': trip_overview})


class TripReviews(ListView):
    """
    List and handle trip reviews.

    This view class fetches and displays all approved reviews
    related to a specific trip. It also handles the review form
    for both adding new reviews and editing existing ones.
    """
    template_name = 'trip-reviews.html'

    def get(self, request, trip_id, review_id=None, *args, **kwargs):
        trip = Trips.objects.get(pk=trip_id)

        reviews = Reviews.objects.select_related('user').prefetch_related(
            Prefetch('user__userprofile', queryset=UserProfile.objects.all())
        ).filter(trip=trip, is_approved=True)

        if review_id:
            existing_review = get_object_or_404(Reviews, id=review_id,
                                                user=request.user)
            review_form = ReviewForm(instance=existing_review)
        else:
            review_form = ReviewForm()

        context = {
            'reviews': reviews,
            'review_form': review_form,
            'trip': trip,
        }

        return render(request, 'includes/reviews/trip-reviews.html', context)


def trip_review_form(request, trip_id, review_id=None):
    """
    Handle the trip review form for adding and editing reviews.

    This function displays a form for adding a new review
    or editing an existing one. It also handles the submission of this form,
    validating the input and either saving a
    new review or updating an existing one.
    """
    trip = get_object_or_404(Trips, id=trip_id)

    existing_review = None
    if review_id:
        existing_review = get_object_or_404(Reviews,
                                            id=review_id,
                                            user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST,
                          request.FILES,
                          instance=existing_review)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user
            new_review.trip = trip
            trip.overall_rating = 0.0
            trip.save()
            new_review.save()
            return render(request, 'includes/reviews/trip-review-success.html')
        else:
            form_action = reverse(
                'trip_review_form_with_id',
                args=[trip.id, review_id]) if review_id else reverse(
                    'trip_review_form',
                    args=[trip.id])
            return render(request, 'includes/reviews/trip-review-form.html',
                          {'review_form': form,
                           'trip': trip,
                           'form_action': form_action})
    else:
        form = ReviewForm(instance=existing_review)

    form_title = 'Edit Review' if existing_review else 'Add Review'
    form_action = reverse(
        'trip_review_form_with_id',
        args=[trip.id, review_id]) if review_id else reverse(
            'trip_review_form',
            args=[trip.id])

    context = {
        'review_form': form,
        'trip': trip,
        'form_title': form_title,
        'form_action': form_action
    }
    return render(request, 'includes/reviews/trip-review-form.html', context)


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

        # Fetch all future available dates for the trip.
        future_dates = AvailableDate.objects.filter(
            trips=trip, 
            start_date__gte=timezone.now().date()
        ).order_by('start_date')

        available_dates = [
            date for date in future_dates if date.is_currently_available]

        if 'HX-Request' in request.headers:
            template = 'includes/booking/available-dates.html'
        else:
            template = self.template_name

        return render(request, template, {
            'trip': trip, 'available_dates': available_dates})
