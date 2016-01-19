from .app.models import Category

from idmap import flush

from ._base import TestCase


class MultiDBTests(TestCase):
    """
    Create and retrieve instances with the same id in different databases, make
    sure they have different ids if the models' multi_db attribute is True
    """

    multi_db = True

    @classmethod
    def setUpClass(cls):
        super(MultiDBTests, cls).setUpClass()
        Category.multi_db = True

    @classmethod
    def tearDownClass(cls):
        super(MultiDBTests, cls).tearDownClass()
        Category.multi_db = False  # back to default

    def setUp(self):
        Category.objects.create(pk=1, name='Category on default')
        Category.objects.using('db1').create(pk=1, name='Category on db1')
        Category.objects.using('db2').create(pk=1, name='Category on db2')

    def test_multi_db(self):

        c0 = Category.objects.get(pk=1)
        c1 = Category.objects.using('db1').get(pk=1)
        c2 = Category.objects.using('db2').get(pk=1)

        self.assertEqual(c0.name, 'Category on default')
        self.assertEqual(c1.name, 'Category on db1')
        self.assertEqual(c2.name, 'Category on db2')

        self.assertEqual(c0._state.db, 'default')
        self.assertEqual(c1._state.db, 'db1')
        self.assertEqual(c2._state.db, 'db2')

        self.assertIs(c0, Category.objects.using('default').get(pk=1))
        self.assertIs(c1, Category.objects.using('db1').get(pk=1))
        self.assertIs(c2, Category.objects.using('db2').get(pk=1))

        self.assertIsNot(c0, c2)
        self.assertIsNot(c0, c2)
        self.assertIsNot(c1, c2)

    def test_flush_db1(self):

        c1 = Category.objects.using('db1').get(pk=1)
        c2 = Category.objects.using('db2').get(pk=1)

        flush(db='db1')

        self.assertIsNot(c1, Category.objects.using('db1').get(pk=1))
        self.assertIs(c2, Category.objects.using('db2').get(pk=1))

    def test_flush_all(self):

        c0 = Category.objects.get(pk=1)
        c1 = Category.objects.using('db1').get(pk=1)
        c2 = Category.objects.using('db2').get(pk=1)

        flush()

        self.assertIsNot(c0, Category.objects.get(pk=1))
        self.assertIsNot(c1, Category.objects.using('db1').get(pk=1))
        self.assertIsNot(c2, Category.objects.using('db2').get(pk=1))
