"""
Serializers Django REST Framework pour l'application CMDB Inventory
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Location, Category, Brand, Tag, Asset, AssetMovement


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class LocationSerializer(serializers.ModelSerializer):
    """Serializer pour les emplacements"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.SerializerMethodField()
    assets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'type', 'parent', 'parent_name', 'description',
            'full_path', 'children_count', 'assets_count',
            'created_at', 'updated_at'
        ]
    
    def get_children_count(self, obj):
        """Retourne le nombre d'emplacements enfants"""
        return obj.children.count()
    
    def get_assets_count(self, obj):
        """Retourne le nombre d'assets dans cet emplacement"""
        return obj.assets.count()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    assets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'parent_name', 'description',
            'icon', 'children_count', 'assets_count',
            'created_at', 'updated_at'
        ]
    
    def get_children_count(self, obj):
        """Retourne le nombre de catégories enfants"""
        return obj.children.count()
    
    def get_assets_count(self, obj):
        """Retourne le nombre d'assets dans cette catégorie"""
        return obj.assets.count()


class BrandSerializer(serializers.ModelSerializer):
    """Serializer pour les marques"""
    
    assets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'website', 'logo', 'assets_count',
            'created_at', 'updated_at'
        ]
    
    def get_assets_count(self, obj):
        """Retourne le nombre d'assets de cette marque"""
        return obj.assets.count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer pour les étiquettes"""
    
    assets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'color', 'description', 'assets_count', 'created_at'
        ]
    
    def get_assets_count(self, obj):
        """Retourne le nombre d'assets avec cette étiquette"""
        return obj.assets.count()


class AssetListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des assets (version allégée)"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    location_name = serializers.CharField(source='current_location.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    warranty_status = serializers.CharField(read_only=True)
    tags_list = TagSerializer(source='tags', many=True, read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'internal_code', 'name', 'category', 'category_name',
            'brand', 'brand_name', 'model', 'serial_number', 'status',
            'current_location', 'location_name', 'assigned_to', 'assigned_to_name',
            'warranty_status', 'tags_list', 'created_at', 'updated_at'
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les assets"""
    
    category_detail = CategorySerializer(source='category', read_only=True)
    brand_detail = BrandSerializer(source='brand', read_only=True)
    location_detail = LocationSerializer(source='current_location', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    warranty_status = serializers.CharField(read_only=True)
    is_warranty_expired = serializers.BooleanField(read_only=True)
    movements_count = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'internal_code', 'name', 'category', 'category_detail',
            'brand', 'brand_detail', 'model', 'serial_number', 'description',
            'purchase_date', 'purchase_price', 'warranty_end', 'warranty_status',
            'is_warranty_expired', 'status', 'current_location', 'location_detail',
            'assigned_to', 'assigned_to_detail', 'tags', 'tags_detail',
            'qr_code_image', 'qr_code_url', 'notes', 'movements_count',
            'created_at', 'updated_at'
        ]
    
    def get_movements_count(self, obj):
        """Retourne le nombre de mouvements de cet asset"""
        return obj.movements.count()
    
    def get_qr_code_url(self, obj):
        """Retourne l'URL complète du QR code"""
        if obj.qr_code_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code_image.url)
            return obj.qr_code_image.url
        return None


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/modification d'assets"""
    
    class Meta:
        model = Asset
        fields = [
            'internal_code', 'name', 'category', 'brand', 'model',
            'serial_number', 'description', 'purchase_date', 'purchase_price',
            'warranty_end', 'status', 'current_location', 'assigned_to',
            'tags', 'notes'
        ]
    
    def validate_internal_code(self, value):
        """Valide l'unicité du code interne"""
        instance = getattr(self, 'instance', None)
        if Asset.objects.filter(internal_code=value).exclude(
            id=instance.id if instance else None
        ).exists():
            raise serializers.ValidationError(
                "Un équipement avec ce code interne existe déjà."
            )
        return value
    
    def validate_serial_number(self, value):
        """Valide l'unicité du numéro de série s'il est fourni"""
        if not value:
            return value
        
        instance = getattr(self, 'instance', None)
        if Asset.objects.filter(serial_number=value).exclude(
            id=instance.id if instance else None
        ).exists():
            raise serializers.ValidationError(
                "Un équipement avec ce numéro de série existe déjà."
            )
        return value


class AssetMovementSerializer(serializers.ModelSerializer):
    """Serializer pour les mouvements d'assets"""
    
    asset_code = serializers.CharField(source='asset.internal_code', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    from_location_name = serializers.CharField(source='from_location.name', read_only=True)
    to_location_name = serializers.CharField(source='to_location.name', read_only=True)
    moved_by_name = serializers.CharField(source='moved_by.get_full_name', read_only=True)
    
    class Meta:
        model = AssetMovement
        fields = [
            'id', 'asset', 'asset_code', 'asset_name',
            'from_location', 'from_location_name',
            'to_location', 'to_location_name',
            'moved_by', 'moved_by_name', 'move_type', 'note', 'created_at'
        ]
        read_only_fields = ['moved_by']
    
    def create(self, validated_data):
        """Crée un nouveau mouvement"""
        # Ajouter l'utilisateur actuel
        validated_data['moved_by'] = self.context['request'].user
        
        # Définir l'emplacement source comme l'emplacement actuel de l'asset
        asset = validated_data['asset']
        validated_data['from_location'] = asset.current_location
        
        return super().create(validated_data)


class AssetMoveFromScanSerializer(serializers.Serializer):
    """Serializer pour déplacer un asset via scan QR"""
    
    asset_id = serializers.UUIDField()
    target_location_id = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True)
    
    def validate_asset_id(self, value):
        """Valide que l'asset existe"""
        try:
            asset = Asset.objects.get(id=value)
            return asset
        except Asset.DoesNotExist:
            raise serializers.ValidationError("Équipement non trouvé.")
    
    def validate_target_location_id(self, value):
        """Valide que l'emplacement cible existe"""
        try:
            location = Location.objects.get(id=value)
            return location
        except Location.DoesNotExist:
            raise serializers.ValidationError("Emplacement non trouvé.")
    
    def create(self, validated_data):
        """Crée le mouvement et met à jour l'asset"""
        asset = validated_data['asset_id']
        target_location = validated_data['target_location_id']
        note = validated_data.get('note', '')
        user = self.context['request'].user
        
        # Créer le mouvement
        movement = AssetMovement.objects.create(
            asset=asset,
            from_location=asset.current_location,
            to_location=target_location,
            moved_by=user,
            move_type='move',
            note=note
        )
        
        return movement


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé du dashboard"""
    
    total_assets = serializers.IntegerField()
    assets_by_status = serializers.DictField()
    assets_by_location = serializers.DictField()
    assets_by_category = serializers.DictField()
    recent_movements = AssetMovementSerializer(many=True)
    assets_needing_maintenance = AssetListSerializer(many=True)
    warranty_expiring_soon = AssetListSerializer(many=True)
    
    
    class AssetSerializer(serializers.ModelSerializer):
        class Meta(AssetDetailSerializer.Meta):
            pass

class AssetSerializer(serializers.ModelSerializer):
    """Serializer complet pour les assets, utilisé pour les détails et les listes"""
    
    category_detail = CategorySerializer(source='category', read_only=True)
    brand_detail = BrandSerializer(source='brand', read_only=True)
    location_detail = LocationSerializer(source='current_location', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    warranty_status = serializers.CharField(read_only=True)
    is_warranty_expired = serializers.BooleanField(read_only=True)
    movements_count = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'internal_code', 'name', 'category', 'category_detail',
            'brand', 'brand_detail', 'model', 'serial_number', 'description',
            'purchase_date', 'purchase_price', 'warranty_end', 'warranty_status',
            'is_warranty_expired', 'status', 'current_location', 'location_detail',
            'assigned_to', 'assigned_to_detail', 'tags', 'tags_detail',
            'qr_code_image', 'qr_code_url', 'notes', 'movements_count',
            'created_at', 'updated_at'
        ]
    
    def get_movements_count(self, obj):
        """Retourne le nombre de mouvements de cet asset"""
        return obj.movements.count()
    
    def get_qr_code_url(self, obj):
        """Retourne l'URL complète du QR code"""
        if obj.qr_code_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code_image.url)
            return obj.qr_code_image.url
        return None