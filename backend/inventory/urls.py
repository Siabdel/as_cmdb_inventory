"""
Configuration des URLs pour l'API CMDB Inventory
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

# Configuration du routeur DRF

from . import views

router = DefaultRouter()
router.register('categories',  views.CategoryViewSet,      basename='category')
router.register('brands',      views.BrandViewSet,         basename='brand')
router.register('locations',   views.LocationViewSet,      basename='location')
router.register('tags',        views.TagViewSet,           basename='tag')
router.register('assets',      views.AssetViewSet,         basename='asset')
router.register('movements',   views.AssetMovementViewSet, basename='movement')
router.register('dashboard',   views.DashboardViewSet,     basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    # Authentification par token
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
]
