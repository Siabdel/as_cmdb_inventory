"""
Views pour l'API CMDB Inventory
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from datetime import datetime

from .models import (
    Location, Category, Brand, Tag,
    Asset, AssetMovement
)
from .serializers import (
    LocationSerializer, CategorySerializer, BrandSerializer, TagSerializer,
    AssetSerializer, AssetMovementSerializer
)
from .maintenance_models import MaintenanceTicket, MaintenanceAction
from .permissions import IsAdminOrReadOnly


class LocationViewSet(viewsets.ModelViewSet):
    """API CRUD pour les emplacements"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    """API CRUD pour les catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class BrandViewSet(viewsets.ModelViewSet):
    """API CRUD pour les marques"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    """API CRUD pour les étiquettes"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class AssetViewSet(viewsets.ModelViewSet):
    """API CRUD pour les actifs"""
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAdminOrReadOnly]


class AssetMovementViewSet(viewsets.ModelViewSet):
    """API CRUD pour les mouvements d'actifs"""
    queryset = AssetMovement.objects.all()
    serializer_class = AssetMovementSerializer
    permission_classes = [IsAdminOrReadOnly]


class DashboardViewSet(viewsets.ViewSet):
    """API pour les statistiques du dashboard"""
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques globales pour le dashboard"""
        stats = {
            'assets': {
                'total': Asset.objects.count(),
                'by_status': dict(Asset.objects.values('condition_state').annotate(count=Count('id')).values_list('condition_state', 'count')),
                'by_location': dict(Asset.objects.values('location__name').annotate(count=Count('id')).values_list('location__name', 'count')),
            },
            'maintenance': {
                'open_tickets': MaintenanceTicket.objects.filter(status='OPEN').count(),
                'in_progress_tickets': MaintenanceTicket.objects.filter(status='IN_PROGRESS').count(),
                'overdue_tickets': MaintenanceTicket.objects.filter(due_date__lt=datetime.now().date(), status__in=['OPEN', 'IN_PROGRESS']).count(),
                'total_actions': MaintenanceAction.objects.count(),
                'total_cost': MaintenanceAction.objects.aggregate(total=Sum('cost_euros'))['total'] or 0,
            },
        }
        return Response(stats)