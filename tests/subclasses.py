from django.utils import six

from idmap import flush_cache

from .app.models import Article, SubArticle, Category, RegularCategory

from ._base import TestCase


class SubclassesTests(TestCase):

    def setUp(self):
        category = Category.objects.create(name="Category")
        regcategory = RegularCategory.objects.create(name="RegCategory")

        for n in six.moves.xrange(0, 10):
            Article.objects.create(name="Article %d" % (n,),
                                   category=category,
                                   category2=regcategory)
            SubArticle.objects.create(name="Article %d" % (n,),
                                      category=category,
                                      category2=regcategory)

    def testFlushSubArticle(self):

        # make a list of Articles so that they're in cache
        article_list = list(Article.objects.all())
        subarticles_list = list(SubArticle.objects.all())
        sub_pkids = [(sa.pk, id(sa)) for sa in subarticles_list]

        # should only flush Article's cache, not SubArticle
        Article.flush_instance_cache()

        # check that nothing was erased on SubArticle's side
        for pk, sa_id in sub_pkids:
            self.assertEqual(id(SubArticle.get_cached_instance(pk)), sa_id)

        # now should flush SubArticle as well
        Article.flush_instance_cache(flush_sub=True)

        for pk, __ in sub_pkids:
            self.assertIsNone(SubArticle.get_cached_instance(pk))

    def testFlushAll(self):

        # make a list of Articles and SubArticles so that they're in cache
        list(Article.objects.all())
        sub_pks = [sa.pk for sa in SubArticle.objects.all()]

        # should flush Article and SubArticle's caches
        flush_cache()

        for pk in sub_pks:
            self.assertIsNone(SubArticle.get_cached_instance(pk))
