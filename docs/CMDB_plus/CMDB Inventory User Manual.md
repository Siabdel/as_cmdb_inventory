# CMDB Inventory User Manual

## Table of Contents

1. Introduction to CMDB
2. System Overview
3. Features
   - Asset Management
   - Maintenance Tickets
   - QR Code Scanning
   - Search and Filtering
4. Step-by-Step User Guides
   - Adding a New Asset
   - Scanning a QR Code
   - Creating a Maintenance Ticket
5. Troubleshooting
   - Common Issues
   - Solutions
6. Conclusion



## Roadmap des fonctionnalités futures

**Court terme (sprint 1-2) :**

- Génération automatique QR à la création d'un `Asset` (signal `post_save`)
- Module `MaintenanceTicket` complet avec workflow de statuts
- API `StockItem` avec alerte `is_low_stock`

**Moyen terme (sprint 3-4) :**

- Système de notifications (email via Celery + `django-notifications`)
- Export PDF des fiches asset + tickets (`weasyprint`)
- Rapport de coûts de maintenance par asset/période
- Authentification JWT (`djangorestframework-simplejwt`) au lieu du `TokenAuthentication` basique

**Long terme :**

- Application mobile Vue.js PWA avec scan QR natif (API `BarcodeDetector`)
- Import/export CSV/Excel masse assets (`openpyxl`)
- Intégration avec fournisseurs pièces (API externe)

 

## 1. Introduction to CMDB

A Configuration Management Database (CMDB) is a centralized database that contains information about the components of an organization's IT infrastructure and the relationships between them. It is a critical tool for IT asset management, helping organizations to track and manage their IT assets effectively.

### Importance of CMDB

- **Asset Management**: Track and manage all IT assets, including hardware, software, and network devices.
- **Incident Management**: Quickly identify and resolve issues by understanding the relationships between IT components.
- **Change Management**: Ensure that changes to IT infrastructure are managed in a controlled and documented manner.
- **Compliance**: Meet regulatory and compliance requirements by maintaining accurate and up-to-date records of IT assets.

## 2. System Overview

The CMDB Inventory system is designed to help organizations manage their IT assets efficiently. It provides features for asset management, maintenance tracking, and QR code scanning for easy asset identification and tracking.

## 3. Features

### 3.1 Asset Management

- **Add New Asset**: Users can add new assets to the system, including details such as internal code, name, category, brand, model, serial number, and more.
- **Edit Asset**: Existing assets can be edited to update their information.
- **View Asset Details**: Detailed information about each asset, including its current status, location, and assigned user, can be viewed.

### 3.2 Maintenance Tickets

- **Create Maintenance Ticket**: Users can create maintenance tickets for assets, specifying the type of maintenance, priority, and due date.
- **Assign Maintenance Ticket**: Tickets can be assigned to specific users for action.
- **Track Maintenance Status**: The status of maintenance tickets can be tracked, including whether they are open, in progress, or closed.

          ┌─────────────────────────────────┐
          │              open               │
          └──────────┬──────────────────────┘
                     │ assign()
                     ▼
          ┌─────────────────────────────────┐
          │            assigned             │
          └──────────┬──────────────────────┘
                     │ transition(in_progress)
                     ▼
          ┌─────────────────────────────────┐
          │           in_progress           │◄──────────┐
          └──────┬─────────────┬────────────┘           │
                 │             │                         │
    waiting_parts│             │pending_review           │ réouverture
                 ▼             ▼                         │
          ┌──────────┐  ┌─────────────────┐             │
          │ waiting  │  │ pending_review  │             │
          │  parts   │  └───────┬─────────┘             │
          └──────────┘          │ resolve()              │
                                ▼                        │
                       ┌─────────────────┐              │
                       │    resolved     │──────────────►┘
                       └───────┬─────────┘
                               │ close()
                               ▼
                       ┌─────────────────┐
                       │     closed      │
                       └─────────────────┘

  cancelled ◄── depuis open / assigned / in_progress / waiting_parts

### 3.3 QR Code Scanning

- **Scan QR Code**: Users can scan QR codes to quickly access asset information.
- **Generate QR Code**: QR codes can be generated and downloaded for each asset.

```ABAP
POST /api/v1/inventory/assets/   →  Asset créé
        ↓ signal post_save
    QRCode créé  →  _generate_qr_image()
        ↓
    media/qr_codes/qr_asset_42_<uuid>.png

Scan mobile  →  GET /api/v1/scanner/scan/<uuid>/
        ↓
    ScanLog enregistré  +  fiche Asset retournée

```

Voici le module `maintenance` complet avec workflow de statuts, transitions contrôlées et API DRF.

------

## 1. `maintenance/models.py`

```
pythonfrom django.db import models
from django.utils import timezone
from inventory.models import Asset, TimeStampMixin


class MaintenanceTicket(TimeStampMixin):

    PRIORITY_CHOICES = [
        ('low',      'Faible'),
        ('medium',   'Moyen'),
        ('high',     'Élevé'),
        ('critical', 'Critique'),
    ]

    STATUS_CHOICES = [
        ('open',           'Ouvert'),
        ('assigned',       'Assigné'),
        ('in_progress',    'En cours'),
        ('waiting_parts',  'Attente pièces'),
        ('pending_review', 'En attente validation'),
        ('resolved',       'Résolu'),
        ('closed',         'Fermé'),
        ('cancelled',      'Annulé'),
    ]

    TYPE_CHOICES = [
        ('repair',      'Réparation'),
        ('diagnostic',  'Diagnostic'),
        ('upgrade',     'Upgrade'),
        ('preventive',  'Préventif'),
        ('cleaning',    'Nettoyage'),
    ]

    # Transitions autorisées : {statut_actuel: [statuts_suivants]}
    ALLOWED_TRANSITIONS = {
        'open':           ['assigned', 'cancelled'],
        'assigned':       ['in_progress', 'cancelled'],
        'in_progress':    ['waiting_parts', 'pending_review', 'cancelled'],
        'waiting_parts':  ['in_progress', 'cancelled'],
        'pending_review': ['resolved', 'in_progress'],
        'resolved':       ['closed', 'in_progress'],  # réouverture possible
        'closed':         [],
        'cancelled':      [],
    }

    ticket_number    = models.CharField(max_length=20, unique=True, blank=True)
    asset            = models.ForeignKey(Asset, on_delete=models.CASCADE,
                                         related_name='tickets')
    title            = models.CharField(max_length=200)
    description      = models.TextField()
    ticket_type      = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                        default='repair')
    priority         = models.CharField(max_length=10, choices=PRIORITY_CHOICES,
                                        default='medium')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                        default='open')
    assigned_tech    = models.CharField(max_length=100, blank=True)
    reported_by      = models.CharField(max_length=100, blank=True)
    due_date         = models.DateField(null=True, blank=True)
    resolved_at      = models.DateTimeField(null=True, blank=True)
    closed_at        = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    labor_cost       = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket de maintenance'
        verbose_name_plural = 'Tickets de maintenance'

    def __str__(self):
        return f"[{self.ticket_number}] {self.title} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # Auto-génération du numéro de ticket
        if not self.ticket_number:
            year = timezone.now().year
            last = MaintenanceTicket.objects.filter(
                ticket_number__startswith=f"TKT-{year}-"
            ).count()
            self.ticket_number = f"TKT-{year}-{last + 1:04d}"
        super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status, user='', notes=''):
        """Effectue la transition avec validation + timestamps automatiques."""
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Transition '{self.status}' → '{new_status}' non autorisée."
            )
        old_status = self.status
        self.status = new_status

        # Timestamps automatiques
        if new_status == 'resolved':
            self.resolved_at = timezone.now()
        if new_status == 'closed':
            self.closed_at = timezone.now()
        # Réouverture : reset resolved_at
        if old_status in ('resolved', 'closed') and new_status == 'in_progress':
            self.resolved_at = None
            self.closed_at = None

        self.save(update_fields=['status', 'resolved_at', 'closed_at', 'updated_at'])

        # Enregistrer dans l'historique
        StatusHistory.objects.create(
            ticket=self,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            notes=notes,
        )
        return self

    @property
    def total_cost(self):
        parts_cost = sum(p.total_cost for p in self.parts.all())
        return self.labor_cost + parts_cost

    @property
    def is_overdue(self):
        if self.due_date and self.status not in ('resolved', 'closed', 'cancelled'):
            return timezone.now().date() > self.due_date
        return False


class StatusHistory(TimeStampMixin):
    """Historique complet des transitions de statut."""
    ticket      = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE,
                                    related_name='status_history')
    from_status = models.CharField(max_length=20)
    to_status   = models.CharField(max_length=20)
    changed_by  = models.CharField(max_length=100, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historique statut'

    def __str__(self):
        return f"{self.ticket.ticket_number}: {self.from_status} → {self.to_status}"


class TicketPart(TimeStampMixin):
    """Pièces détachées consommées pour un ticket."""
    ticket    = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE,
                                  related_name='parts')
    part_name = models.CharField(max_length=200)
    part_ref  = models.CharField(max_length=100, blank=True)
    quantity  = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Pièce utilisée'

    def __str__(self):
        return f"{self.part_name} x{self.quantity}"

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost


class TicketComment(TimeStampMixin):
    """Journal d'activité / commentaires technicien."""
    ticket      = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE,
                                    related_name='comments')
    author      = models.CharField(max_length=100)
    content     = models.TextField()
    is_internal = models.BooleanField(default=False)  # note interne technicien

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Commentaire ticket'

    def __str__(self):
        return f"{self.ticket.ticket_number} — {self.author}"
```

------

## 2. `maintenance/serializers.py`

```
pythonfrom rest_framework import serializers
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
```

------

## 3. `maintenance/views.py`

```
pythonfrom rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.utils import timezone

from .models import MaintenanceTicket, TicketPart, TicketComment
from .serializers import (
    TicketListSerializer, TicketDetailSerializer,
    TicketTransitionSerializer, TicketPartSerializer,
    TicketCommentSerializer,
)


class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter,
                          filters.OrderingFilter]
    filterset_fields   = ['status', 'priority', 'ticket_type',
                          'asset', 'assigned_tech']
    search_fields      = ['ticket_number', 'title', 'description',
                          'asset__name', 'asset__serial_number']
    ordering_fields    = ['created_at', 'due_date', 'priority']
    ordering           = ['-created_at']

    def get_queryset(self):
        return MaintenanceTicket.objects.select_related('asset').prefetch_related(
            'parts', 'comments', 'status_history'
        ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        return TicketDetailSerializer

    # ── Transition de statut ────────────────────────────────

    @action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        """
        Effectue une transition de statut contrôlée.
        Body: { "new_status": "in_progress", "changed_by": "tech01", "notes": "..." }
        """
        ticket = self.get_object()
        serializer = TicketTransitionSerializer(
            data=request.data,
            context={'ticket': ticket}
        )
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        ticket.transition_to(
            new_status=d['new_status'],
            user=d.get('changed_by', request.user.username),
            notes=d.get('notes', ''),
        )
        return Response(TicketDetailSerializer(ticket).data)

    # ── Actions rapides ─────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        """Assigner un technicien et passer en statut 'assigned'."""
        ticket = self.get_object()
        tech = request.data.get('assigned_tech')
        if not tech:
            return Response({'error': 'assigned_tech requis.'}, status=400)
        ticket.assigned_tech = tech
        ticket.save(update_fields=['assigned_tech', 'updated_at'])
        ticket.transition_to('assigned', user=request.user.username,
                             notes=f"Assigné à {tech}")
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Résoudre un ticket avec notes de résolution."""
        ticket = self.get_object()
        notes = request.data.get('resolution_notes', '')
        if notes:
            ticket.resolution_notes = notes
            ticket.save(update_fields=['resolution_notes', 'updated_at'])
        ticket.transition_to('resolved', user=request.user.username, notes=notes)
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.transition_to('closed', user=request.user.username,
                             notes=request.data.get('notes', ''))
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        ticket.transition_to('cancelled', user=request.user.username,
                             notes=request.data.get('notes', 'Annulé'))
        return Response(TicketDetailSerializer(ticket).data)

    # ── Commentaires ────────────────────────────────────────

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == 'GET':
            qs = ticket.comments.all()
            return Response(TicketCommentSerializer(qs, many=True).data)
        serializer = TicketCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket)
        return Response(serializer.data, status=201)

    # ── Pièces ──────────────────────────────────────────────

    @action(detail=True, methods=['get', 'post'], url_path='parts')
    def parts(self, request, pk=None):
        ticket = self.get_object()
        if request.method == 'GET':
            return Response(TicketPartSerializer(ticket.parts.all(), many=True).data)
        serializer = TicketPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket)
        return Response(serializer.data, status=201)

    # ── Listes filtrées ─────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """Tickets en retard (due_date dépassée, non clôturés)."""
        qs = self.get_queryset().filter(
            due_date__lt=timezone.now().date()
        ).exclude(status__in=['resolved', 'closed', 'cancelled'])
        return Response(TicketListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='open')
    def open_tickets(self, request):
        """Tickets actifs (hors resolved/closed/cancelled)."""
        qs = self.get_queryset().exclude(
            status__in=['resolved', 'closed', 'cancelled']
        )
        return Response(TicketListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """KPIs tickets pour dashboard."""
        qs = MaintenanceTicket.objects.all()
        data = {
            'total':          qs.count(),
            'open':           qs.filter(status='open').count(),
            'in_progress':    qs.filter(status='in_progress').count(),
            'waiting_parts':  qs.filter(status='waiting_parts').count(),
            'resolved':       qs.filter(status='resolved').count(),
            'closed':         qs.filter(status='closed').count(),
            'cancelled':      qs.filter(status='cancelled').count(),
            'critical':       qs.filter(priority='critical').count(),
            'overdue':        qs.filter(
                                  due_date__lt=timezone.now().date()
                              ).exclude(
                                  status__in=['resolved', 'closed', 'cancelled']
                              ).count(),
            'total_labor_cost': qs.aggregate(v=Sum('labor_cost'))['v'] or 0,
        }
        return Response(data)
```

------

## 4. `maintenance/urls.py`

```
pythonfrom django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tickets', views.MaintenanceTicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]
```

------

## 5. `config/urls.py`

```
python
path('api/v1/maintenance/', include('maintenance.urls')),
```

------

## 6. `maintenance/admin.py`

```
pythonfrom django.contrib import admin
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
```

------

## Workflow des statuts

```
text          ┌─────────────────────────────────┐
          │              open               │
          └──────────┬──────────────────────┘
                     │ assign()
                     ▼
          ┌─────────────────────────────────┐
          │            assigned             │
          └──────────┬──────────────────────┘
                     │ transition(in_progress)
                     ▼
          ┌─────────────────────────────────┐
          │           in_progress           │◄──────────┐
          └──────┬─────────────┬────────────┘           │
                 │             │                         │
    waiting_parts│             │pending_review           │ réouverture
                 ▼             ▼                         │
          ┌──────────┐  ┌─────────────────┐             │
          │ waiting  │  │ pending_review  │             │
          │  parts   │  └───────┬─────────┘             │
          └──────────┘          │ resolve()              │
                                ▼                        │
                       ┌─────────────────┐              │
                       │    resolved     │──────────────►┘
                       └───────┬─────────┘
                               │ close()
                               ▼
                       ┌─────────────────┐
                       │     closed      │
                       └─────────────────┘

  cancelled ◄── depuis open / assigned / in_progress / waiting_parts
```

------

## Endpoints générés

| Méthode    | URL                                            | Usage               |
| ---------- | ---------------------------------------------- | ------------------- |
| `GET`      | `/api/v1/maintenance/tickets/`                 | Liste tickets       |
| `POST`     | `/api/v1/maintenance/tickets/`                 | Créer ticket        |
| `GET`      | `/api/v1/maintenance/tickets/{id}/`            | Détail complet      |
| `POST`     | `/api/v1/maintenance/tickets/{id}/transition/` | Changer statut      |
| `POST`     | `/api/v1/maintenance/tickets/{id}/assign/`     | Assigner technicien |
| `POST`     | `/api/v1/maintenance/tickets/{id}/resolve/`    | Résoudre            |
| `POST`     | `/api/v1/maintenance/tickets/{id}/close/`      | Clôturer            |
| `POST`     | `/api/v1/maintenance/tickets/{id}/cancel/`     | Annuler             |
| `GET/POST` | `/api/v1/maintenance/tickets/{id}/comments/`   | Commentaires        |
| `GET/POST` | `/api/v1/maintenance/tickets/{id}/parts/`      | Pièces utilisées    |
| `GET`      | `/api/v1/maintenance/tickets/overdue/`         | Tickets en retard   |
| `GET`      | `/api/v1/maintenance/tickets/stats/`           | KPIs dashboard      |

> N'oublie pas : `python manage.py makemigrations maintenance && python manage.py migrate`	

### 3.4 Search and Filtering

- **Search Assets**: Users can search for assets using various criteria such as internal code, name, category, and more.
- **Filter Results**: Search results can be filtered to refine the list of assets.

## 4. Step-by-Step User Guides

### 4.1 Adding a New Asset

1. Navigate to the **Assets** page.
2. Click the **Add New Asset** button.
3. Fill in the required fields such as **Internal Code**, **Name**, **Category**, **Brand**, **Model**, **Serial Number**, and **Description**.
4. Select the **Status** and **Location** of the asset.
5. Click **Save** to add the asset to the system.

### 4.2 Scanning a QR Code

1. Navigate to the **Scan QR** page.
2. Use the QR code scanner to scan the QR code of the asset.
3. The system will display the asset details.

### 4.3 Creating a Maintenance Ticket

1. Navigate to the **Assets** page.
2. Select the asset for which you want to create a maintenance ticket.
3. Click the **Create Maintenance Ticket** button.
4. Fill in the required fields such as **Title**, **Description**, **Priority**, and **Due Date**.
5. Assign the ticket to a user.
6. Click **Save** to create the maintenance ticket.

## 5. Troubleshooting

### 5.1 Common Issues

- **QR Code Scanning Fails**: Ensure that the QR code is clear and not damaged. Check the camera settings and lighting conditions.
- **Search Not Returning Expected Results**: Verify that the search criteria are correct and that the asset information is up-to-date.

### 5.2 Solutions

- **QR Code Scanning Fails**: Try scanning the QR code in a well-lit area and ensure the camera is clean. If the issue persists, regenerate the QR code for the asset.
- **Search Not Returning Expected Results**: Double-check the search criteria and update the asset information if necessary.

## 6. Conclusion

The CMDB Inventory system is a powerful tool for managing IT assets. By following the user guides and troubleshooting tips, you can effectively use the system to track and manage your assets, create and manage maintenance tickets, and ensure the smooth operation of your IT infrastructure.