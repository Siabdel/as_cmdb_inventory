from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count, Q, Sum, Avg
from django.utils.safestring import mark_safe
from .models import Asset, Location, Category, Brand
from .maintenance_models import MaintenanceTicket, MaintenanceType, MaintenanceAction


class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard), name='dashboard'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_dashboard'] = True
        return super().index(request, extra_context=extra_context)
    
    def app_index(self, request, app_label, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_dashboard'] = True
        return super().app_index(request, app_label, extra_context=extra_context)

    def dashboard(self, request):
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        
        # Statistiques des assets
        assets = Asset.objects.aggregate(
            total=Count('id'),
            in_use=Count('id', filter=Q(status='use')),
            in_maintenance=Count('id', filter=Q(status='maintenance')),
            total_value=Sum('purchase_value'),
            avg_value=Avg('purchase_value')
        )
        
        # Statistiques des tickets
        maintenance = MaintenanceTicket.objects.aggregate(
            total=Count('id'),
            in_progress=Count('id', filter=Q(status='EN_COURS')),
            this_month=Count('id', filter=Q(created_at__month=timezone.now().month))
        )
        
        # Rendu du template
        return render(request, 'admin/dashboard.html', {
            'asset_count': assets['total'],
            'assets_in_use': assets['in_use'],
            'assets_in_maintenance': assets['in_maintenance'],
            'total_value': assets['total_value'] or 0,
            'avg_value': assets['avg_value'] or 0,
            'maintenance_count': maintenance['total'],
            'maintenance_in_progress': maintenance['in_progress'],
            'maintenance_this_month': maintenance['this_month']
        })


class StatusFilter(admin.SimpleListFilter):
    title = 'Statut'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Asset.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class ConditionFilter(admin.SimpleListFilter):
    title = 'Condition'
    parameter_name = 'condition'

    def lookups(self, request, model_admin):
        return Asset.CONDITION_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(condition=self.value())
        return queryset


class AssetAdmin(admin.ModelAdmin):
    list_display = ('internal_code', 'name', 'brand', 'category', 'status', 'condition_state', 'current_location', 'age', 'get_stats')
    list_filter = (StatusFilter, ConditionFilter, 'category', 'brand', 'current_location')
    search_fields = ('internal_code', 'name', 'serial_number', 'description', 'tags__name')
    raw_id_fields = ('assigned_to',)
    date_hierarchy = 'purchase_date'
    list_per_page = 50
    actions = ['mark_as_in_use', 'mark_as_in_stock']
    change_form_template = 'admin/inventory/asset/change_form.html'

    def get_stats(self, obj):
        stats = {
            'maintenance_count': MaintenanceTicket.objects.filter(asset=obj).count(),
            'last_maintenance': MaintenanceTicket.objects.filter(asset=obj).order_by('-created_at').first(),
        }
        return mark_safe(f"<div class='stats'>Maintenances: {stats['maintenance_count']}</div>")
    get_stats.short_description = 'Statistiques'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        asset = self.get_object(request, object_id)
        
        # Calcul des statistiques
        maintenance_tickets = MaintenanceTicket.objects.filter(asset=asset)
        extra_context['maintenance_count'] = maintenance_tickets.count()
        extra_context['last_maintenance'] = maintenance_tickets.order_by('-created_at').first()
        
        # Calcul de la durée moyenne
        closed_tickets = maintenance_tickets.filter(closed_at__isnull=False)
        if closed_tickets.exists():
            avg_days = sum(
                (ticket.closed_at - ticket.created_at).days
                for ticket in closed_tickets
            ) / closed_tickets.count()
            extra_context['avg_duration'] = round(avg_days, 1)
        
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def age(self, obj):
        if obj.purchase_date:
            from datetime import date
            return (date.today() - obj.purchase_date).days // 365
        return None
    age.short_description = 'Âge (ans)'

    @admin.action(description='Marquer comme en utilisation')
    def mark_as_in_use(self, request, queryset):
        updated = queryset.update(status='use')
        self.message_user(request, f'{updated} assets marqués comme en utilisation.')

    @admin.action(description='Marquer comme en stock')
    def mark_as_in_stock(self, request, queryset):
        updated = queryset.update(status='stock')
        self.message_user(request, f'{updated} assets marqués comme en stock.')


class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset', 'status', 'priority', 'created_at', 'closed_at', 'duration', 'assigned_to')
    list_filter = ('status', 'priority', 'maintenance_type', 'assigned_to')
    search_fields = ('asset__internal_code', 'asset__name', 'description', 'technician__username')
    date_hierarchy = 'created_at'
    list_select_related = ('asset', 'technician')
    actions = ['close_tickets']
    change_form_template = 'admin/inventory/maintenanceticket/change_form.html'

    def duration(self, obj):
        if obj.closed_at:
            days = (obj.closed_at - obj.created_at).days
            return f"{days} jours"
        return None
    duration.short_description = 'Durée'

    @admin.action(description='Fermer les tickets sélectionnés')
    def close_tickets(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='EN_COURS').update(
            status='TERMINE',
            closed_at=timezone.now()
        )
        self.message_user(request, f'{updated} tickets fermés.')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        ticket = self.get_object(request, object_id)
        
        # Calcul des statistiques
        if ticket.asset:
            maintenance_tickets = MaintenanceTicket.objects.filter(asset=ticket.asset)
            extra_context['maintenance_count'] = maintenance_tickets.count()
            
            # Calcul de la durée moyenne
            closed_tickets = maintenance_tickets.filter(closed_at__isnull=False)
            if closed_tickets.exists():
                avg_days = sum(
                    (ticket.closed_at - ticket.created_at).days
                    for ticket in closed_tickets
                ) / closed_tickets.count()
                extra_context['avg_duration'] = round(avg_days, 1)
            
            # Calcul du coût total
            total_cost = maintenance_tickets.aggregate(total=Sum('cost'))['total']
            extra_context['total_cost'] = total_cost if total_cost else 0
        
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )


admin_site = CustomAdminSite(name='customadmin')
admin.site = admin_site  # Remplace l'instance admin par défaut
admin.site.register(Asset, AssetAdmin)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_preventive', 'estimated_duration_hours')
    list_filter = ('is_preventive',)
    search_fields = ('name', 'description')
    ordering = ('name',)


class MaintenanceActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'action_type', 'performed_at', 'performed_by', 'cost_euros', 'duration_hours')
    list_filter = ('action_type', 'performed_by')
    search_fields = ('ticket__title', 'description', 'parts_used')
    date_hierarchy = 'performed_at'
    list_select_related = ('ticket', 'performed_by')
    raw_id_fields = ('ticket', 'performed_by')


admin.site.register(MaintenanceTicket, MaintenanceTicketAdmin)
admin.site.register(MaintenanceType, MaintenanceTypeAdmin)
admin.site.register(MaintenanceAction, MaintenanceActionAdmin)