# backend/scanner/api/views.py
from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from scanner.models import PrintTemplate, Printer, PrintJob, PrintLog
from scanner.api.serializers import (
    PrintTemplateSerializer,
    PrinterSerializer,
    PrintJobSerializer,
    PrintLogSerializer
)
from scanner.services.pdf_generator import generate_label_pdf
from inventory.models import Asset
import logging

logger = logging.getLogger(__name__)


class PrintTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD Templates d'étiquettes.
    
    list: GET /api/v1/scanner/templates/
    create: POST /api/v1/scanner/templates/
    retrieve: GET /api/v1/scanner/templates/<id>/
    update: PUT /api/v1/scanner/templates/<id>/
    destroy: DELETE /api/v1/scanner/templates/<id>/
    """
    queryset = PrintTemplate.objects.all()
    serializer_class = PrintTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PrintTemplate.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class PrinterViewSet(viewsets.ModelViewSet):
    """
    CRUD Imprimantes.
    
    list: GET /api/v1/scanner/printers/
    create: POST /api/v1/scanner/printers/
    retrieve: GET /api/v1/scanner/printers/<id>/
    update: PUT /api/v1/scanner/printers/<id>/
    destroy: DELETE /api/v1/scanner/printers/<id>/
    test: POST /api/v1/scanner/printers/<id>/test/
    """
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Printer.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
    @decorators.action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Tester l'imprimante avec une étiquette test."""
        printer = self.get_object()
        
        # Créer un asset test temporaire ou utiliser un asset existant
        test_asset = Asset.objects.first()
        if not test_asset:
            return Response(
                {'error': 'Aucun asset disponible pour le test'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from scanner.services.pdf_generator import generate_label_pdf
            pdf_buffer = generate_label_pdf([test_asset], format='50x30', copies=1)
            
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="test_print.pdf"'
            
            printer.last_used_at = timezone.now()
            printer.save(update_fields=['last_used_at'])
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur test impression: {str(e)}")
            return Response(
                {'error': f'Échec test: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PrintJobViewSet(viewsets.ModelViewSet):
    """
    Gestion des jobs d'impression.
    
    list: GET /api/v1/scanner/print-jobs/
    create: POST /api/v1/scanner/print-jobs/
    retrieve: GET /api/v1/scanner/print-jobs/<id>/
    download: GET /api/v1/scanner/print-jobs/<id>/download/
    cancel: POST /api/v1/scanner/print-jobs/<id>/cancel/
    """
    queryset = PrintJob.objects.all()
    serializer_class = PrintJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PrintJob.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    @decorators.action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharger le PDF du PrintJob."""
        job = self.get_object()
        
        if job.status != 'completed':
            return Response(
                {'error': 'Job non terminé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not job.pdf_file:
            return Response(
                {'error': 'PDF non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(job.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="labels_{job.uuid}.pdf"'
        return response
    
    @decorators.action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler un PrintJob."""
        job = self.get_object()
        
        if job.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Job déjà terminé ou annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'cancelled'
        job.save()
        
        return Response({'status': 'cancelled'})
    
    @decorators.action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Générer un nouveau PrintJob.
        
        POST /api/v1/scanner/print-jobs/generate/
        Body:
        {
            "asset_ids": [152, 153, 154],
            "template_id": 1,
            "printer_id": 1,
            "copies": 1,
            "async": true
        }
        """
        asset_ids = request.data.get('asset_ids', [])
        template_id = request.data.get('template_id')
        printer_id = request.data.get('printer_id')
        copies = request.data.get('copies', 1)
        use_async = request.data.get('async', True)
        
        if not asset_ids:
            return Response(
                {'error': 'asset_ids requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Valider assets
        assets = Asset.objects.filter(id__in=asset_ids)
        if len(assets) != len(asset_ids):
            return Response(
                {'error': 'Certains assets n\'existent pas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        
        # Créer PrintJob
        job = PrintJob.objects.create(
            created_by=request.user,
            asset_ids=asset_ids,
            template=template,
            printer=printer,
            copies=copies,
            status='pending'
        )
        
        if use_async:
            # Async avec Celery
            from scanner.tasks import generate_print_job_pdf
            generate_print_job_pdf.delay(job.id)
            return Response({
                'status': 'pending',
                'job_id': job.id,
                'uuid': str(job.uuid),
                'message': 'Job en cours de traitement'
            })
        else:
            # Sync
            pdf_buffer = generate_label_pdf(assets, template, printer, copies)
            
            from django.core.files.base import ContentFile
            filename = f"print_jobs/{timezone.now().strftime('%Y/%m')}/job_{job.uuid}.pdf"
            job.pdf_file.save(filename, ContentFile(pdf_buffer.getvalue()), save=True)
            
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
            return Response({
                'status': 'completed',
                'job_id': job.id,
                'uuid': str(job.uuid),
                'pdf_url': job.pdf_file.url
            })


class PrintLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Logs d'impression (lecture seule).
    
    list: GET /api/v1/scanner/print-logs/
    retrieve: GET /api/v1/scanner/print-logs/<id>/
    """
    queryset = PrintLog.objects.all()
    serializer_class = PrintLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PrintLog.objects.all()
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        asset_id = self.request.query_params.get('asset_id', None)
        
        if date_from:
            queryset = queryset.filter(printed_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(printed_at__date__lte=date_to)
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        return queryset.select_related('asset', 'printed_by', 'job').order_by('-printed_at')