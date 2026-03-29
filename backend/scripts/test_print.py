# test_srp350.py (copie exactement)
from escpos.printer import Usb
import usb.core
import usb.util
from escpos.printer import Usb


# Remplace par tes IDs lsusb
# ID 0419:3c00
VID, PID = 0x0419, 0x3c00
## p = Usb(VID, PID)
# Exemple de test d'impression avec python-escpos
# Assure-toi que l'imprimante est connectée et que les drivers sont installés.
# Remplace les paramètres selon ton modèle d'imprimante (interface, endpoints, etc.)
# Note : les paramètres d'interface et d'endpoints peuvent varier selon le modèle d'imprimante.
# p.cut()lsusb -v, ton SRP-350 expose exactement bConfigurationValue 1, bInterfaceNumber 0, EP 1 OUT et EP 2 IN, donc la bonne config est bien interface=0, in_ep=0x82, out_ep=0x01
#    


dev = usb.core.find(idVendor=0x0419, idProduct=0x3c00)
if dev is None:
    raise RuntimeError("Printer not found")

if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

usb.util.claim_interface(dev, 0)

p = Usb(idVendor=0x0419, idProduct=0x3c00, interface=0, in_ep=0x82, out_ep=0x01)    
p.text("Debian 12 OK\n")
p.close()
print("✅ Imprimé !")
