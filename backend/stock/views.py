from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, F

from .models import StockItem, StockMovement
from .serializers import (StockItemSerializer, StockItemListSerializer, 
                           StockMovementSerializer)
from inventory.models import Category
from django.db.models import Count
from inventory.serializers import CategorySerializer

class StockItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter,
                          filters.OrderingFilter]
    filterset_fields   = ['item_type', 'brand', 'location']
    search_fields      = ['name', 'reference', 'description']
    ordering_fields    = ['name', 'quantity', 'unit_price', 'created_at']
    ordering           = ['name']

    def get_queryset(self):
        return StockItem.objects.select_related(
            'brand', 'location'
        ).prefetch_related('movements').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return StockItemListSerializer
        return StockItemSerializer

    def create(self, request, *args, **kwargs):
        """Permet la création d'un nouvel article de stock via POST."""
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Articles sous le seuil minimum."""
        qs = self.get_queryset().filter(quantity__lte=F('min_quantity'))
        return Response(StockItemListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = StockItem.objects.all()
        return Response({
            'total_items':      qs.count(),
            'low_stock_count':  qs.filter(quantity__lte=F('min_quantity')).count(),
            'out_of_stock':     qs.filter(quantity=0).count(),
            'total_value':      qs.aggregate(
                                    v=Sum(F('quantity') * F('unit_price'))
                                )['v'] or 0,
        })

    @action(detail=True, methods=['post'], url_path='add-stock')
    def add_stock(self, request, pk=None):
        """Entrée rapide de stock."""
        item     = self.get_object()
        quantity = request.data.get('quantity')
        reason   = request.data.get('reason', 'Entrée manuelle')
        done_by  = request.data.get('done_by', request.user.username)

        if not quantity or int(quantity) <= 0:
            return Response({'error': 'quantity doit être > 0'}, status=400)

        mv = StockMovement.objects.create(
            item=item, movement_type='in',
            quantity=int(quantity), reason=reason, done_by=done_by
        )
        return Response(StockMovementSerializer(mv).data, status=201)

    @action(detail=True, methods=['post'], url_path='remove-stock')
    def remove_stock(self, request, pk=None):
        """Sortie rapide de stock."""
        item     = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        if quantity <= 0:
            return Response({'error': 'quantity doit être > 0'}, status=400)
        if item.quantity < quantity:
            return Response({'error': f'Stock insuffisant ({item.quantity} disponible)'},
                            status=400)
        mv = StockMovement.objects.create(
            item=item, movement_type='out',
            quantity=-quantity,
            reason=request.data.get('reason', 'Sortie manuelle'),
            done_by=request.data.get('done_by', request.user.username),
            ticket_id=request.data.get('ticket_id'),
        )
        return Response(StockMovementSerializer(mv).data, status=201)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset           = StockMovement.objects.select_related(
                             'item', 'ticket'
                         ).order_by('-created_at')
    serializer_class   = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['item', 'movement_type', 'ticket']
    ordering_fields    = ['created_at']
    http_method_names  = ['get', 'post', 'head', 'options']  # pas de PUT/DELETE


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vue en lecture seule pour les catégories (utilisées dans le stock).
    """
    queryset = Category.objects.annotate(asset_count=Count('assets')).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
