
#!/bin/bash
echo "=========================================="
echo "VÉRIFICATION USBLP"
echo "=========================================="

echo "1. Module usblp chargé ?"
if lsmod | grep -q usblp; then
    echo "   ❌ OUI - Problème !"
    echo "   Solution: sudo modprobe -r usblp"
else
    echo "   ✅ NON - OK"
fi

echo ""
echo "2. Fichier blacklist existe ?"
if [ -f /etc/modprobe.d/blacklist-usblp.conf ]; then
    echo "   ✅ OUI"
    cat /etc/modprobe.d/blacklist-usblp.conf
else
    echo "   ❌ NON - Créez-le !"
fi

echo ""
echo "3. Imprimante détectée ?"
if lsusb | grep -q "0419:3c00"; then
    echo "   ✅ OUI"
    lsusb | grep "0419:3c00"
else
    echo "   ❌ NON - Vérifiez le câble USB"
fi

echo ""
echo "4. Service CUPS ?"
if systemctl is-active --quiet cups; then
    echo "   ⚠️ ACTIF - Peut causer des conflits"
else
    echo "   ✅ INACTIF - OK"
fi

echo "=========================================="