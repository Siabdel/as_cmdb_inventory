from django.contrib import admin
from scanner.models import QRCode, ScanLog
from .models import ScannedAsset, ScanResult 
from django.utils.html import format_html


# admin.site.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('asset', 'code', 'qr_code_image', 'created_at', 'is_active','uuid_token' )
    readonly_fields = ('qr_code_image',)
    
    def qr_code_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" />', obj.image.url)
        return "No Image"
    qr_code_image.short_description = 'QR Code Image'

class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('qrcode', 'scanned_by', 'ip_address', 'user_agent', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('scanned_by', 'ip_address', 'user_agent', 'location')

class ScannedAssetAdmin(admin.ModelAdmin):
    list_display = ('asset', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('asset__name', 'asset__code') 


admin.site.register(QRCode, QRCodeAdmin)
admin.site.register(ScanLog, ScanLogAdmin)
admin.site.register(ScannedAsset, ScannedAssetAdmin)
admin.site.register(ScanResult)