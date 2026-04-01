from django.contrib import admin
from .models import PrintTemplate, Printer, PrintJob

# Register your models here.
admin.site.register(PrintTemplate)
admin.site.register(Printer)
admin.site.register(PrintJob)
