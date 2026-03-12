from django.contrib import admin
from .models import Category, Brand, Location, Tag, Asset, AssetMovement


class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'model', 'serial_number', 'purchase_date', 'purchase_price', 'warranty_end', 'current_location', 'assigned_to', 'status', 'condition_state')
    list_filter = ('category', 'brand', 'current_location', 'status', 'condition_state')
    search_fields = ('name', 'serial_number', 'model')
    raw_id_fields = ('category', 'brand', 'current_location')

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Location)
admin.site.register(Tag)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetMovement)