# range_filters.py
from django import template
register = template.Library()

@register.filter
def star_range(_):
    return range(1, 6)  # Always 5 stars
