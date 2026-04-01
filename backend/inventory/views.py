"""
Views pour l'API CMDB Inventory
"""
import os
import tempfile
from django.views.generic import TemplateView
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
#  
from django.contrib.admin.views.decorators import staff_member_required
from scanner.models import QRCode

# backend/scanner/views.py (VERSION CORRIGÉE)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO
from scanner.models import QRCode
# qrcode et barcode
import qrcode
import barcode
from barcode.writer import ImageWriter


from .models import Category, Brand, Location, Tag, Asset, AssetMovement
from .serializers import (
    CategorySerializer, BrandSerializer, LocationSerializer,
    TagSerializer, AssetListSerializer, AssetDetailSerializer,
    AssetMovementSerializer, DashboardStatsSerializer,
)

class DashboardView(TemplateView):
    template_name = 'dashboard.html'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['type']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
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
        
        # Transformer les données plates en objets structurés
        structured_data = []
        for item in data:
            structured_data.append({
                'category': {
                    'name': item['category__name'],
                    'icon': item['category__icon']
                },
                'count': item['count']
            })
        
        # Ajouter les assets sans catégorie
        uncategorized = Asset.objects.filter(category__isnull=True).count()
        if uncategorized > 0:
            structured_data.append({
                'category': {
                    'name': 'Non catégorisé',
                    'icon': 'box'
                },
                'count': uncategorized
            })
            
        return Response({'categories': structured_data})
    
    @action(detail=False, methods=['get'], url_path='by-location')
    def by_location(self, request):
        """Répartition par emplacement."""
        data = Asset.objects.values(
            'current_location__name'
        ).annotate(count=Count('id')).order_by('-count')
        return Response({'locations': list(data)})    @action(detail=False, methods=['get'], url_path='movements')
    
    
    def movements(self, request):
        """Liste des mouvements récents (pour dashboard)."""
        movements = AssetMovement.objects.select_related(
            'asset', 'from_location', 'to_location'
        ).order_by('-moved_at')[:10]
        serializer = AssetMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='generate-code')
    def generate_code(self, request, pk=None):
        """Génère un code (QR ou barcode) pour un asset selon son type."""
        from django.contrib.auth.models import User
        import logging
        
        # Configurer le logger
        logger = logging.getLogger(__name__)
        
        asset = self.get_object()
        
        # Déterminer le type de code selon la catégorie
        category_name = asset.category.name if asset.category else ""
        
        # Règles de génération de codes
        if category_name in ['Laptop', 'Serveur', 'Switch']:
            # QR Code avec l'internal_code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(asset.internal_code)
            qr.make(fit=True)
            
            # Générer l'image QR code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Log de génération
            logger.info(f"QR Code généré pour l'asset {asset.id} ({asset.name}) par {request.user.username}")
            
            return Response({
                'type': 'qr_code',
                'data': buffer.getvalue().hex(),
                'asset_id': asset.id,
                'asset_name': asset.name,
                'category': category_name
            })
            
        elif category_name in ['Imprimante', 'NAS', 'Onduleur']:
            # QR Code avec l'internal_code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(asset.internal_code)
            qr.make(fit=True)
            
            # Générer l'image QR code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir en bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Log de génération
            logger.info(f"QR Code généré pour l'asset {asset.id} ({asset.name}) par {request.user.username}")
            
            return Response({
                'type': 'qr_code',
                'data': buffer.getvalue().hex(),
                'asset_id': asset.id,
                'asset_name': asset.name,
                'category': category_name
            })
            
        elif category_name in ['Souris', 'Clavier', 'Écran']:
            # Code-barres avec le serial_number pour les autres catégories
            # Générer le code-barres
            barcode_class = barcode.get_barcode_class('code128')
            barcode_instance = barcode_class(asset.serial_number, writer=ImageWriter())
            
            # Générer l'image
            buffer = BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)
            
            # Log de génération
            logger.info(f"Code-barres généré pour l'asset {asset.id} ({asset.name}) par {request.user.username}")
            
            return Response({
                'type': 'barcode',
                'data': buffer.getvalue().hex(),
                'asset_id': asset.id,
                'asset_name': asset.name,
                'category': category_name
            })
            
        elif category_name in ['Câble', 'Adaptateur']:
            # Code-barres avec le serial_number pour les autres catégories
            # Générer le code-barres
            barcode_class = barcode.get_barcode_class('code128')
            barcode_instance = barcode_class(asset.serial_number, writer=ImageWriter())
            
            # Générer l'image
            buffer = BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)
            
            # Log de génération
            logger.info(f"Code-barres généré pour l'asset {asset.id} ({asset.name}) par {request.user.username}")
            
            return Response({
                'type': 'barcode',
                'data': buffer.getvalue().hex(),
                'asset_id': asset.id,
                'asset_name': asset.name,
                'category': category_name
            })
            
        else:
            # Code interne pour les pièces atelier
            # Générer un code spécifique pour les pièces atelier
            if asset.category and 'pièce' in asset.category.name.lower():
                # Pour les pièces atelier, utiliser le code interne
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(asset.internal_code)
                qr.make(fit=True)
                
                # Générer l'image QR code
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convertir en bytes
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                
                # Log de génération
                logger.info(f"QR Code généré pour la pièce atelier {asset.id} ({asset.name}) par {request.user.username}")
                
                return Response({
                    'type': 'qr_code',
                    'data': buffer.getvalue().hex(),
                    'asset_id': asset.id,
                    'asset_name': asset.name,
                    'category': category_name
                })
            else:
                # Code-barres avec le serial_number pour les autres catégories
                # Générer le code-barres
                barcode_class = barcode.get_barcode_class('code128')
                barcode_instance = barcode_class(asset.serial_number, writer=ImageWriter())
                
                # Générer l'image
                buffer = BytesIO()
                barcode_instance.write(buffer)
                buffer.seek(0)
                
                # Log de génération
                logger.info(f"Code-barres généré pour l'asset {asset.id} ({asset.name}) par {request.user.username}")
                
                return Response({
                    'type': 'barcode',
                    'data': buffer.getvalue().hex(),
                    'asset_id': asset.id,
                    'asset_name': asset.name,
                    'category': category_name
                })
    


class AssetMovementViewSet(viewsets.ModelViewSet):
    queryset = AssetMovement.objects.select_related(
        'asset', 'from_location', 'to_location'
    ).order_by('-moved_at')
    serializer_class = AssetMovementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'from_location', 'to_location']
    ordering_fields = ['moved_at']
    http_method_names = ['get', 'post', 'head', 'options']  # pas de PUT/DELETE


class AssetMovementDetailView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """Détail d'un mouvement spécifique."""
        movement = get_object_or_404(AssetMovement.objects.select_related(
            'asset', 'from_location', 'to_location'
        ), pk=pk)
        serializer = AssetMovementSerializer(movement)
        return Response(serializer.data)    

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        serializer = DashboardStatsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

class DashboardStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        """Stats globales pour le dashboard."""
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
        }
        return Response(DashboardStatsSerializer(data).data)

class AssetMovementsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, pk=None):
        """Mouvements d'un asset spécifique."""
        movements = AssetMovement.objects.filter(asset_id=pk).select_related(
            'from_location', 'to_location'
        ).order_by('-moved_at')
        serializer = AssetMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
class AssetListView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Liste des assets groupés par catégorie."""
        data = Asset.objects.values(
            'category__name', 'category__icon'
        ).annotate(count=Count('id')).order_by('-count')
        return Response({'categories': list(data)})

class AssetDetailView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """Détail d'un asset spécifique."""
        asset = get_object_or_404(Asset.objects.select_related(
            'category', 'brand', 'current_location'
        ).prefetch_related('tags', 'movements'), pk=pk)
        serializer = AssetDetailSerializer(asset)
        return Response(serializer.data)
    

class AssetByLocationView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Répartition des assets par emplacement."""
        data = Asset.objects.values(
            'current_location__name'
        ).annotate(count=Count('id')).order_by('-count')
        return Response({'locations': list(data)})  
    
class AssetMovementsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, pk=None):
        """Mouvements d'un asset spécifique."""
        movements = AssetMovement.objects.filter(asset_id=pk).select_related(
            'from_location', 'to_location'
        ).order_by('-moved_at')
        serializer = AssetMovementSerializer(movements, many=True)
        return Response(serializer.data)
    def pageinate_queryset(self, queryset):
        """Désactiver la pagination pour cette vue."""
        return None
    def get_paginated_response(self, data):
        """Désactiver la pagination pour cette vue."""
        return Response(data)
    

# Vues fonctionnelles pour les graphiques du dashboard (exemples) #
#--- Ces vues peuvent être utilisées pour alimenter des graphiques spécifiques sur le dashboard ---#
class CurrentUserView(APIView):
    """
    Renvoie les informations de l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return Response(data)

## Vues fonctionnelles pour les graphiques du dashboard (exemples) ##
##--- Ces vues peuvent être utilisées pour alimenter des graphiques spécifiques sur le dashboard ##---
def by_location(request):
    """Vue fonctionnelle pour la répartition des assets par emplacement."""
    data = Asset.objects.values(
        'current_location__name'
    ).annotate(count=Count('id')).order_by('-count')
    return Response(data)   

def by_category(request):
    """Vue fonctionnelle pour la répartition des assets par catégorie."""
    data = Asset.objects.values(
        'category__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Ajouter les assets sans catégorie
    uncategorized = Asset.objects.filter(category__isnull=True).count()
    if uncategorized > 0:
        data = list(data)
        data.append({
            'category__name': 'Non catégorisé',
            'count': uncategorized
        })
        
    return Response(data)


# Vues admin pour QR code et impression


   