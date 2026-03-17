from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
import json

from .models import Asset, AssetScan
from .serializers import (
    AssetSerializer, AssetScanSerializer, AssetCreateSerializer,
    ScanCreateSerializer, AssetHistorySerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des assets.
    """
    queryset = Asset.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        Utilise un serializer différent pour la création.
        """
        if self.action == 'create':
            return AssetCreateSerializer
        return AssetSerializer

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """
        Retourne l'historique des scans d'un asset.
        GET /api/assets/<id>/history/
        """
        asset = self.get_object()
        serializer = AssetHistorySerializer(asset, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='print-label')
    def print_label(self, request, pk=None):
        """
        Génère un PDF étiquette pour l'asset.
        POST /api/assets/<id>/print-label/
        """
        asset = self.get_object()
        
        # Ici, vous pouvez intégrer la génération PDF avec reportlab
        # ou l'envoi direct à l'imprimante thermique
        
        # Pour l'instant, retournons une réponse simple
        return Response({
            'message': f'Étiquette générée pour {asset.name}',
            'asset_id': str(asset.id),
            'code': asset.code,
            'print_job_id': 'simulated_123'
        })

    @action(detail=False, methods=['get'], url_path='by-code/(?P<code>[^/.]+)')
    def by_code(self, request, code=None):
        """
        Récupère un asset par son code.
        GET /api/assets/by-code/<code>/
        """
        asset = get_object_or_404(Asset, code=code)
        serializer = self.get_serializer(asset, context={'request': request})
        return Response(serializer.data)


class AssetScanViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des scans d'assets.
    """
    queryset = AssetScan.objects.all()
    serializer_class = AssetScanSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Filtre optionnel par asset_id.
        """
        queryset = super().get_queryset()
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        return queryset


class ScanAPIView(generics.CreateAPIView):
    """
    API pour enregistrer un scan via code d'asset.
    POST /api/scans/
    """
    serializer_class = ScanCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        scan = serializer.save()
        
        # Retourner les détails du scan créé
        scan_serializer = AssetScanSerializer(scan, context={'request': request})
        
        return Response({
            'message': 'Scan enregistré avec succès',
            'scan': scan_serializer.data,
            'asset': {
                'id': str(scan.asset.id),
                'name': scan.asset.name,
                'code': scan.asset.code,
                'location': scan.asset.location
            }
        }, status=status.HTTP_201_CREATED)


class AssetQRCodeView(generics.RetrieveAPIView):
    """
    Retourne l'image du QR code d'un asset.
    GET /api/assets/<id>/qrcode/
    """
    queryset = Asset.objects.all()
    
    def get(self, request, *args, **kwargs):
        asset = self.get_object()
        if asset.qr_code:
            return FileResponse(asset.qr_code.open(), content_type='image/png')
        return Response(
            {'error': 'QR code non disponible'},
            status=status.HTTP_404_NOT_FOUND
        )


class AssetBarcodeView(generics.RetrieveAPIView):
    """
    Retourne l'image du code-barres d'un asset.
    GET /api/assets/<id>/barcode/
    """
    queryset = Asset.objects.all()
    
    def get(self, request, *args, **kwargs):
        asset = self.get_object()
        if asset.barcode:
            return FileResponse(asset.barcode.open(), content_type='image/png')
        return Response(
            {'error': 'Code-barres non disponible'},
            status=status.HTTP_404_NOT_FOUND
        )