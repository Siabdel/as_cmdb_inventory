from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QRCode
from backend.cmdb_admin.barcode_service import generate_qrcode_image
from django.core.files import File
from io import BytesIO

@receiver(post_save, sender=QRCode)
def _generate_qr_image(sender, instance, created, **kwargs):
    """
    Génère l'image QR code après la sauvegarde d'un objet QRCode.
    """
    if created or kwargs.get('force_generate', False):
        # Implémentation de la génération de l'image QR
        # Cette fonction est appelée via scanner.views.regenerate_qr
        pass

def generate_qr_image(qr_obj):
    """
    Fonction pour générer l'image QR code à partir d'un objet QRCode.
    """
    if not qr_obj.asset:
        return
        
    # Générer les données à encoder dans le QR code
    qr_data = qr_obj.url or f"http://localhost:8000/scan/{qr_obj.uuid_token}"
    
    # Générer l'image QR code
    qr_buffer = generate_qrcode_image(qr_data)
    
    # Sauvegarder l'image dans le modèle QRCode
    if qr_buffer:
        qr_buffer.seek(0)
        filename = f"qr_code_{qr_obj.uuid_token}.png"
        qr_obj.image.save(filename, File(qr_buffer), save=True)