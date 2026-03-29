# test_srp350.py (copie exactement)#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_print_final.py - Bixolon SRP-350
Basé sur test_usb.md : Bus 003, Vendor 0x0419, Product 0x3c00
Interface 0, EP OUT 0x01, EP IN 0x82
"""

from escpos.printer import Usb
import usb.core
import usb.util
import sys
import time

class BixolonSRP350:
    VID = 0x0419
    PID = 0x3c00
    INTERFACE = 0
    IN_EP = 0x82
    OUT_EP = 0x01
    
    def __init__(self):
        self.printer = None
        self.device = None
    
    def connect(self, max_retries=3):
        """Connexion avec gestion des conflits kernel"""
        for attempt in range(max_retries):
            try:
                # Trouver le device
                self.device = usb.core.find(idVendor=self.VID, idProduct=self.PID)
                
                if self.device is None:
                    raise Exception("❌ Imprimante non détectée")
                
                print(f"✅ Imprimante trouvée (Bus {self.device.bus}, Addr {self.device.address})")
                
                # Détacher le driver kernel si actif
                if self.device.is_kernel_driver_active(self.INTERFACE):
                    print(f"🔄 Détachement du driver kernel (tentative {attempt + 1})...")
                    self.device.detach_kernel_driver(self.INTERFACE)
                    time.sleep(0.5)
                
                # Claimer l'interface
                usb.util.claim_interface(self.device, self.INTERFACE)
                
                # Initialiser l'imprimante
                self.printer = Usb(
                    idVendor=self.VID,
                    idProduct=self.PID,
                    interface=self.INTERFACE,
                    in_ep=self.IN_EP,
                    out_ep=self.OUT_EP,
                    timeout=5000
                )
                
                # Reset ESC/POS
                self.printer._raw('\x1b\x40')
                time.sleep(0.2)
                
                print("✅ Connexion réussie !")
                return True
                
            except usb.core.USBError as e:
                print(f"⚠️ Erreur USB (tentative {attempt + 1}/{max_retries}): {e}")
                if e.errno == 16:
                    print("💡 Solution: Blacklistez usblp et redémarrez (Étape 1)")
                elif e.errno == 13:
                    print("💡 Solution: Vérifiez les règles udev (Étape 3)")
                
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
                return False
        
        return False
    
    def print_cmdb_label(self, asset_id, qr_data=None, barcode_data=None):
        """Impression étiquette CMDB avec QR Code"""
        if not self.printer:
            print("❌ Imprimante non connectée")
            return False
        
        try:
            # Reset
            self.printer._raw('\x1b\x40')
            time.sleep(0.1)
            
            # En-tête
            self.printer.set(align='center', bold=True, double_height=True, double_width=True)
            self.printer.text("CMDB INVENTORY\n")
            self.printer.set()
            
            # QR Code (CORRIGÉ)
            if qr_data:
                self.printer.set(align='center')
                self.printer.qr(qr_data, size=8, ec='L')
                self.printer.text("\n")
            
            # Code-barres (CORRIGÉ)
            if barcode_data:
                self.printer.set(align='center')
                self.printer.barcode(barcode_data, 'CODE128', width=2, height=64, pos='below')
                self.printer.text("\n")
            
            # Détails
            self.printer.set(align='left', bold=False, double_height=False, double_width=False)
            self.printer.text(f"Asset ID: {asset_id}\n")
            self.printer.text(f"Date: {time.strftime('%Y-%m-%d %H:%M')}\n")
            self.printer.text("\n\n")
            
            # Coupe
            self.printer.cut()
            
            print("✅ Impression terminée !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur d'impression: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close(self):
        """Fermeture propre"""
        if self.printer:
            try:
                self.printer.close()
            except:
                pass
        
        if self.device:
            try:
                usb.util.release_interface(self.device, self.INTERFACE)
            except:
                pass
        
        print("🔌 Imprimante déconnectée")

def main():
    printer = BixolonSRP350()
    
    if printer.connect():
        printer.print_cmdb_label(
            asset_id="SRV-001",
            qr_data="http://cmdb.local/asset/SRV-001",
            barcode_data="SRV001"
        )
        printer.close()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
