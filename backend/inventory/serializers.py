"""
Serializers Django REST Framework pour l'application CMDB Inventory
"""
from rest_framework import serializers
from .models import Category, Brand, Location, Tag, Asset, AssetMovement


# ── Serializers de référence (lecture légère) ──────────────

class CategoryMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']


class BrandMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo']


class LocationMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'type']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'description']


# ── Category ───────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon',
                  'created_at', 'updated_at', 'asset_count']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        from django.utils.text import slugify
        qs = Category.objects.filter(slug=slugify(value))
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Une catégorie avec ce nom existe déjà.")
        return value

    def create(self, validated_data):
        from django.utils.text import slugify
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


# ── Brand ──────────────────────────────────────────────────

class BrandSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'website', 'logo',
                  'asset_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ── Location ───────────────────────────────────────────────

class LocationSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'type', 'description',
                  'parent', 'parent_name', 'asset_count',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ── AssetMovement ──────────────────────────────────────────

class AssetMovementSerializer(serializers.ModelSerializer):
    from_location_detail = LocationMinSerializer(source='from_location', read_only=True)
    to_location_detail   = LocationMinSerializer(source='to_location', read_only=True)

    class Meta:
        model = AssetMovement
        fields = ['id', 'asset', 'from_location', 'from_location_detail',
                  'to_location', 'to_location_detail',
                  'moved_by', 'moved_at', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ── Asset List (léger pour dashboard/tableaux) ─────────────

class AssetListSerializer(serializers.ModelSerializer):
    category = CategoryMinSerializer(read_only=True)
    brand    = BrandMinSerializer(read_only=True)
    location = LocationMinSerializer(source='current_location', read_only=True)
    tags     = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'internal_code', 'model', 'serial_number',
            'category', 'brand', 'location',
            'status', 'condition_state',
            'assigned_to', 'tags', 'photo',
            'purchase_date', 'warranty_end',
            'created_at', 'updated_at',
        ]


# ── Asset Detail (complet pour fiche individuelle) ─────────

class AssetDetailSerializer(serializers.ModelSerializer):
    category         = CategoryMinSerializer(read_only=True)
    brand            = BrandMinSerializer(read_only=True)
    current_location = LocationMinSerializer(read_only=True)
    tags             = TagSerializer(many=True, read_only=True)
    movements        = AssetMovementSerializer(many=True, read_only=True)

    # Champs write-only pour create/update
    category_id         = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True,
        required=False, allow_null=True)
    brand_id            = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source='brand', write_only=True,
        required=False, allow_null=True)
    current_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='current_location', write_only=True,
        required=False, allow_null=True)
    tag_ids             = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags',
        many=True, write_only=True, required=False)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'internal_code', 'model', 'serial_number', 'description',
            'category', 'category_id',
            'brand', 'brand_id',
            'current_location', 'current_location_id',
            'assigned_to', 'status', 'condition_state',
            'purchase_date', 'purchase_price', 'warranty_end',
            'tags', 'tag_ids', 'photo', 'movements',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Asset validate attrs: {attrs}")
        return attrs

    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Asset create validated_data: {validated_data}")
        tags = validated_data.pop('tags', [])
        asset = super().create(validated_data)
        asset.tags.set(tags)
        return asset

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        asset = super().update(instance, validated_data)
        if tags is not None:
            asset.tags.set(tags)
        return asset


# ── Dashboard Stats (lecture seule) ───────────────────────

class DashboardStatsSerializer(serializers.Serializer):
    total_assets      = serializers.IntegerField()
    active_assets     = serializers.IntegerField()
    inactive_assets   = serializers.IntegerField()
    archived_assets   = serializers.IntegerField()
    assets_new        = serializers.IntegerField()
    assets_used       = serializers.IntegerField()
    assets_damaged    = serializers.IntegerField()
    total_value       = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_warranty      = serializers.IntegerField()  # warranty < 30 jours
    recent_movements = serializers.SerializerMethodField()

    def get_recent_movements(self, obj):
        movements = AssetMovement.objects.order_by('-moved_at')[:5]
        return AssetMovementSerializer(movements, many=True).data