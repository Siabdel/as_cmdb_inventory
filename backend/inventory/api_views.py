"""
Views pour l'API CMDB Inventory
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import Category, Brand, Location, Tag, Asset, AssetMovement
from .serializers import (
    CategorySerializer, BrandSerializer, LocationSerializer,
    TagSerializer, AssetListSerializer, AssetDetailSerializer,
    AssetMovementSerializer, DashboardStatsSerializer,
)

from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard.html'



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['type']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'condition_state', 'category', 'brand', 'current_location']
    search_fields = ['name', 'serial_number', 'model', 'assigned_to']
    ordering_fields = ['name', 'purchase_date', 'purchase_price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Asset.objects.select_related(
            'category', 'brand', 'current_location'
        ).prefetch_related('tags', 'movements').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetDetailSerializer

    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Asset create request data: {request.data}")
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Asset create error: {e}", exc_info=True)
            raise

    # ── Actions custom ──────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='move')
    def move(self, request, pk=None):
        """Déplacer un asset vers un nouvel emplacement."""
        asset = self.get_object()
        to_location_id = request.data.get('to_location_id')
        moved_by = request.data.get('moved_by', request.user.username)
        notes = request.data.get('notes', '')

        try:
            to_location = Location.objects.get(pk=to_location_id)
        except Location.DoesNotExist:
            return Response({'error': 'Location introuvable.'}, status=400)

        movement = AssetMovement.objects.create(
            asset=asset,
            from_location=asset.current_location,
            to_location=to_location,
            moved_by=moved_by,
            notes=notes,
        )
        asset.current_location = to_location
        asset.save()

        return Response(AssetMovementSerializer(movement).data, status=201)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        """Assigner un asset à un employé."""
        asset = self.get_object()
        assigned_to = request.data.get('assigned_to')
        if not assigned_to:
            return Response({'error': 'assigned_to requis.'}, status=400)
        asset.assigned_to = assigned_to
        asset.status = 'active'
        asset.save()
        return Response(AssetDetailSerializer(asset).data)

    @action(detail=True, methods=['post'], url_path='retire')
    def retire(self, request, pk=None):
        """Archiver/retirer un asset du stock."""
        asset = self.get_object()
        asset.status = 'archived'
        asset.assigned_to = None
        asset.save()
        return Response({'status': 'archived', 'asset': asset.name})

    @action(detail=False, methods=['get'], url_path='warranty-expiring')
    def warranty_expiring(self, request):
        """Assets dont la garantie expire dans 30 jours."""
        soon = timezone.now().date() + timedelta(days=30)
        qs = Asset.objects.filter(
            warranty_end__lte=soon,
            warranty_end__gte=timezone.now().date(),
            status='active'
        ).select_related('category', 'brand', 'current_location')
        return Response(AssetListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='by-status')
    def by_status(self, request):
        """Répartition des assets par statut (pour graphiques dashboard)."""
        data = Asset.objects.values('status').annotate(count=Count('id'))
        return Response(data)

    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        """Répartition par catégorie."""
        data = Asset.objects.values(
            'category__name', 'category__icon'
        ).annotate(count=Count('id')).order_by('-count')
        return Response(data)


class AssetMovementViewSet(viewsets.ModelViewSet):
    queryset = AssetMovement.objects.select_related(
        'asset', 'from_location', 'to_location'
    ).order_by('-moved_at')
    serializer_class = AssetMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'from_location', 'to_location']
    ordering_fields = ['moved_at']
    http_method_names = ['get', 'post', 'head', 'options']  # pas de PUT/DELETE


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        soon = timezone.now().date() + timedelta(days=30)
        data = {
            'total_assets':    Asset.objects.count(),
            'active_assets':   Asset.objects.filter(status='active').count(),
            'inactive_assets': Asset.objects.filter(status='inactive').count(),
            'archived_assets': Asset.objects.filter(status='archived').count(),
            'assets_new':      Asset.objects.filter(condition_state='new').count(),
            'assets_used':     Asset.objects.filter(condition_state='used').count(),
            'assets_damaged':  Asset.objects.filter(condition_state='damaged').count(),
            'total_value':     Asset.objects.aggregate(
                                   v=Sum('purchase_price'))['v'] or 0,
            'low_warranty':    Asset.objects.filter(
                                   warranty_end__lte=soon,
                                   warranty_end__gte=timezone.now().date()).count(),
            'recent_movements': AssetMovement.objects.select_related(
                                   'asset', 'from_location', 'to_location'
                                ).order_by('-moved_at')[:10],
        }
        return Response(DashboardStatsSerializer(data).data)
