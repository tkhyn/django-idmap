from django.utils import six

from .app.models import Article, Category, RegularCategory

from ._base import TestCase


class GetRelatedTestsBase(TestCase):
    """
    Getter tests to check the behaviour of IdMapQuerySet.get
    when a 'where' clause is present (when using a related manager)
    """

    def setUp(self):
        Article.use_strong_refs = True

        category = Category.objects.create(name="Category")

        for n in six.moves.xrange(0, 10):
            regcategory = RegularCategory.objects.create(
                              name="RegCategory %d" % n)
            Article.objects.create(name="Article %d" % n,
                                   category=category,
                                   category2=regcategory)

    def run_get_related(self):
        category = Category.objects.get(name="Category")
        regcategory = RegularCategory.objects.get(name="RegCategory 0")

        # using direct and relational lookups
        return id(Article.objects.get(name="Article 0")), \
               id(category.article_set.get(category2=regcategory))


class GetRelatedWeakRefsTests(GetRelatedTestsBase):

    def test_get_related(self):
        # we are not using strong refs, the article retrieved via category
        # lookup is not the same as the directly retrieved one
        self.assertNotEqual(*self.run_get_related())


class GetRelatedStrongRefsTests(GetRelatedTestsBase):

    @classmethod
    def setUpClass(cls):
        Article.use_strong_refs = True
        super(GetRelatedStrongRefsTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(GetRelatedStrongRefsTests, cls).tearDownClass()
        # restore defaults
        Article.use_strong_refs = False

    def test_get_related(self):
        # we are using strong refs, the article retrieved via category
        # lookup is the same as the directly retrieved one
        self.assertEqual(*self.run_get_related())
