from jinja2 import Environment

from django.templatetags.static import static
from django.urls import reverse
from django.core.exceptions import NON_FIELD_ERRORS

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'NON_FIELD_ERRORS': NON_FIELD_ERRORS
    })
    return env