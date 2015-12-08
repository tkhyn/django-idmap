from django.apps import AppConfig


class IdMapConfig(AppConfig):
    name = 'idmap'

    def ready(self):

        from . import signals
