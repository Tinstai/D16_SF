from django.apps import AppConfig


class BulletinBoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'APPS.bulletin_board'

    def ready(self):
        from . import signals
