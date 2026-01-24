from django.apps import AppConfig


class CalculatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculator'

    def ready(self):
        # Import translation definitions so modeltranslation can register fields
        from . import translation  # noqa: F401
