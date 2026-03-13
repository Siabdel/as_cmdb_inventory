"""
Views pour l'API CMDB Inventory
"""
from .models import Category, Brand, Location, Tag, Asset, AssetMovement
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard.html'
