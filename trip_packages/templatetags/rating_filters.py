from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def generate_range(value):
    if value is None:
        return range(0)
    return range(value)
