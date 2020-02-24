from urllib.parse import urlparse

from django import template
from django.http import Http404
from django.conf import settings

register = template.Library()

REQUEST_FORMAT_NAME = getattr(settings, 'REQUEST_FORMAT_NAME', 'format')
REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'REQUEST_FORMAT_PDF_VALUE', 'pdf')
TEMPLATE_PDF_CHECK = getattr(settings, 'TEMPLATE_PDF_CHECK', 'DJANGO_PDF_OUTPUT')

@register.simple_tag(takes_context=True)
def pdf_url(context):
    """
    Returns the url of the current page which 
    includes the ?REQUEST_FORMAT_NAME=REQUEST_FORMAT_PDF_VALUE
    """
    request = context['request']
    getvars = request.GET.copy()
    getvars[REQUEST_FORMAT_NAME] = REQUEST_FORMAT_PDF_VALUE

    if len(getvars.keys()) > 1:
        urlappend = "&%s" % getvars.urlencode()
    else:
        urlappend = '%s=%s' % (REQUEST_FORMAT_NAME, REQUEST_FORMAT_PDF_VALUE)

    return '%s?%s' % (request.path, urlappend)


@register.simple_tag
def pdf_url_append(url):
    """
    Returns passed url with pdf parameters appended
    """
    url_parts = urlparse(url)
    url_append = '%s=%s' % (REQUEST_FORMAT_NAME, REQUEST_FORMAT_PDF_VALUE)

    if url_parts.query:
        url_append = '&' + url_append

    return '%s?%s%s' % (url_parts.path, url_parts.query, url_append)
