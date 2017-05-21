from idmap.models import IdMapModel
from django.db import models


class Category(IdMapModel):
    name = models.CharField(max_length=32)


class RegularCategory(models.Model):
    name = models.CharField(max_length=32)


class Article(IdMapModel):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Category)
    category2 = models.ForeignKey(RegularCategory)


class RegularArticle(models.Model):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Category)
    category2 = models.ForeignKey(RegularCategory)


class SubArticle(Article):
    pass


class ArticleProxy(Article):
    class Meta:
        proxy = True
