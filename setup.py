"""
django-idmap
An identity mapper for the Django ORM
(c) 2014 Thomas Khyn
(c) 2009 David Cramer
Simplified BSD License (see LICENSE.txt)
"""

from setuptools import setup, find_packages
import os


# imports __version__ and __version_info__ without importing module
exec(open('idmap/version.py').read())
dev_status = __version_info__[3]

if dev_status == 'alpha' and not __version_info__[4]:
    dev_status = 'pre'

DEV_STATUS = {'pre': '2 - Pre-Alpha',
              'alpha': '3 - Alpha',
              'beta': '4 - Beta',
              'rc': '4 - Beta',
              'final': '5 - Production/Stable'}

setup(
    name='django-idmap',
    version=__version__,
    author='Thomas Khyn',
    author_email='thomas@ksytek.com',
    url='https://bitbucket.org/tkhyn/django-idmap',
    description='An identity mapper for the Django ORM',
    long_description=open(os.path.join('README.rst')).read(),
    keywords=['django', 'identity', 'mapper'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'License :: OSI Approved :: BSD License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Database'
    ],
    packages=find_packages(exclude=('tests',)),
    install_requires=(
      'Django>=1.4',
    ),
)
