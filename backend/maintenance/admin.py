from django.contrib import admin
from django.utils.html import format_html
from .models import MaintenanceTicket, TicketPart, TicketComment, StatusHistory


class TicketPartInline(admin.TabularInline):
    model = TicketPart
    extra = 1


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['created_at']


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by',
                       'notes', 'created_at']
    can_delete = False


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display  = ['ticket_number', 'title', 'asset', 'priority_badge',
                     'status_badge', 'assigned_tech', 'due_date',
                     'is_overdue_display', 'created_at']
    list_filter   = ['status', 'priority', 'ticket_type']
    search_fields = ['ticket_number', 'title', 'asset__name',
                     'asset__serial_number']
    readonly_fields = ['ticket_number', 'resolved_at', 'closed_at',
                       'created_at', 'updated_at']
    inlines       = [TicketPartInline, TicketCommentInline, StatusHistoryInline]

    PRIORITY_COLORS = {
        'low': '#95a5a6', 'medium': '#3498db',
        'high': '#e67e22', 'critical': '#e74c3c',
    }
    STATUS_COLORS = {
        'open': '#3498db',       'assigned': '#9b59b6',
        'in_progress': '#f39c12','waiting_parts': '#e67e22',
        'pending_review': '#1abc9c', 'resolved': '#2ecc71',
        'closed': '#95a5a6',     'cancelled': '#e74c3c',
    }

    def priority_badge(self, obj):
        color = self.PRIORITY_COLORS.get(obj.priority, '#ccc')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priorité'

    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#ccc')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'

    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color:red;font-weight:bold">⚠ En retard</span>')
        return '✓'
    is_overdue_display.short_description = 'Délai'
