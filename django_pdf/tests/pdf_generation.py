import slate
import StringIO
import tempfile
from os import listdir

from django.test import TestCase
from django.http import HttpResponse

from django_pdf.middleware import transform_to_pdf

class TestPDFGeneration(TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an example html file
        cls.string_contents = 'Hello world'
        html = """<html>
                <body>
                <p>%s</p>
                </body>
                </html>""" % cls.string_contents
        
        # Create a stubbed response object
        cls.response = HttpResponse(html)

    def test_pdf_generation(self):
        """ Check we can create a simple pdf file """
        # create our pdf
        response = transform_to_pdf(self.response)
        
        # Check the generated pdf contains our contents
        pdf_content = get_content_from_pdf(response.content)
        assert self.string_contents in pdf_content
    
    def test_filename_handing(self):
        """ Checks the filename handling in the Content-Disposition header """
        # Check a default name is provided
        response = transform_to_pdf(self.response)
        assert 'page.pdf' in response['Content-Disposition']
        
        # Check we can provide our own filename
        response = transform_to_pdf(self.response,'','testfile')
        assert 'testfile.pdf' in response['Content-Disposition']

    def test_temporary_file_cleanup(self):
        """
        Checks that all temporary files are cleaned up after generating the pdf
        """
        temp_files_before = len(listdir(tempfile.gettempdir()))
        response = transform_to_pdf(self.response)
        temp_files_after = len(listdir(tempfile.gettempdir()))
        assert temp_files_before == temp_files_after


def get_content_from_pdf(content):
    """
    Helper function to extract text from pdf using the slate library
    """
    
    output = StringIO.StringIO()
    output.write(content)
    
    doc = ''
    for page in slate.PDF(output):
        doc = doc + page.decode("UTF-8").replace('\t',' ')
    output.close()
    
    return doc