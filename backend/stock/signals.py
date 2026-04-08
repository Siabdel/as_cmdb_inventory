# backend/stock/signals.py
import io
import os
from datetime import datetime
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
import logging
import barcode
from barcode.writer import ImageWriter
from stock.models import StockItem
from scanner.models import ScannableCode
from django.conf import settings

logger = logging.getLogger(__name__)


#============================================================================
# SIGNAL POUR CRÉATION AUTOMATIQUE BARCODE RÉFÉRENCE STOCK
# ============================================================================
@receiver(post_save, sender=StockItem)
def auto_create_stock_barcode(sender, instance, created, **kwargs):
    """
    Signal post_save sur StockItem.
    Crée automatiquement un Barcode de référence pour les consommables.
    
    Format: REF-<reference>-<id>
    """
    if not created:
        return  # Ne pas exécuter pour les mises à jour
    
    logger.info(f'[SIGNAL] StockItem créé: {instance.id} - {instance.reference}')
    
    try:
        # Créer Barcode de référence
        code_value = f"REF-{instance.reference}-{instance.id}"
        
        barcode, created = ScannableCode.objects.get_or_create(
            stock_item=instance,
            code_type='barcode_reference',
            defaults={
                'code': code_value,
                'uuid_token': None,  # Pas d'UUID pour les barcodes référence
            }
        )
        
        if created:
            logger.info(f'[SIGNAL] Barcode référence créé pour StockItem {instance.id}')
            # Générer image QR
            qr_obj = barcode  # Utiliser le barcode créé comme qr_obj
            image_url = _generate_qr_image(qr_obj)

            if image_url:
                logger.info(f'[SIGNAL] QR Code généré: {image_url}')
            else :
                logger.warning(f'[SIGNAL] Échec génération QR pour StockItem {instance.id}')
    except Exception as e:
        logger.error(f'[SIGNAL] Erreur création barcode stock: {str(e)}', exc_info=True)




def _generate_qr_image(qr_obj):
    """
    Génère l'image QR code à partir d'un objet ScannableCode.
    (Fonction existante - inchangée)
    """
    try:
        if not qr_obj or not qr_obj.asset:
            logger.error(f'[QR] ScannableCode ou Asset invalide: {qr_obj}')
            return None
        
        if not qr_obj.uuid_token:
            logger.error(f'[QR] uuid_token manquant pour ScannableCode {qr_obj.id}')
            return None
        
        # Données QR Code
        qr_data = f"qr_asset_{qr_obj.asset.id}_{qr_obj.uuid_token}"
        
        if not qr_obj.code:
            qr_obj.code = qr_data
            qr_obj.save(update_fields=['code'])
        
        logger.info(f'[QR] Génération pour Asset {qr_obj.asset.id} | Data: {qr_data}')
        
        # Créer QR Code
        import ScannableCode
        qr = ScannableCode.ScannableCode(
            version=1,
            error_correction=ScannableCode.constants.ERROR_CORRECT_H,  # 30% recovery
            box_size=12,  # PLUS GRAND pour impression thermique
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder dans buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=100, optimize=False)
        buffer.seek(0)
        
        # Chemin de stockage
        now = datetime.now()
        year_month = now.strftime('%Y/%m')
        filename = f"qr_asset_{qr_obj.asset.id}_{qr_obj.uuid_token}.png"
        filepath = f"qr_codes/{year_month}/{filename}"
        
        # Créer répertoires
        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Sauvegarder fichier
        qr_obj.image.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        logger.info(f'[QR] Image générée: {qr_obj.image.url}')
        return qr_obj.image.url
        
    except Exception as e:
        logger.error(f'[QR] Erreur génération QR Code: {str(e)}', exc_info=True)
        return None


def _generate_barcode_image(barcode_obj):
    """
    Génère l'image code-barres à partir d'un objet ScannableCode (code_type=barcode_*).
    
    Formats supportés:
    - code128: Serial numbers, internal codes
    - ean13: Products grand public
    - ean8: Petits produits
    - code39: Inventaire industriel
    
    Args:
        barcode_obj: Instance de ScannableCode avec code_type='barcode_*'
    
    Returns:
        str: URL de l'image générée ou None en cas d'erreur
    
    Workflow:
        1. Vérifier code_type (code128, ean13, etc.)
        2. Choisir le format barcode approprié
        3. Générer image PNG avec python-barcode
        4. Sauvegarder dans media/barcodes/YYYY/MM/
        5. Mettre à jour ScannableCode.image
        6. Retourner URL
    
    Exemple:
        >>> barcode_obj = ScannableCode.objects.get(code_type='barcode_serial')
        >>> url = _generate_barcode_image(barcode_obj)
        >>> print(url)
        '/media/barcodes/2026/03/barcode_asset_152_1234567890.png'
    """
    try:
        # ====================================================================
        # 1. VALIDATION PRÉALABLE
        # ====================================================================
        if not barcode_obj:
            logger.error(f'[BARCODE] ScannableCode invalide: {barcode_obj}')
            return None
        
        if not barcode_obj.code:
            logger.error(f'[BARCODE] Code manquant pour ScannableCode {barcode_obj.id}')
            return None
        
        # Vérifier que c'est bien un barcode (pas un QR Code)
        if not barcode_obj.code_type.startswith('barcode_'):
            logger.warning(f'[BARCODE] code_type incorrect: {barcode_obj.code_type}')
            return None
        
        logger.info(f'[BARCODE] Génération pour {barcode_obj} | Code: {barcode_obj.code}')
        
        # ====================================================================
        # 2. DÉTERMINER LE FORMAT DE CODE-BARRES
        # ====================================================================
        code = barcode_obj.code
        barcode_format = 'code128'  # Default
        
        # Choisir le format selon le code_type et le contenu
        if barcode_obj.code_type == 'barcode_reference':
            # Référence stock → Code128 (supporte lettres + chiffres)
            barcode_format = 'code128'
            
        elif barcode_obj.code_type == 'barcode_serial':
            # Serial number → Code128 (le plus flexible)
            barcode_format = 'code128'
            
        elif barcode_obj.code_type == 'barcode_internal':
            # Code interne → Code128
            barcode_format = 'code128'
            
        elif code.isdigit() and len(code) == 13:
            # 13 chiffres → EAN13
            barcode_format = 'ean13'
            
        elif code.isdigit() and len(code) == 8:
            # 8 chiffres → EAN8
            barcode_format = 'ean8'
        
        logger.info(f'[BARCODE] Format sélectionné: {barcode_format}')
        
        # ====================================================================
        # 3. CRÉER LE CODE-BARRES AVEC PYTHON-BARCODE
        # ====================================================================
        # Nettoyer le code selon le format
        if barcode_format == 'ean13' and len(code) > 13:
            code = code[:12]  # EAN13 = 12 chiffres + 1 checksum auto
        elif barcode_format == 'ean8' and len(code) > 8:
            code = code[:7]  # EAN8 = 7 chiffres + 1 checksum auto
        
        # Créer le barcode
        barcode_class = barcode.get_barcode_class(barcode_format)
        bc = barcode_class(code, writer=ImageWriter())
        
        # ====================================================================
        # 4. GÉNÉRER IMAGE PNG DANS BUFFER
        # ====================================================================
        buffer = io.BytesIO()
        
        # Options de rendu
        options = {
            'module_width': 0.4,  # Largeur des barres (mm)
            'module_height': 15.0,  # Hauteur des barres (mm)
            'font_size': 10,  # Taille police texte
            'text_distance': 5.0,  # Distance texte/barres
            'background_color': 'white',
            'foreground_color': 'black',
            'write_text': True,  # Afficher le texte sous le barcode
            'quiet_zone': 6.5,  # Marge blanche (mm)
        }
        
        bc.write(buffer, options=options)
        buffer.seek(0)
        
        # ====================================================================
        # 5. CRÉER CHEMIN DE STOCKAGE
        # ====================================================================
        now = datetime.now()
        year_month = now.strftime('%Y/%m')
        
        # Nom de fichier unique
        if barcode_obj.asset:
            filename = f"barcode_asset_{barcode_obj.asset.id}_{barcode_obj.code}.png"
        elif barcode_obj.stock_item:
            filename = f"barcode_stock_{barcode_obj.stock_item.id}_{barcode_obj.code}.png"
        else:
            filename = f"barcode_{barcode_obj.id}_{barcode_obj.code}.png"
        
        # Sanitize filename (enlever caractères spéciaux)
        filename = "".join(c for c in filename if c.isalnum() or c in ('.', '_')).rstrip()
        
        filepath = f"barcodes/{year_month}/{filename}"
        
        # ====================================================================
        # 6. CRÉER RÉPERTOIRES SI NÉCESSAIRE
        # ====================================================================
        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # ====================================================================
        # 7. SAUVEGARDER FICHIER
        # ====================================================================
        barcode_obj.image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        logger.info(f'[BARCODE] Image générée: {barcode_obj.image.url}')
        
        return barcode_obj.image.url
        
    except Exception as e:
        logger.error(f'[BARCODE] Erreur génération code-barres: {str(e)}', exc_info=True)
        import traceback
        traceback.print_exc()
        return None