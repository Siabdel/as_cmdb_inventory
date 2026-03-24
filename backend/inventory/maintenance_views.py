"""
ViewSets pour les modèles de maintenance
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .maintenance_models import MaintenanceType, MaintenanceTicket, MaintenanceAction
from .maintenance_serializers import (
    MaintenanceTypeSerializer,
    MaintenanceTicketSerializer,
    MaintenanceTicketDetailSerializer,
    MaintenanceActionSerializer
)
from .permissions import IsAdminOrReadOnly


class MaintenanceTypeViewSet(viewsets.ModelViewSet):
    """API CRUD pour les types de maintenance"""
    queryset = MaintenanceType.objects.all()
    serializer_class = MaintenanceTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['is_preventive']


class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    """API CRUD pour les tickets de maintenance"""
    queryset = MaintenanceTicket.objects.all()
    serializer_class = MaintenanceTicketSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description', 'asset__name', 'asset__internal_code']
    filterset_fields = ['status', 'priority', 'asset', 'maintenance_type', 'assigned_to']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MaintenanceTicketDetailSerializer
        return MaintenanceTicketSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Fermer un ticket de maintenance"""
        ticket = self.get_object()
        ticket.status = 'CLOSED'
        ticket.save()
        return Response({'status': 'Ticket fermé'})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assigner un ticket à un utilisateur"""
        ticket = self.get_object()
        user_id = request.data.get('user_id')
        if user_id:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
                ticket.assigned_to = user
                ticket.save()
                return Response({'status': 'Ticket assigné', 'assigned_to': user.username})
            except User.DoesNotExist:
                return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user_id requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def transition(self, request, pk=None):
        """Transitionner un ticket de maintenance vers un nouveau statut"""
        ticket = self.get_object()
        new_status = request.data.get('to_status')
        
        if not new_status:
            return Response({'error': 'to_status requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si le statut est valide
        valid_statuses = [choice[0] for choice in MaintenanceTicket.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si la transition est autorisée (simple vérification)
        # Vous pouvez ajouter une logique plus complexe ici si nécessaire
        old_status = ticket.status
        ticket.status = new_status
        ticket.save()
        
        return Response({
            'status': 'Ticket mis à jour',
            'ticket_id': ticket.id,
            'from_status': old_status,
            'to_status': new_status
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des tickets de maintenance"""
        from django.db.models import Count, Sum, Avg
        
        stats = {
            'total': self.queryset.count(),
            'by_status': dict(self.queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_priority': dict(self.queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'open_count': self.queryset.filter(status='OPEN').count(),
            'in_progress_count': self.queryset.filter(status='IN_PROGRESS').count(),
            'overdue_count': self.queryset.filter(due_date__lt=datetime.now().date(), status__in=['OPEN', 'IN_PROGRESS']).count(),
        }
        return Response(stats)


class MaintenanceActionViewSet(viewsets.ModelViewSet):
    """API CRUD pour les actions de maintenance"""
    queryset = MaintenanceAction.objects.all()
    serializer_class = MaintenanceActionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['description', 'parts_used', 'ticket__title']
    filterset_fields = ['action_type', 'ticket', 'ticket__asset']
    ordering_fields = ['performed_at', 'cost_euros']
    ordering = ['-performed_at']
    
    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des actions de maintenance"""
        from django.db.models import Count, Sum, Avg
        
        stats = {
            'total': self.queryset.count(),
            'total_cost': self.queryset.aggregate(total=Sum('cost_euros'))['total'] or 0,
            'avg_cost': self.queryset.aggregate(avg=Avg('cost_euros'))['avg'] or 0,
            'total_duration': self.queryset.aggregate(total=Sum('duration_hours'))['total'] or 0,
            'by_type': dict(self.queryset.values('action_type').annotate(count=Count('id')).values_list('action_type', 'count')),
        }
        return Response(stats)


from datetime import datetime