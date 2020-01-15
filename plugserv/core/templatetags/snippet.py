# import html

from django import template
from django.conf import settings
from django.template import loader
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse


register = template.Library()


@register.simple_tag
def snippet(request, escaped, include_powered_by=True, serve_id=None):
    if serve_id is None:
        serve_id = settings.EXAMPLE_SERVE_ID
    context = {
        'serve_url': request.build_absolute_uri(reverse('serve_plug', args=(serve_id, ))),
        'js_url': request.build_absolute_uri(reverse('js_v1')),
        'include_powered_by': include_powered_by,
    }

    output = loader.get_template('snippet.html').render(context, request)
    if escaped:
        output = escape(output)
    else:
        output = mark_safe(output)

    return output
