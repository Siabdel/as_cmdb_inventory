from django.urls import path, include
from scanner import views
from scanner.api import views as api_views
from scanner.views import public_scan_result
from django.views.generic import TemplateView
from scanner.views import print_labels

# backend/scanner/urls.py
urlpatterns = [
    path('scan/<uuid:uuid_token>/',       views.resolve_qr,    name='resolve-qr'),
    path('assets/<int:asset_id>/regen-qr/', views.regenerate_qr, name='regenerate-qr'),
    ##
    path('scan/<str:uuid>/', public_scan_result, name='public_scan'),  # Sans auth  

    # Landing Page Scan & Print
    path('scan-print/', views.scan_print_landing, name='scan-print-landing'),

    # Page publique scan
    path('scan/<str:uuid>/', public_scan_result, name='public_scan'),  # Sans auth
    
    # Print Management
    path('print/', views.print_labels_view, name='print-labels'),
    path('templates/', api_views.PrintTemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='print-templates'),
    path('templates/<int:pk>/', api_views.PrintTemplateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='print-template-detail'),
    path('printers/', views.PrinterViewSet.as_view({'get': 'list', 'post': 'create'}), name='printers'),
    path('printers/<int:pk>/', views.PrinterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='printer-detail'),
    path('jobs/', api_views.PrintJobViewSet.as_view({'get': 'list', 'post': 'create'}), name='print-jobs'),
    path('jobs/<int:pk>/', api_views.PrintJobViewSet.as_view({'get': 'retrieve'}), name='print-job-detail'),
    path('print-labels/', print_labels, name='print-labels'),
]


urlpatterns += [
    # sanner admin
    path('scanner/dashboard', TemplateView.as_view(template_name='admin/scanner/index.html'), name='admin_scanner') ,
    path('scanner/search/', TemplateView.as_view(template_name='admin/scanner/search.html'), name='admin_scanner_search') ,
]