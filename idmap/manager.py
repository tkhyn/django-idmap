from django.db.models.manager import BaseManager, Manager

from .queryset import IdMapQuerySet


class IdMapManager(BaseManager.from_queryset(IdMapQuerySet), Manager):

    use_for_related_fields = True
