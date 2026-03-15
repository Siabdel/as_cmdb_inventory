"""
Configuration des URLs pour l'API CMDB Inventory
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    LocationViewSet, CategoryViewSet, BrandViewSet, TagViewSet,
    AssetViewSet, AssetMovementViewSet, DashboardViewSet
)
from .maintenance_views import (
    MaintenanceTypeViewSet, MaintenanceTicketViewSet, MaintenanceActionViewSet
)

# Configuration du routeur DRF
router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'tags', TagViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'movements', AssetMovementViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# Routes de maintenance
router.register(r'maintenance-types', MaintenanceTypeViewSet)
router.register(r'maintenance-tickets', MaintenanceTicketViewSet)
router.register(r'maintenance-actions', MaintenanceActionViewSet)

urlpatterns = [
    # Routes API REST
    path('', include(router.urls)),
    
    # Authentification par token
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
]