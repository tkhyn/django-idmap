DEBUG = True
SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'NAME': 'idmap',
        'ENGINE': 'django.db.backends.sqlite3',
    },
    'db1': {
        'NAME': 'db1',
        'ENGINE': 'django.db.backends.sqlite3',
    },
    'db2': {
        'NAME': 'db2',
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

INSTALLED_APPS = (
    'idmap',
    'django_nose',
    'tests.app',
)

MIDDLEWARE_CLASSES = ()

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
