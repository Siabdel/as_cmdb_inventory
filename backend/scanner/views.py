# backend/scanner/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.db.models import Count, Q, F, Sum
from datetime import timedelta
from scanner.models import QRCode, ScanLog
from printer.models import PrintTemplate, Printer, PrintJob, PrintLog
from inventory.models import Asset
from inventory.serializers import AssetDetailSerializer
from maintenance.models import MaintenanceTicket as Ticket


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

