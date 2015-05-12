from django.test import TestCase as DjangoTestCase

from idmap import flush_cache


class TestCase(DjangoTestCase):

    def _pre_setup(self):
        super(TestCase, self)._pre_setup()
        flush_cache()
