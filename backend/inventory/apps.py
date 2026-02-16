"""
Configuration de l'application inventory
"""
from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Configuration de l'application inventory pour la gestion CMDB"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'Gestion d\'Inventaire CMDB'
    
    def ready(self):
        """Méthode appelée quand l'application est prête"""
        # Importer les signaux si nécessaire
        try:
            import inventory.signals  # noqa F401
        except ImportError:
            pass