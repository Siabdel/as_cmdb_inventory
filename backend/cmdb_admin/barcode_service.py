"""
Service de génération de QR codes, code-barres et impression d'étiquettes.
"""

import os
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, inch
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import tempfile


def generate_qrcode_image(data, size=10, border=4):
    """
    Génère une image QR code à partir des données fournies.
    
    Args:
        data (str): Données à encoder dans le QR code
        size (int): Taille des boîtes du QR code
        border (int): Taille de la bordure
    
    Returns:
        BytesIO: Buffer contenant l'image PNG
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        logger.debug(f"QR code généré avec succès pour les données: {data}")
        return buffer
    except Exception as e:
        logger.error(f"Erreur lors de la génération du QR code: {e}")
        raise


def generate_barcode_image(data, writer_options=None):
    """
    Génère une image de code-barres Code128.
    
    Args:
        data (str): Données à encoder
        writer_options (dict): Options pour le writer d'image
    
    Returns:
        BytesIO: Buffer contenant l'image PNG
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if writer_options is None:
        writer_options = {
            'module_height': 15.0,
            'font_size': 10,
            'text_distance': 5.0,
            'quiet_zone': 6.5,
        }
    
    try:
        barcode = Code128(data, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer, writer_options)
        buffer.seek(0)
        
        logger.debug(f"Code-barres généré avec succès pour les données: {data}")
        return buffer
    except Exception as e:
        logger.error(f"Erreur lors de la génération du code-barres: {e}")
        raise


def save_qrcode_to_asset(asset, data=None):
    """
    Génère et sauvegarde un QR code pour un asset.
    
    Args:
        asset (Asset): Instance de l'asset
        data (str, optional): Données à encoder. Par défaut utilise asset.code
    
    Returns:
        str: Chemin du fichier sauvegardé
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if data is None:
        data = asset.code
    
    try:
        buffer = generate_qrcode_image(data)
        
        filename = f'asset_{asset.id}_qrcode.png'
        file_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', filename)
        
        # Vérifier que le dossier de destination existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Sauvegarder le fichier
        asset.qr_code.save(filename, File(buffer), save=False)
        
        # Sauvegarder l'asset pour enregistrer le QR code
        asset.save(update_fields=['qr_code'])
        
        logger.info(f"QR code sauvegardé avec succès pour l'asset {asset.id}")
        return file_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du QR code pour l'asset {asset.id}: {e}")
        raise


def save_barcode_to_asset(asset, data=None):
    """
    Génère et sauvegarde un code-barres pour un asset.
    
    Args:
        asset (Asset): Instance de l'asset
        data (str, optional): Données à encoder. Par défaut utilise asset.code
    
    Returns:
        str: Chemin du fichier sauvegardé
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if data is None:
        data = asset.code
    
    try:
        buffer = generate_barcode_image(data)
        
        filename = f'asset_{asset.id}_barcode.png'
        file_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', filename)
        
        # Vérifier que le dossier de destination existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Sauvegarder le fichier
        asset.barcode.save(filename, File(buffer), save=False)
        
        # Sauvegarder l'asset pour enregistrer le code-barres
        asset.save(update_fields=['barcode'])
        
        logger.info(f"Code-barres sauvegardé avec succès pour l'asset {asset.id}")
        return file_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du code-barres pour l'asset {asset.id}: {e}")
        raise


def generate_label_pdf(asset, output_path=None):
    """
    Génère un PDF d'étiquette pour un asset.
    
    Args:
        asset (Asset): Instance de l'asset
        output_path (str, optional): Chemin de sortie du PDF. Si None, crée un fichier temporaire.
    
    Returns:
        str: Chemin du fichier PDF généré
    """
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        output_path = temp_file.name
    
    # Créer le canvas PDF
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
    
    # QR Code (si disponible)
    if hasattr(asset, 'qrcode') and asset.qrcode and asset.qrcode.image:
        try:
            qr_path = asset.qrcode.image.path
            if os.path.exists(qr_path):
                qr_img = ImageReader(qr_path)
                c.drawImage(qr_img, width - 80, height - 80, width=70, height=70)
        except (ValueError, OSError):
            pass
    
    # Code-barres (si disponible)
    if hasattr(asset, 'barcode') and asset.barcode:
        try:
            barcode_path = asset.barcode.path
            if os.path.exists(barcode_path):
                barcode_img = ImageReader(barcode_path)
                c.drawImage(barcode_img, 10, 10, width=width - 20, height=30)
        except (ValueError, OSError):
            pass
    
    # Footer
    c.setFont("Helvetica-Oblique", 6)
    c.drawString(10, 5, f"CMDB Inventory - Asset ID: {asset.id}")
    
    c.save()
    
    return output_path


def print_to_thermal_printer(asset, printer_type='escpos'):
    """
    Envoie une commande d'impression à une imprimante thermique.
    
    Args:
        asset (Asset): Instance de l'asset
        printer_type (str): Type d'imprimante ('escpos', 'zpl', 'epl')
    
    Returns:
        bool: True si l'impression a réussi
    """
    try:
        if printer_type == 'escpos':
            return _print_escpos(asset)
        elif printer_type == 'zpl':
            return _print_zpl(asset)
        elif printer_type == 'epl':
            return _print_epl(asset)
        else:
            print(f"Type d'imprimante non supporté: {printer_type}")
            return False
    except Exception as e:
        print(f"Erreur d'impression: {e}")
        return False


def _print_escpos(asset):
    """
    Impression via protocole ESC/POS (imprimantes thermiques courantes).
    """
    try:
        # Import conditionnel pour éviter les erreurs si la librairie n'est pas installée
        from escpos.printer import Usb
        
        # Configuration de l'imprimante USB
        # À adapter selon votre imprimante
        printer = Usb(0x0416, 0x5011)  # Exemple pour une imprimante Generic
        
        # En-tête
        printer.set(align='center')
        printer.text("CMDB INVENTORY\n")
        printer.text("================\n")
        
        # Informations de l'asset
        printer.set(align='left')
        printer.text(f"Asset: {asset.name}\n")
        printer.text(f"Code: {asset.code}\n")
        if asset.location:
            printer.text(f"Localisation: {asset.location}\n")
        
        # QR Code
        printer.set(align='center')
        printer.qr(f"{asset.code}", size=8)
        printer.text("\n")
        
        # Code-barres
        printer.barcode(f'{asset.code}', 'CODE128', height=100, width=2, pos='BELOW')
        printer.text("\n")
        
        # Footer
        printer.text(f"ID: {asset.id}\n")
        printer.text(f"Date: {asset.created_at.strftime('%d/%m/%Y %H:%M')}\n")
        
        # Couper le papier
        printer.cut()
        
        return True
        
    except ImportError:
        print("Bibliothèque escpos-python non installée. Installation: pip install escpos-python")
        return False
    except Exception as e:
        print(f"Erreur ESC/POS: {e}")
        return False


def _print_zpl(asset):
    """
    Impression via langage ZPL (Zebra Printers).
    """
    # Code ZPL de base pour une étiquette
    zpl_template = f"""
    ^XA
    ^FO50,50^A0N,40,40^FDCMDB INVENTORY^FS
    ^FO50,100^A0N,30,30^FD{asset.name}^FS
    ^FO50,140^A0N,25,25^FDCode: {asset.code}^FS
    ^FO50,180^BQN,2,10^FDQA,{asset.code}^FS
    ^FO50,350^BY3^BCN,100,Y,N,N^FD{asset.code}^FS
    ^XZ
    """
    
    # Ici, vous enverriez le ZPL à l'imprimante réseau ou USB
    # Exemple avec socket réseau:
    # import socket
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect(('192.168.1.100', 9100))
    # sock.send(zpl_template.encode())
    # sock.close()
    
    print("Code ZPL généré (à envoyer à l'imprimante):")
    print(zpl_template)
    
    return True


def _print_epl(asset):
    """
    Impression via langage EPL (Eltron Printers).
    """
    epl_template = f"""
    N
    q609
    Q203,26
    A50,50,0,4,1,1,N,"CMDB INVENTORY"
    A50,100,0,3,1,1,N,"{asset.name}"
    A50,140,0,2,1,1,N,"Code: {asset.code}"
    B50,180,0,1,3,7,100,B,"{asset.code}"
    P1
    """
    
    print("Code EPL généré (à envoyer à l'imprimante):")
    print(epl_template)
    
    return True


def get_asset_images_urls(asset, request=None):
    """
    Retourne les URLs des images QR code et code-barres d'un asset.
    
    Args:
        asset (Asset): Instance de l'asset
        request (HttpRequest, optional): Requête pour construire les URLs absolues
    
    Returns:
        dict: Dictionnaire avec les URLs
    """
    urls = {
        'qr_code': None,
        'barcode': None,
    }
    
    if asset.qr_code:
        if request:
            urls['qr_code'] = request.build_absolute_uri(asset.qr_code.url)
        else:
            urls['qr_code'] = asset.qr_code.url
    
    if asset.barcode:
        if request:
            urls['barcode'] = request.build_absolute_uri(asset.barcode.url)
        else:
            urls['barcode'] = asset.barcode.url
    
    return urls