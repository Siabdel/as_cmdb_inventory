from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
import json

from inventory.models import Asset, Category, Location, Brand
from maintenance.models import MaintenanceTicket
from stock.models import StockItem
from django.views.generic import ListView


class StockView(ListView):
    """
    Vue pour la gestion du stock dans l'admin
    """
    template_name = 'admin/stock/list.html'
    model = StockItem
    context_object_name = 'stock_items'
    
    def get(self, request):
        from inventory.models import Brand
        stock_items = StockItem.objects.select_related('brand', 'location').all()
        brands = Brand.objects.all()
        
        # Calcul des statistiques de stock
        total_items = stock_items.count()
        low_stock = stock_items.filter(quantity__lte=F('min_quantity')).count()
        out_of_stock = stock_items.filter(quantity=0).count()
        
        return render(request, self.template_name, {
            'stock_items': stock_items,
            'categories': Category.objects.all(),
            'locations': Location.objects.all(),
            'brands': brands,
            'total_items': total_items,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
        })

def dashboard_public(request):
    """
    Vue pour le dashboard public
    """
    return render(request, 'admin/dashboard.html', {
        'asset_count': Asset.objects.count(),
        'maintenance_count': MaintenanceTicket.objects.count()
    })


def dashboard_stats_api(request):
    """
    API Endpoint pour statistiques dashboard (JSON)
    """
    from django.http import JsonResponse
    stats = {
        'assets': {
            'total': Asset.objects.count(),
            'active': Asset.objects.filter(status='active').count()
        },
        'tickets': {
            'total': MaintenanceTicket.objects.count(),
            'open': MaintenanceTicket.objects.filter(status='open').count()
        }
    }
    return JsonResponse(stats)


def asset_list(request):
    """
    Vue personnalisée pour la liste des assets avec compteurs
    """
    assets = Asset.objects.all()
    
    # Récupérer les assets avec les relations nécessaires pour le frontend
    assets_data = []
    for asset in assets:
        assets_data.append({
            'id': asset.id,
            'name': asset.name,
            'internal_code': asset.internal_code,
            'category': asset.category.name if asset.category else None,
            'category_name': asset.category.name if asset.category else '-',
            'brand': asset.brand.name if asset.brand else None,
            'brand_name': asset.brand.name if asset.brand else '-',
            'model': asset.model,
            'serial_number': asset.serial_number,
            'status': asset.status,
            'photo': asset.photo,
            'location': asset.current_location.name if asset.current_location else None,
            'location_name': asset.current_location.name if asset.current_location else '-',
        })
    
    context = {
        'asset_count': assets.count(),
        'active_assets': assets.filter(status='active').count(),
        'maintenance_count': MaintenanceTicket.objects.count(),
        'open_tickets': MaintenanceTicket.objects.filter(status='open').count(),
        'assets': assets_data,
        'categories': [{'id': cat.id, 'name': cat.name} for cat in Category.objects.all()],
        'brands': [{'id': brand.id, 'name': brand.name} for brand in Brand.objects.all()],
        'locations': [{'id': loc.id, 'name': loc.name} for loc in Location.objects.all()],
    }
    
    return render(request, 'admin/assets/list.html', context)


def admin_login_view(request):
    """
    Vue personnalisée pour la page de login admin avec authentification Django
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/admin/')
        else:
            return render(request, 'admin/admin_login.html', {
                'error': 'Identifiants invalides'
            })
    
    return render(request, 'admin/admin_login.html')


def admin_logout_view(request):
    """
    Vue pour la déconnexion admin
    """
    logout(request)
    return redirect('/admin/tickets/login/')


@login_required
def admin_dashboard_view(request):
    """
    Vue protégée pour le dashboard admin
    """
    return render(request, 'admin/dashboard.html')

