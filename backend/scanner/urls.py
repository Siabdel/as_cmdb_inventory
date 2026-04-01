from django.urls import path, include
from scanner import views
from scanner.api import views as api_views
from django.views.generic import TemplateView
from scanner import utils
from printer.api  import viewsets 


# backend/scanner/urls.py
urlpatterns = [
    path('scan/<uuid:uuid_token>/', utils.resolve_qr,    name='resolve-qr'),
    path('assets/<int:asset_id>/regen-qr/', utils.regenerate_qr, name='regenerate-qr'),
    ##

    # Landing Page Scan & Print
    path('scan-print/', views.scan_print_landing, name='scan-print-landing'),

    # Page publique scan
    path('scan/<str:uuid>/', utils.public_scan_result, name='public_scan'),  # Sans auth

    # API Endpoints for scanner
    path('print-logs/', viewsets.PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
    path('logs/', viewsets.PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
    path('printers/', viewsets.PrinterViewSet.as_view({'get': 'list'}), name='printers'),
]

# API Endpoints
urlpatterns += [
    ## Admin URLs for print management
    ##path('admin/print-templates/', views.PrintTemplateListView.as_view(), name='admin_print_templates'),
    path('admin/scan-print/', views.scan_print_landing, name='admin_scan_print_landing'),
    # sanner admin
    path('dashboard/', TemplateView.as_view(template_name='admin/scanner/index.html'), name='admin_scanner') ,
    path('scanner/search/', TemplateView.as_view(template_name='admin/scanner/search.html'), name='admin_scanner_search') ,
]