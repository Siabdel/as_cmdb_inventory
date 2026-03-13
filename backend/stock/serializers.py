
from rest_framework import serializers
from .models import StockItem, StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model  = StockMovement
        fields = ['id', 'item', 'item_name', 'movement_type', 'quantity',
                  'reason', 'done_by', 'ticket', 'reference_doc', 'created_at']
        read_only_fields = ['created_at']


class StockItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    total_value  = serializers.DecimalField(max_digits=10, decimal_places=2,
                                             read_only=True)
    movements    = StockMovementSerializer(many=True, read_only=True)
    brand_name   = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model  = StockItem
        fields = ['id', 'name', 'reference', 'item_type',
                  'brand', 'brand_name', 'description',
                  'quantity', 'min_quantity', 'unit_price',
                  'total_value', 'is_low_stock',
                  'location', 'photo', 'movements',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StockItemListSerializer(serializers.ModelSerializer):
    """Version légère pour listes et dashboard."""
    is_low_stock = serializers.BooleanField(read_only=True)
    total_value  = serializers.DecimalField(max_digits=10, decimal_places=2,
                                             read_only=True)
    brand_name   = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model  = StockItem
        fields = ['id', 'name', 'reference', 'item_type',
                  'brand_name', 'quantity', 'min_quantity',
                  'unit_price', 'total_value', 'is_low_stock',
                  'photo', 'updated_at']
