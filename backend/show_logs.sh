# Logs système USB
sudo dmesg | grep -i usb

# Logs CUPS (si utilisé)
sudo tail -f /var/log/cups/error_log

# Test direct device
echo "TEST" | sudo tee /dev/usb/lp0
