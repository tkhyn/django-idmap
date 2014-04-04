from tests import settings as SETTINGS
from django.conf import settings

settings.configure(**{k: getattr(SETTINGS, k) for k in dir(SETTINGS) \
                          if k[0].isupper()})

from django.test.simple import DjangoTestSuiteRunner

test_runner = DjangoTestSuiteRunner(verbosity=1)
test_runner.run_tests(['tests', ])
