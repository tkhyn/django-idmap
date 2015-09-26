from django.apps import AppConfig


class IdMapConfig(AppConfig):
    name = 'idmap'
    verbose_name = 'Django ID mapper'

    def ready(self):
        from . import signals
