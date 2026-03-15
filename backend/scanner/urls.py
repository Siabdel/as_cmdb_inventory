from django.urls import path, include
from . import views
from scanner.views import public_scan_result

urlpatterns = [
    path('scan/<uuid:uuid_token>/',       views.resolve_qr,    name='resolve-qr'),
    path('assets/<int:asset_id>/regen-qr/', views.regenerate_qr, name='regenerate-qr'),
    ##
    path('scan/<str:uuid>/', public_scan_result, name='public_scan'),  # Sans auth  
]