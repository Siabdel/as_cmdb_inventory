"""
Vues API Django REST Framework pour l'application CMDB Inventory
"""

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import Location, Category, Brand, Tag, Asset, AssetMovement
from .serializers import (
    LocationSerializer, CategorySerializer, BrandSerializer, TagSerializer,
    AssetListSerializer, AssetDetailSerializer, AssetCreateUpdateSerializer,
    AssetMovementSerializer, AssetMoveFromScanSerializer, DashboardSummarySerializer
)


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des emplacements"""
    
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des catégories"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BrandViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des marques"""
    
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'website']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des étiquettes"""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class AssetFilter(django_filters.FilterSet):
    """Filtres personnalisés pour les assets"""
    
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.all())
    current_location = django_filters.ModelChoiceFilter(queryset=Location.objects.all())
    assigned_to = django_filters.ModelChoiceFilter(queryset=None)
    tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all())
    status = django_filters.MultipleChoiceFilter(choices=Asset.STATUS_CHOICES)
    purchase_date_from = django_filters.DateFilter(field_name='purchase_date', lookup_expr='gte')
    purchase_date_to = django_filters.DateFilter(field_name='purchase_date', lookup_expr='lte')
    warranty_expired = django_filters.BooleanFilter(method='filter_warranty_expired')
    
    class Meta:
        model = Asset
        fields = [
            'category', 'brand', 'current_location', 'assigned_to', 'tags',
            'status', 'purchase_date_from', 'purchase_date_to', 'warranty_expired'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamiquement définir les choix pour assigned_to
        from django.contrib.auth.models import User
        self.filters['assigned_to'].queryset = User.objects.filter(
            assigned_assets__isnull=False
        ).distinct()
    
    def filter_warranty_expired(self, queryset, name, value):
        """Filtre les assets avec garantie expirée"""
        today = timezone.now().date()
        if value:
            return queryset.filter(warranty_end__lt=today)
        else:
            return queryset.filter(Q(warranty_end__gte=today) | Q(warranty_end__isnull=True))


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des assets"""
    
    queryset = Asset.objects.select_related(
        'category', 'brand', 'current_location', 'assigned_to'
    ).prefetch_related('tags')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AssetFilter
    search_fields = [
        'internal_code', 'name', 'model', 'serial_number', 'description',
        'category__name', 'brand__name', 'current_location__name'
    ]
    ordering_fields = [
        'internal_code', 'name', 'status', 'created_at', 'updated_at',
        'purchase_date', 'warranty_end'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'list':
            return AssetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        else:
            return AssetDetailSerializer
    
    @action(detail=True, methods=['get'])
    def qr_image(self, request, pk=None):
        """Retourne l'image QR code de l'asset"""
        asset = self.get_object()
        if not asset.qr_code_image:
            asset.generate_qr_code()
            asset.refresh_from_db()
        
        if asset.qr_code_image:
            response = HttpResponse(
                asset.qr_code_image.read(),
                content_type='image/png'
            )
            response['Content-Disposition'] = f'inline; filename="qr_{asset.internal_code}.png"'
            return response
        else:
            return Response(
                {'error': 'QR code non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Retourne l'historique des mouvements de l'asset"""
        asset = self.get_object()
        movements = asset.movements.all().order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = AssetMovementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AssetMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def move_from_scan(self, request):
        """Déplace un asset via scan QR"""
        serializer = AssetMoveFromScanSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            movement = serializer.save()
            return Response(
                AssetMovementSerializer(movement).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Exporte la liste des assets en CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assets_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Code Interne', 'Nom', 'Catégorie', 'Marque', 'Modèle',
            'Numéro de Série', 'Statut', 'Emplacement', 'Assigné à',
            'Date d\'achat', 'Prix d\'achat', 'Fin de garantie', 'Créé le'
        ])
        
        # Appliquer les filtres
        queryset = self.filter_queryset(self.get_queryset())
        
        for asset in queryset:
            writer.writerow([
                asset.internal_code,
                asset.name,
                asset.category.name if asset.category else '',
                asset.brand.name if asset.brand else '',
                asset.model,
                asset.serial_number,
                asset.get_status_display(),
                asset.current_location.name if asset.current_location else '',
                asset.assigned_to.get_full_name() if asset.assigned_to else '',
                asset.purchase_date.strftime('%d/%m/%Y') if asset.purchase_date else '',
                asset.purchase_price or '',
                asset.warranty_end.strftime('%d/%m/%Y') if asset.warranty_end else '',
                asset.created_at.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response


class AssetMovementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des mouvements d'assets"""
    
    queryset = AssetMovement.objects.select_related(
        'asset', 'from_location', 'to_location', 'moved_by'
    ).all()
    serializer_class = AssetMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'move_type', 'from_location', 'to_location', 'moved_by']
    search_fields = ['asset__internal_code', 'asset__name', 'note']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Ajoute l'utilisateur actuel lors de la création"""
        serializer.save(moved_by=self.request.user)


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet pour les données du dashboard"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Retourne un résumé des données pour le dashboard"""
        
        # Statistiques générales
        total_assets = Asset.objects.count()
        
        # Répartition par statut
        assets_by_status = dict(
            Asset.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )
        
        # Répartition par emplacement (top 10)
        assets_by_location = dict(
            Asset.objects.filter(
                current_location__isnull=False
            ).values(
                'current_location__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10].values_list(
                'current_location__name', 'count'
            )
        )
        
        # Répartition par catégorie (top 10)
        assets_by_category = dict(
            Asset.objects.filter(
                category__isnull=False
            ).values(
                'category__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10].values_list(
                'category__name', 'count'
            )
        )
        
        # Mouvements récents (10 derniers)
        recent_movements = AssetMovement.objects.select_related(
            'asset', 'from_location', 'to_location', 'moved_by'
        ).order_by('-created_at')[:10]
        
        # Assets nécessitant une maintenance (statut broken ou maintenance)
        assets_needing_maintenance = Asset.objects.filter(
            status__in=['broken', 'maintenance']
        ).select_related('category', 'brand', 'current_location')[:10]
        
        # Garanties expirant bientôt (dans les 30 prochains jours)
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        warranty_expiring_soon = Asset.objects.filter(
            warranty_end__lte=thirty_days_from_now,
            warranty_end__gte=timezone.now().date()
        ).select_related('category', 'brand', 'current_location')[:10]
        
        data = {
            'total_assets': total_assets,
            'assets_by_status': assets_by_status,
            'assets_by_location': assets_by_location,
            'assets_by_category': assets_by_category,
            'recent_movements': AssetMovementSerializer(recent_movements, many=True).data,
            'assets_needing_maintenance': AssetListSerializer(assets_needing_maintenance, many=True).data,
            'warranty_expiring_soon': AssetListSerializer(warranty_expiring_soon, many=True).data,
        }
        
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retourne des statistiques détaillées"""
        
        # Statistiques par mois (12 derniers mois)
        from django.db.models import Extract
        from django.utils import timezone
        import calendar
        
        twelve_months_ago = timezone.now().date().replace(day=1) - timedelta(days=365)
        
        monthly_stats = Asset.objects.filter(
            created_at__date__gte=twelve_months_ago
        ).extra(
            select={'month': 'EXTRACT(month FROM created_at)', 'year': 'EXTRACT(year FROM created_at)'}
        ).values('month', 'year').annotate(
            count=Count('id')
        ).order_by('year', 'month')
        
        # Formater les données mensuelles
        monthly_data = []
        for stat in monthly_stats:
            month_name = calendar.month_name[int(stat['month'])]
            monthly_data.append({
                'period': f"{month_name} {int(stat['year'])}",
                'count': stat['count']
            })
        
        # Valeur totale des assets
        from django.db.models import Sum
        total_value = Asset.objects.aggregate(
            total=Sum('purchase_price')
        )['total'] or 0
        
        return Response({
            'monthly_acquisitions': monthly_data,
            'total_value': float(total_value),
            'average_value': float(total_value / total_assets) if total_assets > 0 else 0,
        })