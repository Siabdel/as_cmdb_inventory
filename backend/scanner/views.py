from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import QRCode, ScanLog, ScannedAsset, ScanResult
from inventory.serializers import AssetDetailSerializer
# scanner/views.py
from inventory.models import Asset
from maintenance.models import MaintenanceTicket as Ticket


@api_view(['GET'])
@permission_classes([AllowAny])  # public — accès sans auth
def resolve_qr(request, uuid_token):
    """
    Endpoint scanné par mobile.
    Enregistre le ScanLog et retourne la fiche asset complète.
    """
    try:
        qr_obj = QRCode.objects.select_related('asset').get(uuid_token=uuid_token)
    except QRCode.DoesNotExist:
        # Si ce n'est pas un QR code valide, vérifier si c'est un code à barres
        from inventory.models import Asset
        try:
            # Essayer de trouver l'asset par son numéro de série
            asset = Asset.objects.get(serial_number=uuid_token)
            # Créer un QR code pour cet asset s'il n'existe pas
            qr_obj, created = QRCode.objects.get_or_create(asset=asset)
            if created:
                # Générer l'image QR code si nécessaire
                from scanner.signals import _generate_qr_image
                _generate_qr_image(qr_obj)
        except Asset.DoesNotExist:
            # Essayer de trouver l'asset par son code interne
            try:
                asset = Asset.objects.get(internal_code=uuid_token)
                # Créer un QR code pour cet asset s'il n'existe pas
                qr_obj, created = QRCode.objects.get_or_create(asset=asset)
                if created:
                    # Générer l'image QR code si nécessaire
                    from scanner.signals import _generate_qr_image
                    _generate_qr_image(qr_obj)
            except Asset.DoesNotExist:
                return Response({'error': 'Code scanné invalide.'}, status=status.HTTP_404_NOT_FOUND)

    # Enregistrer le scan
    scan_log = ScanLog.objects.create(
        qrcode=qr_obj,
        scanned_by=request.query_params.get('user', ''),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )

    # Créer l'asset scanné
    scanned_asset, created = ScannedAsset.objects.get_or_create(
        asset=qr_obj.asset,
        qrcode=qr_obj,
        scan_log=scan_log
    )

    # Enregistrer les résultats détaillés du scan
    scan_result, created = ScanResult.objects.get_or_create(
        scanned_asset=scanned_asset,
        key='scan_result',
        defaults={
            'value': 'Scan réussi',
            'notes': f'Scan effectué via {request.META.get("HTTP_USER_AGENT", "inconnu")}'
        }
    )

    # Incrémenter le compteur
    QRCode.objects.filter(pk=qr_obj.pk).update(
        scanned_count=qr_obj.scanned_count + 1,
        last_scanned_at=timezone.now()
    )

    return Response(AssetDetailSerializer(qr_obj.asset).data)


@api_view(['POST'])
def regenerate_qr(request, asset_id):
    """Force la régénération du QR code d'un asset."""
    from inventory.models import Asset
    from scanner.signals import _generate_qr_image

    try:
        asset = Asset.objects.get(pk=asset_id)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset introuvable.'}, status=404)

    qr_obj, _ = QRCode.objects.get_or_create(asset=asset)
    _generate_qr_image(qr_obj)

    return Response({
        'uuid': str(qr_obj.uuid_token),
        'url': qr_obj.url,
        'image': request.build_absolute_uri(qr_obj.image.url) if qr_obj.image else None,
    })


def public_scan_result(request, uuid):
    """Page publique de résultat de scan - sans authentification"""
    # Résoudre l'UUID vers l'asset
    asset = get_object_or_404(Asset, qr_uuid=uuid)
    
    # Enregistrer le scan (optionnel, pour stats)
    # ScanLog.objects.create(asset=asset, scanned_by='public', scanned_at=timezone.now())
    
    # Tickets ouverts liés
    open_tickets = Ticket.objects.filter(asset=asset, status__in=['open', 'assigned', 'in_progress'])
    
    context = {
        'asset': asset,
        'open_tickets': open_tickets,
        'scan_date': timezone.now()
    }
    return render(request, 'public/scan_result.html', context)