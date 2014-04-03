#!/usr/bin/env python

from setuptools import setup, find_packages

# imports __version__ and __version_info__ without importing module
exec(open('idmapper/version.py').read())
dev_status = __version_info__[3]

if dev_status == 'alpha' and not __version_info__[4]:
    dev_status = 'pre'

DEV_STATUS = {'pre': '2 - Pre-Alpha',
              'alpha': '3 - Alpha',
              'beta': '4 - Beta',
              'rc': '5 - Production/Stable',
              'final': '5 - Production/Stable'}

setup(
    name='django-idmapper',
    version=__version__,
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/dcramer/django-idmapper',
    description = 'An identify mapper for the Django ORM',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'License :: OSI Approved :: BSD License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Database'
    ],
)
