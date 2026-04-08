# backend/scanner/models.py
from django.db import models
import uuid
from django.db import models
from inventory.models import Asset, TimeStampMixin

from django.conf import settings

# backend/scanner/models.py — VERSION CLARIFIÉE ✅
CODE_TYPE_CHOICES = [
        ('qr_code', 'QR Code (2D)'),
        ('barcode_128', 'Code 128 (1D)'),
        ('barcode_ean13', 'EAN-13 (1D)'),
        ('barcode_ean8', 'EAN-8 (1D)'),
        ('barcode_39', 'Code 39 (1D)'),
    ]
class ScannableCode(models.Model):
    """
    Modèle générique pour TOUS les codes scannables.
    Supporte QR Code ET Code-Barres.
    QR Code associé à un Asset.
    Généré automatiquement à la création d'Asset (signal post_save).
    Le champ code_type distingue le format.
    """
    
    
    
    asset = models.OneToOneField('inventory.Asset', on_delete=models.CASCADE, related_name='scannable_codes', null=True, blank=True)
    stock_item = models.ForeignKey('stock.StockItem', on_delete=models.CASCADE, related_name='scannable_codes', null=True, blank=True)
    
    code = models.CharField(max_length=255, unique=True, db_index=True, help_text="Valeur du code scanné")
    code_type = models.CharField(max_length=30, choices=CODE_TYPE_CHOICES, default='qr_code')
    
    # Champs spécifiques QR Code (optionnels)
    uuid_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, null=True, blank=True)
    
    # Image (QR ou Barcode)
    image = models.ImageField(upload_to='scannable_codes/%Y/%m/', blank=True, null=True)
    
    # Métadonnées
    format = models.CharField(max_length=20, default='PNG')
    size = models.PositiveIntegerField(default=300)
    
    # Tracking
    is_active = models.BooleanField(default=True)
    scanned_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Code Scannable'
        verbose_name_plural = 'Codes Scannables'
    
    def __str__(self):
        return f"{self.get_code_type_display()} - {self.code}"
    
    def __str__(self):
        if self.asset:
            return f"{self.get_code_type_display()} - Asset {self.asset.id} ({self.asset.name})"
        elif self.stock_item:
            return f"{self.get_code_type_display()} - Stock Item {self.stock_item.id} ({self.stock_item.name})"
        else:   
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
    ScannableCode = models.ForeignKey(ScannableCode, on_delete=models.CASCADE,
                                    related_name='scan_logs')
    # ✅ NOUVEAU: Lien direct à l'asset (même sans ScannableCode)
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
        choices=CODE_TYPE_CHOICES,
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
