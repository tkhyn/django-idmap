import sys

from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'NAME': 'idmapper',
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    INSTALLED_APPS=('django.contrib.auth',
                    'django.contrib.contenttypes',
                    'django.contrib.sessions',
                    'django.contrib.admin',
                    'idmapper',),
)

from django.test.simple import DjangoTestSuiteRunner

test_runner = DjangoTestSuiteRunner(verbosity=1)
test_runner.run_tests(['idmapper', ])
