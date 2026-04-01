"""
Utilitaires de vérification des permissions USB pour l'impression
"""
import subprocess
import usb.core
import logging

logger = logging.getLogger(__name__)

def check_usb_permissions() -> dict:
    """Vérifie l'environnement USB pour l'impression"""
    result = {
        'ok': False,
        'device_found': False,
        'udev_ok': False,
        'groups': [],
        'cups_active': False,
        'message': ''
    }
    
    # 1. Device détecté ?
    dev = usb.core.find(idVendor=0x0419, idProduct=0x3c00)
    result['device_found'] = dev is not None
    
    if not result['device_found']:
        result['message'] = "Imprimante non détectée sur USB"
        return result
    
    # 2. Règle udev
    try:
        proc = subprocess.run(
            ['ls', '-l', f'/dev/bus/usb/{dev.bus:03d}/'],
            capture_output=True, text=True, timeout=5
        )
        result['udev_ok'] = 'plugdev' in proc.stdout or 'rw-rw-rw-' in proc.stdout
    except:
        result['udev_ok'] = False
    
    # 3. Groupes utilisateur
    try:
        proc = subprocess.run(['groups'], capture_output=True, text=True)
        result['groups'] = proc.stdout.strip().split(': ')[1].split() if proc.returncode == 0 else []
    except:
        pass
    
    # 4. CUPS actif ?
    try:
        proc = subprocess.run(
            ['systemctl', 'is-active', 'cups'],
            capture_output=True, text=True
        )
        result['cups_active'] = proc.stdout.strip() == 'active'
    except:
        pass
    
    # 5. Synthèse
    if result['device_found'] and result['udev_ok']:
        result['ok'] = True
        result['message'] = "Configuration USB OK"
    else:
        issues = []
        if not result['udev_ok']:
            issues.append("permissions udev")
        if result['cups_active']:
            issues.append("CUPS actif (conflit possible)")
        result['message'] = f"Problèmes: {', '.join(issues)}" if issues else "Configuration incomplète"
    
    return result