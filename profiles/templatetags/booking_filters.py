from django import template

register = template.Library()


@register.filter
def filter_not_canceled(queryset):
    return [item for item in queryset if item.status != 'canceled']
