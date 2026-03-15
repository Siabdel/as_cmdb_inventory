from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.CategoryViewSet.as_view({'get': 'list'})),
    path('location/', views.LocationViewSet.as_view({'get': 'list'})),
    path('brand/', views.BrandViewSet.as_view({'get': 'list'})),
    path('dashboard/', views.DashboardViewSet.as_view({'get': 'list'})),
    path('dashboard/stats/', views.DashboardStatsView.as_view({'get': 'list'}), name='dashboard-stats'),
    path('assets/<int:pk>/movements/', views.AssetMovementsView.as_view({'get': 'list'}), name='asset-movements'),

    path('assets/', views.AssetViewSet.as_view({'get': 'list'}), name='asset-list'),


    path('assets/by-category/', views.AssetViewSet.as_view({'get': 'list'}), name='asset-by-category'),
    path('assets/by-status/', views.AssetViewSet.as_view({'get': 'list'}), name='asset-by-status'),
    path('assets/by-location/', views.AssetViewSet.as_view({'get': 'list'}), name='asset-by-location'),
    path('assets/<int:pk>/move/', views.AssetViewSet.as_view({'post': 'move'}), name='asset-move'),

    path('movements/', views.AssetMovementViewSet.as_view({'get': 'list'}), name='asset-movements'),
    path('assets/warranty-expiring/', views.AssetViewSet.as_view({'get': 'list'}), name='warranty-expiring'),
]
