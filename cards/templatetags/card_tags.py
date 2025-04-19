from django import template
import json

register = template.Library()

@register.filter
def pretty_json(value):
    """Форматирует JSON для удобного отображения в шаблоне."""
    return json.dumps(value, indent=4, ensure_ascii=False)