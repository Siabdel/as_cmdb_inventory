from django.contrib import admin
from scanner.models import QRCode, ScanLog
from .models import ScannedAsset, ScanResult



admin.site.register(QRCode)
admin.site.register(ScanLog)
admin.site.register(ScannedAsset)
admin.site.register(ScanResult)