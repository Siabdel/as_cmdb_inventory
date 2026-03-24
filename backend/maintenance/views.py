from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from .models import MaintenanceTicket, TicketPart, TicketComment
from .serializers import (
    TicketListSerializer, TicketDetailSerializer,
    TicketTransitionSerializer, TicketPartSerializer,
    TicketCommentSerializer,
)


# backend/maintenance/views.py

class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tickets de maintenance.
    """
    # ── Authentification & Permissions ─────────────────────
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    ##permission_classes = [IsAuthenticated or IsAdminUser]
    
    # ── Filtrage & Recherche ───────────────────────────────
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'ticket_type', 'asset', 'assigned_tech']
    search_fields = ['ticket_number', 'title', 'description', 'asset__name', 'asset__serial_number']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        return MaintenanceTicket.objects.select_related('asset').prefetch_related(
            'parts', 'comments', 'status_history'
        ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        return TicketDetailSerializer

    # ── Transition de statut ────────────────────────────────
    @action(
        detail=True,
        methods=['POST', 'GET', 'PATCH'],
        url_path='transition',
        authentication_classes=[JWTAuthentication, SessionAuthentication],
        permission_classes=[IsAuthenticated]
    )
    def transition(self, request, pk=None):
        """
        Effectue une transition de statut contrôlée.
        Body: { "new_status": "in_progress", "changed_by": "tech01", "notes": "..." }
        """
        ticket = self.get_object()
        
        if request.method == 'GET':
            # Retourne les statuts possibles pour ce ticket
            return Response({
                'current_status': ticket.status,
                'allowed_transitions': ticket.get_allowed_transitions()
            })
        
        # Vérification supplémentaire de l'autorisation de transition
        if not ticket.can_transition_to(request.data.get('new_status')):
            return Response({
                'error': 'Transition non autorisée',
                'allowed_transitions': ticket.get_allowed_transitions()
            }, status=403)
        
        # Vérification que l'utilisateur a le droit de faire cette transition
        # (facultatif - l'authentification est déjà gérée)
        if not request.user.is_authenticated:
            return Response({
                'error': 'Utilisateur non authentifié'
            }, status=401)
        
        serializer = TicketTransitionSerializer(
            data=request.data,
            context={'ticket': ticket, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        ticket.transition_to(
            new_status=d['new_status'],
            user=request.user.username,
            notes=d.get('notes', ''),
        )
        return Response(TicketDetailSerializer(ticket).data)

    # ── Autres actions (assign, resolve, close, cancel...) ──
    # ... (reste de votre code)
    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        return TicketDetailSerializer

    # ── Transition de statut ────────────────────────────────

    @action(
        detail=True,
        methods=['POST', 'GET', 'PATCH'],
        url_path='transition',
        permission_classes=[IsAuthenticated]
    )
    def transition(self, request, pk=None):
        """
        Effectue une transition de statut contrôlée.
        Body: { "new_status": "in_progress", "changed_by": "tech01", "notes": "..." }
        """
        ticket = self.get_object()
        if request.method == 'GET':
            # Retourne les statuts possibles pour ce ticket
            # Pour simplifier, on retourne tous les statuts possibles
            return Response({
                'current_status': ticket.status,
                'allowed_transitions': ['OPEN', 'IN_PROGRESS', 'CLOSED', 'CANCELLED']
            })
        
        serializer = TicketTransitionSerializer(
            data=request.data,
            context={'ticket': ticket, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        ticket.transition_to(
            new_status=d['new_status'],
            user=request.user.username,
            notes=d.get('notes', ''),
        )
        return Response(TicketDetailSerializer(ticket).data)

    # ── Actions rapides ─────────────────────────────────────

    @action(detail=True, methods=['POST'], url_path='assign')
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

    @action(detail=True, methods=['POST'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Résoudre un ticket avec notes de résolution."""
        ticket = self.get_object()
        notes = request.data.get('resolution_notes', '')
        if notes:
            ticket.resolution_notes = notes
            ticket.save(update_fields=['resolution_notes', 'updated_at'])
        ticket.transition_to('resolved', user=request.user.username, notes=notes)
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['POST'], url_path='close')
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.transition_to('closed', user=request.user.username,
                             notes=request.data.get('notes', ''))
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['POST'], url_path='cancel')
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        ticket.transition_to('cancelled', user=request.user.username,
                             notes=request.data.get('notes', 'Annulé'))
        return Response(TicketDetailSerializer(ticket).data)

    # ── Commentaires ────────────────────────────────────────

    @action(detail=True, methods=['GET', 'POST'], url_path='comments')
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

    @action(detail=True, methods=['GET', 'POST'], url_path='parts')
    def parts(self, request, pk=None):
        ticket = self.get_object()
        if request.method == 'GET':
            return Response(TicketPartSerializer(ticket.parts.all(), many=True).data)
        serializer = TicketPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket)
        return Response(serializer.data, status=201)

    # ── Listes filtrées ─────────────────────────────────────

    @action(detail=False, methods=['GET'], url_path='overdue')
    def overdue(self, request):
        """Tickets en retard (due_date dépassée, non clôturés)."""
        qs = self.get_queryset().filter(
            due_date__lt=timezone.now().date()
        ).exclude(status__in=['resolved', 'closed', 'cancelled'])
        return Response(TicketListSerializer(qs, many=True).data)

    @action(detail=False, methods=['GET'], url_path='open')
    def open_tickets(self, request):
        """Tickets actifs (hors resolved/closed/cancelled)."""
        qs = self.get_queryset().exclude(
            status__in=['resolved', 'closed', 'cancelled']
        )
        return Response(TicketListSerializer(qs, many=True).data)

    @action(detail=False, methods=['GET'], url_path='stats')
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
