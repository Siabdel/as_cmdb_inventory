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
import ScannableCode
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings

from inventory.models import Asset
from scanner.models import ScannableCode

logger = logging.getLogger(__name__)

def _generate_qr_image(qr_obj):
    """
    Fonction pour générer l'image QR code à partir d'un objet ScannableCode.
    
    Args:
        qr_obj: Instance de ScannableCode (doit avoir asset, uuid_token, code)
    
    Returns:
        str: URL de l'image générée ou None en cas d'erreur
    
    Workflow:
        1. Créer données QR (code = qr_asset_<id>_<uuid>)
        2. Générer image PNG avec ScannableCode library
        3. Sauvegarder dans media/qr_codes/YYYY/MM/
        4. Mettre à jour ScannableCode.image
        5. Retourner URL
    
    Exemple:
        >>> qr_obj = ScannableCode.objects.create(asset=asset)
        >>> url = _generate_qr_image(qr_obj)
        >>> print(url)
        '/media/qr_codes/2026/03/qr_asset_152_abc123.png'
    """
    try:
        if not qr_obj or not qr_obj.asset:
            logger.error(f'[QR] ScannableCode ou Asset invalide: {qr_obj}')
            return None
        
        if not qr_obj.uuid_token:
            logger.error(f'[QR] uuid_token manquant pour ScannableCode {qr_obj.id}')
            return None
        
        # ====================================================================
        # CORRECTION CRITIQUE: S'assurer que uuid_token est un string valide
        # ====================================================================
        import uuid as uuid_lib
        
        # Si uuid_token est un objet UUID, le convertir en string AVEC tirets
        if isinstance(qr_obj.uuid_token, uuid_lib.UUID):
            uuid_str = str(qr_obj.uuid_token)  # 'abc123-def456-789g-hijk-lmnopqrstuvw'
        else:
            # Si c'est déjà un string, s'assurer qu'il a le bon format
            uuid_str = str(qr_obj.uuid_token)
            # Validation: doit avoir 5 segments avec tirets (format standard UUID)
            if uuid_str.count('-') != 4:
                logger.warning(f'[QR] UUID suspect: {uuid_str}')
        
        # Format QR Code: qr_asset_<asset_id>_<uuid_complet>
        qr_data = f"qr_asset_{qr_obj.asset.id}_{uuid_str}"
        
        logger.info(f'[QR] Données QR générées: {qr_data}')
        
        # Mettre à jour le champ code si vide
        if not qr_obj.code:
            qr_obj.code = qr_data
            qr_obj.save(update_fields=['code'])
        
        # ====================================================================
        # Génération image QR (inchangé)
        # ====================================================================
        import io
        import ScannableCode
        from django.core.files.base import ContentFile
        from datetime import datetime
        
        qr = ScannableCode.ScannableCode(
            version=1,
            error_correction=ScannableCode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95, optimize=True)
        buffer.seek(0)
        
        now = datetime.now()
        year_month = now.strftime('%Y/%m')
        filename = f"qr_asset_{qr_obj.asset.id}_{uuid_str}.png"
        filepath = f"qr_codes/{year_month}/{filename}"
        
        from django.conf import settings
        import os
        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        qr_obj.image.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        logger.info(f'[QR] Image générée: {qr_obj.image.url}')
        return qr_obj.image.url
        
    except Exception as e:
        logger.error(f'[QR] Erreur génération QR Code: {str(e)}', exc_info=True)
        return None


# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

@receiver(post_save, sender=Asset)
def auto_create_ScannableCode(sender, instance, created, **kwargs):
    """
    Signal post_save sur Asset.
    Crée automatiquement ScannableCode + génère image à la création d'Asset.
    
    Déclencheur: Asset.objects.create() ou Asset.save()
    Condition: created=True (nouvel asset uniquement)
    
    Workflow:
        1. Asset créé via POST /api/v1/inventory/assets/
        2. Signal post_save déclenché
        3. ScannableCode.objects.create(asset=instance)
        4. _generate_qr_image(qr_obj) appelé
        5. Image sauvegardée dans media/qr_codes/
    """
    if created:
        logger.info(f'[SIGNAL] Asset créé: {instance.id} - {instance.name}')
        
        try:
            # Créer ScannableCode associé
            qr_obj, created = ScannableCode.objects.get_or_create(
                asset=instance,
                defaults={
                    'code': f"qr_asset_{instance.id}_",  # Sera mis à jour avec uuid
                    'uuid_token': uuid.uuid4(),
                    
                }
            )
            
            if created:
                logger.info(f'[SIGNAL] ScannableCode créé pour Asset {instance.id}')
                
                # Générer image QR
                image_url = _generate_qr_image(qr_obj)
                
                if image_url:
                    logger.info(f'[SIGNAL] QR Code généré: {image_url}')
                else:
                    logger.warning(f'[SIGNAL] Échec génération QR pour Asset {instance.id}')
            else:
                logger.info(f'[SIGNAL] ScannableCode existant pour Asset {instance.id}')
                
        except Exception as e:
            logger.error(f'[SIGNAL] Erreur création ScannableCode: {str(e)}', exc_info=True)


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
        # Vérifier si ScannableCode existe
        qr_obj = ScannableCode.objects.filter(asset=instance).first()
        
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
    assets_without_qr = Asset.objects.filter(ScannableCode__isnull=True)
    count = assets_without_qr.count()
    
    logger.info(f'[BATCH] {count} assets sans QR Code trouvés')
    
    success = 0
    failed = 0
    
    for asset in assets_without_qr:
        try:
            qr_obj, created = ScannableCode.objects.get_or_create(asset=asset)
            
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
            qr_obj, _ = ScannableCode.objects.get_or_create(asset=asset)
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

    # backend/scanner/signals.py

# ============================================================================
# SIGNALS POUR GÉNÉRATION AUTOMATIQUE QR CODE & BARCODE
# Version: 2.0 — Mars 2026
# ============================================================================
@receiver(post_save, sender=Asset)
def auto_create_scannable_code(sender, instance, created, **kwargs):
    """
    Signal post_save sur Asset.
    Crée QR Code + Barcode selon le type d'asset.
    """
    if not created:
        return  # Ne traiter que les nouveaux assets
    
    logger.info(f'[SIGNAL] Asset créé: {instance.id} - {instance.name}')
    
    try:
        # ====================================================================
        # DÉTERMINER LE TYPE DE CODE À GÉNÉRER (Par Catégorie)
        # ====================================================================
        category_name = instance.category.name.lower() if instance.category else ''
        
        # ✅ Règles métier pour déterminer code_type
        if any(kw in category_name for kw in ['laptop', 'pc', 'serveur', 'server', 'network', 'switch', 'routeur']):
            # Asset IT Critique → QR Code + Barcode Serial
            codes_to_create = [
                {'code_type': 'qr_code', 'generate_image': True},
                {'code_type': 'barcode_serial', 'generate_image': False},
            ]
            
        elif any(kw in category_name for kw in ['écran', 'monitor', 'clavier', 'souris', 'périphérique']):
            # Périphérique → Barcode Serial uniquement (QR optionnel)
            codes_to_create = [
                {'code_type': 'barcode_serial', 'generate_image': False},
            ]
            
        elif any(kw in category_name for kw in ['ram', 'ssd', 'disque', 'batterie', 'consommable']):
            # Consommable → Rien (géré via StockItem)
            codes_to_create = []
            
        else:
            # Default → QR Code uniquement
            codes_to_create = [
                {'code_type': 'qr_code', 'generate_image': True},
            ]
        
        # ====================================================================
        # CRÉER LES CODES SCANNABLES
        # ====================================================================
        for config in codes_to_create:
            code_type = config['code_type']
            generate_image = config['generate_image']
            
            # Déterminer le code à stocker
            if code_type == 'qr_code':
                code_value = f"qr_asset_{instance.id}_{uuid.uuid4()}"
            elif code_type == 'barcode_serial' and instance.serial_number:
                code_value = instance.serial_number
            elif code_type == 'barcode_internal' and instance.internal_code:
                code_value = instance.internal_code
            else:
                continue  # Skip si pas de données
            
            # Créer l'objet ScannableCode/Barcode
            scannable, scannable_created = ScannableCode.objects.get_or_create(
                asset=instance,
                code_type=code_type,
                defaults={
                    'code': code_value,
                    'uuid_token': uuid.uuid4() if code_type == 'qr_code' else None,
                }
            )
            
            if scannable_created:
                logger.info(f'[SIGNAL] {code_type} créé pour Asset {instance.id}')
                
                # Générer image uniquement pour QR Code
                if generate_image and code_type == 'qr_code':
                    image_url = _generate_qr_image(scannable)
                    if image_url:
                        logger.info(f'[SIGNAL] Image QR générée: {image_url}')
                        
    except Exception as e:
        logger.error(f'[SIGNAL] Erreur création code scannable: {str(e)}', exc_info=True)


# ============================================================================
# SIGNAL POUR CRÉATION AUTOMATIQUE BARCODE RÉFÉRENCE STOCK
# ============================================================================
@receiver(post_save, sender='stock.StockItem')
def auto_create_stock_barcode(sender, instance, created, **kwargs):
    """
    Signal post_save sur StockItem.
    Crée automatiquement un Barcode de référence pour les consommables.
    
    Format: REF-<reference>-<id>
    """
    if not created:
        return
    
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
            
    except Exception as e:
        logger.error(f'[SIGNAL] Erreur création barcode stock: {str(e)}', exc_info=True)