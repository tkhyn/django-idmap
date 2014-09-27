from django.test import TestCase

from models import Category, RegularCategory, Article, RegularArticle
from idmap import flush_cache


class SharedMemoryWeakRefsTests(TestCase):

    def setUp(self):
        flush_cache()
        n = 0
        category = Category.objects.create(name="Category %d" % (n,))
        regcategory = RegularCategory.objects.create(name="Category %d" % (n,))

        for n in xrange(0, 10):
            Article.objects.create(name="Article %d" % (n,),
                                   category=category,
                                   category2=regcategory)
            RegularArticle.objects.create(name="Article %d" % (n,),
                                          category=category,
                                          category2=regcategory)

    def testSharedMemoryReferences(self):
        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIs(article.category, last_article.category)
            last_article = article

    def testRegularReferences(self):
        article_list = RegularArticle.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIsNot(article.category2, last_article.category2)
            last_article = article

    def testRegularToShared(self):
        article_list = RegularArticle.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIs(article.category, last_article.category)
            last_article = article

    def testSharedToRegular(self):
        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIsNot(article.category2, last_article.category2)
            last_article = article

    def testObjectDeletion(self):
        # This must executed first so its guaranteed to be in memory.
        article_list = list(Article.objects.all().select_related('category'))

        article = Article.objects.all()[0:1].get()
        pk = article.pk
        article.delete()
        self.assertIsNone(Article.get_cached_instance(pk))
