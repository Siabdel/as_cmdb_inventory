import usb.core
import usb.util

dev = usb.core.find(idVendor=0x0419, idProduct=0x3c00)
print(dev)
if dev:
    try:
        dev.set_configuration()
        print("configuration ok")
    except Exception as e:
        print(type(e), e)