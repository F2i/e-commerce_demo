from django.apps import AppConfig


class StoreCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store_core'

    def ready(self) -> None:
        import store_core.signals.handlers
        return super().ready()