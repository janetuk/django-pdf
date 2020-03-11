from urllib.parse import urlparse

from django.conf import settings

from django import template
from django.http import Http404

register = template.Library()

@register.simple_tag(takes_context=True)
def pdf_url(context):
    """
    Returns the url of the current page which 
    includes the ?REQUEST_FORMAT_NAME=REQUEST_FORMAT_PDF_VALUE
    """
    request = context['request']
    getvars = request.GET.copy()
    getvars[settings.REQUEST_FORMAT_NAME] = settings.REQUEST_FORMAT_PDF_VALUE

    if len(getvars.keys()) > 1:
        urlappend = "&%s" % getvars.urlencode()
    else:
        urlappend = '%s=%s' % (settings.REQUEST_FORMAT_NAME, settings.REQUEST_FORMAT_PDF_VALUE)

    return '%s?%s' % (request.path, urlappend)


@register.simple_tag
def pdf_url_append(url):
    """
    Returns passed url with pdf parameters appended
    """
    url_parts = urlparse(url)
    url_append = '%s=%s' % (settings.REQUEST_FORMAT_NAME, settings.REQUEST_FORMAT_PDF_VALUE)

    if url_parts.query:
        url_append = '&' + url_append

    return '%s?%s%s' % (url_parts.path, url_parts.query, url_append)
