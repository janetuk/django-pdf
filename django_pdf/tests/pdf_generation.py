# encoding: utf-8
import slate
import StringIO
import tempfile
from os import listdir

from django.test import TestCase
from django.http import HttpResponse

from django_pdf.middleware import transform_to_pdf, get_filename


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
        response = transform_to_pdf(self.response, '', 'testfile')
        assert 'testfile.pdf' in response['Content-Disposition']

    def test_temporary_file_cleanup(self):
        """
        Checks that all temporary files are cleaned up after generating the pdf
        """
        temp_files_before = len(listdir(tempfile.gettempdir()))
        transform_to_pdf(self.response)
        temp_files_after = len(listdir(tempfile.gettempdir()))
        assert temp_files_before == temp_files_after

    def test_character_encodings(self):
        """
        Tests that the pdf generation can support various character sets for 
        different alphabets
        """
        html = u"""<html>
                <body>
                <p>Can the pdf generate these?</p>
                    ISO 8859-5 - чуоюющяа (Cyrillic ru)
                    ISO 8859-6 - ﻗﻠﯿﻼ (Arabic ar)
                    ISO 8859-7 - ΔΦψ (Greek el)
                    ISO 8859-8 - úŵËÕŷîâöòÆṫ (Hebrew he)
                    ISO 8859-14 - Ṫêċï (Welsh and Gaelic gd/ga)
                    ISO 639 - 電电 (Chinese simplified & traditional zh)
                    ISO-2022-JP - ゴシック (Japanese ja)
                </body>
                </html>"""

        response = HttpResponse(html)
        response = transform_to_pdf(response)

        # Check the generated pdf contains our contents
        pdf_content = get_content_from_pdf(response.content)

        assert u'чуоюющяа' in pdf_content
        assert u'ﻗﻠﯿﻼ' in pdf_content
        assert u'ΔΦψ' in pdf_content
        assert u'úŵËÕŷîâöòÆṫ' in pdf_content
        assert u'Ṫêċï' in pdf_content
        assert u'電电' in pdf_content
        assert u'ゴシック' in pdf_content

        assert u'\x00' not in pdf_content

    def test_get_filename_method(self):
        assert get_filename('') == 'page.pdf'
        assert get_filename('/') == 'page.pdf'
        assert get_filename('/test') == 'test.pdf'
        assert get_filename('/test?a=etc') == 'test.pdf'
        assert get_filename('/test/') == 'test.pdf'
        assert get_filename('/test/?a=etc') == 'test.pdf'


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