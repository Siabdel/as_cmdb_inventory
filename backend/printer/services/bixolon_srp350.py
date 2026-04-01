"""
printer/services/bixolon_srp350.py
Driver pour Bixolon SRP-350 via USB direct (pyusb)
Contourne les conflits de configuration USB [Errno 16]
Basé sur test_usb.md : Vendor 0x0419, Product 0x3c00
#
Implémente les commandes ESC/POS natives pour:
- QR Code (GS ( k)
- Code-barres CODE128 (GS k)
- Texte formaté
- Coupe papier
"""

import usb.core
import usb.util
import time
import logging
from typing import Optional

from .printer_base import AbstractThermalPrinter
from ..utils.escpos_commands import ESCPOS

logger = logging.getLogger(__name__)

class BixolonSRP350(AbstractThermalPrinter):
    """Driver USB direct pour Bixolon SRP-350"""
    
    # Configuration USB (depuis test_usb.md)
    VID = 0x0419          # Vendor ID Samsung/Bixolon
    PID = 0x3c00          # Product ID SRP-350
    INTERFACE = 0         # Interface number
    OUT_EP = 0x01         # Endpoint Bulk OUT
    IN_EP = 0x82          # Endpoint Bulk IN
    TIMEOUT = 5000        # Timeout USB en ms
    
    def __init__(self, device_id: Optional[str] = None):
        self.device = None
        self.device_id = device_id
        self._connected = False
    
    def connect(self, max_retries: int = 3) -> bool:
        """
        Connexion USB avec gestion des erreurs kernel
        
        Algorithme:
        1. Trouver le device USB (vid/pid)
        2. Détacher le driver kernel si actif (usblp)
        3. Claimer l'interface USB
        4. Retourner True si succès
        """
        for attempt in range(max_retries):
            try:
                # 1. Trouver le device
                self.device = usb.core.find(
                    idVendor=self.VID,
                    idProduct=self.PID
                )
                
                if self.device is None:
                    raise ConnectionError("Imprimante non détectée")
                
                logger.info(f"Imprimante trouvée (Bus {self.device.bus}, Addr {self.device.address})")
                
                # 2. Détacher driver kernel (conflit usblp)
                if self.device.is_kernel_driver_active(self.INTERFACE):
                    logger.debug("Détachement driver kernel usblp...")
                    self.device.detach_kernel_driver(self.INTERFACE)
                    time.sleep(0.3)
                
                # 3. Claimer l'interface
                usb.util.claim_interface(self.device, self.INTERFACE)
                
                self._connected = True
                logger.info("✅ Connexion USB établie")
                return True
                
            except usb.core.USBError as e:
                logger.warning(f"Tentative {attempt+1} échouée: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    self._cleanup()
                    continue
                return False
    
    def print_cmdb_label(
        self,
        asset_id: str,
        qr_data: Optional[str] = None,
        barcode_data: Optional[str] = None,
        custom_text: Optional[str] = None
    ) -> bool:
        """
        Impression d'une étiquette CMDB complète
        
        Séquence ESC/POS:
        1. Reset imprimante (ESC @)
        2. En-tête centrée (ESC a 1, ESC E 1, ESC ! 30)
        3. QR Code natif (GS ( k) si qr_data fourni
        4. Code-barres natif (GS k) si barcode_data fourni
        5. Texte détails (ESC a 0)
        6. Coupe papier (GS V 42 00)
        """
        if not self._connected:
            logger.error("Tentative d'impression sans connexion")
            return False
        
        try:
            # 1. Reset
            self._write(ESCPOS.INIT)
            time.sleep(0.1)
            
            # 2. En-tête (centré, gras, double)
            self._write(ESCPOS.align_center())
            self._write(ESCPOS.bold_on())
            self._write(ESCPOS.double_on())
            self._write(b"CMDB INVENTORY\n")
            
            self._write(ESCPOS.bold_off())
            self._write(ESCPOS.double_off())
            self._write(b"\n")
            
            # 3. QR Code natif (SI fourni)
            if qr_data:
                self._print_native_qr(qr_data)
                self._write(b"\n")
            
            # 4. Code-barres natif (SI fourni)
            if barcode_data:
                self._print_native_barcode(barcode_data)
                self._write(b"\n")
            
            # 5. Détails (gauche)
            self._write(ESCPOS.align_left())
            self._write(f"Asset ID: {asset_id}\n".encode('utf-8'))
            
            if custom_text:
                self._write(f"{custom_text}\n".encode('utf-8'))
            
            self._write(f"Date: {time.strftime('%Y-%m-%d %H:%M')}\n".encode('utf-8'))
            self._write(b"\n\n\n")
            
            # 6. Coupe
            self._write(ESCPOS.CUT)
            time.sleep(1)
            
            logger.info(f"✅ Étiquette imprimée pour {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur impression {asset_id}: {e}")
            return False
    
    def _print_native_qr(self, qr_data: str, size: int = 8):
        """
        Génération QR Code via commandes ESC/POS natives
        
        Séquence GS ( k:
        1. Sélectionner modèle 2 (GS ( k 04 00 31 41 32 00)
        2. Définir taille module (GS ( k 03 00 31 43 size)
        3. Définir correction erreur (GS ( k 03 00 31 45 30)
        4. Stocker données (GS ( k pL pH 31 50 30 data)
        5. Imprimer (GS ( k 03 00 31 51 30)
        """
        data_bytes = qr_data.encode('utf-8')
        data_len = len(data_bytes)
        
        # 1. Modèle 2
        self._write(b'\x1d\x28\x6b\x04\x00\x31\x41\x32\x00')
        
        # 2. Taille module (4-8)
        self._write(bytes([0x1d, 0x28, 0x6b, 0x03, 0x00, 0x31, 0x43, size]))
        
        # 3. Correction L
        self._write(b'\x1d\x28\x6b\x03\x00\x31\x45\x30')
        
        # 4. Stockage données
        header = b'\x1d\x28\x6b' + bytes([data_len + 3, 0, 0x31, 0x50, 0x30])
        self._write(header + data_bytes)
        
        # 5. Impression
        self._write(b'\x1d\x28\x6b\x03\x00\x31\x51\x30')
    
    def _print_native_barcode(self, barcode_data: str):
        """
        Code-barres CODE128 natif
        
        Commande: GS k m n d1...dk NUL
        m=0x49 pour CODE128 automatique
        """
        data_bytes = barcode_data.encode('utf-8')
        data_len = len(data_bytes)
        
        cmd = b'\x1d\x6b\x49' + bytes([data_len]) + data_bytes + b'\x00'
        self._write(cmd)
    
    def _write(self, data: bytes):
        """Écriture directe sur endpoint OUT"""
        if not self._connected or not self.device:
            raise RuntimeError("Imprimante non connectée")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self.device.write(self.OUT_EP, data, self.TIMEOUT)
    
    def _cleanup(self):
        """Libérer ressources USB"""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.INTERFACE)
            except:
                pass
            self.device = None
        self._connected = False
    
    def close(self):
        """Fermeture propre"""
        self._cleanup()
        logger.debug("Connexion fermée")
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self.device is not None