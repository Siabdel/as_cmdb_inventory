# test_srp350.py (copie exactement)#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# diagnostic_complet.py
import usb.core
import usb.util
import subprocess

def check_system():
    print("=" * 50)
    print("DIAGNOSTIC SYSTEME USB")
    print("=" * 50)
    
    # 1. Vérifier module usblp
    result = subprocess.run(['lsmod'], capture_output=True, text=True)
    if 'usblp' in result.stdout:
        print("❌ WARNING: Module usblp est chargé !")
        print("   Solution: sudo modprobe -r usblp")
    else:
        print("✅ Module usblp non chargé")
    
    # 2. Vérifier device USB
    dev = usb.core.find(idVendor=0x0419, idProduct=0x3c00)
    if dev is None:
        print("❌ Imprimante non détectée")
        return
    
    print("✅ Imprimante détectée")
    print(f"   Bus: {dev.bus}, Address: {dev.address}")
    
    # 3. Vérifier driver kernel
    if dev.is_kernel_driver_active(0):
        print("⚠️ Driver kernel actif sur interface 0")
    else:
        print("✅ Driver kernel inactif")
    
    # 4. Vérifier permissions
    try:
        dev.reset()
        print("✅ Permissions OK")
    except usb.core.USBError as e:
        print(f"❌ Permissions: {e}")
    
    # 5. Vérifier processus CUPS
    result = subprocess.run(['pgrep', '-f', 'cups'], capture_output=True)
    if result.returncode == 0:
        print("⚠️ CUPS est en cours d'exécution")
    else:
        print("✅ CUPS arrêté")
    
    print("=" * 50)

if __name__ == "__main__":
    check_system()