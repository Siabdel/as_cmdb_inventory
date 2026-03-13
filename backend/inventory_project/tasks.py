# inventory_project/tasks.py
from celery import shared_task
from django.conf import settings


@shared_task
def generate_qr_code(asset_id: int):
    """Génère l'image QR et la sauvegarde dans media/qr_codes/."""
    import qrcode, io
    from django.core.files import File
    from scanner.models import QRCode
    qr_obj, _ = QRCode.objects.get_or_create(asset_id=asset_id)
    img = qrcode.make(f"{settings.QR_CODE_BASE_URL}/scan/{qr_obj.uuid_token}/")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_obj.image.save(f"qr_{asset_id}.png", File(buffer), save=True)

@shared_task
def check_low_stock():
    """Alerte quotidienne pour les pièces sous le seuil min."""
    # Envoi email / notification

@shared_task
def warranty_expiry_alert():
    """Déjà prévu en vue, transformer en tâche Celery Beat planifiée."""

