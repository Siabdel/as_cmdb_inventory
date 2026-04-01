Voici le rapport Markdown généré sous forme de Cheatsheet. Tu peux également **télécharger le fichier directement ici : [rapport_final_imprimantes.md](https://www.perplexity.ai/search/rapport_final_imprimantes.md)**.

# 🛠️ Cheatsheet : Gestion Imprimantes Thermiques & Linux (Projet CMDB)

Ce rapport compile toutes les commandes système, diagnostics USB, et configurations abordés pour faire fonctionner les imprimantes thermiques (Bixolon, Epson, Mini 5809D) avec Python/Django sous Debian/Linux.

------

## 1. Détection et Diagnostic USB (Hardware)

Ces commandes permettent de vérifier que l'imprimante est bien vue par le système et d'obtenir ses identifiants (VID:PID) et Endpoints.

```shell
bashlsusb                                     # Liste tous les périphériques USB connectés
lsusb | grep -i "samsung\|epson"          # Filtre pour trouver rapidement l'imprimante
lsusb -v -d 0419:3c00                     # Affiche les infos détaillées d'un device précis (ex: SRP-350)
lsusb -vvv -d 0419:3c00 | grep -E "bInterfaceNumber|bEndpointAddress|bConfigurationValue" # Trouve les Endpoints (in_ep, out_ep)
ls -la /dev/usb/lp*                       # Vérifie si le device est monté comme imprimante USB (et ses droits)
dmesg -w                                  # Suit les logs Kernel en temps réel (utile pour voir si l'imprimante se déconnecte - Errno 19)
```

## 2. Gestion des Permissions (Udev & Groupes)

Indispensable pour éviter l'erreur `[Errno 13] Access denied` avec `python-escpos`.

```shell
bash# Vérifier ses groupes actuels
groups

# Ajouter l'utilisateur 'django' au groupe plugdev (ou lp)
sudo usermod -aG plugdev django
newgrp plugdev                            # Appliquer le groupe sans se déconnecter

# Créer une règle udev pour autoriser l'accès USB (Exemple Bixolon)
sudo tee /etc/udev/rules.d/99-srp350.rules <<EOF
SUBSYSTEM=="usb", ATTR{idVendor}=="0419", ATTR{idProduct}=="3c00", MODE="0666", GROUP="plugdev"
EOF

# Recharger les règles udev après modification
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## 3. Gestion du Spooler CUPS (Résolution de conflits)

CUPS peut monopoliser le port USB (Erreur `[Errno 16] Resource busy`).

```shell
bashsudo systemctl stop cups                  # Arrête temporairement CUPS pour libérer le port USB
sudo systemctl stop cups-browsed          # Arrête le service de découverte réseau CUPS
lpstat -p -d -t                           # Affiche l'état des imprimantes CUPS, files d'attente et jobs
lpadmin -p SRP350 -E -v usb://...         # Ajoute ou modifie une imprimante en ligne de commande
cupsctl --remote-admin                    # Autorise l'administration CUPS à distance (port 631)
```

## 4. Tests d'Impression Bas Niveau (Raw)

Pour tester si le matériel répond indépendamment de Python.

```shell
bash# Envoi direct de commandes ESC/POS hexa au port /dev/usb/lp0
echo -ne '\x1b\x40TEST\n\x1d\x56\x41\x00' > /tmp/test.raw
sudo dd if=/tmp/test.raw of=/dev/usb/lp0 bs=1
```

## 5. Gestion de l'Environnement Python

Pour éviter le `ModuleNotFoundError` dû à l'utilisation de `sudo` avec un Virtualenv.

```shell
bashwhich python                              # Vérifie quel interpréteur Python est actif
source /chemin/vers/envCMDBIventory/bin/activate  # Active le virtualenv
python -m pip show python-escpos          # Vérifie si le module est installé au bon endroit
# Ne JAMAIS faire : sudo python script.py (cela sort du venv, créant l'erreur de module introuvable)
```

------

## 📦 SECTION PACKAGES UTILES À INSTALLER

## Packages Système (Debian/Ubuntu via `apt`)

```shell
bashsudo apt update
# Dépendances requises pour compiler pycups et utiliser libusb :
sudo apt install libusb-1.0-0-dev libudev-dev libcups2-dev libcupsimage2-dev build-essential python3-dev

# Drivers d'impression (si on passe par CUPS au lieu de direct USB) :
sudo apt install printer-driver-brlaser   # Pilotes pour imprimantes Brother (laser)
sudo apt install printer-driver-escpos    # Pilotes génériques pour imprimantes thermiques (Epson, Bixolon...)
sudo apt install cups cups-client         # Spooler d'impression standard et ses commandes (lp, lpstat)
```

## Packages Python (via `pip`)

À exécuter **dans le virtualenv** du projet CMDB :

```shell
bashpip install --upgrade python-escpos       # Librairie principale pour imprimer tickets et QR codes
pip install --upgrade pyusb               # Communication USB bas niveau (nécessaire pour escpos)
pip install --upgrade pycups              # API Python pour interagir avec CUPS (nécessite libcups2-dev)
```

------

## 📊 TABLEAU DE SYNTHÈSE GLOBAL

| Composant / Matériel      | Rôle / Caractéristique                          | Problèmes rencontrés & Solutions                             |
| ------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| **Bixolon SRP-350**       | Imprimante thermique 80mm de base.              | **Access Denied (Err 13)** $\rightarrow$ Créer règle `udev`. **Resource Busy (Err 16)** $\rightarrow$ Arrêter CUPS. |
| **Epson TM-T20III**       | Imprimante 80mm recommandée.                    | Excellent support direct via `profile="TM-T20II"`.           |
| **Epson TM-H6000II**      | Machine de caisse lourde/hybride.               | Imprime les reçus thermiques mais plus complexe.             |
| **Mini POS-5809D**        | Portable (58mm) sur batterie.                   | Parfaite pour mobilité CMDB. Driver générique ESC/POS.       |
| **libusb / pyusb**        | Connecteur direct Python $\leftrightarrow$ USB. | L'accès "Raw" évite les marges forcées par CUPS pour les QR. |
| **Virtualenv (venv)**     | Isolateur de dépendances Python.                | L'utilisation de `sudo python` perd le contexte du `venv`.   |
| **staff_member_required** | Sécurisation des vues d'impression.             | *Code:* Importer de `django.contrib.admin.views.decorators`. |