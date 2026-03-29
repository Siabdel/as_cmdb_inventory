# backend/scanner/api/serializers.py
from rest_framework import serializers
from scanner.models import PrintTemplate, Printer, PrintJob, PrintLog


class PrintTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintTemplate
        fields = '__all__'


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = '__all__'


class PrintJobSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    printer_name = serializers.CharField(source='printer.name', read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PrintJob
        fields = '__all__'
        read_only_fields = ['uuid', 'status', 'pdf_file', 'created_at', 'completed_at']


class PrintLogSerializer(serializers.ModelSerializer):
    printed_by_username = serializers.CharField(source='printed_by.username', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = PrintLog
        fields = '__all__'