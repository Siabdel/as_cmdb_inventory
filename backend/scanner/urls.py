from django.urls import path, include
from scanner import views
from scanner.api import views as api_views
from django.views.generic import TemplateView
from scanner import views as scanner_views
from printer.api  import viewsets 
from . import utils


# backend/scanner/urls.py
urlpatterns = [
    # API Endpoints
    ## Pages pour scanner (résolution QR code, stats, logs)
    path('scan/<str:uuid_token>/', scanner_views.resolve_qr, name='resolve_qr'),
    path('assets/<int:asset_id>/regen-qr/', scanner_views.regenerate_qr, name='regen_qr'),
    path('stats/', scanner_views.scan_stats, name='scan_stats'),
    path('logs/', scanner_views.scan_logs, name='scan_logs'),
    # Page publique (sans /api/)
    ##path('scan/<str:uuid>/', utils.public_scan_result, name='public_scan'),  # Sans auth

    # Landing Page Scan & Print
    path('scan-print/', utils.scan_print_landing, name='scan-print-landing'),
    # API Endpoints for scanner
    path('print-logs/', viewsets.PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
    path('logs/', viewsets.PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
    path('printers/', viewsets.PrinterViewSet.as_view({'get': 'list'}), name='printers'),
]

# API Endpoints
urlpatterns += [
    ## Admin URLs for print management
    ##path('admin/print-templates/', views.PrintTemplateListView.as_view(), name='admin_print_templates'),
    path('admin/scan-print/', utils.scan_print_landing, name='admin_scan_print_landing'),
    # sanner admin
    path('dashboard/', TemplateView.as_view(template_name='admin/scanner/index.html'), name='admin_scanner') ,
    path('scanner/search/', TemplateView.as_view(template_name='admin/scanner/search.html'), name='admin_scanner_search') ,
]