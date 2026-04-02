
# backend/scanner/services/printer_service.py
import subprocess
import logging
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)


class PrinterService:
    """Service d'impression via CUPS pour Django."""
    
    def __init__(self, printer_name='MUNBYN_RW403B'):
        self.printer_name = printer_name
    
    def print_pdf(self, pdf_path, copies=1, options=None):
        """
        Imprimer un PDF via CUPS.
        
        Args:
            pdf_path: Chemin du fichier PDF
            copies: Nombre de copies
            options: Dict options CUPS
        
        Returns:
            bool: True si succès
        """
        cmd = ['lp', '-d', self.printer_name, '-n', str(copies)]
        
        if options:
            for key, value in options.items():
                cmd.extend(['-o', f'{key}={value}'])
        
        cmd.append(pdf_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Impression réussie: {pdf_path}")
                return True
            else:
                logger.error(f"Erreur impression: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout impression")
            return False
        except Exception as e:
            logger.error(f"Exception impression: {str(e)}")
            return False
    
    def print_pdf_buffer(self, pdf_buffer, copies=1, options=None):
        """
        Imprimer depuis buffer PDF en mémoire.
        
        Args:
            pdf_buffer: BytesIO buffer PDF
            copies: Nombre de copies
            options: Dict options CUPS
        
        Returns:
            bool: True si succès
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_buffer.getvalue())
            tmp_path = tmp.name
        
        try:
            success = self.print_pdf(tmp_path, copies, options)
            Path(tmp_path).unlink()  # Cleanup
            return success
        except Exception as e:
            logger.error(f"Erreur cleanup: {str(e)}")
            return False
    
    def get_printer_status(self):
        """Vérifier statut imprimante."""
        cmd = ['lpstat', '-p', self.printer_name, '-l']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return {
                'available': 'idle' in result.stdout.lower(),
                'status': result.stdout.strip()
            }
        except Exception as e:
            return {
                'available': False,
                'status': f'Error: {str(e)}'
            }
    
    def get_queue(self):
        """Récupérer jobs en attente."""
        cmd = ['lpstat', '-o', self.printer_name]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            jobs = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        jobs.append({
                            'job_id': parts[1],
                            'user': parts[2],
                            'size': parts[3] if len(parts) > 3 else 'N/A'
                        })
            return jobs
        except Exception as e:
            return []
    
    def cancel_job(self, job_id):
        """Annuler un job d'impression."""
        cmd = ['cancel', job_id]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Erreur annulation: {str(e)}")
            return False


# Usage dans une view Django
def print_label_view(request, asset_id):
    from scanner.services.pdf_generator import generate_label_pdf
    from scanner.services.printer_service import PrinterService
    
    asset = get_object_or_404(Asset, id=asset_id)
    pdf_buffer = generate_label_pdf([asset], format='50x30')
    
    printer = PrinterService('MUNBYN_RW403B')
    success = printer.print_pdf_buffer(pdf_buffer, copies=1)
    
    if success:
        return JsonResponse({'status': 'ok', 'message': 'Impression lancée'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Échec impression'}, status=500)