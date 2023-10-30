from .models import Trips
from datetime import datetime, timedelta
from django_countries import countries


MONTHS = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

display_funcs = {
    'price': lambda x: x,
    'difficulty': lambda x: Trips(difficulty=x).difficulty_str(),
    'duration': lambda x: f"{x} day{'s' if x > 1 else ''}",
    'season': lambda x: ', '.join([MONTHS[month] for month in x]),
    'max_group_size': lambda x: f"Up to {x}",
    'overall_rating': lambda x: f"{x}",
    'location': lambda x: 'UK' if x == 'GB' else dict(countries).get(x, x),
}


def generate_available_dates(season, duration, include_departure_day=True):
    """
    Generates a list of available dates based on the
    provided season and duration.
    """
    available_dates = []
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    one_year_later = today + timedelta(days=365)

    active_duration = duration - 1 if not include_departure_day else duration

    for year in [today.year, today.year + 1]:
        for month in season:
            first_day = datetime(year, month, 1).date()
            last_day = (
                datetime(year, month + 1, 1).date() - timedelta(days=1)
                if month < 12
                else datetime(year + 1, 1, 1).date() - timedelta(days=1)
            )

            start_date = first_day
            while start_date <= last_day - timedelta(days=active_duration):
                if (
                    start_date > tomorrow and
                    start_date.weekday() == 4 and
                    start_date <= one_year_later
                ):
                    available_dates.append(start_date)
                start_date += timedelta(days=1)

    return available_dates


def populate_filled_stars(trips_queryset):
    for trip in trips_queryset:
        trip.filled_stars = 0 if trip.overall_rating is None else round(
            trip.overall_rating)
    return trips_queryset
