#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-pdf',
    version='0.1',
    description='django-pdf despite its simplicity has the pompous mission of automagically converting on-the-fly views HTML output to PDF --without modifying your views.',
    long_description=open('README.txt').read(),
    author='directeur',
    maintainer="Chris Bailey",
    maintainer_email="chris.p.bailey@gmail.com",
    license="GPL 2.0",
    url='https://github.com/chrispbailey/django-pdf/',
    packages=['django_pdf',],
    package_data={
        'django_pdf': ['templatetags/*',],
    },
)
