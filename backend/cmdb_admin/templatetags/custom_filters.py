from django import template

register = template.Library()

@register.filter(name='length_minus')
def length_minus(value, arg):
    try:
        return len(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def add(value, arg):
    """Ajoute deux nombres."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='subtract')
def subtract(value, arg):
    """Soustrait deux nombres."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='multiply')
def multiply_filter(value, arg):
    """Multiplie deux nombres (filter syntax: {{ value|multiply:arg }})."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def multiply(value, arg):
    """Multiplie deux nombres (tag syntax: {% multiply value arg as result %})."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0