from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Création du router DRF
router = DefaultRouter()
router.register(r'assets', views.AssetViewSet, basename='asset')
router.register(r'asset-scans', views.AssetScanViewSet, basename='asset-scan')

# URLs spécifiques
urlpatterns = [
    # Routes DRF via router
    path('', include(router.urls)),
    
    # Scan via code d'asset
    path('scans/', views.ScanAPIView.as_view(), name='scan-create'),
    
    # Récupération d'asset par code
    path('assets/by-code/<str:code>/', views.AssetViewSet.as_view({'get': 'by_code'}), name='asset-by-code'),
    
    # Images QR code et code-barres
    path('assets/<uuid:pk>/qrcode/', views.AssetQRCodeView.as_view(), name='asset-qrcode'),
    path('assets/<uuid:pk>/barcode/', views.AssetBarcodeView.as_view(), name='asset-barcode'),
    
    # Historique des scans (déjà inclus via router avec @action)
]

# URLs API complètes
api_urlpatterns = [
    path('api/', include(urlpatterns)),
]