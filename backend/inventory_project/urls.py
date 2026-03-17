"""
Configuration des URLs pour le projet CMDB Inventory
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from inventory.views import DashboardView, CurrentUserView, generate_qrcode_view, print_label_view
from scanner.views import public_scan_result
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),  # ← accueil
    # URLs personnalisées pour l'admin (QR code et impression) - doivent être avant admin.site.urls
    path('django-admin/inventory/asset/<int:asset_id>/generate_qrcode/',
         generate_qrcode_view,
         name='admin_generate_qrcode'),
    path('django-admin/inventory/asset/<int:asset_id>/print_label/',
         print_label_view,
         name='admin_print_label'),
    # Interface d'administration Django
    path('django-admin/', admin.site.urls),
     # Administration CMDB (interface custom)
    path('admin/', include('cmdb_admin.urls')),
    
    # API REST
    ## API endpoints
    path('api/v1/assets/', include('inventory.urls')),  # URLs admin custom
    path('api/v1/inventory/',  include('inventory.urls')),# URLs de l'app inventory (CRUD assets, catégories, etc.)
    path('api/v1/maintenance/', include('maintenance.urls')),
    path('api/v1/scanner/', include('scanner.urls')), # URLs spécifiques au scanner QR code
    path('api/v1/maintenance/', include('maintenance.urls')), # URLs spécifiques à la maintenance
    # config/urls.py
    path('api/v1/stock/', include('stock.urls')),
    # Authentification DRF
    path('api-auth/', include('rest_framework.urls')),
    # Authentification par token (pour le frontend)
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/user/', CurrentUserView.as_view(), name='api_current_user'),
]

# URLs en mode DEBUG uniquement
if settings.DEBUG:
    # Servir les fichiers media et static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # DRF Spectacular - Documentation API OpenAPI 3
    urlpatterns += [
        # Schema OpenAPI 3
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        # Swagger UI
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        # Redoc
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('scan/<str:uuid>/', public_scan_result, name='public_scan'),  # Sans auth
    ]
 


    # config/urls.py


# Configuration de l'admin
admin.site.site_header = "CMDB Inventory - Administration"
admin.site.site_title = "CMDB Admin"
admin.site.index_title = "Gestion de l'inventaire matériel"