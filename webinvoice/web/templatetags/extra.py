from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    return value*arg

@register.filter(name='tax')
def tax(value, arg):
    return value * settings.TAX_RATE * arg

