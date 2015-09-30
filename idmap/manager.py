from django.db.models.manager import BaseManager

from .queryset import IdMapQuerySet


class IdMapManager(BaseManager.from_queryset(IdMapQuerySet)):

    use_for_related_fields = True
