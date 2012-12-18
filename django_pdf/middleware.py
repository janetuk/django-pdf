#!/usr/bin/env python

import os.path
import xhtml2pdf.pisa as pisa
import cStringIO as StringIO
import cgi
from django import http
from django.http import HttpResponse
from django.conf import settings

REQUEST_FORMAT_NAME = getattr(settings, 'REQUEST_FORMAT_NAME', 'format')
REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'REQUEST_FORMAT_PDF_VALUE', 'pdf')
TEMPLATE_PDF_CHECK = getattr(settings, 'TEMPLATE_PDF_CHECK', 'DJANGO_PDF_OUTPUT')


def fetch_resources(uri, rel):
    """
    Prepares paths for pisa
    """
    path = os.path.join(settings.STATIC_ROOT,
            uri.replace(settings.STATIC_URL, ""))
    return path


def transform_to_pdf(response, name):
    content = response.content.encode("UTF-8")
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(content), result, link_callback=fetch_resources)
    if not pdf.err:
        response = http.HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'filename=%s.pdf' % name
        return response
    else:
        return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))


class PdfMiddleware(object):
    """
    Converts the response to a pdf one.
    """
    def process_response(self, request, response):
        format = request.GET.get(REQUEST_FORMAT_NAME, None)
        if format == REQUEST_FORMAT_PDF_VALUE:
            path = request.path
            response = transform_to_pdf(response, path[path.rfind('/')+1:])
        return response
