from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from printer.api import viewsets

# Initialisation du routeur
router = DefaultRouter()

# Enregistrement des ViewSets
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'location', views.LocationViewSet, basename='location')
router.register(r'brand', views.BrandViewSet, basename='brand')
router.register(r'assets', views.AssetViewSet, basename='asset')
router.register(r'movements', views.AssetMovementViewSet, basename='asset-movement')

# URLs spécifiques (non couvertes par le routeur)
urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard
    path('dashboard/', views.DashboardViewSet.as_view({'get': 'list'}), name='dashboard'),
    path('dashboard/stats/', views.DashboardStatsView.as_view({'get': 'list'}), name='dashboard-stats'),
    # asset endpoints
    path('assets/', views.AssetListView.as_view({'get': 'list'}), name='asset-list'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view({'get': 'retrieve'}), name='asset-detail'),
    
    # Actions custom
    path('assets/warranty-expiring/', views.AssetViewSet.as_view({'get': 'warranty_expiring'}), name='warranty-expiring-assets'),
    path('assets/by-category/', views.AssetViewSet.as_view({'get': 'by_category'}), name='asset-by-category-assets'),
    path('assets/by-status/', views.AssetViewSet.as_view({'get': 'by_status'}), name='asset-by-status-assets'),
    
    # Autres endpoints nécessitant une configuration manuelle
    path('<int:pk>/movements/', views.AssetMovementsView.as_view({'get': 'list'}), name='asset-movements'),
    path('asset-movements/<int:pk>/', views.AssetMovementDetailView.as_view({'get': 'retrieve'}), name='asset-movement-detail'),
    path('assets/<int:pk>/movements/', views.AssetMovementsView.as_view({'get': 'list'}), name='asset-movements'),
    
    # Endpoint pour la génération de codes
    path('assets/<int:asset_id>/print/', viewsets.CodePrintView.as_view(), name='asset-print-code'),
    
    # Endpoint pour les utilisateurs avec filtre par rôle (ex: /api/v1/auth/users/?role=technicien)
    # Supprimé - déplacé vers l'application staff
]
