from django.utils import six

from idmap import flush

from .app.models import Category, RegularCategory, Article, RegularArticle,\
    ArticleProxy

from ._base import TestCase


class IdMapWeakRefsTests(TestCase):

    def setUp(self):
        n = 0
        self.cat = Category.objects.create(name="Category %d" % n)
        self.rcat = RegularCategory.objects.create(name="Category %d" % n)

        for n in six.moves.xrange(0, 10):
            Article.objects.create(name="Article %d" % n,
                                   category=self.cat,
                                   category2=self.rcat)
            RegularArticle.objects.create(name="Article %d" % n,
                                          category=self.cat,
                                          category2=self.rcat)

    def test_retrieve_by_pk(self):
        for article in Article.objects.all():
            Article.objects.get(pk=article.pk)

    def test_cached_references(self):
        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIs(article.category, last_article.category)
            last_article = article

    def test_regular_references(self):
        article_list = RegularArticle.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIsNot(article.category2, last_article.category2)
            last_article = article

    def test_regular_to_cached(self):
        article_list = RegularArticle.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIs(article.category, last_article.category)
            last_article = article

    def test_cached_to_regular(self):
        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIsNot(article.category2, last_article.category2)
            last_article = article

    def test_object_deletion(self):
        # This must executed first so its guaranteed to be in memory.
        article_list = list(Article.objects.all().select_related('category'))

        article = Article.objects.all()[0:1].get()
        pk = article.pk
        article.delete()
        self.assertIsNone(Article.get_cached_instance(pk))

    def test_proxy_model(self):
        # check that access to instances of the same 'proxy' family is possible
        # through all the classes of the 'proxy' family
        article_list = list(Article.objects.all().select_related('category'))
        proxy_list = []
        for n in six.moves.xrange(0, 10):
            a = ArticleProxy.objects.create(name="Proxy article %d" % n,
                                            category=article_list[n].category,
                                            category2=article_list[n].category2)
            proxy_list.append(a)

        for n in six.moves.xrange(0, 10):
            article = ArticleProxy.get_cached_instance(article_list[n].pk)
            self.assertTrue(isinstance(article, Article))
            self.assertIs(article, article_list[n])

        for n in six.moves.xrange(0, 10):
            article = Article.get_cached_instance(proxy_list[n].pk)
            self.assertTrue(isinstance(article, ArticleProxy))
            self.assertIs(article, proxy_list[n])

    def test_refresh_from_db(self):
        Category.objects.filter(pk=self.cat.pk).update(name='Category 1')
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.name, 'Category 1')

    def test_refresh_from_db_after_flush(self):
        flush()
        self.cat.refresh_from_db()
        cached_c = Category.get_cached_instance(pk=self.cat.pk)
        self.assertIsNotNone(cached_c)
