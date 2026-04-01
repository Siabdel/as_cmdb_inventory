# 1. Blacklist usblp
sudo bash -c 'echo -e "blacklist usblp\ninstall usblp /bin/true" > /etc/modprobe.d/blacklist-usblp.conf'

# 2. Arrêter CUPS
sudo systemctl stop cups
sudo systemctl disable cups
sudo systemctl mask cups

# 3. Règle udev
sudo bash -c 'echo "ATTR{idVendor}==\"0419\", ATTR{idProduct}==\"3c00\", MODE=\"0666\", GROUP=\"lp\"" > /etc/udev/rules.d/99-bixolon-srp350.rules'
sudo udevadm control --reload-rules
sudo udevadm trigger

# 4. Initramfs
sudo update-initramfs -u

# 5. Décharger usblp
sudo modprobe -r usblp

# 6. Redémarrer
sudo reboot

# 7. Après reboot
lsmod | grep usblp && echo "❌ PROBLÈME" || echo "✅ OK"
python3 test_print_v3.py