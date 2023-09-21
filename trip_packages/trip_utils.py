from .models import Trips

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
    'overall_rating': lambda x: f"{x} Stars",
    'location': lambda x: x
}
