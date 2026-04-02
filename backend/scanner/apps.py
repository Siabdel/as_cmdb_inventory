# backend/scanner/apps.py
from django.apps import AppConfig


class ScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scanner'
    verbose_name = 'Scanner QR/Code-Barres'
    
    def ready(self):
        """
        Import signals au démarrage de l'application.
        Nécessaire pour que les receivers soient enregistrés.
        """
        try:
            import scanner.signals  # noqa
        except ImportError:
            pass