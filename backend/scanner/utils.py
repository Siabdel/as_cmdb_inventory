# backend/scanner/utils.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from inventory.models import Asset
from maintenance.models import MaintenanceTicket as Ticket
from printer.models import PrintLog
# backend/scanner/views.py
from django.http import HttpResponse
from inventory.serializers import AssetDetailSerializer
from maintenance.models import MaintenanceTicket as Ticket
# backend/scanner/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, Sum
from datetime import timedelta
from scanner.models import ScannableCode as QRCode, ScanLog
from inventory.models import Asset
from inventory.serializers import AssetDetailSerializer
from maintenance.models import MaintenanceTicket as Ticket
# backend/scanner/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from scanner.services.pdf_generator import generate_label_pdf
from inventory.models import Asset
import logging
from printer.models import Printer, PrintJob, PrintLog, PrintTemplate


@api_view(['GET'])
@permission_classes([AllowAny])  # Public — accès sans auth
def resolve_qr(request, uuid_token):
    """
    Endpoint scanné par mobile/desktop.
    Accepte : QR Code UUID, Serial Number, ou Internal Code
    Enregistre le ScanLog et retourne la fiche asset complète.
    """
    qr_obj = None
    asset = None
    code_type = 'unknown'
    
    try:
        # 1. Essayer de trouver par QR Code UUID
        qr_obj = QRCode.objects.select_related('asset').get(uuid_token=uuid_token)
        asset = qr_obj.asset
        code_type = 'qr_code'
        
    except QRCode.DoesNotExist:
        # 2. Essayer de trouver par Numéro de Série (code-barres)
        try:
            asset = Asset.objects.select_related(
                'category', 'brand', 'location', 'assigned_to'
            ).prefetch_related('tags').get(serial_number=uuid_token)
            
            # Créer QR code s'il n'existe pas
            qr_obj, created = QRCode.objects.get_or_create(asset=asset)
            if created:
                from scanner.signals import _generate_qr_image
                _generate_qr_image(qr_obj)
            
            code_type = 'barcode_serial'
            
        except Asset.DoesNotExist:
            # 3. Essayer de trouver par Code Interne (code-barres)
            try:
                asset = Asset.objects.select_related(
                    'category', 'brand', 'location', 'assigned_to'
                ).prefetch_related('tags').get(internal_code=uuid_token)
                
                # Créer QR code s'il n'existe pas
                qr_obj, created = QRCode.objects.get_or_create(asset=asset)
                if created:
                    from scanner.signals import generate_qr_image
                    _generate_qr_image(qr_obj)
                
                code_type = 'barcode_internal'
                
            except Asset.DoesNotExist:
                return Response(
                    {'error': f'Code scanné invalide : {uuid_token}'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    # Enregistrer le scan avec le type de code
    ScanLog.objects.create(
        qrcode=qr_obj,
        scanned_by=request.query_params.get('user', ''),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        code_type=code_type,
        scanned_code=uuid_token
    )
    
    # Incrémenter le compteur
    QRCode.objects.filter(pk=qr_obj.pk).update(
        scanned_count=qr_obj.scanned_count + 1,
        last_scanned_at=timezone.now()
    )
    
    # Retourner les données avec le type de code scanné
    from inventory.serializers import AssetDetailSerializer
    data = AssetDetailSerializer(asset).data
    data['scanned_code'] = uuid_token
    data['code_type'] = code_type
    
    return Response(data)


def public_scan_result(request, uuid):
    """
    Page publique de résultat de scan - sans authentification
    URL: /scan/<uuid>/
    """
    # ⚠️ CORRECTION: Ne PAS utiliser qr_uuid (n'existe pas dans Asset)
    # Chercher d'abord dans QRCode, puis récupérer l'asset lié
    
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
    return render(request, 'public/scan_result.html', context)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def regenerate_qr(request, asset_id):
    """Force la régénération du QR code d'un asset."""
    from inventory.models import Asset
    from cmdb_admin.barcode_service import generate_qrcode_image
    
    try:
        asset = Asset.objects.get(pk=asset_id)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset introuvable.'}, status=404)

    qr_obj, _ = QRCode.objects.get_or_create(asset=asset)
    ## Forcer la régénération de l'image QR
    generate_qrcode_image(qr_obj)

    return Response({
        'uuid': str(qr_obj.uuid_token),
        'url': qr_obj.url,
        'image': request.build_absolute_uri(qr_obj.image.url) if qr_obj.image else None,
    })




logger = logging.getLogger(__name__)




# ⚠️ CORRECTION: Import conditionnel (éviter erreur si module manquant)
try:
    from scanner.services.pdf_generator import generate_label_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    generate_label_pdf = None


@api_view(['GET'])
@permission_classes([AllowAny])
def resolve_qr(request, uuid_token):
    """
    Endpoint scanné par mobile/desktop.
    Accepte : QR Code UUID, Serial Number, ou Internal Code
    """
    qr_obj = None
    asset = None
    code_type = 'unknown'
    
    try:
        # 1. QR Code UUID
        qr_obj = QRCode.objects.select_related('asset').get(uuid_token=uuid_token)
        asset = qr_obj.asset
        code_type = 'qr_code'
        
    except QRCode.DoesNotExist:
        # 2. Serial Number (Barcode)
        try:
            asset = Asset.objects.select_related(
                'category', 'brand', 'location', 'assigned_to'
            ).prefetch_related('tags').get(serial_number=uuid_token)
            
            qr_obj, created = QRCode.objects.get_or_create(asset=asset)
            if created:
                from scanner.signals import generate_qr_image
                generate_qr_image(qr_obj)
            
            code_type = 'barcode_serial'
            
        except Asset.DoesNotExist:
            # 3. Internal Code (Barcode)
            try:
                asset = Asset.objects.select_related(
                    'category', 'brand', 'location', 'assigned_to'
                ).prefetch_related('tags').get(internal_code=uuid_token)
                
                qr_obj, created = QRCode.objects.get_or_create(asset=asset)
                if created:
                    from scanner.signals import generate_qr_image
                    generate_qr_image(qr_obj)
                
                code_type = 'barcode_internal'
                
            except Asset.DoesNotExist:
                return Response(
                    {'error': f'Code scanné invalide : {uuid_token}'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    # Enregistrer le scan
    ScanLog.objects.create(
        qrcode=qr_obj,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        code_type=code_type,
        scanned_code=uuid_token
    )
    
    # Incrémenter compteur
    QRCode.objects.filter(pk=qr_obj.pk).update(
        scanned_count=qr_obj.scanned_count + 1,
        last_scanned_at=timezone.now()
    )
    
    # Retourner les données
    data = AssetDetailSerializer(asset).data
    data['scanned_code'] = uuid_token
    data['code_type'] = code_type
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_qr(request, asset_id):
    """Force la régénération du QR code d'un asset."""
    from cmdb_admin.barcode_service import generate_qrcode_image
    
    try:
        asset = Asset.objects.get(pk=asset_id)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset introuvable.'}, status=404)

    qr_obj, _ = QRCode.objects.get_or_create(asset=asset)
    generate_qrcode_image(qr_obj)

    return Response({
        'uuid': str(qr_obj.uuid_token),
        'url': qr_obj.url,
        'image': request.build_absolute_uri(qr_obj.image.url) if qr_obj.image else None,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def print_label_pdf(request, asset_id):
    """
    Génère un PDF d'étiquette pour un asset.
    GET /api/v1/scanner/print-label/<asset_id>/
    """
    if not PDF_AVAILABLE:
        return Response(
            {'error': 'Module PDF non installé (reportlab)'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    asset = get_object_or_404(Asset, id=asset_id)
    format = request.query_params.get('format', '50x30')
    copies = int(request.query_params.get('copies', 1))
    
    pdf_buffer = generate_label_pdf([asset], format=format, copies=copies)
    
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="label_{asset.id}.pdf"'
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def print_labels_batch(request):
    """
    Génère un PDF batch pour multiple assets.
    POST /api/v1/scanner/print-labels/
    Body: {"asset_ids": [1,2,3], "format": "50x30", "copies": 1}
    """
    if not PDF_AVAILABLE:
        return Response(
            {'error': 'Module PDF non installé (reportlab)'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    asset_ids = request.data.get('asset_ids', [])
    format = request.data.get('format', '50x30')
    copies = request.data.get('copies', 1)
    
    if not asset_ids:
        return Response({'error': 'asset_ids requis'}, status=400)
    
    assets = Asset.objects.filter(id__in=asset_ids)
    if not assets.exists():
        return Response({'error': 'Aucun asset trouvé'}, status=404)
    
    pdf_buffer = generate_label_pdf(assets, format=format, copies=copies)
    
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="labels_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


def public_scan_result(request, uuid):
    """Page publique de résultat de scan - sans authentification"""
    # Chercher par QRCode UUID
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
    return render(request, 'public/scan_result.html', context)



# ============================================================================
# LANDING PAGE SCAN & PRINT HUB
# ============================================================================

@login_required
def scan_print_landing(request):
    """
    Landing page centrale pour les techniciens — Hub Scan & Print.
    URL: /admin/scan-print/
    
    Affiche:
    - Statistiques en temps réel (scans, prints, assets, printers)
    - Activité récente (derniers scans et impressions)
    - Accès rapide à toutes les fonctionnalités
    """
    # Statistiques du jour
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Scans aujourd'hui
    scans_today = ScanLog.objects.filter(
        created_at__date=today
    ).count()
    
    # Impressions aujourd'hui
    prints_today = PrintLog.objects.filter(
        printed_at__date=today
    ).count()
    
    # Total assets
    total_assets = Asset.objects.count()
    
    # Imprimantes actives
    printers_active = Printer.objects.filter(is_active=True).count()
    
    # Activité récente (10 derniers événements)
    recent_scans = ScanLog.objects.select_related(
        'qrcode__asset'
    ).order_by('-created_at')[:5]
    
    recent_prints = PrintLog.objects.select_related(
        'asset', 'printed_by', 'job'
    ).order_by('-printed_at')[:5]
    
    # Combiner et trier par date
    activity = []
    
    for scan in recent_scans:
        activity.append({
            'type': 'scan',
            'title': f"📷 Scan: {scan.qrcode.asset.name if scan.qrcode and scan.qrcode.asset else 'Asset inconnu'}",
            'meta': f"Par: {scan.scanned_by or 'Inconnu'} • IP: {scan.ip_address or 'N/A'}",
            'time': scan.created_at,
            'icon': '📷'
        })
    
    for print_log in recent_prints:
        activity.append({
            'type': 'print',
            'title': f"🖨️ Impression: {print_log.asset.name if print_log.asset else 'Asset inconnu'}",
            'meta': f"Par: {print_log.printed_by or 'Inconnu'} • {print_log.printer_name}",
            'time': print_log.printed_at,
            'icon': '🖨️'
        })
    
    # Trier par date décroissante
    activity.sort(key=lambda x: x['time'], reverse=True)
    activity = activity[:10]  # Garder seulement 10
    
    # Assets par statut (pour stats rapides)
    assets_by_status = Asset.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Jobs d'impression récents
    recent_jobs = PrintJob.objects.select_related(
        'created_by', 'template', 'printer'
    ).order_by('-created_at')[:5]
    
    context = {
        # Stats
        'scans_today': scans_today,
        'prints_today': prints_today,
        'total_assets': total_assets,
        'printers_active': printers_active,
        
        # Activité
        'recent_activity': activity,
        'recent_scans': recent_scans,
        'recent_prints': recent_prints,
        
        # Assets
        'assets_by_status': assets_by_status,
        
        # Jobs
        'recent_jobs': recent_jobs,
        
        # Meta
        'page_title': 'Scan & Print Hub',
        'today': today,
    }
    
    return render(request, 'admin/scan_print/landing.html', context)


# ============================================================================
# API ENDPOINTS POUR STATS (utilisés par le frontend Vue.js)
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scan_print_stats(request):
    """
    API Endpoint pour statistiques Scan & Print.
    GET /api/v1/scanner/stats/
    
    Retourne:
    {
        "scans_today": 145,
        "prints_today": 89,
        "total_assets": 210,
        "printers_active": 3,
        "scans_this_week": 890,
        "prints_this_week": 456,
        "assets_by_status": [...],
        "top_scanned_assets": [...]
    }
    """
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Stats jour
    scans_today = ScanLog.objects.filter(
        created_at__date=today
    ).count()
    
    prints_today = PrintLog.objects.filter(
        printed_at__date=today
    ).count()
    
    # Stats semaine
    scans_week = ScanLog.objects.filter(
        created_at__date__gte=week_ago
    ).count()
    
    prints_week = PrintLog.objects.filter(
        printed_at__date__gte=week_ago
    ).count()
    
    # Total assets
    total_assets = Asset.objects.count()
    
    # Assets par statut
    assets_by_status = list(Asset.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')[:5])
    
    # Imprimantes actives
    printers_active = Printer.objects.filter(is_active=True).count()
    
    # Top assets scannés (7 jours)
    top_scanned = ScanLog.objects.filter(
        created_at__date__gte=week_ago
    ).values(
        'qrcode__asset__id',
        'qrcode__asset__name',
        'qrcode__asset__serial_number'
    ).annotate(
        scan_count=Count('id')
    ).order_by('-scan_count')[:5]
    
    return Response({
        'scans_today': scans_today,
        'prints_today': prints_today,
        'total_assets': total_assets,
        'printers_active': printers_active,
        'scans_this_week': scans_week,
        'prints_this_week': prints_week,
        'assets_by_status': assets_by_status,
        'top_scanned_assets': list(top_scanned),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """
    API Endpoint pour activité récente.
    GET /api/v1/scanner/recent-activity/
    
    Retourne les 10 derniers événements (scans + prints)
    """
    # Derniers scans
    recent_scans = ScanLog.objects.select_related(
        'qrcode__asset', 'scanned_by'
    ).order_by('-created_at')[:5]
    
    # Dernières impressions
    recent_prints = PrintLog.objects.select_related(
        'asset', 'printed_by', 'job'
    ).order_by('-printed_at')[:5]
    
    activity = []
    
    for scan in recent_scans:
        activity.append({
            'id': f'scan-{scan.id}',
            'type': 'scan',
            'asset_id': scan.qrcode.asset.id if scan.qrcode and scan.qrcode.asset else None,
            'asset_name': scan.qrcode.asset.name if scan.qrcode and scan.qrcode.asset else 'Inconnu',
            'user': scan.scanned_by.username if scan.scanned_by else 'Inconnu',
            'ip_address': scan.ip_address,
            'timestamp': scan.created_at.isoformat(),
            'icon': '📷'
        })
    
    for print_log in recent_prints:
        activity.append({
            'id': f'print-{print_log.id}',
            'type': 'print',
            'asset_id': print_log.asset.id if print_log.asset else None,
            'asset_name': print_log.asset.name if print_log.asset else 'Inconnu',
            'user': print_log.printed_by.username if print_log.printed_by else 'Inconnu',
            'printer': print_log.printer_name,
            'timestamp': print_log.printed_at.isoformat(),
            'icon': '🖨️'
        })
    
    # Trier par timestamp
    activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response(activity[:10])


# ============================================================================
# PRINT MANAGEMENT VIEWS
# ============================================================================

@login_required
def print_labels_view(request):
    """
    Page d'impression d'étiquettes.
    URL: /admin/scanner/print/
    
    Permet de:
    - Sélectionner des assets
    - Choisir template et imprimante
    - Générer et imprimer PDF batch
    """
    # Récupérer templates
    templates = PrintTemplate.objects.filter(is_default=True)
    
    # Récupérer imprimantes
    printers = Printer.objects.filter(is_default=True)
    
    # Assets sélectionnés (depuis URL params)
    asset_ids = request.GET.get('assets', '')
    if asset_ids:
        asset_ids = [int(id) for id in asset_ids.split(',')]
        selected_assets = Asset.objects.filter(id__in=asset_ids)
    else:
        selected_assets = Asset.objects.none()
    
    context = {
        'templates': templates,
        'printers': printers,
        'selected_assets': selected_assets,
        'asset_ids': asset_ids,
    }
    
    return render(request, 'admin/scanner/print.html', context)


@login_required
def print_templates_view(request):
    """
    Gestion des templates d'étiquettes.
    URL: /admin/scanner/templates/
    """
    templates = PrintTemplate.objects.all()
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'admin/scanner/templates.html', context)


@login_required
def printers_view(request):
    """
    Gestion des imprimantes.
    URL: /admin/scanner/printers/
    """
    printers = Printer.objects.all()
    
    context = {
        'printers': printers,
    }
    
    return render(request, 'admin/scanner/printers.html', context)


@login_required
def print_jobs_view(request):
    """
    Historique des jobs d'impression.
    URL: /admin/scanner/jobs/
    """
    jobs = PrintJob.objects.select_related(
        'created_by', 'template', 'printer'
    ).order_by('-created_at')[:50]
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'admin/scanner/jobs.html', context)


@login_required
def print_logs_view(request):
    """
    Logs d'audit d'impression.
    URL: /admin/scanner/logs/
    """
    logs = PrintLog.objects.select_related(
        'asset', 'printed_by', 'job'
    ).order_by('-printed_at')[:100]
    
    # Filtres
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    asset_id = request.GET.get('asset_id')
    user_id = request.GET.get('user_id')
    
    if date_from:
        logs = logs.filter(printed_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(printed_at__date__lte=date_to)
    if asset_id:
        logs = logs.filter(asset_id=asset_id)
    if user_id:
        logs = logs.filter(printed_by_id=user_id)
    
    context = {
        'logs': logs,
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'asset_id': asset_id,
            'user_id': user_id,
        }
    }
    
    return render(request, 'admin/scanner/logs.html', context)