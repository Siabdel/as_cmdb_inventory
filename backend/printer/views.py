from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status, decorators
from rest_framework.permissions import IsAuthenticated
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from inventory.models import Asset
from django.shortcuts import render, get_object_or_404
from printer.models import PrintTemplate, Printer, PrintJob, PrintLog

# backend/printer/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
import tempfile
import os


def generate_label_pdf(asset, output_path=None):
    """
    Génère un PDF d'étiquette pour un asset — VERSION VALIDÉE ✅.
    
    Args:
        asset (Asset): Instance de l'asset
        output_path (str, optional): Chemin de sortie du PDF
    
    Returns:
        str: Chemin du fichier PDF généré
    """
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        output_path = temp_file.name
        temp_file.close()
    
    # Créer le canvas PDF (3×2 pouces = 76×50mm)
    c = canvas.Canvas(output_path, pagesize=(3 * inch, 2 * inch))
    width, height = 3 * inch, 2 * inch
    
    # Titre
    c.setFont("Helvetica-Bold", 10)
    c.drawString(10, height - 20, f"ASSET: {asset.name}")
    
    # Code
    c.setFont("Helvetica", 9)
    c.drawString(10, height - 40, f"Code: {asset.internal_code}")
    
    # Localisation
    if asset.current_location:
        c.drawString(10, height - 55, f"Localisation: {asset.current_location}")
    
    # Date de création
    created_str = asset.created_at.strftime("%d/%m/%Y")
    c.drawString(10, height - 70, f"Créé le: {created_str}")
    
    # QR Code (IMAGE PNG — C'EST ÇA QUI MARCHE ✅)
    if hasattr(asset, 'qrcode') and asset.qrcode and asset.qrcode.image:
        try:
            qr_path = asset.qrcode.image.path
            if os.path.exists(qr_path):
                qr_img = ImageReader(qr_path)
                c.drawImage(qr_img, width - 80, height - 80, width=70, height=70)
        except (ValueError, OSError) as e:
            print(f"⚠️ Erreur QR Code: {e}")
    
    # Footer
    c.setFont("Helvetica-Oblique", 6)
    c.drawString(10, 5, f"CMDB Inventory - Asset ID: {asset.id}")
    
    c.save()
    
    return output_path


def print_label_pdf_view(request, asset_id):
    """
    Génère et retourne PDF pour impression — ENDPOINT VALIDÉ ✅.
    
    URL: /django-admin/inventory/asset/<id>/print_label/
    """
    from inventory.models import Asset
    
    asset = get_object_or_404(Asset, id=asset_id)
    pdf_path = generate_label_pdf(asset)
    
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="label_{asset.id}.pdf"'
        
        # Nettoyage fichier temporaire
        try:
            os.unlink(pdf_path)
        except:
            pass
        
        return response


@decorators.permission_classes([IsAuthenticated])
def print_labels(request):
    """
    Impression batch d'étiquettes.
    
    POST /api/v1/scanner/print-labels/
    Body:
    {
        "asset_ids": [152, 153, 154],
        "printer_id": 1,
        "template_id": 1,
        "copies": 1
    }
    """
    asset_ids = request.data.get('asset_ids', [])
    printer_id = request.data.get('printer_id')
    template_id = request.data.get('template_id')
    copies = request.data.get('copies', 1)
    
    if not asset_ids:
        return Response({'error': 'asset_ids requis'}, status=400)
    
    # Récupérer assets
    assets = Asset.objects.filter(id__in=asset_ids)
    if not assets.exists():
        return Response({'error': 'Aucun asset trouvé'}, status=404)
    
    # Template
    template = None
    if template_id:
        template = get_object_or_404(PrintTemplate, id=template_id)
    else:
        template = PrintTemplate.objects.filter(is_default=True).first()
    
    # Printer
    printer = None
    if printer_id:
        printer = get_object_or_404(Printer, id=printer_id)
    
    # Générer PDF
    try:
        pdf_buffer = generate_label_pdf(assets, template, printer, copies)
        
        # Créer PrintJob pour audit
        job = PrintJob.objects.create(
            created_by=request.user,
            asset_ids=asset_ids,
            template=template,
            printer=printer,
            copies=copies,
            status='completed'
        )
        
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="labels_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        logger.info(f"Impression batch: {len(asset_ids)} assets, Printer: {printer.name if printer else 'N/A'}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur impression batch: {str(e)}")
        return Response({'error': str(e)}, status=500)

    ##Response['Content-Disposition'] = f'attachment; filename="qr_asset_{asset.internal_code}.png"'
    ##return Response
    # ============================================================================
# PRINT MANAGEMENT VIEWS
# ============================================================================

@login_required
def print_labels_view(request):
    """
    Page d'impression d'étiquettes.
    URL: /admin/scanner/print/
    
    Permet de:
    - Sélectionner des assets
    - Choisir template et imprimante
    - Générer et imprimer PDF batch
    """
    # Récupérer templates
    templates = PrintTemplate.objects.filter(is_active=True)
    
    # Récupérer imprimantes
    printers = Printer.objects.filter(is_active=True)
    
    # Assets sélectionnés (depuis URL params)
    asset_ids = request.GET.get('assets', '')
    if asset_ids:
        asset_ids = [int(id) for id in asset_ids.split(',')]
        selected_assets = Asset.objects.filter(id__in=asset_ids)
    else:
        selected_assets = Asset.objects.none()
    
    context = {
        'templates': templates,
        'printers': printers,
        'selected_assets': selected_assets,
        'asset_ids': asset_ids,
    }
    
    return render(request, 'admin/scanner/print.html', context)


@login_required
def print_templates_view(request):
    """
    Gestion des templates d'étiquettes.
    URL: /admin/scanner/templates/
    """
    templates = PrintTemplate.objects.all()
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'admin/scanner/templates.html', context)


@login_required
def printers_view(request):
    """
    Gestion des imprimantes.
    URL: /admin/scanner/printers/
    """
    printers = Printer.objects.all()
    
    context = {
        'printers': printers,
    }
    
    return render(request, 'admin/scanner/printers.html', context)


@login_required
def print_jobs_view(request):
    """
    Historique des jobs d'impression.
    URL: /admin/scanner/jobs/
    """
    jobs = PrintJob.objects.select_related(
        'created_by', 'template', 'printer'
    ).order_by('-created_at')[:50]
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'admin/scanner/jobs.html', context)

@login_required
def print_logs_view(request):
    """
    Logs d'audit d'impression.
    URL: /admin/scanner/logs/
    """
    logs = PrintLog.objects.select_related(
        'asset', 'printed_by', 'job'
    ).order_by('-printed_at')[:100]
    
    # Filtres
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    asset_id = request.GET.get('asset_id')
    user_id = request.GET.get('user_id')
    
    if date_from:
        logs = logs.filter(printed_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(printed_at__date__lte=date_to)
    if asset_id:
        logs = logs.filter(asset_id=asset_id)
    if user_id:
        logs = logs.filter(printed_by_id=user_id)
    
    context = {
        'logs': logs,
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'asset_id': asset_id,
            'user_id': user_id,
        }
    }
    
    return render(request, 'admin/scanner/logs.html', context)