from django.db.models.manager import BaseManager

from .queryset import SharedMemoryQuerySet


class SharedMemoryManager(BaseManager.from_queryset(SharedMemoryQuerySet)):

    use_for_related_fields = True
