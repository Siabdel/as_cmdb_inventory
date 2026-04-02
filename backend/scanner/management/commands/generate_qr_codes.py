# backend/scanner/management/commands/generate_qr_codes.py
from django.core.management.base import BaseCommand
from scanner.signals import generate_missing_qr_codes, regenerate_all_qr_codes


class Command(BaseCommand):
    """ Commande personnalisée pour générer les QR Codes manquants ou régénérer tous les QR Codes.
    Usage:
    - Générer les QR Codes manquants: `python manage.py generate_qr_codes`
    - Régénérer tous les QR Codes: `python manage.py generate_qr_codes --all`
    - Mode dry-run (affiche ce qui serait fait sans exécuter): `python manage.py generate_qr_codes --dry-run`
    """
    
    help = 'Génère les QR Codes manquants ou régénère tous les QR Codes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Régénérer TOUS les QR Codes (pas seulement manquants)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait fait sans exécuter'
        )
    
    def handle(self, *args, **options):
        if options['all']:
            self.stdout.write('⚠️  Régénération de TOUS les QR Codes...')
            
            if options['dry_run']:
                count = Asset.objects.count()
                self.stdout.write(f'📊 {count} assets seraient traités')
                return
            
            result = regenerate_all_qr_codes()
        else:
            self.stdout.write('🔍 Recherche QR Codes manquants...')
            
            if options['dry_run']:
                count = Asset.objects.filter(qrcode__isnull=True).count()
                self.stdout.write(f'📊 {count} QR Codes seraient générés')
                return
            
            result = generate_missing_qr_codes()
        
        self.stdout.write(self.style.SUCCESS(f'''
✅ Terminé!
   Total: {result['total']}
   Succès: {result['success']}
   Échecs: {result['failed']}
   Timestamp: {result['timestamp']}
'''))