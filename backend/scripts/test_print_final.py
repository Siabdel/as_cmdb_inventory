#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_print_final.py - Bixolon SRP-350 avec pyusb DIRECT
Contourne l'erreur [Errno 16] en évitant python-escpos Usb class
Basé sur test_usb.md : Vendor 0x0419, Product 0x3c00
Interface 0, EP OUT 0x01, EP IN 0x82
"""

import usb.core
import usb.util
import sys
import time

class BixolonSRP350:
    VID = 0x0419
    PID = 0x3c00
    INTERFACE = 0
    OUT_EP = 0x01
    IN_EP = 0x82
    TIMEOUT = 5000
    
    # Commandes ESC/POS de base
    CMD_INIT = b'\x1b\x40'           # Reset imprimante
    CMD_CUT = b'\x1d\x56\x42\x00'     # Coupe papier
    CMD_ALIGN_CENTER = b'\x1b\x61\x01'
    CMD_ALIGN_LEFT = b'\x1b\x61\x00'
    CMD_BOLD_ON = b'\x1b\x45\x01'
    CMD_BOLD_OFF = b'\x1b\x45\x00'
    CMD_DOUBLE_ON = b'\x1b\x21\x30'
    CMD_DOUBLE_OFF = b'\x1b\x21\x00'
    
    def __init__(self):
        self.device = None
    
    def connect(self, max_retries=3):
        """Connexion directe avec pyusb"""
        for attempt in range(max_retries):
            try:
                # Trouver le device
                self.device = usb.core.find(idVendor=self.VID, idProduct=self.PID)
                
                if self.device is None:
                    raise Exception("❌ Imprimante non détectée")
                
                print(f"✅ Imprimante trouvée (Bus {self.device.bus}, Addr {self.device.address})")
                
                # Vérifier configuration active
                try:
                    config = self.device.get_active_configuration()
                    print(f"   Configuration active: {config.bConfigurationValue}")
                except:
                    pass
                
                # Détacher le driver kernel si actif
                if self.device.is_kernel_driver_active(self.INTERFACE):
                    print(f"🔄 Détachement du driver kernel...")
                    self.device.detach_kernel_driver(self.INTERFACE)
                    time.sleep(0.3)
                
                # Claimer l'interface
                usb.util.claim_interface(self.device, self.INTERFACE)
                print("✅ Interface claimée avec succès")
                
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
        """Écrire des données directement sur l'endpoint OUT"""
        if self.device is None:
            raise Exception("Imprimante non connectée")
        
        # Convertir string en bytes si nécessaire
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Écrire sur l'endpoint OUT (0x01 selon test_usb.md)
        self.device.write(self.OUT_EP, data, self.TIMEOUT)
    
    def print_cmdb_label(self, asset_id, qr_data=None, barcode_data=None):
        """Impression étiquette CMDB"""
        if self.device is None:
            print("❌ Imprimante non connectée")
            return False
        
        try:
            # Reset
            self.write(self.CMD_INIT)
            time.sleep(0.1)
            
            # En-tête (centré, gras, double)
            self.write(self.CMD_ALIGN_CENTER)
            self.write(self.CMD_BOLD_ON)
            self.write(self.CMD_DOUBLE_ON)
            self.write("CMDB INVENTORY\n")
            
            # Reset style
            self.write(self.CMD_BOLD_OFF)
            self.write(self.CMD_DOUBLE_OFF)
            self.write("\n")
            
            # QR Code (si python-escpos installé pour génération)
            if qr_data is not None:
                try:
                    from escpos import printer as escpos_printer
                    # Utiliser escpos juste pour générer le QR, pas pour l'USB
                    print(f"   QR Code: {qr_data}")
                    # Note: QR Code natif nécessite commandes spécifiques SRP-350
                    # Pour simplifier, on imprime le texte URL
                    self.write(self.CMD_ALIGN_CENTER)
                    self.write(f"{qr_data}\n")
                except:
                    self.write(f"{qr_data}\n")
            
            # Code-barres
            if barcode_data is not None:
                self.write(self.CMD_ALIGN_CENTER)
                # Commande barcode CODE128 natif
                barcode_cmd = b'\x1d\x6b\x49' + bytes([len(barcode_data)]) + barcode_data.encode('utf-8') + b'\x00'
                self.write(barcode_cmd)
                self.write("\n")
            
            # Détails (gauche, normal)
            self.write(self.CMD_ALIGN_LEFT)
            self.write(f"Asset ID: {asset_id}\n")
            self.write(f"Date: {time.strftime('%Y-%m-%d %H:%M')}\n")
            self.write("\n\n\n")
            
            # Coupe
            self.write(self.CMD_CUT)
            time.sleep(1)  # Attendre la coupe
            
            print("✅ Impression terminée !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur d'impression: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close(self):
        """Fermeture propre"""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.INTERFACE)
                print("🔌 Interface relâchée")
            except:
                pass
        
        print("🔌 Imprimante déconnectée")

def main():
    printer = BixolonSRP350()
    
    if printer.connect():
        printer.print_cmdb_label(
            asset_id="SRV-001",
            qr_data="http://localhost:8000/django-admin/inventory/asset/210/print_label/",
            barcode_data="SRV001"
        )
        printer.close()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()