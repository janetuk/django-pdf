#!/usr/bin/env python

import os.path
from django import http
from django.http import HttpResponse
from django.conf import settings

from StringIO import StringIO
from subprocess import Popen, call, PIPE
import os
import tempfile

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
    """
    This function writes the html to a temp file and passes it to PhantomJS
    which renders it to a temp PDF file, the contents of which are rendered 
    back to the client
    """
    # create a temp file to write our HTML to
    input_file = tempfile.NamedTemporaryFile(delete=True)
    input_file.write(response.content.encode("UTF-8"))
    
    # construct parameters to our phantom instance
    args = [settings.APP_ROOT + "/bin/phantomjs",
            os.path.dirname(__file__)+"/html2pdf.js",
            input_file.name,
            input_file.name+'.pdf']
    
    # create the process
    p = call(args)
    
    # read the generated pdf output
    output_file = open(input_file.name+'.pdf','r')

    contents = output_file.read()

    # delete the files
    input_file.close()
    output_file.close()
    os.remove(output_file.name)
    
    # return contents to browser with appropriate mimetype
    response = http.HttpResponse(contents, content_type='application/pdf')
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
            if path.endswith('/'):
                path = path[:-1]
            response = transform_to_pdf(response, path[path.rfind('/')+1:])
        return response
