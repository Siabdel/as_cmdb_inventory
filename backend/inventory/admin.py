"""
Configuration de l'interface d'administration Django pour CMDB Inventory
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Location, Category, Brand, Tag, Asset, AssetMovement
from .maintenance_models import MaintenanceType, MaintenanceTicket, MaintenanceAction


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Administration des emplacements"""
    
    list_display = ['name', 'type', 'parent', 'assets_count', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_per_page = 25
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'type', 'parent')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def assets_count(self, obj):
        """Affiche le nombre d'assets dans cet emplacement"""
        count = obj.assets.count()
        if count > 0:
            url = reverse('admin:inventory_asset_changelist') + f'?current_location__id__exact={obj.id}'
            return format_html('<a href="{}">{} équipements</a>', url, count)
        return '0 équipement'
    assets_count.short_description = 'Équipements'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration des catégories"""
    
    list_display = ['name', 'parent', 'assets_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'parent', 'icon')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def assets_count(self, obj):
        """Affiche le nombre d'assets dans cette catégorie"""
        count = obj.assets.count()
        if count > 0:
            url = reverse('admin:inventory_asset_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} équipements</a>', url, count)
        return '0 équipement'
    assets_count.short_description = 'Équipements'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Administration des marques"""
    
    list_display = ['name', 'website', 'logo_preview', 'assets_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'website']
    ordering = ['name']
    list_per_page = 25
    
    def logo_preview(self, obj):
        """Affiche un aperçu du logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 30px; max-width: 50px;" />',
                obj.logo.url
            )
        return 'Pas de logo'
    logo_preview.short_description = 'Logo'
    
    def assets_count(self, obj):
        """Affiche le nombre d'assets de cette marque"""
        count = obj.assets.count()
        if count > 0:
            url = reverse('admin:inventory_asset_changelist') + f'?brand__id__exact={obj.id}'
            return format_html('<a href="{}">{} équipements</a>', url, count)
        return '0 équipement'
    assets_count.short_description = 'Équipements'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Administration des étiquettes"""
    
    list_display = ['name', 'color_preview', 'assets_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_per_page = 25
    
    def color_preview(self, obj):
        """Affiche un aperçu de la couleur"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div> {}',
            obj.color, obj.color
        )
    color_preview.short_description = 'Couleur'
    
    def assets_count(self, obj):
        """Affiche le nombre d'assets avec cette étiquette"""
        count = obj.assets.count()
        if count > 0:
            url = reverse('admin:inventory_asset_changelist') + f'?tags__id__exact={obj.id}'
            return format_html('<a href="{}">{} équipements</a>', url, count)
        return '0 équipement'
    assets_count.short_description = 'Équipements'


class AssetMovementInline(admin.TabularInline):
    """Inline pour afficher les mouvements dans l'admin des assets"""
    
    model = AssetMovement
    extra = 0
    readonly_fields = ['created_at']
    fields = ['from_location', 'to_location', 'move_type', 'moved_by', 'note', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Administration des équipements"""
    
    list_display = [
        'internal_code', 'name', 'category', 'brand', 'status',
        'current_location', 'assigned_to', 'warranty_status_display',
        'qr_code_preview', 'created_at'
    ]
    list_filter = [
        'status', 'category', 'brand', 'current_location',
        'created_at', 'purchase_date', 'warranty_end'
    ]
    search_fields = [
        'internal_code', 'name', 'model', 'serial_number',
        'description', 'category__name', 'brand__name'
    ]
    ordering = ['-created_at']
    list_per_page = 25
    readonly_fields = ['id', 'qr_code_preview', 'warranty_status', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    inlines = [AssetMovementInline]
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'internal_code', 'name', 'category', 'brand')
        }),
        ('Détails techniques', {
            'fields': ('model', 'serial_number', 'description'),
            'classes': ('collapse',)
        }),
        ('Informations financières', {
            'fields': ('purchase_date', 'purchase_price', 'warranty_end', 'warranty_status'),
            'classes': ('collapse',)
        }),
        ('Statut et localisation', {
            'fields': ('status', 'current_location', 'assigned_to')
        }),
        ('Métadonnées', {
            'fields': ('tags', 'notes'),
            'classes': ('collapse',)
        }),
        ('QR Code', {
            'fields': ('qr_code_image', 'qr_code_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def qr_code_preview(self, obj):
        """Affiche un aperçu du QR code"""
        if obj.qr_code_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.qr_code_image.url
            )
        return 'QR code non généré'
    qr_code_preview.short_description = 'Aperçu QR Code'
    
    def warranty_status_display(self, obj):
        """Affiche le statut de la garantie avec couleur"""
        status = obj.warranty_status
        if status == 'Expirée':
            color = 'red'
        elif status == 'Expire bientôt':
            color = 'orange'
        elif status == 'Valide':
            color = 'green'
        else:
            color = 'gray'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    warranty_status_display.short_description = 'Garantie'
    
    actions = ['generate_qr_codes', 'mark_as_broken', 'mark_as_stock']
    
    def generate_qr_codes(self, request, queryset):
        """Action pour générer les QR codes des assets sélectionnés"""
        count = 0
        for asset in queryset:
            if not asset.qr_code_image:
                asset.generate_qr_code()
                count += 1
        
        self.message_user(
            request,
            f'{count} QR codes générés avec succès.'
        )
    generate_qr_codes.short_description = 'Générer les QR codes'
    
    def mark_as_broken(self, request, queryset):
        """Action pour marquer les assets comme en panne"""
        count = queryset.update(status='broken')
        self.message_user(
            request,
            f'{count} équipements marqués comme en panne.'
        )
    mark_as_broken.short_description = 'Marquer comme en panne'
    
    def mark_as_stock(self, request, queryset):
        """Action pour marquer les assets comme en stock"""
        count = queryset.update(status='stock')
        self.message_user(
            request,
            f'{count} équipements marqués comme en stock.'
        )
    mark_as_stock.short_description = 'Marquer comme en stock'


@admin.register(AssetMovement)
class AssetMovementAdmin(admin.ModelAdmin):
    """Administration des mouvements d'équipements"""
    
    list_display = [
        'asset', 'move_type', 'from_location', 'to_location',
        'moved_by', 'created_at'
    ]
    list_filter = ['move_type', 'created_at', 'from_location', 'to_location']
    search_fields = [
        'asset__internal_code', 'asset__name', 'note',
        'moved_by__username', 'moved_by__first_name', 'moved_by__last_name'
    ]
    ordering = ['-created_at']
    list_per_page = 25
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Mouvement', {
            'fields': ('asset', 'move_type', 'from_location', 'to_location')
        }),
        ('Détails', {
            'fields': ('moved_by', 'note', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        """Empêche l'ajout direct de mouvements via l'admin"""
        return False


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    """Administration des types de maintenance"""
    
    list_display = ['name', 'is_preventive', 'estimated_duration_hours', 'created_at']
    list_filter = ['is_preventive', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'is_preventive', 'estimated_duration_hours')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )


class MaintenanceActionInline(admin.TabularInline):
    """Actions de maintenance en ligne dans le ticket"""
    model = MaintenanceAction
    extra = 0
    fields = ['action_type', 'description', 'cost_euros', 'duration_hours', 'performed_by', 'performed_at']
    readonly_fields = ['performed_at']


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    """Administration des tickets de maintenance"""
    
    list_display = ['id', 'asset', 'title', 'priority', 'status', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'maintenance_type']
    search_fields = ['title', 'description', 'asset__name', 'asset__internal_code']
    ordering = ['-created_at']
    list_select_related = ['asset', 'maintenance_type', 'created_by', 'assigned_to']
    inlines = [MaintenanceActionInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('asset', 'maintenance_type', 'title', 'description')
        }),
        ('Statut et priorité', {
            'fields': ('priority', 'status')
        }),
        ('Attribution', {
            'fields': ('assigned_to',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('due_date',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MaintenanceAction)
class MaintenanceActionAdmin(admin.ModelAdmin):
    """Administration des actions de maintenance"""
    
    list_display = ['ticket', 'action_type', 'cost_euros', 'duration_hours', 'performed_by', 'performed_at']
    list_filter = ['action_type', 'performed_at']
    search_fields = ['description', 'ticket__title', 'parts_used']
    ordering = ['-performed_at']
    list_select_related = ['ticket', 'ticket__asset', 'performed_by']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('ticket', 'action_type', 'description')
        }),
        ('Coûts et durée', {
            'fields': ('cost_euros', 'duration_hours')
        }),
        ('Statuts', {
            'fields': ('before_status', 'after_status')
        }),
        ('Pièces et exécution', {
            'fields': ('parts_used', 'performed_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)


# Configuration globale de l'admin
admin.site.site_header = "CMDB Inventory - Administration"
admin.site.site_title = "CMDB Admin"
admin.site.index_title = "Gestion de l'inventaire matériel"