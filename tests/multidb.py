from django.test import TestCase

from .app.models import Category


class MultiDBTests(TestCase):
    """
    Create and retrieve instances with the same id in different databases, make
    sure they have different ids if the models' multi_db attribute is True
    """

    @classmethod
    def setUpClass(cls):
        Category.multi_db = True

    @classmethod
    def tearDownClass(cls):
        Category.multi_db = False  # back to default

    def test_multi_db(self):
        Category.objects.using('db1').create(pk=1, name='Category on db1')
        Category.objects.using('db2').create(pk=1, name='Category on db2')

        c1 = Category.objects.using('db1').get(pk=1)
        c2 = Category.objects.using('db2').get(pk=1)

        self.assertEqual(c1.name, 'Category on db1')
        self.assertEqual(c2.name, 'Category on db2')

        self.assertEqual(c1._state.db, 'db1')
        self.assertEqual(c2._state.db, 'db2')

        self.assertIsNot(c1, c2)
