# backend/scanner/api/views.py
# backend/scanner/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from scanner.services.printer_service import PrinterService
from scanner.services.pdf_generator import generate_label_pdf
from inventory.models import Asset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def print_to_printer(request, asset_id):
    """
    Imprimer étiquette directement sur imprimante configurée.
    
    POST /api/v1/scanner/print-to/<asset_id>/
    Body: {
        "copies": 1,
        "printer_name": "MUNBYN_RW403B"
    }
    """
    try:
        asset = Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset introuvable'}, status=404)
    
    copies = request.data.get('copies', 1)
    printer_name = request.data.get('printer_name', 'MUNBYN_RW403B')
    
    # Générer PDF
    pdf_buffer = generate_label_pdf([asset], format='50x30', copies=copies)
    
    # Imprimer via CUPS
    printer = PrinterService(printer_name)
    success = printer.print_pdf_buffer(pdf_buffer, copies=1)
    
    if success:
        # Enregistrer PrintLog
        from scanner.models import PrintLog
        PrintLog.objects.create(
            asset=asset,
            printed_by=request.user,
            printer_name=printer_name,
            template_name='Standard 50x30',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return Response({'status': 'ok', 'message': 'Impression lancée'})
    else:
        return Response({'status': 'error', 'message': 'Échec impression'}, status=500)