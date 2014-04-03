from django.test import TestCase

from base import SharedMemoryModel
from django.db import models

class Category(SharedMemoryModel):
    name = models.CharField(max_length=32)

class RegularCategory(models.Model):
    name = models.CharField(max_length=32)

class Article(SharedMemoryModel):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Category)
    category2 = models.ForeignKey(RegularCategory)

class RegularArticle(models.Model):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Category)
    category2 = models.ForeignKey(RegularCategory)

class SharedMemorysTest(TestCase):
    # TODO: test for cross model relation (singleton to regular)

    def setUp(self):
        n = 0
        category = Category.objects.create(name="Category %d" % (n,))
        regcategory = RegularCategory.objects.create(name="Category %d" % (n,))

        for n in xrange(0, 10):
            Article.objects.create(name="Article %d" % (n,), category=category, category2=regcategory)
            RegularArticle.objects.create(name="Article %d" % (n,), category=category, category2=regcategory)

    def testSharedMemoryReferences(self):
        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertEquals(article.category is last_article.category, True)
            last_article = article

    def testRegularReferences(self):
        article_list = RegularArticle.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertEquals(article.category2 is last_article.category2, False)
            last_article = article

    def testMixedReferences(self):
        article_list = RegularArticle.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertEquals(article.category is last_article.category, True)
            last_article = article

        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertEquals(article.category2 is last_article.category2, False)
            last_article = article

    def testObjectDeletion(self):
        # This must execute first so its guaranteed to be in memory.
        article_list = list(Article.objects.all().select_related('category'))

        article = Article.objects.all()[0:1].get()
        pk = article.pk
        article.delete()
        self.assertIsNone(Article.get_cached_instance(pk))

