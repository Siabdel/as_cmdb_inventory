from django import template

register = template.Library()

@register.filter
def formatCurrency(value):
    """Formate un nombre en devise (ex: 1234.56 → 1 234,56 €)."""
    try:
        return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return value

@register.simple_tag
def add(value, arg):
    """Ajoute deux nombres."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def subtract_tag(value, arg):
    """Soustrait deux nombres (tag syntax)."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='subtract')
def subtract_filter(value, arg):
    """Soustrait deux nombres (filter syntax)."""
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

@register.filter(name='divide')
def divide_filter(value, arg):
    """Divise deux nombres."""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def getMovementTypeLabel(value):
    """Retourne le libellé du type de mouvement."""
    labels = {
        'entry': 'Entrée',
        'exit': 'Sortie',
        'transfer': 'Transfert',
        'repair': 'Réparation',
        'maintenance': 'Maintenance',
    }
    return labels.get(value, value)

@register.filter
def formatDate(value):
    """Formate une date."""
    try:
        return value.strftime('%Y-%m-%d %H:%M:%S')
    except (AttributeError, TypeError):
        return value
