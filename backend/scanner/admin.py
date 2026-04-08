from django.contrib import admin
from scanner.models import ScannableCode, ScanLog
from django.utils.html import format_html


# admin.site.register(ScannableCode)
class ScannableCodeAdmin(admin.ModelAdmin):
    list_display = ('asset', 'code','code_type', 'qr_code_image', 'created_at', 'is_active','uuid_token' )
    readonly_fields = ('qr_code_image',)
    list_filter = ('code_type', 'created_at', 'is_active')
    search_fields = ('code', 'asset__name', 'asset__code')
    
    def qr_code_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" />', obj.image.url)
        return "No Image"
    qr_code_image.short_description = 'QR Code Image'

class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('ScannableCode', 'scanned_by', 'ip_address', 'user_agent', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('scanned_by', 'ip_address', 'user_agent', 'location')

class ScannedAssetAdmin(admin.ModelAdmin):
    list_display = ('asset', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('asset__name', 'asset__code') 


admin.site.register(ScannableCode, ScannableCodeAdmin)
admin.site.register(ScanLog, ScanLogAdmin)