# backend/scanner/views.py
# ============================================================================
# SCANNER VIEWS — QR Code & Code-Barres
# Version: 2.0 — Mars 2026
# ============================================================================

from django.shortcuts import render 
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import QRCode, ScanLog
from inventory.models import Asset
from inventory.serializers import AssetDetailSerializer
from maintenance.models import MaintenanceTicket as Ticket
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def extract_uuid_from_qr(qr_text):
    """
    Extrait l'UUID depuis différents formats de QR Code.
    
    Formats supportés:
    1. qr_asset_<id>_<uuid>  → Extrait UUID
    2. <uuid>                → UUID direct
    3. <serial_number>       → Numéro de série (retourne tel quel)
    4. <internal_code>       → Code interne (retourne tel quel)
    
    Args:
        qr_text: Texte brut du QR Code scanné
    
    Returns:
        str: UUID extrait ou texte brut pour recherche backend
    """
    # Format: qr_asset_<id>_<uuid>
    if qr_text.startswith('qr_asset_'):
        parts = qr_text.split('_')
        if len(parts) >= 3:
            uuid = parts[-1]  # Dernier élément = UUID
            logger.info(f'[QR] Format détecté: qr_asset_<id>_<uuid> → {uuid}')
            return uuid
    
    # Format: UUID direct (validation basique)
    import uuid as uuid_lib
    try:
        uuid_lib.UUID(qr_text)
        logger.info(f'[QR] Format détecté: UUID direct → {qr_text}')
        return qr_text
    except ValueError:
        pass
    
    # Format: Numéro de série ou code interne (retourne tel quel)
    logger.info(f'[QR] Format détecté: Serial/Code → {qr_text}')
    return qr_text


def resolve_by_serial_or_code(code):
    """
    Résout un code vers un Asset par numéro de série ou code interne.
    
    Args:
        code: Numéro de série ou code interne
    
    Returns:
        Asset or None: Instance Asset si trouvé, None sinon
    """
    # 1. Essayer par numéro de série
    try:
        asset = Asset.objects.select_related(
            'category', 'brand', 'location', 'assigned_to'
        ).prefetch_related('tags').get(serial_number=code)
        logger.info(f'[QR] Asset trouvé par serial_number: {code}')
        return asset
    except Asset.DoesNotExist:
        pass
    
    # 2. Essayer par code interne
    try:
        asset = Asset.objects.select_related(
            'category', 'brand', 'location', 'assigned_to'
        ).prefetch_related('tags').get(internal_code=code)
        logger.info(f'[QR] Asset trouvé par internal_code: {code}')
        return asset
    except Asset.DoesNotExist:
        pass
    
    # 3. Essayer par nom (fuzzy search)
    try:
        asset = Asset.objects.select_related(
            'category', 'brand', 'location', 'assigned_to'
        ).prefetch_related('tags').filter(name__icontains=code).first()
        if asset:
            logger.info(f'[QR] Asset trouvé par name: {code}')
            return asset
    except Exception as e:
        logger.warning(f'[QR] Erreur recherche par nom: {e}')
    
    logger.warning(f'[QR] Asset non trouvé pour code: {code}')
    return None


# ============================================================================
# API ENDPOINTS
# ============================================================================

# backend/scanner/views.py

# backend/scanner/views.py
# ============================================================================
# SCANNER VIEWS — QR Code & Code-Barres
# Version: 3.0 — Correction erreur request
# ============================================================================

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpRequest  # ✅ Import explicite si besoin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request  # ✅ DRF Request type

from .models import QRCode, ScanLog
from inventory.models import Asset
from inventory.serializers import AssetDetailSerializer
from maintenance.models import MaintenanceTicket as Ticket

import logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])  # Public — accès sans auth
def resolve_qr(request, uuid_token):
    """
    Endpoint scanné par mobile/desktop.
    Enregistre le ScanLog et retourne la fiche asset complète.
    
    URL: GET /api/v1/scanner/scan/<uuid_token>/
    
    Formats supportés:
    1. QR Code UUID
    2. Serial Number (code-barres)
    3. Internal Code (code-barres)
    """
    logger.info(f'[QR] Scan reçu: {uuid_token}')
    
    qr_obj = None
    asset = None
    code_type = 'unknown'
    
    # ====================================================================
    # 1. RÉSOLUTION DU CODE SCANNÉ
    # ====================================================================
    try:
        # Essayer QR Code UUID
        qr_obj = QRCode.objects.select_related('asset').get(uuid_token=uuid_token)
        asset = qr_obj.asset
        code_type = 'qr_code'
        logger.info(f'[QR] Trouvé par QRCode UUID: {uuid_token}')
        
    except QRCode.DoesNotExist:
        # Essayer par serial_number (code-barres)
        try:
            asset = Asset.objects.select_related(
                'category', 'brand', 'location', 'assigned_to'
            ).prefetch_related('tags').get(serial_number=uuid_token)
            
            qr_obj, created = QRCode.objects.get_or_create(asset=asset)
            if created:
                qr_obj.code_type = 'barcode_serial'
                qr_obj.save(update_fields=['code_type'])
                from scanner.signals import _generate_qr_image
                _generate_qr_image(qr_obj)
            
            code_type = 'barcode_serial'
            logger.info(f'[QR] Trouvé par serial_number: {uuid_token}')
            
        except Asset.DoesNotExist:
            # Essayer par internal_code (code-barres)
            try:
                asset = Asset.objects.select_related(
                    'category', 'brand', 'location', 'assigned_to'
                ).prefetch_related('tags').get(internal_code=uuid_token)
                
                qr_obj, created = QRCode.objects.get_or_create(asset=asset)
                if created:
                    qr_obj.code_type = 'barcode_internal'
                    qr_obj.save(update_fields=['code_type'])
                
                code_type = 'barcode_internal'
                logger.info(f'[QR] Trouvé par internal_code: {uuid_token}')
                
            except Asset.DoesNotExist:
                logger.warning(f'[QR] Code non reconnu: {uuid_token}')
                return Response(
                    {'error': f'Code scanné invalide: {uuid_token}'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    # ====================================================================
    # 2. ENREGISTRER SCANLOG — ✅ CORRECTION ICI
    # ====================================================================
    try:
        # ✅ CORRECTION: Utiliser request.user pour l'utilisateur connecté
        # Si authentifié: username, sinon: 'anonymous' ou IP
        if hasattr(request, 'user') and request.user.is_authenticated:
            scanned_by = request.user.username
            logger.info(f'[QR] Utilisateur authentifié: {scanned_by}')
        else:
            # Fallback: essayer query param ou anonymous
            scanned_by = request.query_params.get('user', 'anonymous')
            logger.info(f'[QR] Utilisateur non authentifié: {scanned_by}')
        
        # Déterminer la localisation actuelle
        location_at_scan = None
        if asset and hasattr(asset, 'current_location'):
            location_at_scan = asset.current_location
        
        scan_log = ScanLog.objects.create(
            qrcode=qr_obj,
            asset=asset,
            scanned_by=scanned_by,  # ✅ Maintenant correct
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            code_type=code_type,
            scanned_code=uuid_token,
            location_at_scan=location_at_scan,
        )
        logger.info(f'[QR] ScanLog créé: {scan_log.id} par {scanned_by}')
        
    except Exception as e:
        logger.error(f'[QR] Erreur création ScanLog: {e}', exc_info=True)
        # Continue même si ScanLog échoue (non bloquant)
    # ====================================================================
    # 3. INCRÉMENTER COMPTEUR
    # ====================================================================
    if qr_obj:
        try:
            QRCode.objects.filter(pk=qr_obj.pk).update(
                scanned_count=qr_obj.scanned_count + 1,
                last_scanned_at=timezone.now()
            )
        except Exception as e:
            logger.error(f'[QR] Erreur incrément compteur: {e}')
    
    # ====================================================================
    # 4. RETOURNER LES DONNÉES
    # ====================================================================
    data = AssetDetailSerializer(asset).data
    data['scanned_code'] = uuid_token
    data['code_type'] = code_type
    
    logger.info(f'[QR] Scan terminé: {asset.name}')
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_qr(request, asset_id):
    """
    Force la régénération du QR code d'un asset.
    
    URL: POST /api/v1/scanner/assets/<asset_id>/regen-qr/
    """
    logger.info(f'[QR] Régénération QR pour asset {asset_id}')
    
    try:
        asset = Asset.objects.get(pk=asset_id)
    except Asset.DoesNotExist:
        logger.warning(f'[QR] Asset introuvable: {asset_id}')
        return Response({'error': 'Asset introuvable.'}, status=404)

    qr_obj, _ = QRCode.objects.get_or_create(asset=asset)
    
    from scanner.signals import _generate_qr_image
    _generate_qr_image(qr_obj)
    
    logger.info(f'[QR] QR Code régénéré pour asset {asset_id}')
    
    return Response({
        'uuid': str(qr_obj.uuid_token),
        'url': qr_obj.url,
        'image': request.build_absolute_uri(qr_obj.image.url) if qr_obj.image else None,
    })


def public_scan_result(request, uuid):
    """
    Page publique de résultat de scan - sans authentification.
    
    URL: GET /scan/<uuid>/
    
    ✅ CORRECTION: Chercher via QRCode, pas Asset.qr_uuid (n'existe pas)
    """
    logger.info(f'[QR] Page publique scan: {uuid}')
    
    # ✅ CORRECTION: Chercher d'abord dans QRCode
    asset = None
    
    try:
        qr_obj = QRCode.objects.select_related('asset').get(uuid_token=uuid)
        asset = qr_obj.asset
    except QRCode.DoesNotExist:
        # Essayer par serial_number
        try:
            asset = Asset.objects.get(serial_number=uuid)
        except Asset.DoesNotExist:
            # Essayer par internal_code
            try:
                asset = Asset.objects.get(internal_code=uuid)
            except Asset.DoesNotExist:
                logger.warning(f'[QR] Asset non trouvé pour page publique: {uuid}')
                return render(request, 'public/scan_not_found.html', {'code': uuid})
    
    # Tickets ouverts liés
    open_tickets = Ticket.objects.filter(
        asset=asset,
        status__in=['open', 'assigned', 'in_progress']
    )
    
    context = {
        'asset': asset,
        'open_tickets': open_tickets,
        'scan_date': timezone.now()
    }
    
    logger.info(f'[QR] Page publique affichée: {asset.name}')
    return render(request, 'public/scan_result.html', context)

# ============================================================================
# ENDPOINT DE RÉGÉNÉRATION DE QR CODE (ADMIN)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_qr(request, asset_id):
    """
    Force la régénération du QR code d'un asset.
    
    URL: POST /api/v1/scanner/assets/<asset_id>/regen-qr/
    
    Args:
        asset_id: ID de l'asset
    
    Returns:
        Response: UUID, URL, image
    """
    try:
        asset = Asset.objects.get(pk=asset_id)
    except Asset.DoesNotExist:
        logger.warning(f'[QR] Asset introuvable: {asset_id}')
        return Response({'error': 'Asset introuvable.'}, status=404)
    
    # Créer ou récupérer QRCode
    qr_obj, _ = QRCode.objects.get_or_create(asset=asset)
    
    # Régénérer l'image
    from scanner.signals import _generate_qr_image
    _generate_qr_image(qr_obj)
    
    logger.info(f'[QR] QR Code régénéré pour asset {asset_id}')
    
    return Response({
        'uuid': str(qr_obj.uuid_token),
        'url': qr_obj.url,
        'image': request.build_absolute_uri(qr_obj.image.url) if qr_obj.image else None,
    })


# ============================================================================
# PAGE PUBLIQUE (Sans Authentication)
# ============================================================================

def public_scan_result(request, uuid):
    """
    Page publique de résultat de scan — sans authentification.
    
    URL: GET /scan/<uuid>/
    
    Usage: Smartphone natif scanne QR → ouvre page web publique
    
    Args:
        uuid: UUID du QR Code ou serial_number
    
    Returns:
        HttpResponse: Template HTML public
    """
    logger.info(f'[QR] Page publique scan: {uuid}')
    
    # 1. Extraire UUID selon format
    extracted_uuid = extract_uuid_from_qr(uuid)
    
    # 2. Trouver l'asset
    asset = None
    
    # Essayer par QRCode UUID
    try:
        qr_obj = QRCode.objects.select_related('asset').get(uuid_token=extracted_uuid)
        asset = qr_obj.asset
    except QRCode.DoesNotExist:
        pass
    
    # Essayer par serial_number ou internal_code
    if not asset:
        asset = resolve_by_serial_or_code(extracted_uuid)
    
    # Asset non trouvé
    if not asset:
        logger.warning(f'[QR] Asset non trouvé pour page publique: {uuid}')
        return render(request, 'public/scan_not_found.html', {'code': uuid}, status=404)
    
    # 3. Tickets ouverts liés
    open_tickets = Ticket.objects.filter(
        asset=asset,
        status__in=['open', 'assigned', 'in_progress']
    )
    
    # 4. Contexte template
    context = {
        'asset': asset,
        'open_tickets': open_tickets,
        'scan_date': timezone.now()
    }
    
    logger.info(f'[QR] Page publique affichée: {asset.name}')
    return render(request, 'public/scan_result.html', context)


# ============================================================================
# STATS & AUDIT (Optionnel)
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scan_stats(request):
    """
    Statistiques des scans.
    
    URL: GET /api/v1/scanner/stats/
    
    Returns:
        Response: Stats scans (today, week, total)
    """
    from django.db.models import Count
    from datetime import timedelta
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    stats = {
        'scans_today': ScanLog.objects.filter(created_at__date=today).count(),
        'scans_week': ScanLog.objects.filter(created_at__date__gte=week_ago).count(),
        'scans_total': ScanLog.objects.count(),
        'assets_scanned': ScanLog.objects.values('qrcode__asset').distinct().count(),
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scan_logs(request):
    """
    Historique des scans.
    
    URL: GET /api/v1/scanner/logs/
    
    Query Params:
        - limit: Nombre de résultats (default: 50)
        - asset: Filtrer par asset ID
        - date_from: Date début
        - date_to: Date fin
    
    Returns:
        Response: Liste des ScanLog
    """
    limit = int(request.query_params.get('limit', 50))
    asset_id = request.query_params.get('asset')
    
    logs = ScanLog.objects.select_related('qrcode__asset').order_by('-created_at')
    
    if asset_id:
        logs = logs.filter(qrcode__asset_id=asset_id)
    
    logs = logs[:limit]
    
    data = [{
        'id': log.id,
        'asset_id': log.qrcode.asset.id if log.qrcode and log.qrcode.asset else None,
        'asset_name': log.qrcode.asset.name if log.qrcode and log.qrcode.asset else 'N/A',
        'scanned_by': log.scanned_by,
        'scanned_at': log.created_at.isoformat(),
        'ip_address': log.ip_address,
        'code_type': log.code_type,
        'scanned_code': log.scanned_code,
    } for log in logs]
    
    return Response(data)