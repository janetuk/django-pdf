#!/usr/bin/env python

import os.path
from django import http
from django.http import HttpResponse
from django.conf import settings

import subprocess
import os

REQUEST_FORMAT_NAME = getattr(settings, 'REQUEST_FORMAT_NAME', 'format')
REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'REQUEST_FORMAT_PDF_VALUE', 'pdf')
TEMPLATE_PDF_CHECK = getattr(settings, 'TEMPLATE_PDF_CHECK', 'DJANGO_PDF_OUTPUT')

def fetch_resources(uri, rel):
    """
    Prepares paths for pisa
    """
    if uri.startswith('http'):
        return uri

    path = os.path.join(settings.STATIC_ROOT,
            uri.replace(settings.STATIC_URL, ""))
    return path


def transform_to_pdf(response, url):
    output_file = settings.APP_ROOT + '/stdout.pdf'
    args = [settings.APP_ROOT + "/bin/phantomjs",
            os.path.dirname(__file__)+"/html2pdf.js",
            url, output_file]
    
    #print args

    contents = subprocess.check_output(args)
    
    response = http.HttpResponse(contents, mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=%s.pdf' % 'output'
    return response
    

class PdfMiddleware(object):
    """
    Converts the response to a pdf one.
    """
    def process_response(self, request, response):
        format = request.GET.get(REQUEST_FORMAT_NAME, None)
        if format == REQUEST_FORMAT_PDF_VALUE:
            path = 'http://'
            if request.is_secure():
                path = 'https://'
            path = path + request.get_host() + request.path
            response = transform_to_pdf(response, path)
        return response
