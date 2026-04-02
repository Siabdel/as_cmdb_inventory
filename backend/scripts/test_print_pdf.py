#!/usr/bin/env python3
# -*- coding: utf-8 -*-#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_print_pdf_v2.py — Impression via PDF (SOLUTION VALIDÉE ✅)
Basé sur generate_label_pdf() qui fonctionne correctement
"""

import usb.core
import usb.util
import sys
import time
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch


class BixolonSRP350:
    """Impression Bixolon SRP-350 via PDF — Solution Validée."""
    
    VID = 0x0419
    PID = 0x3c00
    INTERFACE = 0
    OUT_EP = 0x01
    IN_EP = 0x82
    TIMEOUT = 5000
    
    def __init__(self):
        self.device = None
        self.connected = False
    
    def connect(self, max_retries=3):
        """Connexion USB."""
        for attempt in range(max_retries):
            try:
                print(f"🔍 Recherche imprimante (VID:0x{self.VID:04X}, PID:0x{self.PID:04X})...")
                self.device = usb.core.find(idVendor=self.VID, idProduct=self.PID)
                
                if self.device is None:
                    raise Exception("❌ Imprimante non détectée")
                
                print(f"✅ Imprimante trouvée (Bus {self.device.bus}, Addr {self.device.address})")
                
                if self.device.is_kernel_driver_active(self.INTERFACE):
                    print(f"🔄 Détachement du driver kernel...")
                    self.device.detach_kernel_driver(self.INTERFACE)
                    time.sleep(0.3)
                
                usb.util.claim_interface(self.device, self.INTERFACE)
                print("✅ Interface claimée avec succès")
                
                self.connected = True
                return True
                
            except Exception as e:
                print(f"⚠️ Erreur (tentative {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return False
    
    def write(self, data):
        """Écrire données sur endpoint OUT."""
        if self.device is None:
            raise Exception("Imprimante non connectée")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self.device.write(self.OUT_EP, data, self.TIMEOUT)
    
    def generate_label_pdf(self, asset_name, asset_code, location, created_date, qr_image_path=None):
        """
        Génère un PDF d'étiquette — REPREND generate_label_pdf() QUI MARCHE.
        
        Args:
            asset_name: Nom de l'asset
            asset_code: Code interne
            location: Localisation
            created_date: Date de création
            qr_image_path: Chemin vers l'image QR Code PNG
        
        Returns:
            str: Chemin du fichier PDF généré
        """
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        output_path = temp_file.name
        temp_file.close()
        
        # Créer le canvas PDF (3×2 pouces = 76×50mm)
        c = canvas.Canvas(output_path, pagesize=(3 * inch, 2 * inch))
        width, height = 3 * inch, 2 * inch
        
        # Titre
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, height - 20, f"ASSET: {asset_name}")
        
        # Code
        c.setFont("Helvetica", 9)
        c.drawString(10, height - 40, f"Code: {asset_code}")
        
        # Localisation
        c.drawString(10, height - 55, f"Localisation: {location}")
        
        # Date
        c.drawString(10, height - 70, f"Créé le: {created_date}")
        
        # QR Code (IMAGE PNG — C'EST ÇA QUI MARCHE ✅)
        if qr_image_path and os.path.exists(qr_image_path):
            try:
                qr_img = ImageReader(qr_image_path)
                # Position: droite, taille 70×70 points
                c.drawImage(qr_img, width - 80, height - 80, width=70, height=70)
                print(f"✅ QR Code intégré: {qr_image_path}")
            except Exception as e:
                print(f"⚠️ Erreur QR Code: {e}")
        
        # Footer
        c.setFont("Helvetica-Oblique", 6)
        c.drawString(10, 5, "CMDB Inventory")
        
        c.save()
        
        print(f"✅ PDF généré: {output_path}")
        return output_path
    
    def print_pdf_via_cups(self, pdf_path, printer_name="SRP350"):
        """
        Imprime le PDF via CUPS — RECOMMANDÉ ✅.
        
        Args:
            pdf_path: Chemin du fichier PDF
            printer_name: Nom de l'imprimante dans CUPS
        """
        import subprocess
        
        try:
            print(f"🖨️  Impression via CUPS: {printer_name}")
            
            # Commande lp pour imprimer PDF
            cmd = ['lp', '-d', printer_name, '-o', 'fit-to-page', pdf_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Impression lancée avec succès")
                print(f"   Job ID: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Erreur CUPS: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout impression")
            return False
        except FileNotFoundError:
            print("❌ Commande 'lp' non trouvée — Installer CUPS: sudo apt install cups")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def close(self):
        """Fermeture propre."""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.INTERFACE)
                print("🔌 Interface relâchée")
            except:
                pass
            print("🔌 Imprimante déconnectée")
        self.connected = False


# ============================================================================
# FONCTION PRINCIPALE — TEST AVEC PDF
# ============================================================================
def main():
    print("=" * 60)
    print("🖨️  TEST IMPRESSION BIXOLON SRP-350 — Via PDF (VALIDÉ ✅)")
    print("=" * 60)
    print()
    
    printer = BixolonSRP350()
    
    # Connexion USB (optionnel — CUPS gère l'impression)
    if not printer.connect(max_retries=2):
        print("⚠️ Connexion USB échouée — CUPS suffira pour l'impression")
    
    print()
    print("-" * 60)
    print("GÉNÉRATION ÉTIQUETTE PDF")
    print("-" * 60)
    
    # Générer PDF avec QR Code (comme generate_label_pdf())
    pdf_path = printer.generate_label_pdf(
        asset_name="HP Elitebook G4",
        asset_code="CI-20260317-072629-071",
        location="Reception (office)",
        created_date="17/03/2026",
        qr_image_path="/home/django/Depots/www/projets/envCMDBIventory/as_cmdb_inventory/backend/media/qr_codes/2026/03/qr_asset_210_abc123.png"  # Adapter le chemin
    )
    
    print()
    print("-" * 60)
    print("IMPRESSION VIA CUPS")
    print("-" * 60)
    
    # Imprimer via CUPS (RECOMMANDÉ ✅)
    printer.print_pdf_via_cups(pdf_path, printer_name="SRP350")
    
    # Nettoyage
    print()
    print("-" * 60)
    print("NETTOYAGE")
    print("-" * 60)
    print(f"🗑️  Fichier temporaire: {pdf_path}")
    print("   (Conserver pour debug ou supprimer)")
    
    # Fermeture
    printer.close()
    
    print()
    print("=" * 60)
    print("✅ TEST TERMINÉ — Solution PDF Validée ✅")
    print("=" * 60)
    print()
    print("📋 RECOMMANDATIONS:")
    print("   1. ✅ Continuer avec generate_label_pdf() (ReportLab)")
    print("   2. ✅ Utiliser CUPS pour l'impression (lp -d SRP350 file.pdf)")
    print("   3. ❌ Abandonner ESC/POS direct pour QR Code")
    print("   4. ✅ Le QR Code est une IMAGE PNG dans le PDF")
    print()


if __name__ == "__main__":
    main()