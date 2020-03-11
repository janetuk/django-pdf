
from django.conf import settings

def check_format(request):
    """
    Adds a TEMPLATE_PDF_CHECK variable to the context.
    This var will normally be used in templates like this:
    {% if DJANGO_PDF_OUTPUT %}
        ... content to be displayed only in the PDF output
    {% endif %}
    or:
    {% if not DJANGO_PDF_OUTPUT %}
        ... content that won't be displayed only in the PDF output
    {% endif %}

    Notice:
    Here the value of TEMPLATE_PDF_CHECK settings var is the default one, i.e.
    DJANGO_PDF_OUTPUT. You can change this in your settings
    """
    format = request.GET.get(settings.REQUEST_FORMAT_NAME, None)
    if format == settings.REQUEST_FORMAT_PDF_VALUE:
        return {settings.TEMPLATE_PDF_CHECK: True}
    else:
        return {settings.TEMPLATE_PDF_CHECK: False}
