from django.test import TestCase
from django.utils import six

from idmap import flush_cache

from .app.models import Article, Category, RegularCategory


class GetRelatedTests(TestCase):
    """
    Getter tests to check the behaviour of SharedMemoryQuerySet.get
    when a 'where' clause is present (when using a related manager)
    """

    def setUp(self):
        flush_cache()

        category = Category.objects.create(name="Category")

        for n in six.moves.xrange(0, 10):
            regcategory = RegularCategory.objects.create(
                              name="RegCategory %d" % n)
            Article.objects.create(name="Article %d" % n,
                                   category=category,
                                   category2=regcategory)

    def test_get_related(self):
        category = Category.objects.get(name="Category")
        regcategory = RegularCategory.objects.get(name="RegCategory 0")
        # using related manager
        category.article_set.get(category2=regcategory)
