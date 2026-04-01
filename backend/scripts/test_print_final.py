#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_print_final.py - Bixolon SRP-350 avec pyusb DIRECT
Contourne l'erreur [Errno 16] en évitant python-escpos Usb class
Basé sur test_usb.md : Vendor 0x0419, Product 0x3c00
Interface 0, EP OUT 0x01, EP IN 0x82
##
test_print_final_v2.py - Bixolon SRP-350 avec pyusb DIRECT
Version: 2.0 — Correction Commandes QR Code ESC/POS

Basé sur test_usb.md :
- Vendor: 0x0419
- Product: 0x3c00
- Interface: 0
- EP OUT: 0x01
- EP IN: 0x82

Documentation ESC/POS QR Code:
- GS ( k standard commands for QR Code
- Reference: https://www.bixolon.com/support/Manual_down?idx=269
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_print_final_v3.py — Bixolon SRP-350 avec QR Code CORRECT
Version: 3.0 — Correction commandes ESC/POS QR Code

Basé sur test_usb.md :
- Vendor: 0x0419
- Product: 0x3c00
- Interface: 0
- EP OUT: 0x01
- EP IN: 0x82

Documentation ESC/POS QR Code (GS k standard):
- https://www.bixolon.com/support/Manual_down?idx=269
- https://www.epson-biz.com/modules/ref_escpos/index.php?content_id=140
"""

import usb.core
import usb.util
import sys
import time
from datetime import datetime


class BixolonSRP350:
    """Classe d'impression pour Bixolon SRP-350 avec QR Code CORRECT."""
    
    # ========================================================================
    # CONFIGURATION USB (depuis test_usb.md)
    # ========================================================================
    VID = 0x0419          # Samsung Electronics
    PID = 0x3c00          # SRP-350
    INTERFACE = 0         # Interface Printer
    OUT_EP = 0x01         # Endpoint OUT (Bulk)
    IN_EP = 0x82          # Endpoint IN (Bulk)
    TIMEOUT = 5000        # Timeout USB en ms
    
    # ========================================================================
    # COMMANDES ESC/POS DE BASE
    # ========================================================================
    CMD_INIT = b'\x1b\x40'           # Initialisation imprimante
    CMD_CUT = b'\x1d\x56\x42\x00'     # Coupe papier (type B)
    CMD_ALIGN_CENTER = b'\x1b\x61\x01'
    CMD_ALIGN_LEFT = b'\x1b\x61\x00'
    CMD_BOLD_ON = b'\x1b\x45\x01'
    CMD_BOLD_OFF = b'\x1b\x45\x00'
    CMD_DOUBLE_ON = b'\x1b\x21\x30'
    CMD_DOUBLE_OFF = b'\x1b\x21\x00'
    CMD_LINE_SPACE = b'\x1b\x33\x18'
    
    # ========================================================================
    # COMMANDES QR CODE — FORMAT CORRECT GS ( k
    # ========================================================================
    # Format: 1D 28 6B pL pH cn fn m [data]
    # cn = 0x31 (QR Code)
    
    # 1. Définir modèle QR (Model 2 = standard)
    # 1D 28 6B 04 00 31 41 32 00
    QR_SET_MODEL = b'\x1d\x28\x6b\x04\x00\x31\x41\x32\x00'
    
    # 2. Définir taille module (1-16, recommandé 4-6)
    # 1D 28 6B 03 00 31 43 [size]
    QR_SET_SIZE = b'\x1d\x28\x6b\x03\x00\x31\x43\x04'  # Taille 4
    
    # 3. Définir correction d'erreur
    # L=7% (0x30), M=15% (0x31), Q=25% (0x32), H=30% (0x33)
    QR_SET_ERROR_L = b'\x1d\x28\x6b\x03\x00\x31\x45\x30'  # L (7%)
    QR_SET_ERROR_M = b'\x1d\x28\x6b\x03\x00\x31\x45\x31'  # M (15%) ← RECOMMANDÉ
    QR_SET_ERROR_Q = b'\x1d\x28\x6b\x03\x00\x31\x45\x32'  # Q (25%)
    QR_SET_ERROR_H = b'\x1d\x28\x6b\x03\x00\x31\x45\x33'  # H (30%)
    
    # 4. Imprimer QR Code
    # 1D 28 6B 03 00 31 51 30
    QR_PRINT = b'\x1d\x28\x6b\x03\x00\x31\x51\x30'
    
    def __init__(self):
        self.device = None
        self.connected = False
    
    def connect(self, max_retries=3):
        """Connexion directe avec pyusb."""
        for attempt in range(max_retries):
            try:
                print(f"🔍 Recherche imprimante (VID:0x{self.VID:04X}, PID:0x{self.PID:04X})...")
                self.device = usb.core.find(idVendor=self.VID, idProduct=self.PID)
                
                if self.device is None:
                    raise Exception("❌ Imprimante non détectée sur le bus USB")
                
                print(f"✅ Imprimante trouvée (Bus {self.device.bus}, Addr {self.device.address})")
                
                # Détacher driver kernel si actif
                if self.device.is_kernel_driver_active(self.INTERFACE):
                    print(f"🔄 Détachement du driver kernel (interface {self.INTERFACE})...")
                    self.device.detach_kernel_driver(self.INTERFACE)
                    time.sleep(0.3)
                
                # Claimer l'interface
                usb.util.claim_interface(self.device, self.INTERFACE)
                print("✅ Interface claimée avec succès")
                
                # Initialiser l'imprimante
                self.write(self.CMD_INIT)
                time.sleep(0.3)
                
                self.connected = True
                return True
                
            except usb.core.USBError as e:
                print(f"⚠️ Erreur USB (tentative {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    try:
                        if self.device:
                            usb.util.release_interface(self.device, self.INTERFACE)
                    except:
                        pass
                    continue
            except Exception as e:
                print(f"❌ Erreur: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return False
    
    def write(self, data):
        """Écrire des données sur l'endpoint OUT."""
        if self.device is None:
            raise Exception("Imprimante non connectée")
        
        if isinstance(data, str):
            data = data.encode('utf-8', errors='replace')
        
        try:
            self.device.write(self.OUT_EP, data, self.TIMEOUT)
            time.sleep(0.05)  # Petit délai entre écritures
        except usb.core.USBError as e:
            print(f"❌ Erreur écriture USB: {e}")
            raise
    
    def _build_qr_command(self, data, size=4, error_correction='M'):
        """
        Construire la commande QR Code complète — FORMAT CORRECT.
        
        Args:
            data: Données à encoder
            size: Taille module (1-16)
            error_correction: 'L', 'M', 'Q', 'H'
        
        Returns:
            bytes: Commande QR complète
        """
        commands = bytearray()
        
        # 1. Modèle QR (Model 2)
        commands.extend(self.QR_SET_MODEL)
        
        # 2. Taille module
        if size != 4:
            qr_size = b'\x1d\x28\x6b\x03\x00\x31\x43' + bytes([size])
            commands.extend(qr_size)
        else:
            commands.extend(self.QR_SET_SIZE)
        
        # 3. Correction erreur
        error_map = {
            'L': self.QR_SET_ERROR_L,
            'M': self.QR_SET_ERROR_M,
            'Q': self.QR_SET_ERROR_Q,
            'H': self.QR_SET_ERROR_H
        }
        commands.extend(error_map.get(error_correction, self.QR_SET_ERROR_M))
        
        # 4. Données QR Code
        # Format: GS ( k pL pH cn fn m + data
        # pL + pH × 256 = len(data) + 3 (pour cn + fn + m)
        data_bytes = data.encode('utf-8')
        data_len = len(data_bytes)
        total_len = data_len + 3  # +3 pour 0x31, 0x50, 0x00
        
        pL = total_len % 256
        pH = total_len // 256
        
        qr_data_cmd = bytearray()
        qr_data_cmd.extend(b'\x1d\x28\x6b')  # GS ( k
        qr_data_cmd.append(pL)               # pL
        qr_data_cmd.append(pH)               # pH
        qr_data_cmd.append(0x31)             # cn (QR Code)
        qr_data_cmd.append(0x50)             # fn (stocker données)
        qr_data_cmd.append(0x00)             # m (0x00)
        qr_data_cmd.extend(data_bytes)       # Données
        
        commands.extend(qr_data_cmd)
        
        # 5. Imprimer QR Code
        commands.extend(self.QR_PRINT)
        
        return bytes(commands)
    
    def print_qr_code(self, data, size=4, error_correction='M'):
        """
        Imprimer un QR Code — VERSION CORRIGÉE.
        
        Args:
            data: Données à encoder
            size: Taille module (1-16)
            error_correction: 'L', 'M', 'Q', 'H'
        
        Returns:
            bool: True si succès
        """
        if not self.connected:
            print("❌ Imprimante non connectée")
            return False
        
        try:
            print(f"📱 Génération QR Code: {data[:50]}...")
            print(f"   Taille: {size}, Correction: {error_correction}")
            
            # Reset imprimante
            self.write(self.CMD_INIT)
            time.sleep(0.3)
            
            # Alignement centre
            self.write(self.CMD_ALIGN_CENTER)
            
            # Construire et envoyer commande QR
            qr_cmd = self._build_qr_command(data, size, error_correction)
            print(f"   Commande QR: {len(qr_cmd)} bytes")
            self.write(qr_cmd)
            
            # IMPORTANT: Attendre impression QR (plus lent que texte)
            print("   ⏳ Impression QR en cours...")
            time.sleep(1.5)
            
            # Lignes vides après QR
            self.write(b'\n\n\n')
            time.sleep(0.5)
            
            print(f"✅ QR Code imprimé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur impression QR Code: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_cmdb_label(self, asset_id, qr_data=None, barcode_data=None, copies=1):
        """Impression étiquette CMDB complète."""
        if not self.connected:
            print("❌ Imprimante non connectée")
            return False
        
        for copy in range(copies):
            try:
                print(f"\n{'='*60}")
                print(f"COPIE {copy + 1}/{copies}")
                print(f"{'='*60}")
                
                # Reset
                self.write(self.CMD_INIT)
                time.sleep(0.3)
                
                # ====================================================================
                # EN-TÊTE
                # ====================================================================
                print("📝 Impression en-tête...")
                self.write(self.CMD_ALIGN_CENTER)
                self.write(self.CMD_BOLD_ON)
                self.write(self.CMD_DOUBLE_ON)
                self.write("CMDB INVENTORY\n")
                self.write(self.CMD_BOLD_OFF)
                self.write(self.CMD_DOUBLE_OFF)
                self.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
                time.sleep(0.3)
                
                # ====================================================================
                # QR CODE
                # ====================================================================
                if qr_data:
                    print("📱 Impression QR Code...")
                    self.print_qr_code(qr_data, size=4, error_correction='M')
                else:
                    print("⚠️ Pas de données QR fournies")
                
                # ====================================================================
                # CODE-BARRES
                # ====================================================================
                if barcode_data:
                    print("📊 Impression code-barres...")
                    self.write(self.CMD_ALIGN_CENTER)
                    # CODE128: 1D 6B 49 [len] [data]
                    barcode_bytes = barcode_data.encode('utf-8')
                    barcode_cmd = b'\x1d\x6b\x49' + bytes([len(barcode_bytes)]) + barcode_bytes
                    self.write(barcode_cmd)
                    self.write(f"\n{barcode_data}\n\n")
                    time.sleep(0.5)
                
                # ====================================================================
                # DÉTAILS ASSET
                # ====================================================================
                print("📝 Impression détails...")
                self.write(self.CMD_ALIGN_LEFT)
                self.write(f"Asset ID: {asset_id}\n")
                self.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                # ====================================================================
                # COUPE
                # ====================================================================
                print("✂️ Coupe papier...")
                self.write(self.CMD_ALIGN_CENTER)
                self.write("─" * 30 + "\n")
                self.write(self.CMD_CUT)
                time.sleep(1.5)  # Attendre coupe complète
                
                if copies > 1:
                    time.sleep(1.0)  # Pause entre copies
                
            except Exception as e:
                print(f"❌ Erreur impression (copie {copy + 1}): {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print(f"\n✅ IMPRESSION TERMINÉE ! ({copies} copie(s))")
        return True
    
    def close(self):
        """Fermeture propre."""
        if self.device:
            try:
                self.write(self.CMD_INIT)
                time.sleep(0.2)
                usb.util.release_interface(self.device, self.INTERFACE)
                print("🔌 Interface relâchée")
            except Exception as e:
                print(f"⚠️ Erreur fermeture: {e}")
            print("🔌 Imprimante déconnectée")
        self.connected = False


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================
def main():
    print("=" * 60)
    print("🖨️  TEST IMPRESSION BIXOLON SRP-350 — Version 3.0")
    print("    Correction QR Code ESC/POS")
    print("=" * 60)
    print()
    
    printer = BixolonSRP350()
    
    # Connexion
    if not printer.connect(max_retries=3):
        print("❌ Échec connexion imprimante")
        sys.exit(1)
    
    print()
    
    # Test QR Code seul d'abord
    print("-" * 60)
    print("TEST 1: QR Code seul (diagnostic)")
    print("-" * 60)
    qr_url = "http://localhost:8000/scan/abc123-def456"
    printer.print_qr_code(qr_url, size=4, error_correction='M')
    time.sleep(2)
    
    # Test étiquette complète
    print()
    print("-" * 60)
    print("TEST 2: Étiquette CMDB complète")
    print("-" * 60)
    printer.print_cmdb_label(
        asset_id="SRV-210",
        qr_data="http://localhost:8000/scan/abc123-def456",
        barcode_data="SRV001234567",
        copies=1
    )
    
    # Fermeture
    printer.close()
    
    print()
    print("=" * 60)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("=" * 60)
    print()
    print("📋 Si QR Code toujours non imprimé:")
    print("   1. Vérifier que l'imprimante supporte QR Code (SRP-350 oui)")
    print("   2. Augmenter taille QR (size=5 ou 6)")
    print("   3. Vérifier densité d'impression (panneau imprimante)")
    print("   4. Tester avec QR plus court (ex: 'TEST123')")
    print()


if __name__ == "__main__":
    main()