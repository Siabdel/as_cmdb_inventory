from rest_framework import serializers
from .models import Asset, AssetScan


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Asset avec URLs des images QR code et code-barres.
    """
    qr_code_url = serializers.SerializerMethodField()
    barcode_url = serializers.SerializerMethodField()
    scan_count = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'code', 'location',
            'qr_code', 'barcode', 'qr_code_url', 'barcode_url',
            'scan_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['qr_code', 'barcode', 'created_at', 'updated_at']

    def get_qr_code_url(self, obj):
        """
        Retourne l'URL absolue du QR code.
        """
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None

    def get_barcode_url(self, obj):
        """
        Retourne l'URL absolue du code-barres.
        """
        request = self.context.get('request')
        if obj.barcode and request:
            return request.build_absolute_uri(obj.barcode.url)
        return None

    def get_scan_count(self, obj):
        """
        Retourne le nombre de scans pour cet asset.
        """
        return obj.scans.count()


class AssetScanSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle AssetScan.
    """
    asset_code = serializers.CharField(source='asset.code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)

    class Meta:
        model = AssetScan
        fields = [
            'id', 'asset', 'asset_code', 'asset_name',
            'scanned_at', 'scanned_by', 'scan_location',
            'source', 'notes'
        ]
        read_only_fields = ['scanned_at']


class AssetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer spécifique pour la création d'asset.
    Génère automatiquement un code si non fourni.
    """
    class Meta:
        model = Asset
        fields = ['name', 'code', 'location']
        extra_kwargs = {
            'code': {'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        """
        Crée un asset et génère automatiquement les QR codes et code-barres.
        """
        # Si aucun code n'est fourni, générer un code unique
        if not validated_data.get('code'):
            import uuid
            validated_data['code'] = str(uuid.uuid4())[:8].upper()
        
        asset = Asset.objects.create(**validated_data)
        # Les QR codes et barcodes sont générés automatiquement via le save() du modèle
        return asset


class ScanCreateSerializer(serializers.Serializer):
    """
    Serializer pour l'enregistrement d'un scan via API.
    """
    asset_code = serializers.CharField(max_length=255, required=True)
    scanned_by = serializers.CharField(max_length=255, required=True)
    scan_location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    source = serializers.ChoiceField(
        choices=AssetScan.SCAN_SOURCES,
        default='web_frontend',
        required=False
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_asset_code(self, value):
        """
        Vérifie que l'asset existe.
        """
        try:
            asset = Asset.objects.get(code=value)
        except Asset.DoesNotExist:
            raise serializers.ValidationError(f"Asset avec le code '{value}' non trouvé.")
        return value

    def create(self, validated_data):
        """
        Crée un enregistrement de scan.
        """
        asset_code = validated_data.pop('asset_code')
        asset = Asset.objects.get(code=asset_code)
        
        scan = AssetScan.objects.create(
            asset=asset,
            **validated_data
        )
        return scan


class AssetHistorySerializer(serializers.ModelSerializer):
    """
    Serializer pour l'historique des scans d'un asset.
    """
    scans = AssetScanSerializer(many=True, read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'code', 'location',
            'qr_code_url', 'barcode_url',
            'created_at', 'scans'
        ]
