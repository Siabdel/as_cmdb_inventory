from django.db import models

# Create your models here.

# scanner/models.py
import uuid
from django.db import models
from inventory.models import Asset, TimeStampMixin

class QRCode(TimeStampMixin):
    asset       = models.OneToOneField(Asset, on_delete=models.CASCADE,
                                       related_name='qrcode')
    uuid_token  = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    image       = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    url         = models.URLField(blank=True)   # URL encodée dans le QR
    scanned_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"QR-{self.asset.serial_number}"


class ScanLog(TimeStampMixin):
    """Historique de chaque scan QR."""
    qrcode      = models.ForeignKey(QRCode, on_delete=models.CASCADE,
                                    related_name='scan_logs')
    scanned_by  = models.CharField(max_length=100, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    location    = models.CharField(max_length=200, blank=True)  # GPS optionnel

    class Meta:
        ordering = ['-created_at']

class ScannedAsset(TimeStampMixin):
    """Détails de l'équipement scanné."""
    asset       = models.ForeignKey(Asset, on_delete=models.CASCADE,
                                    related_name='scanned_assets')
    qrcode      = models.ForeignKey(QRCode, on_delete=models.CASCADE,
                                    related_name='scanned_assets')
    scan_log    = models.ForeignKey(ScanLog, on_delete=models.CASCADE,
                                    related_name='scanned_assets')
    scan_result = models.CharField(max_length=200, blank=True)  # Résultat du scan (ex: "OK", "Maintenance requise")

class ScanResult(TimeStampMixin):
    """Résultats détaillés du scan pour analyse."""
    scanned_asset = models.ForeignKey(ScannedAsset, on_delete=models.CASCADE,
                                     related_name='scan_results')
    key          = models.CharField(max_length=100)  # Ex: "battery_health"
    value        = models.CharField(max_length=200)  # Ex: "Good", "Replace soon"   
    notes        = models.TextField(blank=True)  # Notes supplémentaires du technicien
    def __str__(self):
        return f"{self.key}: {self.value} ({self.scanned_asset.asset.serial_number})"
    
