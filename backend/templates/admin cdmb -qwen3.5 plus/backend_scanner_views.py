# scanner/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from inventory.models import Asset
from maintenance.models import Ticket

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