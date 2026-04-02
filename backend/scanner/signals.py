# backend/scanner/signals.py
# ============================================================================
# SIGNALS POUR GÉNÉRATION AUTOMATIQUE QR CODE
# Déclencheur: post_save sur Asset (inventory app)
# Version: 2.0 — Mars 2026
# ============================================================================

import os
import io
import uuid
import logging
import qrcode
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings

from inventory.models import Asset
from scanner.models import QRCode

logger = logging.getLogger(__name__)


def _generate_qr_image(qr_obj):
    """
    Fonction pour générer l'image QR code à partir d'un objet QRCode.
    
    Args:
        qr_obj: Instance de QRCode (doit avoir asset, uuid_token, code)
    
    Returns:
        str: URL de l'image générée ou None en cas d'erreur
    
    Workflow:
        1. Créer données QR (code = qr_asset_<id>_<uuid>)
        2. Générer image PNG avec qrcode library
        3. Sauvegarder dans media/qr_codes/YYYY/MM/
        4. Mettre à jour QRCode.image
        5. Retourner URL
    
    Exemple:
        >>> qr_obj = QRCode.objects.create(asset=asset)
        >>> url = _generate_qr_image(qr_obj)
        >>> print(url)
        '/media/qr_codes/2026/03/qr_asset_152_abc123.png'
    """
    try:
        # ====================================================================
        # 1. VALIDATION PRÉALABLE
        # ====================================================================
        if not qr_obj or not qr_obj.asset:
            logger.error(f'[QR] QRCode ou Asset invalide: {qr_obj}')
            return None
        
        if not qr_obj.uuid_token:
            logger.error(f'[QR] uuid_token manquant pour QRCode {qr_obj.id}')
            return None
        
        # ====================================================================
        # 2. PRÉPARER DONNÉES QR CODE
        # ====================================================================
        # Format: qr_asset_<asset_id>_<uuid_token>
        qr_data = f"qr_asset_{qr_obj.asset.id}_{qr_obj.uuid_token}"
        
        # Mettre à jour le champ code si vide
        if not qr_obj.code:
            qr_obj.code = qr_data
            qr_obj.save(update_fields=['code'])
        
        logger.info(f'[QR] Génération pour Asset {qr_obj.asset.id} | Data: {qr_data}')
        
        # ====================================================================
        # 3. CRÉER QR CODE AVEC LIBRAIRIE QRCode
        # ====================================================================
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust si nécessaire
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% recovery
            box_size=10,  # Taille des pixels
            border=4,  # Marge standard
        )
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # ====================================================================
        # 4. GÉNÉRER IMAGE PNG
        # ====================================================================
        img = qr.make_image(
            fill_color="black",
            back_color="white"
        )
        
        # ====================================================================
        # 5. SAUVEGARDER DANS BUFFER MÉMOIRE
        # ====================================================================
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95, optimize=True)
        buffer.seek(0)
        
        # ====================================================================
        # 6. CRÉER CHEMIN DE STOCKAGE
        # ====================================================================
        # Organisation: media/qr_codes/YYYY/MM/qr_asset_<id>_<uuid>.png
        now = datetime.now()
        year_month = now.strftime('%Y/%m')
        
        filename = f"qr_asset_{qr_obj.asset.id}_{qr_obj.uuid_token}.png"
        filepath = f"qr_codes/{year_month}/{filename}"
        
        # ====================================================================
        # 7. CRÉER RÉPERTOIRES SI NÉCESSAIRE
        # ====================================================================
        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # ====================================================================
        # 8. SAUVEGARDER FICHIER
        # ====================================================================
        # Utiliser Django FileField save() pour gestion propre
        qr_obj.image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        logger.info(f'[QR] Image générée avec succès: {qr_obj.image.url}')
        
        return qr_obj.image.url
        
    except Exception as e:
        logger.error(f'[QR] Erreur génération QR Code: {str(e)}', exc_info=True)
        return None


# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

@receiver(post_save, sender=Asset)
def auto_create_qrcode(sender, instance, created, **kwargs):
    """
    Signal post_save sur Asset.
    Crée automatiquement QRCode + génère image à la création d'Asset.
    
    Déclencheur: Asset.objects.create() ou Asset.save()
    Condition: created=True (nouvel asset uniquement)
    
    Workflow:
        1. Asset créé via POST /api/v1/inventory/assets/
        2. Signal post_save déclenché
        3. QRCode.objects.create(asset=instance)
        4. _generate_qr_image(qr_obj) appelé
        5. Image sauvegardée dans media/qr_codes/
    """
    if created:
        logger.info(f'[SIGNAL] Asset créé: {instance.id} - {instance.name}')
        
        try:
            # Créer QRCode associé
            qr_obj, created = QRCode.objects.get_or_create(
                asset=instance,
                defaults={
                    'code': f"qr_asset_{instance.id}_",  # Sera mis à jour avec uuid
                }
            )
            
            if created:
                logger.info(f'[SIGNAL] QRCode créé pour Asset {instance.id}')
                
                # Générer image QR
                image_url = _generate_qr_image(qr_obj)
                
                if image_url:
                    logger.info(f'[SIGNAL] QR Code généré: {image_url}')
                else:
                    logger.warning(f'[SIGNAL] Échec génération QR pour Asset {instance.id}')
            else:
                logger.info(f'[SIGNAL] QRCode existant pour Asset {instance.id}')
                
        except Exception as e:
            logger.error(f'[SIGNAL] Erreur création QRCode: {str(e)}', exc_info=True)


@receiver(post_save, sender=Asset)
def regenerate_qr_on_serial_change(sender, instance, **kwargs):
    """
    Signal post_save sur Asset.
    Régénère QR Code si le numéro de série change.
    
    Déclencheur: Asset.save() avec serial_number modifié
    Condition: serial_number différent de l'ancienne valeur
    
    Note: Nécessite de stocker l'ancienne valeur (pre_save)
    Pour simplification, on régénère à chaque save (peut être optimisé)
    """
    if not instance.pk:
        return  # Asset pas encore créé
    
    try:
        # Vérifier si QRCode existe
        qr_obj = QRCode.objects.filter(asset=instance).first()
        
        if qr_obj:
            # Régénérer QR (utile si serial_number changé)
            image_url = _generate_qr_image(qr_obj)
            
            if image_url:
                logger.info(f'[SIGNAL] QR Code régénéré pour Asset {instance.id}')
                
    except Exception as e:
        logger.error(f'[SIGNAL] Erreur régénération QR: {str(e)}', exc_info=True)


# ============================================================================
# COMMANDE DJANGO POUR GÉNÉRATION BATCH
# ============================================================================

def generate_missing_qr_codes():
    """
    Fonction utilitaire pour générer QR Codes manquants.
    À utiliser via management command ou shell Django.
    
    Usage:
        python manage.py shell
        >>> from scanner.signals import generate_missing_qr_codes
        >>> generate_missing_qr_codes()
    
    Ou créer management command:
        python manage.py generate_qr_codes --all
    """
    from django.utils import timezone
    
    # Trouver assets sans QR Code
    assets_without_qr = Asset.objects.filter(qrcode__isnull=True)
    count = assets_without_qr.count()
    
    logger.info(f'[BATCH] {count} assets sans QR Code trouvés')
    
    success = 0
    failed = 0
    
    for asset in assets_without_qr:
        try:
            qr_obj, created = QRCode.objects.get_or_create(asset=asset)
            
            if created:
                image_url = _generate_qr_image(qr_obj)
                
                if image_url:
                    success += 1
                    logger.info(f'[BATCH] QR généré pour Asset {asset.id}')
                else:
                    failed += 1
                    logger.error(f'[BATCH] Échec QR pour Asset {asset.id}')
        except Exception as e:
            failed += 1
            logger.error(f'[BATCH] Erreur Asset {asset.id}: {str(e)}')
    
    logger.info(f'[BATCH] Terminé: {success} succès, {failed} échecs')
    
    return {
        'total': count,
        'success': success,
        'failed': failed,
        'timestamp': timezone.now()
    }


def regenerate_all_qr_codes():
    """
    Régénère TOUS les QR Codes (utile après migration ou changement format).
    
    ⚠️ ATTENTION: Peut être long sur grand parc (>1000 assets)
    ⚠️ À exécuter hors heures de production
    
    Usage:
        python manage.py shell
        >>> from scanner.signals import regenerate_all_qr_codes
        >>> regenerate_all_qr_codes()
    """
    from django.utils import timezone
    
    all_assets = Asset.objects.all()
    count = all_assets.count()
    
    logger.info(f'[BATCH] {count} assets à traiter')
    
    success = 0
    failed = 0
    
    for asset in all_assets:
        try:
            qr_obj, _ = QRCode.objects.get_or_create(asset=asset)
            image_url = _generate_qr_image(qr_obj)
            
            if image_url:
                success += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            logger.error(f'[BATCH] Erreur Asset {asset.id}: {str(e)}')
    
    logger.info(f'[BATCH] Terminé: {success} succès, {failed} échecs')
    
    return {
        'total': count,
        'success': success,
        'failed': failed,
        'timestamp': timezone.now()
    }