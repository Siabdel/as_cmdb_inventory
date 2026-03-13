"""
Configuration des URLs pour le projet CMDB Inventory
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # API REST
    path('api/v1/inventory/',  include('inventory.urls')),# URLs de l'app inventory (CRUD assets, catégories, etc.)
    path('api/v1/maintenance/', include('maintenance.urls')),
    path('api/v1/scanner/', include('scanner.urls')), # URLs spécifiques au scanner QR code
    path('api/v1/maintenance/', include('maintenance.urls')), # URLs spécifiques à la maintenance
    # config/urls.py
    path('api/v1/stock/', include('stock.urls')),


    
    # Authentification DRF
    path('api-auth/', include('rest_framework.urls')),
]

# URLs en mode DEBUG uniquement
if settings.DEBUG:
    # Servir les fichiers media et static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # DRF Spectacular - Documentation API OpenAPI 3
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
    urlpatterns += [
        # Schema OpenAPI 3
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        # Swagger UI
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        # Redoc
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

    # config/urls.py


# Configuration de l'admin
admin.site.site_header = "CMDB Inventory - Administration"
admin.site.site_title = "CMDB Admin"
admin.site.index_title = "Gestion de l'inventaire matériel"