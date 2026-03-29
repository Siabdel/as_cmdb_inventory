from django.contrib import admin
from scanner.models import QRCode, ScanLog
from .models import ScannedAsset, ScanResult, PrintTemplate, Printer, PrintJob



admin.site.register(QRCode)
admin.site.register(ScanLog)
admin.site.register(ScannedAsset)
admin.site.register(ScanResult)
admin.site.register(PrintTemplate)
admin.site.register(Printer)
admin.site.register(PrintJob)
