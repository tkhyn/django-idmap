from idmapper.models import SharedMemoryModel
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


class SubArticle(Article):
    pass
