"""
Configuration des URLs pour le projet CMDB Inventory
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # API REST
    path('api/', include('inventory.urls')),
    
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

# Configuration de l'admin
admin.site.site_header = "CMDB Inventory - Administration"
admin.site.site_title = "CMDB Admin"
admin.site.index_title = "Gestion de l'inventaire matériel"