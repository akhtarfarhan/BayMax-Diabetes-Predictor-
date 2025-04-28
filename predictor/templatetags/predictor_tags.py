from django import template
import json

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def json_parse(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []