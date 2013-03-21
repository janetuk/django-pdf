#!/usr/bin/env python

import os
import tempfile

from subprocess import call

from django.http import HttpResponse
from django.conf import settings

REQUEST_FORMAT_NAME = getattr(settings, 'REQUEST_FORMAT_NAME', 'format')
REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'REQUEST_FORMAT_PDF_VALUE', 'pdf')
TEMPLATE_PDF_CHECK = getattr(settings, 'TEMPLATE_PDF_CHECK', 'DJANGO_PDF_OUTPUT')
PHANTOMJS_EXECUTABLE = getattr(settings, 'PHANTOMJS_EXECUTABLE', 'phantomjs')

def transform_to_pdf(response, host, name):
    """
    This function writes the html to a temp file and passes it to PhantomJS
    which renders it to a temp PDF file, the contents of which are rendered 
    back to the client
    """
    # create a temp file to write our HTML to
    input_file = tempfile.NamedTemporaryFile(delete=False)
    
    # insert base so that static resources are loaded correctly
    content = response.content.encode("UTF-8")
    content = content.replace('<head>','<head><base href="%s">' % host)
    
    input_file.write(content)
    
    # construct parameters to our phantom instance
    args = [PHANTOMJS_EXECUTABLE,
            os.path.dirname(__file__)+"/html2pdf.js",
            input_file.name,
            input_file.name+'.pdf']
    
    # create the process
    p = call(args)
    
    # read the generated pdf output
    output_file = open(input_file.name+'.pdf','rb')
    
    contents = output_file.read()
    
    # delete the files
    input_file.close()
    output_file.close()
    os.remove(output_file.name)
    
    # return contents to browser with appropriate mimetype
    response = HttpResponse(contents, content_type='application/pdf')
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
            response = transform_to_pdf(response, request.build_absolute_uri('/'), path[path.rfind('/')+1:])
        return response
