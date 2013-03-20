#!/usr/bin/env python

import os.path
from django import http
from django.http import HttpResponse
from django.conf import settings

from StringIO import StringIO
from subprocess import Popen, PIPE
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


def transform_to_pdf(response, name):
    
    # trick phantom into sending the pdf to STDOUT
    output_file = settings.APP_ROOT + '/stdout.pdf'
    
    if not os.path.islink(output_file):
        os.symlink("/dev/stdout", output_file)
    
    # construct parameters to our phantom instance
    args = [settings.APP_ROOT + "/bin/phantomjs",
            os.path.dirname(__file__)+"/html2pdf.js",
            output_file]
    
    # create the process
    p = Popen(args, stdin=PIPE, stdout=PIPE)
    
    # send the html to stdin and read the stdout
    print response.content.encode("UTF-8")
    contents = p.communicate(input = response.content.encode("UTF-8"))[0]
    
    # return contents to browser with appropiate mimetype
    response = http.HttpResponse(contents, mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=%s.pdf' % name
    return response
    

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
