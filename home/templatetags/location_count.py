from django import template
from django_countries.data import COUNTRIES

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter to retrieve an item from a dictionary using its key.
    """
    return dictionary.get(key)


@register.filter(name='country_name')
def country_name(country_code):
    """
    Template filter to convert a country code to its name, with a special case
    for the United Kingdom.
    """
    country_name = COUNTRIES.get(country_code, country_code)
    if country_name == "United Kingdom of Great Britain and Northern Ireland":
        return "UK"
    return country_name
