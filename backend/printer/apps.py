from django.apps import AppConfig

class PrinterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'printer'
    verbose_name = 'Gestion des Impressions'
    
    def ready(self):
        # Vérification optionnelle au startup
        import printer.utils.usb_permissions as usb_utils
        usb_utils.check_usb_permissions()  # Log warning si problème