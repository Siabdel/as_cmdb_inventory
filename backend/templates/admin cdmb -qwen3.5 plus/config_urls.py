# config/urls.py
from django.urls import path
from scanner.views import public_scan_result

urlpatterns = [
    # ... autres URLs
    path('admin/scanner/', include('scanner.urls_admin')),  # Avec auth
    path('scan/<str:uuid>/', public_scan_result, name='public_scan'),  # Sans auth
]