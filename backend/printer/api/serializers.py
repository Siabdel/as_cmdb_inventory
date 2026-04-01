from rest_framework import serializers
from django.conf import settings
from rest_framework import serializers
from django.conf import settings
from inventory.models import Asset

from printer.models import PrintTemplate, Printer, PrintJob, PrintLog


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
# Serializer pour la demande d'impression de labels
class PrintLabelSerializer(serializers.Serializer):
    """
    Serializer pour la demande d'impression
    
    Auto-génère qr_content et barcode_content si non fournis
    """
    
    asset_id = serializers.CharField(
        max_length=100,
        required=True,
        help_text="ID de l'asset (clé primaire)"
    )
    
    qr_content = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Texte pour QR Code (auto-généré si vide)"
    )
    
    barcode_content = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Texte pour code-barres (auto-généré si vide)"
    )
    
    custom_text = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Texte additionnel (localisation, etc.)"
    )
    
    copies = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        default=1,
        help_text="Nombre de copies (1-5)"
    )
    
    def validate_asset_id(self, value):
        """Vérifier que l'asset existe"""
        if not Asset.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Asset '{value}' introuvable dans la CMDB"
            )
        return value
    
    def validate_qr_content(self, value):
        """
        Auto-générer l'URL QR si non fournie
        Ex: http://cmdb.local/assets/210
        """
        if not value:  # Si vide, None, ou ""
            asset_id = self.initial_data.get('asset_id')
            if asset_id:
                base_url = getattr(settings, 'CMDB_BASE_URL', 'http://localhost:8000')
                value = f"{base_url}/assets/{asset_id}"
        return value
    
    def validate_barcode_content(self, value):
        """Auto-générer le code-barres si vide"""
        if not value:
            asset_id = self.initial_data.get('asset_id')
            if asset_id:
                value = f"ASSET{str(asset_id).replace('-', '').upper()}"
        return value