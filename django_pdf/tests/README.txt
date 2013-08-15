Tests require slate:
$>bin/pip install slate

You will need to update the PHANTOMJS_EXECUTABLE variable in the django_pdf/tests/settings.py file.

Then run with:
$>bin/django-admin.py test django_pdf --settings=django_pdf.tests.settings