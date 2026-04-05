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
    Supporte QR Code ET Code-Barres.
    QR Code associé à un Asset.
    Généré automatiquement à la création d'Asset (signal post_save).
    Le champ code_type distingue le format.
    """
    
    CODE_TYPE_CHOICES = [
        ('qr_code', 'QR Code (2D)'),
        ('barcode_serial', 'Code-Barres Serial (1D)'),
        ('barcode_internal', 'Code-Barres Interne (1D)'),
        ('barcode_reference', 'Code-Barres Référence Stock'),
    ]
    
    asset = models.OneToOneField(
        'inventory.Asset',
        on_delete=models.CASCADE,
        related_name='qrcode'
    )
    uuid_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
        help_text="Token unique pour l'URL de scan (ex: qr_asset_<id>_<uuid>)"
    )
    code = models.CharField(
        max_length=255,
        unique=True,
        help_text="Format: qr_asset_<id>_<uuid>",
        default="default_qr_code",
    )

    # ✅ NOUVEAU: Type de code pour traçabilité
    code_type = models.CharField(
        max_length=30,
        choices=CODE_TYPE_CHOICES,
        default='qr_code',
        help_text="Format du code: QR, Barcode Serial, Barcode Internal"
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
        verbose_name = 'Code Scannable (QR/Barres)'
        verbose_name_plural = 'Codes Scannables (QR/Barres)'
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
    
    @property
    def is_qr_code(self):
        return self.code_type == 'qr_code'
    
    @property
    def is_barcode(self):
        return self.code_type.startswith('barcode_')


class ScanLog(TimeStampMixin):
    """Historique de chaque scan QR.
    Log de chaque scan pour audit et traçabilité.
    """
    
    SCAN_CONTEXT_CHOICES = [
        ('inventory', 'Inventaire'),
        ('maintenance', 'Maintenance'),
        ('movement', 'Mouvement'),
        ('audit', 'Audit'),
        ('reception', 'Réception'),
    ]
    qrcode      = models.ForeignKey(QRCode, on_delete=models.CASCADE,
                                    related_name='scan_logs')
    # ✅ NOUVEAU: Lien direct à l'asset (même sans QRCode)
    asset = models.ForeignKey('inventory.Asset', on_delete=models.CASCADE, related_name='scan_logs', null=True, blank=True)
    
    # ✅ NOUVEAU: Lien au stock item (pour consommables)
    stock_item = models.ForeignKey('stock.StockItem', on_delete=models.CASCADE, related_name='scan_logs', null=True, blank=True)
    
    scanned_by  = models.CharField(max_length=100, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    location    = models.CharField(max_length=200, blank=True)  # GPS optionnel
    code_type   = models.CharField(max_length=50, blank=True)  # Type de code scanné
    scanned_code = models.CharField(max_length=255, blank=True, help_text="Code brut scanné")

     # ✅ NOUVEAU: Contexte du scan
    scan_context = models.CharField(
        max_length=30,
        choices=SCAN_CONTEXT_CHOICES,
        default='inventory',
        help_text="Pourquoi ce scan a été fait"
    )
    
    # ✅ NOUVEAU: Type de code scanné
    code_type = models.CharField(
        max_length=30,
        choices=QRCode.CODE_TYPE_CHOICES,
        default='qr_code'
    )
    
    # ✅ NOUVEAU: Localisation au moment du scan
    location_at_scan = models.ForeignKey('inventory.Location', on_delete=models.SET_NULL, null=True, blank=True)
    
    # ✅ NOUVEAU: Lien au ticket maintenance si applicable
    ticket = models.ForeignKey('maintenance.MaintenanceTicket', on_delete=models.SET_NULL, null=True, blank=True, related_name='scan_logs')
    
    # ✅ NOUVEAU: Notes libres
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', '-created_at']),
            models.Index(fields=['scanned_by', '-created_at']),
            models.Index(fields=['scan_context', '-created_at']),
        ]
    
    def __str__(self):
        return f"Scan {self.asset or self.stock_item} - {self.created_at}"
