from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Brand, Location, Tag, Asset, AssetMovement, UserProfile
from scanner.models import QRCode


class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'model', 'serial_number', 'purchase_date', 'purchase_price', 'warranty_end', 'current_location', 'assigned_to', 'status', 'condition_state', 'qr_code_preview')
    list_filter = ('category', 'brand', 'current_location', 'status', 'condition_state')
    search_fields = ('name', 'serial_number', 'model', 'internal_code')
    raw_id_fields = ('category', 'brand', 'current_location')
    readonly_fields = ('internal_code', 'created_at', 'updated_at', 'qr_code_preview')
    fieldsets = (
        ('Identification', {
            'fields': ('name', 'internal_code', 'category', 'brand', 'model', 'serial_number', 'description')
        }),
        ('Acquisition', {
            'fields': ('purchase_date', 'purchase_price', 'warranty_end')
        }),
        ('Localisation & Affectation', {
            'fields': ('current_location', 'assigned_to')
        }),
        ('État', {
            'fields': ('status', 'condition_state', 'tags', 'photo')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
        ('QR Code & Impression', {
            'fields': ('qr_code_preview',),
            'classes': ('collapse',)
        }),
    )
    change_form_template = 'admin/inventory/asset/change_form.html'
    
    def qr_code_preview(self, obj):
        if not obj.id:
            return "—"
        try:
            qr = QRCode.objects.get(asset=obj)
            if qr.image:
                return format_html('<img src="{}" width="150" height="150" alt="QR Code" />', qr.image.url)
            else:
                return format_html('<span class="text-muted">QR code non généré</span>')
        except QRCode.DoesNotExist:
            return format_html('<span class="text-warning">QR code non créé</span>')
    qr_code_preview.short_description = 'QR Code'
    
    def print_button(self, obj):
        if not obj.id:
            return "—"
        url = reverse('admin_print_label', args=[obj.id])
        return format_html('<a href="{}" class="button" target="_blank">🖨️ Imprimer l\'étiquette</a>', url)
    print_button.short_description = 'Impression'
    
    class Media:
        css = {
            'all': ('admin/css/asset_admin.css',)
        }
        js = ('admin/js/asset_admin.js',)


# Enregistrer le modèle UserProfile dans l'admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

# Les modèles Category, Brand, Location, Tag, Asset, AssetMovement sont déjà enregistrés dans le fichier original
# On ne les enregistre pas à nouveau
admin.site.register(UserProfile, UserProfileAdmin)


class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'model', 'serial_number', 'purchase_date', 'purchase_price', 'warranty_end', 'current_location', 'assigned_to', 'status', 'condition_state', 'qr_code_preview')
    list_filter = ('category', 'brand', 'current_location', 'status', 'condition_state')
    search_fields = ('name', 'serial_number', 'model', 'internal_code')
    raw_id_fields = ('category', 'brand', 'current_location')
    readonly_fields = ('internal_code', 'created_at', 'updated_at', 'qr_code_preview')
    fieldsets = (
        ('Identification', {
            'fields': ('name', 'internal_code', 'category', 'brand', 'model', 'serial_number', 'description')
        }),
        ('Acquisition', {
            'fields': ('purchase_date', 'purchase_price', 'warranty_end')
        }),
        ('Localisation & Affectation', {
            'fields': ('current_location', 'assigned_to')
        }),
        ('État', {
            'fields': ('status', 'condition_state', 'tags', 'photo')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
        ('QR Code & Impression', {
            'fields': ('qr_code_preview',),
            'classes': ('collapse',)
        }),
    )
    change_form_template = 'admin/inventory/asset/change_form.html'
    
    def qr_code_preview(self, obj):
        if not obj.id:
            return "—"
        try:
            qr = QRCode.objects.get(asset=obj)
            if qr.image:
                return format_html('<img src="{}" width="150" height="150" alt="QR Code" />', qr.image.url)
            else:
                return format_html('<span class="text-muted">QR code non généré</span>')
        except QRCode.DoesNotExist:
            return format_html('<span class="text-warning">QR code non créé</span>')
    qr_code_preview.short_description = 'QR Code'
    
    def print_button(self, obj):
        if not obj.id:
            return "—"
        url = reverse('admin_print_label', args=[obj.id])
        return format_html('<a href="{}" class="button" target="_blank">🖨️ Imprimer l\'étiquette</a>', url)
    print_button.short_description = 'Impression'
    
    class Media:
        css = {
            'all': ('admin/css/asset_admin.css',)
        }
        js = ('admin/js/asset_admin.js',)

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Location)
admin.site.register(Tag)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetMovement)