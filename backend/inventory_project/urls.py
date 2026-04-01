"""
Configuration des URLs pour le projet CMDB Inventory
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from inventory import views as inventory_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    # Authentification DRF
    path('api-auth/', include('rest_framework.urls')),
    # Administration CMDB (interface custom)
    path('admin/', include('cmdb_admin.urls')),
    # api scanner 
    path('scanner/', include('scanner.urls')),
    # printer urls
    path('printer/', include('printer.urls')),
]

urlpatterns += [
    # Accueil - Dashboard public
    path('', inventory_views.DashboardView.as_view(), name='dashboard'),  # ← accueil
    # API REST
    path('api/v1/staff/', include('staff.urls')),
    path('api/stats/', include('cmdb_admin.urls')),
    # Printer API
    path('api/printer/', include('printer.urls')),
    # Interface d'administration Django
    ## API endpoints
    path('api/v1/inventory/',  include('inventory.urls')),# URLs de l'app inventory (CRUD assets, catégories, etc.)
    path('api/v1/maintenance/', include('maintenance.urls')),
    path('api/v1/scanner/', include('scanner.urls')), # URLs spécifiques au scanner QR code
    # config/urls.py
    path('api/v1/stock/', include('stock.urls')),
    path('api/v1/inventory/dashboard/stats/', include('inventory.urls')),
    # Authentification par token (pour le frontend)
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/user/', inventory_views.CurrentUserView.as_view(), name='api_current_user'),
    # Authentification JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# backend/config/urls.py (extrait)

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
    ]
 


    # config/urls.py


# Configuration de l'admin
admin.site.site_header = "CMDB Inventory - Administration"
admin.site.site_title = "CMDB Admin"
admin.site.index_title = "Gestion de l'inventaire matériel"