from django import template
import os

register = template.Library()


@register.filter(name='filename')
def filename(value):
    return os.path.basename(value)
