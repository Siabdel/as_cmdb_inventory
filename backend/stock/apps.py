# backend/stock/apps.py
# ============================================================================
# STOCK APP CONFIGURATION
# Importe les signals au démarrage de l'application Django
# ============================================================================

from django.apps import AppConfig


class StockConfig(AppConfig):
    """Configuration de l'application Stock."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock'
    verbose_name = 'Gestion de Stock'
    
    def ready(self):
        """
        Méthode appelée quand l'application est prête.
        Importe les signals pour qu'ils soient enregistrés.
        """
        # ✅ Import des signals stock
        import stock.signals
        
        # Logging pour debug (optionnel)
        import logging
        logger = logging.getLogger(__name__)
        logger.info('[STOCK] Signals enregistrés avec succès')