from rest_framework import serializers
from .models import MaintenanceTicket, StatusHistory, TicketPart, TicketComment


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = ['id', 'from_status', 'to_status', 'changed_by',
                  'notes', 'created_at']
        read_only_fields = fields


class TicketPartSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(max_digits=8, decimal_places=2,
                                          read_only=True)
    class Meta:
        model = TicketPart
        fields = ['id', 'part_name', 'part_ref', 'quantity',
                  'unit_cost', 'total_cost']


class TicketCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketComment
        fields = ['id', 'author', 'content', 'is_internal', 'created_at']
        read_only_fields = ['created_at']


# ── Liste légère ───────────────────────────────────────────

class TicketListSerializer(serializers.ModelSerializer):
    asset_name    = serializers.CharField(source='asset.name', read_only=True)
    total_cost    = serializers.DecimalField(max_digits=10, decimal_places=2,
                                             read_only=True)
    is_overdue    = serializers.BooleanField(read_only=True)
    next_statuses = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'ticket_number', 'title', 'ticket_type',
            'priority', 'status', 'asset', 'asset_name',
            'assigned_tech', 'reported_by', 'due_date',
            'is_overdue', 'total_cost', 'next_statuses',
            'created_at', 'updated_at',
        ]

    def get_next_statuses(self, obj):
        """Retourne les transitions possibles depuis le statut actuel."""
        return MaintenanceTicket.ALLOWED_TRANSITIONS.get(obj.status, [])


# ── Détail complet ─────────────────────────────────────────

class TicketDetailSerializer(serializers.ModelSerializer):
    parts          = TicketPartSerializer(many=True, read_only=True)
    comments       = TicketCommentSerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    total_cost     = serializers.DecimalField(max_digits=10, decimal_places=2,
                                              read_only=True)
    is_overdue     = serializers.BooleanField(read_only=True)
    next_statuses  = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'ticket_number', 'title', 'description',
            'ticket_type', 'priority', 'status',
            'asset', 'assigned_tech', 'reported_by',
            'due_date', 'resolved_at', 'closed_at',
            'resolution_notes', 'labor_cost', 'total_cost',
            'is_overdue', 'next_statuses',
            'parts', 'comments', 'status_history',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['ticket_number', 'resolved_at',
                            'closed_at', 'created_at', 'updated_at']

    def get_next_statuses(self, obj):
        return MaintenanceTicket.ALLOWED_TRANSITIONS.get(obj.status, [])


# ── Transition de statut ───────────────────────────────────

class TicketTransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=MaintenanceTicket.STATUS_CHOICES)
    changed_by = serializers.CharField(max_length=100, required=False, default='')
    notes      = serializers.CharField(required=False, default='', allow_blank=True)

    def validate(self, data):
        ticket = self.context['ticket']
        if not ticket.can_transition_to(data['new_status']):
            allowed = MaintenanceTicket.ALLOWED_TRANSITIONS.get(ticket.status, [])
            raise serializers.ValidationError(
                f"Transition '{ticket.status}' → '{data['new_status']}' impossible. "
                f"Transitions autorisées : {allowed}"
            )
        return data