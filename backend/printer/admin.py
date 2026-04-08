from django.contrib import admin
from .models import PrintTemplate, Printer, PrintJob

# Register your models here.
class PrintTemplateAdmin(admin.ModelAdmin):
    list_display = [ field.name for field in PrintTemplate._meta.fields if field.name not in ('id', 'created_at', 'updated_at')]
   

class PrinterAdmin(admin.ModelAdmin):
    #list_display = ('name', 'model', 'connection_type',)
    search_fields = ('name', 'model')

class PrintJobAdmin(admin.ModelAdmin):
    #list_display = ('printer', 'template', 'status',)
    list_filter = ('status', 'created_at')
    search_fields = ('printer__name', 'template__name')


admin.site.register(PrintTemplate, PrintTemplateAdmin)
admin.site.register(Printer, PrinterAdmin)
admin.site.register(PrintJob, PrintJobAdmin)
