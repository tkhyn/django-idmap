from django.utils import six

from .app.models import Category, RegularCategory, Article, RegularArticle

from ._base import TestCase


class IdMapWeakRefsTests(TestCase):

    def setUp(self):
        n = 0
        category = Category.objects.create(name="Category %d" % (n,))
        regcategory = RegularCategory.objects.create(name="Category %d" % (n,))

        for n in six.moves.xrange(0, 10):
            Article.objects.create(name="Article %d" % (n,),
                                   category=category,
                                   category2=regcategory)
            RegularArticle.objects.create(name="Article %d" % (n,),
                                          category=category,
                                          category2=regcategory)

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
