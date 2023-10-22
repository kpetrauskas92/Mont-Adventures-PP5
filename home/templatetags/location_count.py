from django import template
from django_countries.data import COUNTRIES

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='country_name')
def country_name(country_code):
    country_name = COUNTRIES.get(country_code, country_code)
    if country_name == "United Kingdom of Great Britain and Northern Ireland":
        return "UK"
    return country_name
