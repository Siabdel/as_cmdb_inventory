from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.CategoryViewSet.as_view({'get': 'list'})),
    path('location/', views.LocationViewSet.as_view({'get': 'list'})),
    path('brand/', views.BrandViewSet.as_view({'get': 'list'})),
    path('dashboard/', views.DashboardViewSet.as_view({'get': 'list'})),
    path('dashboard/stats/', views.DashboardStatsView.as_view({'get': 'list'}), name='dashboard-stats'),
    path('<int:pk>/movements/', views.AssetMovementsView.as_view({'get': 'list'}), name='asset-movements'),

    path('', views.AssetViewSet.as_view({'get': 'list', 'post': 'create'}), name='asset-list'),
    path('<int:pk>/', views.AssetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='asset-detail'),
    path('assets/', views.AssetViewSet.as_view({'get': 'list'}), name='asset-list-assets'),
    path('assets/by-status/', views.AssetViewSet.as_view({'get': 'by_status'}), name='asset-by-status-assets'),

    path('assets/by-category/', views.AssetViewSet.as_view({'get': 'by_category'}), name='asset-by-category-assets'),
    path('assets/warranty-expiring/', views.AssetViewSet.as_view({'get': 'warranty_expiring'}), name='warranty-expiring-assets'),

    path('by-category/', views.AssetViewSet.as_view({'get': 'by_category'}), name='asset-by-category'),
    path('by-status/', views.AssetViewSet.as_view({'get': 'by_status'}), name='asset-by-status'),
    path('by-location/', views.AssetViewSet.as_view({'get': 'by_location'}), name='asset-by-location'),
    path('<int:pk>/move/', views.AssetViewSet.as_view({'post': 'move'}), name='asset-move'),

    path('movements/', views.AssetMovementViewSet.as_view({'get': 'list'}), name='asset-movements'),
    path('warranty-expiring/', views.AssetViewSet.as_view({'get': 'warranty_expiring'}), name='warranty-expiring'),
]
