"""
Serializers pour les modèles de maintenance
"""

from rest_framework import serializers
from .maintenance_models import MaintenanceType, MaintenanceTicket, MaintenanceAction
from .serializers import UserSerializer


class MaintenanceTypeSerializer(serializers.ModelSerializer):
    """Serializer pour les types de maintenance"""
    
    class Meta:
        model = MaintenanceType
        fields = '__all__'


class MaintenanceActionSerializer(serializers.ModelSerializer):
    """Serializer pour les actions de maintenance"""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    performed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceAction
        fields = [
            'id', 'ticket', 'action_type', 'action_type_display',
            'description', 'cost_euros', 'duration_hours',
            'performed_by', 'performed_by_name', 'performed_at',
            'before_status', 'after_status', 'parts_used'
        ]
        read_only_fields = ['performed_at']
    
    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return f"{obj.performed_by.first_name} {obj.performed_by.last_name}".strip() or obj.performed_by.username
        return None


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les tickets de maintenance"""
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_internal_code = serializers.CharField(source='asset.internal_code', read_only=True)
    maintenance_type_name = serializers.CharField(source='maintenance_type.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    actions_count = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'asset', 'asset_name', 'asset_internal_code',
            'maintenance_type', 'maintenance_type_name',
            'title', 'description', 'priority', 'priority_display',
            'status', 'status_display',
            'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name',
            'created_at', 'updated_at', 'due_date', 'closed_at',
            'actions_count', 'total_cost', 'duration_hours'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None
    
    def get_actions_count(self, obj):
        return obj.actions.count()
    
    def get_total_cost(self, obj):
        return obj.total_cost
    
    def get_duration_hours(self, obj):
        return obj.duration_hours


class MaintenanceTicketDetailSerializer(MaintenanceTicketSerializer):
    """Serializer détaillé avec les actions"""
    actions = MaintenanceActionSerializer(many=True, read_only=True)
    
    class Meta(MaintenanceTicketSerializer.Meta):
        fields = MaintenanceTicketSerializer.Meta.fields + ['actions']
