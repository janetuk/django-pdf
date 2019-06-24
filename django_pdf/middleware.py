#!/usr/bin/env python

import os
import tempfile

from subprocess import call

from django.http import HttpResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

REQUEST_FORMAT_NAME = getattr(settings, 'REQUEST_FORMAT_NAME', 'format')
REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'REQUEST_FORMAT_PDF_VALUE', 'pdf')
TEMPLATE_PDF_CHECK = getattr(settings, 'TEMPLATE_PDF_CHECK', 'DJANGO_PDF_OUTPUT')
PHANTOMJS_EXECUTABLE = getattr(settings, 'PHANTOMJS_EXECUTABLE', 'phantomjs')


def transform_to_pdf(response, host='', filename='page.pdf'):
    """
    This function writes the html to a temp file and passes it to PhantomJS
    which renders it to a temp PDF file, the contents of which are rendered 
    back to the client
    """
    # create a temp file to write our HTML to
    input_file = tempfile.NamedTemporaryFile(prefix='django_pdf_', delete=False)
    # And one to store the pdf output in
    output_file = tempfile.NamedTemporaryFile(prefix='django_pdf_',
                                              suffix='.pdf',
                                              delete=False)
    
    # insert <base> tag so that static resources are loaded correctly
    content = response.content.decode("UTF-8").encode("UTF-8")

    if host != 'http://testserver/':
        content = content.replace('<head>','<head><base href="%s">' % host)

    input_file.write(content)
    input_file.close()

    # construct parameters to our phantom instance
    args = [PHANTOMJS_EXECUTABLE,
            os.path.dirname(__file__)+"/html2pdf.js",
            input_file.name,
            output_file.name]

    # create the process
    p = call(args)

    # read the generated pdf output
    contents = output_file.read()

    # delete the files
    output_file.close()
    os.remove(input_file.name)
    os.remove(output_file.name)

    # return contents to browser with appropriate mimetype
    response = HttpResponse(contents, content_type='application/pdf')

    # Add extension if missing
    if not filename.endswith('.pdf'):
        filename = "%s.pdf" % filename

    response['Content-Disposition'] = 'filename=%s' % filename
    return response

def get_filename(path):
    """
    Returns a string representation of the url path to be used as a filename
    """
    if path.find('?') > 0:
        path = path[:path.find('?')]
    if path.endswith('/'):
        path = path[:-1]
    filename = path[path.rfind('/')+1:]
    if not filename:
        filename = 'page'
    return filename+'.pdf'

class PdfMiddleware(MiddlewareMixin):
    """
    Converts the response to a pdf one.
    """
    def process_response(self, request, response):
        format = request.GET.get(REQUEST_FORMAT_NAME, None)
        if format == REQUEST_FORMAT_PDF_VALUE:
            filename = get_filename(request.path)
            response = transform_to_pdf(response,
                                        request.build_absolute_uri('/'),
                                        filename)
        return response

