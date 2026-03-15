# backend/dashboard/views.py
from django.shortcuts import render
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from inventory.models import Asset, Category, Brand, Location
from maintenance.models import MaintenanceTicket as  Ticket
from stock.models import StockItem
import json

def dashboard_public(request):
    """
    Dashboard vitrine publique — Lecture seule
    URL: /
    Audience: Public (pas d'authentification requise)
    """
    
    # === KPIs Principaux ===
    total_assets = Asset.objects.count()
    active_assets = Asset.objects.filter(status='active').count()
    in_stock_assets = Asset.objects.filter(status='stock').count()
    in_maintenance = Asset.objects.filter(status__in=['maintenance', 'repair']).count()
    
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status__in=['open', 'assigned', 'in_progress']).count()
    resolved_tickets_30d = Ticket.objects.filter(
        status='resolved',
        resolved_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    total_stock_items = StockItem.objects.count()
    low_stock_items = StockItem.objects.filter(
        quantity__lte=F('min_quantity')
    ).count()
    out_of_stock_items = StockItem.objects.filter(quantity=0).count()
    
    # === Répartition par Statut (Assets) ===
    assets_by_status = Asset.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # === Répartition par Catégorie ===
    assets_by_category = Asset.objects.values(
        'category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # === Top Marques ===
    top_brands = Asset.objects.values(
        'brand__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # === Assets Récents (10 derniers) ===
    recent_assets = Asset.objects.select_related(
        'category', 'brand', 'location'
    ).order_by('-created_at')[:10]
    
    # === Tickets Récents (10 derniers) ===
    recent_tickets = Ticket.objects.select_related(
        'asset', 'assignee'
    ).order_by('-created_at')[:10]
    
    # === Valeur Totale du Stock ===
    stock_total_value = StockItem.objects.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0
    
    # === Assets par Localisation ===
    assets_by_location = Asset.objects.values(
        'current_location__name'
    ).annotate(
        count=Count('id')
    ).filter(current_location__isnull=False).order_by('-count')[:5]
    
    # === Garanties Expirant Bientôt (30 jours) ===
    warranty_expiring_soon = Asset.objects.filter(
        warranty_end__isnull=False,
        warranty_end__lte=timezone.now() + timedelta(days=30),
        warranty_end__gte=timezone.now()
    ).count()
    
    # === Données pour Graphiques (JSON) ===
    chart_assets_status = json.dumps({
        'labels': [item['status'] for item in assets_by_status],
        'data': [item['count'] for item in assets_by_status]
    })
    
    chart_assets_category = json.dumps({
        'labels': [item['category__name'] or 'Non catégorisé' for item in assets_by_category],
        'data': [item['count'] for item in assets_by_category]
    })
    
    # === Contexte Template ===
    context = {
        # KPIs
        'total_assets': total_assets,
        'active_assets': active_assets,
        'in_stock_assets': in_stock_assets,
        'in_maintenance': in_maintenance,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'resolved_tickets_30d': resolved_tickets_30d,
        'total_stock_items': total_stock_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'stock_total_value': stock_total_value,
        'warranty_expiring_soon': warranty_expiring_soon,
        
        # Répartitions
        'assets_by_status': assets_by_status,
        'assets_by_category': assets_by_category,
        'top_brands': top_brands,
        'assets_by_location': assets_by_location,
        
        # Listes récentes
        'recent_assets': recent_assets,
        'recent_tickets': recent_tickets,
        
        # Graphiques
        'chart_assets_status': chart_assets_status,
        'chart_assets_category': chart_assets_category,
        
        # Meta
        'page_title': 'Dashboard CMDB Inventory',
        'last_updated': timezone.now()
    }
    
    return render(request, 'dashboard.html', context)


def dashboard_stats_api(request):
    """
    API Endpoint pour statistiques dashboard (JSON)
    URL: /api/v1/dashboard/stats/
    Utilisé par le frontend Vue.js pour rafraîchissement dynamique
    """
    from django.http import JsonResponse
    from django.db.models import Count, F, Sum
    from django.utils import timezone
    from datetime import timedelta
    
    stats = {
        'assets': {
            'total': Asset.objects.count(),
            'active': Asset.objects.filter(status='active').count(),
            'stock': Asset.objects.filter(status='stock').count(),
            'maintenance': Asset.objects.filter(status__in=['maintenance', 'repair']).count(),
            'retired': Asset.objects.filter(status='retired').count()
        },
        'tickets': {
            'total': Ticket.objects.count(),
            'open': Ticket.objects.filter(status='open').count(),
            'in_progress': Ticket.objects.filter(status='in_progress').count(),
            'resolved_30d': Ticket.objects.filter(
                status='resolved',
                resolved_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        },
        'stock': {
            'total_items': StockItem.objects.count(),
            'low_stock': StockItem.objects.filter(quantity__lte=F('min_stock')).count(),
            'out_of_stock': StockItem.objects.filter(quantity=0).count(),
            'total_value': float(StockItem.objects.aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )['total'] or 0)
        },
        'alerts': {
            'warranty_expiring': Asset.objects.filter(
                warranty_end__isnull=False,
                warranty_end__lte=timezone.now() + timedelta(days=30)
            ).count(),
            'overdue_tickets': Ticket.objects.filter(
                due_date__lt=timezone.now(),
                status__in=['open', 'assigned', 'in_progress']
            ).count()
        }
    }
    
    return JsonResponse(stats)