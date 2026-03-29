from django.db import models

# Create your models here.

# scanner/models.py
import uuid
from django.db import models
from inventory.models import Asset, TimeStampMixin

# backend/scanner/models.py

# backend/scanner/models.py (extrait)
import uuid
from django.db import models
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
    

# backend/scanner/models.py
import uuid
from django.db import models
from django.conf import settings
from datetime import timedelta


class PrintTemplate(models.Model):
    """
    Template d'étiquette configurable.
    Permet différents formats selon le type d'asset.
    """
    FORMAT_CHOICES = [
        ('30x20', '30mm x 20mm (Petit matériel)'),
        ('50x30', '50mm x 30mm (Standard)'),
        ('70x40', '70mm x 40mm (Grand matériel)'),
        ('80x50', '80mm x 50mm (Rack/Serveur)'),
        ('100x50', '100mm x 50mm (Armoire)'),
    ]
    
    name = models.CharField(max_length=100)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='50x30')
    width_mm = models.PositiveIntegerField(default=50)
    height_mm = models.PositiveIntegerField(default=30)
    
    # Layout configuration
    qr_size_mm = models.PositiveIntegerField(default=25)
    qr_position_x_mm = models.PositiveIntegerField(default=5)
    qr_position_y_mm = models.PositiveIntegerField(default=5)
    
    font_size_title = models.PositiveIntegerField(default=10)
    font_size_text = models.PositiveIntegerField(default=8)
    
    # Fields to display
    show_serial = models.BooleanField(default=True)
    show_internal_code = models.BooleanField(default=True)
    show_category = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_purchase_date = models.BooleanField(default=False)
    show_warranty = models.BooleanField(default=False)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.format})"


class Printer(models.Model):
    """
    Configuration des imprimantes thermiques.
    Supporte USB, Bluetooth, Ethernet.
    """
    CONNECTION_CHOICES = [
        ('usb', 'USB'),
        ('bluetooth', 'Bluetooth'),
        ('ethernet', 'Ethernet/WiFi'),
        ('network', 'Network Printer'),
    ]
    
    name = models.CharField(max_length=100)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_CHOICES)
    
    # Network config
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.PositiveIntegerField(default=9100)
    
    # USB/Bluetooth
    device_path = models.CharField(max_length=255, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    
    # Printer settings
    dpi = models.PositiveIntegerField(default=203)
    speed = models.PositiveIntegerField(default=3)  # 1-5
    density = models.PositiveIntegerField(default=10)  # 1-15
    
    # Paper
    default_template = models.ForeignKey(PrintTemplate, on_delete=models.SET_NULL, null=True)
    paper_width_mm = models.PositiveIntegerField(default=50)
    paper_height_mm = models.PositiveIntegerField(default=30)
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_connection_type_display()})"


class PrintJob(models.Model):
    """
    Job d'impression (batch ou single).
    Track le statut et l'historique.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    asset_ids = models.JSONField(help_text="Liste des asset IDs à imprimer")
    template = models.ForeignKey(PrintTemplate, on_delete=models.SET_NULL, null=True)
    printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, null=True)
    
    copies = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    pdf_file = models.FileField(upload_to='print_jobs/%Y/%m/', blank=True, null=True)
    
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PrintJob #{self.id} - {self.status}"
    
    @property
    def asset_count(self):
        return len(self.asset_ids) if self.asset_ids else 0


class PrintLog(models.Model):
    """
    Log d'audit pour chaque impression.
    Compliance et traçabilité.
    """
    job = models.ForeignKey(PrintJob, on_delete=models.CASCADE, related_name='logs')
    asset = models.ForeignKey('inventory.Asset', on_delete=models.CASCADE)
    printed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    printer_name = models.CharField(max_length=100)
    template_name = models.CharField(max_length=100)
    
    printed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-printed_at']
        indexes = [
            models.Index(fields=['asset', '-printed_at']),
            models.Index(fields=['printed_by', '-printed_at']),
        ]
