
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, decorators
from django.conf import settings
from django.utils import timezone
import logging
import time
from .serializers import PrintLabelSerializer
from ..services.factory import PrinterFactory
from ..utils.usb_permissions import check_usb_permissions
from printer.models import PrintTemplate, Printer, PrintJob, PrintLog
from printer.api.serializers import (
    PrintTemplateSerializer,
    PrinterSerializer,
    PrintJobSerializer,
    PrintLogSerializer
)
from scanner.services.pdf_generator import generate_label_pdf
from inventory.models import Asset
from rest_framework.views import APIView
##
from django.shortcuts import get_object_or_404

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


class PrinterViewSet__(viewsets.ModelViewSet):
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

class PrintLabelViewSet(viewsets.GenericViewSet):
    """
    ViewSet pour l'impression d'étiquettes CMDB
    
    Endpoints:
    - POST /api/printer/labels/ : Imprimer une étiquette
    - GET  /api/printer/labels/status/ : État de l'imprimante
    """
    
    serializer_class = PrintLabelSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Endpoint principal: Imprimer une ou plusieurs étiquettes
        
        Algorithme:
        1. Valider les données entrantes
        2. Auto-générer qr_content/barcode_content si vides
        3. Vérifier les permissions USB
        4. Connecter à l'imprimante via USB
        5. Boucle d'impression pour copies multiples
        6. Enregistrer dans l'historique (PrintJob)
        7. Retourner la réponse JSON
        """
        
        # 1. Validation serializer (auto-génération incluse)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        asset_id = data['asset_id']
        copies = data.get('copies', 1)
        
        logger.info(f"Demande impression asset {asset_id} par {request.user}")
        
        # 2. Créer un PrintJob pour l'historique
        print_job = PrintJob.objects.create(
            asset_id=asset_id,
            user=request.user,
            copies=copies,
            status='pending'
        )
        
        # 3. Vérification permissions USB
        usb_check = check_usb_permissions()
        if not usb_check.get('ok'):
            logger.warning(f"Permissions USB: {usb_check.get('message')}")
        
        try:
            # 4. Instancier l'imprimante via Factory
            printer = PrinterFactory.create(
                model=data.get('printer_model', 'bixolon_srp350')
            )
            
            # 5. Connexion USB
            if not printer.connect(max_retries=2):
                print_job.status = 'failed'
                print_job.error_message = 'Imprimante non connectée'
                print_job.save()
                
                return Response(
                    {'status': 'error', 'message': 'Imprimante non connectée'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # 6. Boucle d'impression (copies multiples)
            printed = 0
            for i in range(copies):
                success = printer.print_cmdb_label(
                    asset_id=asset_id,
                    qr_data=data.get('qr_content'),      # ← Auto-généré
                    barcode_data=data.get('barcode_content'),  # ← Auto-généré
                    custom_text=data.get('custom_text')
                )
                
                if success:
                    printed += 1
                    logger.debug(f"Copie {i+1}/{copies} imprimée")
                else:
                    logger.error(f"Échec copie {i+1}/{copies}")
                    break
                
                # Pause entre copies (mécanique de coupe)
                if i < copies - 1:
                    time.sleep(0.8)
            
            printer.close()
            
            # 7. Mettre à jour PrintJob
            if printed > 0:
                print_job.status = 'success'
                print_job.save()
                
                logger.info(f"✅ {printed}/{copies} étiquette(s) imprimée(s)")
                
                return Response({
                    'status': 'success',
                    'message': f"{printed} étiquette(s) imprimée(s)",
                    'data': {
                        'asset_id': asset_id,
                        'qr_content': data.get('qr_content'),
                        'barcode_content': data.get('barcode_content'),
                        'printed_copies': printed,
                        'printed_at': timezone.now().isoformat()
                    }
                }, status=status.HTTP_200_OK)
            else:
                print_job.status = 'failed'
                print_job.error_message = 'Échec complet'
                print_job.save()
                
                return Response(
                    {'status': 'error', 'message': 'Échec d\'impression'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.exception(f"Erreur critique: {e}")
            print_job.status = 'failed'
            print_job.error_message = str(e)
            print_job.save()
            
            return Response(
                {'status': 'error', 'message': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='status')
    def printer_status(self, request):
        """Endpoint de diagnostic: état imprimante + USB"""
        usb_info = check_usb_permissions()
        
        return Response({
            'printer': {
                'status': 'online' if usb_info.get('device_found') else 'offline',
                'model': 'bixolon_srp350',
                'usb': usb_info
            },
            'permissions': {
                'user_groups': usb_info.get('groups', []),
                'udev_ok': usb_info.get('udev_ok', False)
            }
        }, status=status.HTTP_200_OK)
    

class PrinterViewSet(viewsets.ModelViewSet):
    """
    CRUD Imprimantes thermiques.
    
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
    
    @decorators.action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Tester l'imprimante avec une étiquette test.
        
        POST /api/v1/scanner/printers/<id>/test/
        """
        printer = self.get_object()
        
        try:
            # Générer PDF test
            from io import BytesIO
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import mm
            
            buffer = BytesIO()
            width = printer.paper_width_mm * mm
            height = printer.paper_height_mm * mm
            
            p = canvas.Canvas(buffer, pagesize=(width, height))
            p.setFont("Helvetica-Bold", 12)
            p.drawString(10*mm, height-20*mm, "TEST IMPRESSION")
            p.setFont("Helvetica", 10)
            p.drawString(10*mm, height-30*mm, f"Imprimante: {printer.name}")
            p.drawString(10*mm, height-40*mm, f"Date: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
            p.drawString(10*mm, height-50*mm, f"Connexion: {printer.get_connection_type_display()}")
            p.showPage()
            p.save()
            
            buffer.seek(0)
            
            # Retourner PDF pour impression navigateur
            response = HttpResponse(buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="test_print.pdf"'
            
            printer.last_used_at = timezone.now()
            printer.save(update_fields=['last_used_at'])
            
            logger.info(f"Test impression réussi: {printer.name}")
            return response
            
        except Exception as e:
            logger.error(f"Erreur test impression: {str(e)}")
            return Response(
                {'error': f'Échec test: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CodePrintView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, asset_id):
        """Renvoie les codes pour impression."""
        try:
            asset = Asset.objects.get(id=asset_id)
            
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
                
                return Response({
                    'type': 'barcode',
                    'data': buffer.getvalue().hex(),
                    'asset_id': asset.id,
                    'asset_name': asset.name,
                    'category': category_name
                })
                
        except Asset.DoesNotExist:
            return Response({'error': 'Asset introuvable'}, status=404)

