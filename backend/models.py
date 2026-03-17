import uuid
import os
from django.db import models
from django.conf import settings
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File


class Asset(models.Model):
    """
    Modèle représentant un asset matériel avec QR code et code-barres.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Nom")
    code = models.CharField(max_length=255, unique=True, verbose_name="Code unique")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Localisation")
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, verbose_name="QR Code")
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True, verbose_name="Code-barres")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        """
        Génère automatiquement le QR code et le code-barres lors de la création.
        """
        if not self.code:
            # Générer un code unique si non fourni
            self.code = str(uuid.uuid4())[:8].upper()

        super().save(*args, **kwargs)

        # Générer les images seulement si elles n'existent pas encore
        if not self.qr_code:
            self.generate_qrcode()
        if not self.barcode:
            self.generate_barcode()

    def generate_qrcode(self):
        """
        Génère un QR code PNG à partir du code de l'asset et le sauvegarde dans qr_code.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.code)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'asset_{self.id}_qrcode.png'
        self.qr_code.save(filename, File(buffer), save=False)
        self.save(update_fields=['qr_code'])

    def generate_barcode(self):
        """
        Génère un code-barres Code128 à partir du code de l'asset et le sauvegarde dans barcode.
        """
        # Utiliser le code comme données pour le code-barres
        barcode_data = self.code
        # Créer le code-barres
        barcode = Code128(barcode_data, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer)
        buffer.seek(0)

        filename = f'asset_{self.id}_barcode.png'
        self.barcode.save(filename, File(buffer), save=False)
        self.save(update_fields=['barcode'])

    def get_qrcode_url(self):
        """
        Retourne l'URL absolue du QR code.
        """
        if self.qr_code:
            return self.qr_code.url
        return None

    def get_barcode_url(self):
        """
        Retourne l'URL absolue du code-barres.
        """
        if self.barcode:
            return self.barcode.url
        return None


class AssetScan(models.Model):
    """
    Modèle pour tracer chaque scan d'un asset.
    """
    SCAN_SOURCES = [
        ('scanner_usb', 'Scanner USB'),
        ('mobile_app', 'Application mobile'),
        ('web_frontend', 'Interface web'),
        ('bluetooth', 'Scanner Bluetooth'),
        ('manual', 'Saisie manuelle'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='scans', verbose_name="Asset")
    scanned_at = models.DateTimeField(auto_now_add=True, verbose_name="Scanné le")
    scanned_by = models.CharField(max_length=255, verbose_name="Scanné par")
    scan_location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lieu du scan")
    source = models.CharField(max_length=50, choices=SCAN_SOURCES, default='web_frontend', verbose_name="Source")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        ordering = ['-scanned_at']
        verbose_name = "Scan d'asset"
        verbose_name_plural = "Scans d'assets"

    def __str__(self):
        return f"Scan #{self.id} - {self.asset.code} par {self.scanned_by}"
