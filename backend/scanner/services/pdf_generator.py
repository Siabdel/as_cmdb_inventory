# backend/scanner/services/pdf_generator.py
"""
Service de génération PDF pour étiquettes QR Code.
Supporte multiple formats d'étiquettes thermiques.
"""

import io
import logging
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as reportlab_mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


class PDFLabelGenerator:
    """Générateur de PDF pour étiquettes d'assets."""
    
    # Formats prédéfinis (largeur x hauteur en mm)
    FORMATS = {
        '30x20': (30 * mm, 20 * mm),
        '50x30': (50 * mm, 30 * mm),
        '70x40': (70 * mm, 40 * mm),
        '80x50': (80 * mm, 50 * mm),
        '100x50': (100 * mm, 50 * mm),
    }
    
    def __init__(self, format='50x30'):
        """
        Initialize le générateur avec un format.
        
        Args:
            format: Format d'étiquette ('30x20', '50x30', '70x40', '80x50', '100x50')
        """
        self.format = format
        self.width, self.height = self.FORMATS.get(format, self.FORMATS['50x30'])
    
    def generate_single(self, asset, copies=1):
        """
        Génère PDF pour un seul asset.
        
        Args:
            asset: Asset instance
            copies: Nombre de copies
        
        Returns:
            BytesIO: Buffer PDF
        """
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=(self.width, self.height))
        
        for i in range(copies):
            self._draw_page(p, asset)
            if i < copies - 1:
                p.showPage()
        
        p.save()
        buffer.seek(0)
        return buffer
    
    def generate_batch(self, assets, copies=1):
        """
        Génère PDF pour multiple assets.
        
        Args:
            assets: QuerySet ou list d'assets
            copies: Nombre de copies par asset
        
        Returns:
            BytesIO: Buffer PDF
        """
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=(self.width, self.height))
        
        first_page = True
        for asset in assets:
            for i in range(copies):
                if not first_page:
                    p.showPage()
                first_page = False
                self._draw_page(p, asset)
        
        p.save()
        buffer.seek(0)
        return buffer
    
    def _draw_page(self, canvas_obj, asset):
        """Dessine une page/étiquette."""
        # QR Code
        try:
            if hasattr(asset, 'qrcode') and asset.qrcode and asset.qrcode.image:
                self._draw_qr_code(canvas_obj, asset.qrcode.image.path)
        except Exception as e:
            logger.warning(f"QR Code non disponible pour asset {asset.id}: {e}")
        
        # Texte
        self._draw_text(canvas_obj, asset)
        
        # Barcode (optionnel - serial number)
        if asset.serial_number:
            self._draw_barcode(canvas_obj, asset.serial_number)
    
    def _draw_qr_code(self, canvas_obj, image_path):
        """Dessine le QR Code."""
        try:
            from reportlab.lib.utils import ImageReader
            
            # Calculer position et taille (25% de la largeur)
            qr_size = self.width * 0.4
            x = 5 * mm
            y = (self.height - qr_size) / 2
            
            qr_img = ImageReader(image_path)
            canvas_obj.drawImage(
                qr_img, x, y,
                width=qr_size, height=qr_size,
                preserveAspectRatio=True
            )
        except Exception as e:
            logger.error(f"Erreur dessin QR Code: {e}")
    
    def _draw_text(self, canvas_obj, asset):
        """Dessine le texte de l'étiquette."""
        # Position texte (à droite du QR)
        text_x = self.width * 0.45
        text_y = self.height - 8 * mm
        
        # Titre (Nom asset) - Bold
        canvas_obj.setFont("Helvetica-Bold", 10)
        canvas_obj.drawString(text_x, text_y, asset.name[:35])
        text_y -= 5 * mm
        
        # Serial Number
        canvas_obj.setFont("Helvetica", 8)
        if asset.serial_number:
            canvas_obj.drawString(text_x, text_y, f"S/N: {asset.serial_number}")
            text_y -= 4 * mm
        
        # Internal Code
        if hasattr(asset, 'internal_code') and asset.internal_code:
            canvas_obj.drawString(text_x, text_y, f"ID: {asset.internal_code}")
            text_y -= 4 * mm
        
        # Category
        if asset.category:
            canvas_obj.drawString(text_x, text_y, f"Cat: {asset.category.name}")
            text_y -= 4 * mm
        
        # Location
        if hasattr(asset, 'current_location') and asset.current_location:
            canvas_obj.drawString(text_x, text_y, f"Loc: {asset.current_location.name}")
            text_y -= 4 * mm
        
        # Purchase Date
        if asset.purchase_date:
            canvas_obj.drawString(text_x, text_y, f"Achat: {asset.purchase_date.strftime('%d/%m/%Y')}")
            text_y -= 4 * mm
        
        # Status
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawString(text_x, text_y, f"Statut: {asset.status.upper()}")
    
    def _draw_barcode(self, canvas_obj, serial_number):
        """Dessine le code-barres (en bas de l'étiquette)."""
        try:
            from reportlab.graphics.barcode import code128
            
            barcode = code128.Code128(
                serial_number,
                barHeight=8 * mm,
                barWidth=0.4 * mm
            )
            barcode.drawOn(
                canvas_obj,
                5 * mm,
                3 * mm
            )
        except Exception as e:
            logger.warning(f"Erreur dessin barcode: {e}")


def generate_label_pdf(assets, format='50x30', copies=1):
    """
    Fonction utilitaire pour générer PDF d'étiquettes.
    
    Args:
        assets: List ou QuerySet d'assets
        format: Format d'étiquette ('30x20', '50x30', '70x40', '80x50', '100x50')
        copies: Nombre de copies par asset
    
    Returns:
        BytesIO: Buffer PDF
    """
    generator = PDFLabelGenerator(format)
    
    if hasattr(assets, '__iter__') and not isinstance(assets, str):
        return generator.generate_batch(assets, copies)
    else:
        return generator.generate_single(assets, copies)