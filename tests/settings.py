DEBUG = True
SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'NAME': 'idmap',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'idmap',
    'django_nose',
    'tests',
)

MIDDLEWARE_CLASSES = ()  # so that Django 1.7 does not complain

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
