"""
Configuration des URLs pour   CMDB Admin
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
# from .views import dashboard_public, dashboard_stats_api, asset_list, admin_login_view, admin_logout_view, admin_dashboard_view
from cmdb_admin import views as cmdb_views

app_name = 'cmdb_admin'

urlpatterns = [
    # On désactive le Django admin pour les modèles métier
    # path('admin/', admin.site.urls),  # ← commenté ou supprimé
    
    # Interface admin custom complète
    path('', cmdb_views.admin_dashboard_view, name='admin_dashboard'),
    path('login/', cmdb_views.admin_login_view, name='admin_login'),
    path('logout/', cmdb_views.admin_logout_view, name='admin_logout'),
    path('search/', TemplateView.as_view(template_name='admin/search/results.html'), name='admin_search'),
    path('assets/', TemplateView.as_view(template_name='admin/search/results.html'), name='admin_search'),
    path('assets/list/',  cmdb_views.asset_list, name='admin_assets_list'),
    path('assets/<int:pk>/', TemplateView.as_view(template_name='admin/assets/detail.html'), name='admin_asset_detail'),
    path('assets/new/', RedirectView.as_view(url='/django-admin/inventory/asset/add/'), name='admin_asset_new'),
    # sanner admin
    path('scanner/', TemplateView.as_view(template_name='admin/scanner/index.html'), name='admin_scanner') ,
    path('scanner/search/', TemplateView.as_view(template_name='admin/scanner/search.html'), name='admin_scanner_search') ,
    
    ## stock admin
    path('stock/', cmdb_views.StockView.as_view(), name='admin_stock'),
    path('stock/list/', TemplateView.as_view(template_name='admin/stock/list.html'), name='admin_stock_list') ,
    path('stock/<int:pk>/', TemplateView.as_view(template_name='admin/stock/detail.html'), name='admin_stock_detail') ,
    path('stock/movement/', TemplateView.as_view(template_name='admin/stock/list.html'), name='admin_stock_movement'),  # TODO: créer template dédié
    ## ticket admin
    path('tickets/', TemplateView.as_view(template_name='admin/tickets/list.html'), name='admin_tickets'),
    path('tickets/login/', TemplateView.as_view(template_name='admin/admin_login.html'), name='admin_login') ,
    path('tickets/dashboard/', TemplateView.as_view(template_name='admin/tickets/list.html'), name='admin_tickets_dashboard') ,
    path('tickets/new/', RedirectView.as_view(url='/django-admin/maintenance/maintenanceticket/add/'), name='admin_ticket_new'),

]

# backend/dashboard/urls.py


urlpatterns += [
    # Dashboard public
    path('', cmdb_views.dashboard_public, name='dashboard_public'),
    
    # API Stats (pour rafraîchissement Vue.js)
    path('api/stats/', cmdb_views.dashboard_stats_api, name='dashboard_stats'),
]