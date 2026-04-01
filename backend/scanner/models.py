from django.db import models

# Create your models here.

# scanner/models.py
import uuid
from django.db import models
from inventory.models import Asset, TimeStampMixin

# backend/scanner/models.py
# backend/scanner/models.py (extrait)
from django.conf import settings


class QRCode(models.Model):
    """
    QR Code associé à un Asset.
    Généré automatiquement à la création d'Asset (signal post_save).
    """
    asset = models.OneToOneField(
        'inventory.Asset',
        on_delete=models.CASCADE,
        related_name='qrcode'
    )
    uuid_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False
    )
    code = models.CharField(
        max_length=255,
        unique=True,
        help_text="Format: qr_asset_<id>_<uuid>",
        default="default_qr_code"
    )
    
    # Image stockée en filesystem, URL en base
    image = models.ImageField(
        upload_to='qr_codes/%Y/%m/',
        blank=True,
        null=True,
        help_text="Image PNG du QR Code"
    )
    
    # Métadonnées
    format = models.CharField(max_length=20, default='PNG')
    size = models.PositiveIntegerField(default=300)  # pixels
    error_correction = models.CharField(max_length=10, default='M')
    
    # Tracking
    is_active = models.BooleanField(default=True)
    scanned_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uuid_token']),
            models.Index(fields=['code']),
            models.Index(fields=['asset', '-created_at']),
        ]
    
    def __str__(self):
        return f"QR Code - Asset {self.asset.id} ({self.asset.name})"
    
    @property
    def url(self):
        """URL publique du QR Code"""
        if self.image:
            return self.image.url
        return None
    
    @property
    def full_url(self):
        """URL absolue (avec domain)"""
        if self.image:
            from django.conf import settings
            return f"{settings.MEDIA_URL}{self.image.url}"
        return None


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
    

