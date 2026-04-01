# 📖 Manuel Technique - Application d'Impression CMDB

## Système d'Impression d'Étiquettes Code-Barres & QR Code

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#1-vue-densemble)
2. [Architecture du Système](#2-architecture-du-système)
3. [Composants Backend](#3-composants-backend)
4. [API Endpoints](#4-api-endpoints)
5. [Interface Utilisateur (Frontend)](#5-interface-utilisateur-frontend)
6. [Algorithme d'Impression](#6-algorithme-dimpression)
7. [Flux de Données Complet](#7-flux-de-données-complet)
8. [Configuration & Déploiement](#8-configuration--déploiement)

---

## 1. Vue d'Ensemble

### 1.1 Objectif
Application Django permettant l'impression d'étiquettes d'inventaire CMDB avec:
- **QR Code** contenant l'URL de l'asset
- **Code-barres CODE128** avec l'identifiant
- **Informations textuelles** (Asset ID, localisation, date)

### 1.2 Matériel Supporté
- **Imprimante**: Bixolon/Samsung SRP-350 (thermique)
- **Interface**: USB direct (pyusb)
- **Résolution**: 203 DPI
- **Largeur papier**: 80mm

### 1.3 Stack Technologique
```
Backend:  Django 4.x + Django REST Framework
Frontend: Bootstrap 5 + JavaScript (Fetch API)
USB:      pyusb + commandes ESC/POS natives
Base:     PostgreSQL (modèle Asset)
```

---

## 2. Architecture du Système

### 2.1 Diagramme d'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  landingpage.html (Bootstrap 5 Responsive)          │   │
│  │  - Liste des assets                                 │   │
│  │  - Bouton "Imprimer Étiquette"                      │   │
│  │  - Modal de confirmation                            │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │ HTTP/JSON (AJAX)
┌─────────────────────▼──────────────────────────────────────┐
│                    COUCHE API (DRF)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ViewSets & Serializers                             │   │
│  │  - AssetViewSet (CRUD)                              │   │
│  │  - PrintLabelViewSet (Impression)                   │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│                COUCHE MÉTIER (Services)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PrinterFactory                                     │   │
│  │  BixolonSRP350 (Driver USB)                         │   │
│  │  - Génération QR Code natif ESC/POS                 │   │
│  │  - Génération Code-barres natif                     │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │ USB (pyusb)
┌─────────────────────▼──────────────────────────────────────┐
│                    MATÉRIEL                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Bixolon SRP-350                                    │   │
│  │  - Vendor ID: 0x0419                                │   │
│  │  - Product ID: 0x3c00                               │   │
│  │  - Interface: 0, EP OUT: 0x01, EP IN: 0x82         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Structure des Fichiers

```
as_cmdb_inventory/
├── backend/
│   ├── inventory/                    # App Gestion des Assets
│   │   ├── models.py                 # Modèle Asset
│   │   ├── api/
│   │   │   ├── serializers.py        # AssetSerializer
│   │   │   └── viewsets.py           # AssetViewSet
│   │   └── templates/
│   │       └── inventory/
│   │           └── landingpage.html  # UI Principale
│   │
│   ├── printer/                      # App Impression (NOUVELLE)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                 # PrintJob (historique)
│   │   ├── admin.py
│   │   │
│   │   ├── api/                      # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py        # PrintLabelSerializer
│   │   │   ├── viewsets.py           # PrintLabelViewSet
│   │   │   └── urls.py               # Router DRF
│   │   │
│   │   ├── services/                 # Drivers Imprimantes
│   │   │   ├── __init__.py
│   │   │   ├── printer_base.py       # AbstractBasePrinter
│   │   │   ├── bixolon_srp350.py     # Driver SRP-350
│   │   │   └── factory.py            # PrinterFactory
│   │   │
│   │   ├── utils/                    # Utilitaires
│   │   │   ├── __init__.py
│   │   │   ├── escpos_commands.py    # Constantes ESC/POS
│   │   │   └── usb_permissions.py    # Vérif permissions
│   │   │
│   │   ├── migrations/
│   │   └── tests/
│   │
│   ├── settings.py                   # Config Django
│   ├── urls.py                       # URLs principales
│   └── middleware.py                 # CSRF exemption API
│
└── manage.py
```

---

## 3. Composants Backend

### 3.1 Modèle de Données

#### `inventory/models.py`

```python
from django.db import models

class Asset(models.Model):
    """Modèle représentant un asset IT dans la CMDB"""
    
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_asset'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.id} - {self.name}"
    
    @property
    def qr_url(self):
        """URL pour le QR Code (auto-générée)"""
        from django.conf import settings
        base_url = getattr(settings, 'CMDB_BASE_URL', 'http://localhost:8000')
        return f"{base_url}/assets/{self.id}"
    
    @property
    def barcode_value(self):
        """Valeur du code-barres (format standardisé)"""
        return f"ASSET{self.id.replace('-', '').upper()}"
```

#### `printer/models.py`

```python
from django.db import models
from django.conf import settings

class PrintJob(models.Model):
    """Historique des impressions"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('success', 'Succès'),
        ('failed', 'Échoué'),
    ]
    
    asset = models.ForeignKey('inventory.Asset', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    printed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    copies = models.IntegerField(default=1)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'printer_printjob'
        ordering = ['-printed_at']
```

---

### 3.2 Serializers

#### `printer/api/serializers.py`

```python
from rest_framework import serializers
from django.conf import settings
from inventory.models import Asset

class PrintLabelSerializer(serializers.Serializer):
    """
    Serializer pour la demande d'impression
    
    Auto-génère qr_content et barcode_content si non fournis
    """
    
    asset_id = serializers.CharField(
        max_length=100,
        required=True,
        help_text="ID de l'asset (clé primaire)"
    )
    
    qr_content = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Texte pour QR Code (auto-généré si vide)"
    )
    
    barcode_content = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Texte pour code-barres (auto-généré si vide)"
    )
    
    custom_text = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Texte additionnel (localisation, etc.)"
    )
    
    copies = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        default=1,
        help_text="Nombre de copies (1-5)"
    )
    
    def validate_asset_id(self, value):
        """Vérifier que l'asset existe"""
        if not Asset.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Asset '{value}' introuvable dans la CMDB"
            )
        return value
    
    def validate_qr_content(self, value):
        """
        Auto-générer l'URL QR si non fournie
        Ex: http://cmdb.local/assets/210
        """
        if not value:  # Si vide, None, ou ""
            asset_id = self.initial_data.get('asset_id')
            if asset_id:
                base_url = getattr(settings, 'CMDB_BASE_URL', 'http://localhost:8000')
                value = f"{base_url}/assets/{asset_id}"
        return value
    
    def validate_barcode_content(self, value):
        """Auto-générer le code-barres si vide"""
        if not value:
            asset_id = self.initial_data.get('asset_id')
            if asset_id:
                value = f"ASSET{str(asset_id).replace('-', '').upper()}"
        return value
```

---

### 3.3 ViewSets API

#### `printer/api/viewsets.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone
import logging
import time

from .serializers import PrintLabelSerializer
from ..services.factory import PrinterFactory
from ..utils.usb_permissions import check_usb_permissions
from ..models import PrintJob

logger = logging.getLogger(__name__)

class PrintLabelViewSet(viewsets.GenericViewSet):
    """
    ViewSet pour l'impression d'étiquettes CMDB
    
    Endpoints:
    - POST /api/printer/labels/ : Imprimer une étiquette
    - GET  /api/printer/labels/status/ : État de l'imprimante
    """
    
    serializer_class = PrintLabelSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Endpoint principal: Imprimer une ou plusieurs étiquettes
        
        Algorithme:
        1. Valider les données entrantes
        2. Auto-générer qr_content/barcode_content si vides
        3. Vérifier les permissions USB
        4. Connecter à l'imprimante via USB
        5. Boucle d'impression pour copies multiples
        6. Enregistrer dans l'historique (PrintJob)
        7. Retourner la réponse JSON
        """
        
        # 1. Validation serializer (auto-génération incluse)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        asset_id = data['asset_id']
        copies = data.get('copies', 1)
        
        logger.info(f"Demande impression asset {asset_id} par {request.user}")
        
        # 2. Créer un PrintJob pour l'historique
        print_job = PrintJob.objects.create(
            asset_id=asset_id,
            user=request.user,
            copies=copies,
            status='pending'
        )
        
        # 3. Vérification permissions USB
        usb_check = check_usb_permissions()
        if not usb_check.get('ok'):
            logger.warning(f"Permissions USB: {usb_check.get('message')}")
        
        try:
            # 4. Instancier l'imprimante via Factory
            printer = PrinterFactory.create(
                model=data.get('printer_model', 'bixolon_srp350')
            )
            
            # 5. Connexion USB
            if not printer.connect(max_retries=2):
                print_job.status = 'failed'
                print_job.error_message = 'Imprimante non connectée'
                print_job.save()
                
                return Response(
                    {'status': 'error', 'message': 'Imprimante non connectée'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # 6. Boucle d'impression (copies multiples)
            printed = 0
            for i in range(copies):
                success = printer.print_cmdb_label(
                    asset_id=asset_id,
                    qr_data=data.get('qr_content'),      # ← Auto-généré
                    barcode_data=data.get('barcode_content'),  # ← Auto-généré
                    custom_text=data.get('custom_text')
                )
                
                if success:
                    printed += 1
                    logger.debug(f"Copie {i+1}/{copies} imprimée")
                else:
                    logger.error(f"Échec copie {i+1}/{copies}")
                    break
                
                # Pause entre copies (mécanique de coupe)
                if i < copies - 1:
                    time.sleep(0.8)
            
            printer.close()
            
            # 7. Mettre à jour PrintJob
            if printed > 0:
                print_job.status = 'success'
                print_job.save()
                
                logger.info(f"✅ {printed}/{copies} étiquette(s) imprimée(s)")
                
                return Response({
                    'status': 'success',
                    'message': f"{printed} étiquette(s) imprimée(s)",
                    'data': {
                        'asset_id': asset_id,
                        'qr_content': data.get('qr_content'),
                        'barcode_content': data.get('barcode_content'),
                        'printed_copies': printed,
                        'printed_at': timezone.now().isoformat()
                    }
                }, status=status.HTTP_200_OK)
            else:
                print_job.status = 'failed'
                print_job.error_message = 'Échec complet'
                print_job.save()
                
                return Response(
                    {'status': 'error', 'message': 'Échec d\'impression'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.exception(f"Erreur critique: {e}")
            print_job.status = 'failed'
            print_job.error_message = str(e)
            print_job.save()
            
            return Response(
                {'status': 'error', 'message': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='status')
    def printer_status(self, request):
        """Endpoint de diagnostic: état imprimante + USB"""
        usb_info = check_usb_permissions()
        
        return Response({
            'printer': {
                'status': 'online' if usb_info.get('device_found') else 'offline',
                'model': 'bixolon_srp350',
                'usb': usb_info
            },
            'permissions': {
                'user_groups': usb_info.get('groups', []),
                'udev_ok': usb_info.get('udev_ok', False)
            }
        }, status=status.HTTP_200_OK)
```

---

### 3.4 Service d'Impression (Driver USB)

#### `printer/services/bixolon_srp350.py`

```python
"""
Driver pour Bixolon SRP-350 via USB direct (pyusb)
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
```

---

## 4. API Endpoints

### 4.1 endpoints Disponibles

| Méthode | Endpoint                             | Description              | Auth |
| ------- | ------------------------------------ | ------------------------ | ---- |
| `GET`   | `/api/v1/assets/`                    | Liste tous les assets    | Oui  |
| `GET`   | `/api/v1/assets/{id}/`               | Détails d'un asset       | Oui  |
| `POST`  | `/api/v1/assets/{id}/generate-code/` | Génère QR/barcode (JSON) | Oui  |
| `POST`  | `/api/printer/labels/`               | **Imprime étiquette**    | Oui  |
| `GET`   | `/api/printer/labels/status/`        | État imprimante          | Oui  |

---

### 4.2 Endpoint Principal: Impression

#### **`POST /api/printer/labels/`**

**Description**: Imprime une étiquette pour un asset donné

**Headers**:
```http
Content-Type: application/json
Authorization: Token <votre_token>
```

**Body Request**:
```json
{
  "asset_id": "210",
  "qr_content": "http://cmdb.local/assets/210",  // Optionnel (auto-généré)
  "barcode_content": "ASSET210",                  // Optionnel (auto-généré)
  "custom_text": "Rack A3 - Slot 12",            // Optionnel
  "copies": 1                                     // Optionnel (1-5)
}
```

**Response Succès (HTTP 200)**:
```json
{
  "status": "success",
  "message": "1 étiquette(s) imprimée(s) pour l'asset 210",
  "data": {
    "asset_id": "210",
    "qr_content": "http://cmdb.local/assets/210",
    "barcode_content": "ASSET210",
    "printed_copies": 1,
    "printed_at": "2026-03-30T01:30:45.123456"
  }
}
```

**Response Erreur (HTTP 503)**:
```json
{
  "status": "error",
  "message": "Imprimante non connectée"
}
```

---

### 4.3 Endpoint: Génération QR Code (JSON uniquement)

#### **`POST /api/v1/assets/210/generate-code/`**

**Description**: Génère les données QR/barcode sans imprimer

**Request**:
```json
{
  "asset_id": "210"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "asset_id": "210",
    "qr_content": "http://cmdb.local/assets/210",
    "barcode_content": "ASSET210",
    "qr_image_base64": "iVBORw0KGgoAAAANS...",  // Optionnel
    "barcode_image_base64": "iVBORw0KGgoAAAANS..."  // Optionnel
  }
}
```

---

## 5. Interface Utilisateur (Frontend)

### 5.1 landingpage.html - Structure

```html
<!-- inventory/templates/inventory/landingpage.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMDB Inventory - Gestion des Assets</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        .asset-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .asset-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .printer-status-online { color: #28a745; }
        .printer-status-offline { color: #dc3545; }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-server"></i> CMDB Inventory
            </a>
            <div class="navbar-nav ms-auto">
                <span class="nav-link" id="printerStatus">
                    <i class="fas fa-print"></i> 
                    <span class="badge bg-secondary">Vérification...</span>
                </span>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mt-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <h2><i class="fas fa-list"></i> Liste des Assets</h2>
                <p class="text-muted">Cliquez sur un asset pour imprimer son étiquette</p>
            </div>
        </div>

        <!-- Assets Grid -->
        <div class="row" id="assetsGrid">
            <!-- Les assets seront injectés ici par JavaScript -->
        </div>

        <!-- Loading Spinner -->
        <div class="text-center mt-5" id="loadingSpinner" style="display:none;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
        </div>
    </div>

    <!-- Modal Confirmation Impression -->
    <div class="modal fade" id="printModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-print"></i> Confirmer l'impression
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <strong>Asset ID:</strong> <span id="modalAssetId"></span>
                    </div>
                    <div class="mb-3">
                        <strong>Nom:</strong> <span id="modalAssetName"></span>
                    </div>
                    <div class="mb-3">
                        <strong>Localisation:</strong> <span id="modalAssetLocation"></span>
                    </div>
                    <div class="mb-3">
                        <strong>QR Code:</strong><br>
                        <small class="text-muted" id="modalQRContent"></small>
                    </div>
                    <div class="mb-3">
                        <label for="copiesInput" class="form-label">Nombre de copies:</label>
                        <input type="number" class="form-control" id="copiesInput" 
                               min="1" max="5" value="1">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        Annuler
                    </button>
                    <button type="button" class="btn btn-primary" id="confirmPrintBtn">
                        <i class="fas fa-print"></i> Imprimer
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="liveToast" class="toast" role="alert">
            <div class="toast-header">
                <i class="fas fa-info-circle me-2"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body" id="toastMessage"></div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="{% static 'js/printer.js' %}"></script>
</body>
</html>
```

---

### 5.2 JavaScript: printer.js

```javascript
/**
 * printer.js - Gestion de l'interface et appels API
 */

// Configuration
const API_BASE_URL = '/api';
let authToken = null;
let currentAsset = null;
let printModal = null;

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer le token CSRF Django
    const csrftoken = getCookie('csrftoken');
    
    // Initialiser le modal
    printModal = new bootstrap.Modal(document.getElementById('printModal'));
    
    // Charger les assets
    loadAssets();
    
    // Vérifier l'état de l'imprimante
    checkPrinterStatus();
    
    // Écouteur bouton impression
    document.getElementById('confirmPrintBtn').addEventListener('click', handlePrint);
});

/**
 * Charger la liste des assets depuis l'API
 */
async function loadAssets() {
    const grid = document.getElementById('assetsGrid');
    const spinner = document.getElementById('loadingSpinner');
    
    spinner.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/v1/assets/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (!response.ok) throw new Error('Erreur chargement assets');
        
        const assets = await response.json();
        
        // Générer le HTML pour chaque asset
        grid.innerHTML = assets.map(asset => `
            <div class="col-md-4 mb-4">
                <div class="card asset-card" onclick="openPrintModal('${asset.id}')">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h5 class="card-title mb-0">${asset.id}</h5>
                            <span class="badge bg-${asset.status === 'active' ? 'success' : 'secondary'}">
                                ${asset.status}
                            </span>
                        </div>
                        <p class="card-text text-muted mb-1">${asset.name}</p>
                        <p class="card-text small text-muted mb-3">
                            <i class="fas fa-map-marker-alt"></i> ${asset.location || 'Non spécifié'}
                        </p>
                        <button class="btn btn-sm btn-primary w-100" onclick="event.stopPropagation(); openPrintModal('${asset.id}')">
                            <i class="fas fa-print"></i> Imprimer étiquette
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Erreur:', error);
        showToast('Erreur de chargement des assets', 'danger');
    } finally {
        spinner.style.display = 'none';
    }
}

/**
 * Ouvrir le modal de confirmation d'impression
 */
async function openPrintModal(assetId) {
    // Trouver l'asset dans la liste
    const response = await fetch(`${API_BASE_URL}/v1/assets/${assetId}/`, {
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    
    if (!response.ok) {
        showToast('Asset non trouvé', 'danger');
        return;
    }
    
    const asset = await response.json();
    currentAsset = asset;
    
    // Remplir le modal
    document.getElementById('modalAssetId').textContent = asset.id;
    document.getElementById('modalAssetName').textContent = asset.name;
    document.getElementById('modalAssetLocation').textContent = asset.location || 'N/A';
    document.getElementById('modalQRContent').textContent = 
        `http://cmdb.local/assets/${asset.id}`;
    document.getElementById('copiesInput').value = 1;
    
    // Afficher le modal
    printModal.show();
}

/**
 * Gérer l'impression (appel API)
 */
async function handlePrint() {
    if (!currentAsset) return;
    
    const copies = parseInt(document.getElementById('copiesInput').value);
    const btn = document.getElementById('confirmPrintBtn');
    
    // Désactiver le bouton pendant l'impression
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Impression...';
    
    try {
        const payload = {
            asset_id: currentAsset.id,
            qr_content: `http://cmdb.local/assets/${currentAsset.id}`,
            barcode_content: `ASSET${currentAsset.id.replace('-', '').toUpperCase()}`,
            custom_text: currentAsset.location || '',
            copies: copies
        };
        
        const response = await fetch(`${API_BASE_URL}/printer/labels/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'Authorization': `Token ${authToken}`  // Si TokenAuth utilisé
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            showToast(`✅ ${result.message}`, 'success');
            printModal.hide();
        } else {
            showToast(`❌ Erreur: ${result.message}`, 'danger');
        }
        
    } catch (error) {
        console.error('Erreur impression:', error);
        showToast('Erreur de connexion au serveur', 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-print"></i> Imprimer';
    }
}

/**
 * Vérifier l'état de l'imprimante
 */
async function checkPrinterStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/printer/labels/status/`, {
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        
        const data = await response.json();
        const statusEl = document.getElementById('printerStatus');
        
        if (data.printer.status === 'online') {
            statusEl.innerHTML = `
                <i class="fas fa-print printer-status-online"></i>
                <span class="badge bg-success">Imprimante prête</span>
            `;
        } else {
            statusEl.innerHTML = `
                <i class="fas fa-print printer-status-offline"></i>
                <span class="badge bg-danger">Hors ligne</span>
            `;
        }
        
    } catch (error) {
        console.error('Erreur status:', error);
    }
}

/**
 * Afficher une notification toast
 */
function showToast(message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
    toastEl.classList.add(`bg-${type}`, 'text-white');
    
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

/**
 * Utility: Récupérer un cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

---

## 6. Algorithme d'Impression

### 6.1 Workflow Complet (Asset ID=210)

```
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 1: UTILISATEUR (UI)                                   │
├─────────────────────────────────────────────────────────────┤
│ 1.1 Affichage landingpage.html                              │
│     - Requête GET /api/v1/assets/                           │
│     - Affichage grille Bootstrap responsive                 │
│                                                             │
│ 1.2 Clic sur asset "210"                                    │
│     - Ouvre modal de confirmation                           │
│     - Affiche:                                              │
│       • Asset ID: 210                                       │
│       • Nom: Serveur Web Prod                               │
│       • Localisation: Rack A3 - Slot 12                     │
│       • QR URL: http://cmdb.local/assets/210                │
│       • Nombre de copies: [1]                               │
│                                                             │
│ 1.3 Clic "Imprimer"                                         │
│     - Déclenche handlePrint()                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 2: FRONTEND (JavaScript)                              │
├─────────────────────────────────────────────────────────────┤
│ 2.1 Construction payload JSON:                              │
│     {                                                       │
│       "asset_id": "210",                                    │
│       "qr_content": "http://cmdb.local/assets/210",         │
│       "barcode_content": "ASSET210",                        │
│       "custom_text": "Rack A3 - Slot 12",                   │
│       "copies": 1                                           │
│     }                                                       │
│                                                             │
│ 2.2 Appel API fetch():                                      │
│     POST /api/printer/labels/                               │
│     Headers:                                                │
│       • Content-Type: application/json                      │
│       • X-CSRFToken: <token_django>                         │
│       • Authorization: Token <token>                        │
│     Body: JSON.stringify(payload)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 3: BACKEND DJANGO (PrintLabelViewSet)                 │
├─────────────────────────────────────────────────────────────┤
│ 3.1 Validation serializer:                                  │
│     - PrintLabelSerializer.is_valid()                       │
│     - Vérifie asset_id existe en DB                         │
│     - Auto-génère qr_content si vide                        │
│     - Auto-génère barcode_content si vide                   │
│                                                             │
│ 3.2 Création PrintJob (historique):                         │
│     PrintJob.objects.create(                                │
│         asset_id="210",                                     │
│         user=request.user,                                  │
│         status="pending"                                    │
│     )                                                       │
│                                                             │
│ 3.3 Vérification permissions USB:                           │
│     check_usb_permissions()                                 │
│     - Vérifie device 0419:3c00 présent                      │
│     - Vérifie règle udev (MODE="0666")                      │
│     - Vérifie groupe plugdev                                │
│                                                             │
│ 3.4 Instanciation imprimante:                               │
│     printer = PrinterFactory.create('bixolon_srp350')       │
│                                                             │
│ 3.5 Connexion USB:                                          │
│     printer.connect(max_retries=2)                          │
│     a) usb.core.find(idVendor=0x0419, idProduct=0x3c00)     │
│     b) Si kernel driver actif (usblp):                      │
│        device.detach_kernel_driver(0)                       │
│     c) usb.util.claim_interface(device, 0)                  │
│     d) Retourne True si succès                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 4: SERVICE D'IMPRESSION (BixolonSRP350)               │
├─────────────────────────────────────────────────────────────┤
│ 4.1 print_cmdb_label(                                       │
│       asset_id="210",                                       │
│       qr_data="http://cmdb.local/assets/210",               │
│       barcode_data="ASSET210",                              │
│       custom_text="Rack A3 - Slot 12"                       │
│     )                                                       │
│                                                             │
│ 4.2 Séquence ESC/POS envoyée via USB:                       │
│                                                             │
│     a) Reset imprimante:                                    │
│        _write(ESCPOS.INIT)  // \x1b\x40                     │
│                                                             │
│     b) En-tête centrée:                                     │
│        _write(\x1b\x61\x01)  // Alignement centre           │
│        _write(\x1b\x45\x01)  // Gras ON                    │
│        _write(\x1b\x21\x30)  // Double hauteur/largeur      │
│        _write("CMDB INVENTORY\n")                           │
│        _write(\x1b\x45\x00)  // Gras OFF                   │
│        _write(\x1b\x21\x00)  // Double OFF                 │
│                                                             │
│     c) QR Code natif (si qr_data):                          │
│        _print_native_qr("http://cmdb.local/assets/210")     │
│        Séquence ESC/POS:                                    │
│          \x1d\x28\x6b\x04\x00\x31\x41\x32\x00  (Modèle 2)   │
│          \x1d\x28\x6b\x03\x00\x31\x43\x08      (Taille 8)   │
│          \x1d\x28\x6b\x03\x00\x31\x45\x30      (Correction L)│
│          \x1d\x28\x6b + [longueur+3, 0, 0x31, 0x50, 0x30]   │
│          + "http://cmdb.local/assets/210"       (Données)   │
│          \x1d\x28\x6b\x03\x00\x31\x51\x30      (Imprimer)   │
│                                                             │
│     d) Code-barres natif (si barcode_data):                 │
│        _print_native_barcode("ASSET210")                    │
│        Séquence:                                            │
│          \x1d\x6b\x49 + [7] + "ASSET210" + \x00             │
│          (GS k m=0x49 CODE128, n=7, données, NUL)           │
│                                                             │
│     e) Détails asset:                                       │
│        _write(\x1b\x61\x00)  // Alignement gauche           │
│        _write("Asset ID: 210\n")                            │
│        _write("Rack A3 - Slot 12\n")                        │
│        _write("Date: 2026-03-30 01:30\n")                   │
│        _write("\n\n\n")  // Espacement                      │
│                                                             │
│     f) Coupe papier:                                        │
│        _write(\x1d\x56\x42\x00)  // GS V 42 00              │
│        time.sleep(1)  // Attendre mécanique                 │
│                                                             │
│ 4.3 Écriture USB:                                           │
│     device.write(OUT_EP=0x01, data, timeout=5000)           │
│     → Données envoyées sur le bus USB vers l'imprimante     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 5: IMPRIMANTE (Bixolon SRP-350)                       │
├─────────────────────────────────────────────────────────────┤
│ 5.1 Réception données USB (Endpoint Bulk IN 0x82)           │
│                                                             │
│ 5.2 Interprétation commandes ESC/POS:                       │
│     - Reset: initialise l'imprimante                        │
│     - Alignement: centre/gauche le texte                    │
│     - Style: gras, double taille                            │
│     - QR Code: génère matrice 2D native                     │
│     - Barcode: génère barres CODE128 native                 │
│     - Texte: imprime caractères ASCII                       │
│     - Coupe: active le cutter après 3 sauts de ligne        │
│                                                             │
│ 5.3 Impression physique:                                    │
│     ┌─────────────────────────┐                             │
│     │   CMDB INVENTORY        │ ← En-tête centrée           │
│     │                         │                             │
│     │   ████████ ████████     │ ← QR Code natif             │
│     │   ██  ██  ██ ██  ██     │   (URL encodée)             │
│     │   ████████ ████████     │                             │
│     │                         │                             │
│     │   |||| || |||| ||||     │ ← Code-barres CODE128       │
│     │   ASSET210              │   (texte sous barres)       │
│     │                         │                             │
│     │   Asset ID: 210         │ ← Détails                   │
│     │   Rack A3 - Slot 12     │                             │
│     │   Date: 2026-03-30 01:30│                             │
│     │                         │                             │
│     └─────────────────────────┘                             │
│                           ✂️ ← Coupe automatique            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 6: RETOUR BACKEND → FRONTEND                          │
├─────────────────────────────────────────────────────────────┤
│ 6.1 Mise à jour PrintJob:                                   │
│     print_job.status = 'success'                            │
│     print_job.save()                                        │
│                                                             │
│ 6.2 Fermeture connexion:                                    │
│     printer.close()                                         │
│     → usb.util.release_interface(device, 0)                 │
│                                                             │
│ 6.3 Réponse JSON au frontend:                               │
│     HTTP 200 OK                                             │
│     {                                                       │
│       "status": "success",                                  │
│       "message": "1 étiquette(s) imprimée(s)",              │
│       "data": {                                             │
│         "asset_id": "210",                                  │
│         "qr_content": "http://cmdb.local/assets/210",       │
│         "barcode_content": "ASSET210",                      │
│         "printed_copies": 1,                                │
│         "printed_at": "2026-03-30T01:30:45.123456"          │
│       }                                                     │
│     }                                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 7: FRONTEND (Notification Utilisateur)                │
├─────────────────────────────────────────────────────────────┤
│ 7.1 Réception réponse fetch()                               │
│                                                             │
│ 7.2 Affichage toast Bootstrap:                              │
│     showToast("✅ 1 étiquette(s) imprimée(s)", "success")   │
│                                                             │
│ 7.3 Fermeture modal:                                        │
│     printModal.hide()                                       │
│                                                             │
│ 7.4 Réactivation bouton:                                    │
│     btn.disabled = false                                    │
│     btn.innerHTML = '<i class="fas fa-print"></i> Imprimer' │
│                                                             │
│ ✅ FIN DU PROCESSUS                                         │
└─────────────────────────────────────────────────────────────┘
```

---

### 6.2 Algorithme de Génération QR Code (ESC/POS)

```python
# Pseudo-code de l'algorithme _print_native_qr()

def _print_native_qr(qr_data, size=8):
    """
    Algorithme de génération QR Code natif ESC/POS
    
    Entrée: qr_data = "http://cmdb.local/assets/210"
    Sortie: QR Code imprimé sur papier thermique
    """
    
    # 1. Encodage des données
    data_bytes = qr_data.encode('utf-8')
    data_len = len(data_bytes)  # Ex: 34 bytes
    
    # 2. Sélection du modèle QR Code (Modèle 2)
    # Commande: GS ( k 04 00 31 41 32 00
    write_bytes([0x1D, 0x28, 0x6B, 0x04, 0x00, 0x31, 0x41, 0x32, 0x00])
    
    # 3. Définir la taille du module (4-8 pixels)
    # Commande: GS ( k 03 00 31 43 size
    write_bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, size])
    # size=8 → module de 8x8 pixels
    
    # 4. Définir le niveau de correction d'erreur
    # L (7%), M (15%), Q (25%), H (30%)
    # Commande: GS ( k 03 00 31 45 ec
    ec_level = 0x30  # L = 0x30
    write_bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, ec_level])
    
    # 5. Stocker les données dans le symbole QR
    # Format: GS ( k pL pH cn fn m d1...dk
    # pL+pH = longueur des données + 3 (low byte, high byte)
    # cn=0x31, fn=0x50, m=0x30 pour stockage
    
    pL = (data_len + 3) % 256      # Low byte
    pH = (data_len + 3) // 256     # High byte
    
    write_bytes([0x1D, 0x28, 0x6B, pL, pH, 0x31, 0x50, 0x30])
    write_bytes(data_bytes)  # Les données URL
    
    # 6. Imprimer le QR Code
    # Commande: GS ( k 03 00 31 51 30
    write_bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x51, 0x30])
    
    # Résultat: QR Code imprimé nativement par l'imprimante
    # L'imprimante génère elle-même la matrice 2D
```

---

## 7. Flux de Données Complet

### 7.1 Diagramme de Séquence

```
Utilisateur    Frontend        Backend         Service         Imprimante
    │             │               │               │                 │
    │ Clic "210"  │               │               │                 │
    ├────────────>│               │               │                 │
    │             │               │               │                 │
    │             │GET /assets/210│               │                 │
    │             ├──────────────>│               │                 │
    │             │               │               │                 │
    │             │JSON asset     │               │                 │
    │             │<──────────────│               │                 │
    │             │               │               │                 │
    │             │Ouvre modal    │               │                 │
    │             │               │               │                 │
    │ Clic Print  │               │               │                 │
    │<────────────│               │               │                 │
    │             │               │               │                 │
    │             │POST /labels/  │               │                 │
    │             │{asset_id:210} │               │                 │
    │             ├──────────────>│               │                 │
    │             │               │               │                 │
    │             │               │Serializer     │                 │
    │             │               │validate()     │                 │
    │             │               ├──────────────>│                 │
    │             │               │               │                 │
    │             │               │qr_content auto│                 │
    │             │               │<──────────────│                 │
    │             │               │               │                 │
    │             │               │PrinterFactory │                 │
    │             │               │.create()      │                 │
    │             │               ├──────────────>│                 │
    │             │               │               │                 │
    │             │               │BixolonSRP350  │                 │
    │             │               │<──────────────│                 │
    │             │               │               │                 │
    │             │               │printer.connect()                │
    │             │               ├──────────────────────────────>│
    │             │               │               │                 │
    │             │               │               │usb.core.find()  │
    │             │               │               │detach_kernel()  │
    │             │               │               │claim_interface()│
    │             │               │               │                 │
    │             │               │               │<────────────────│
    │             │               │               │                 │
    │             │               │print_cmdb_label()               │
    │             │               ├──────────────────────────────>│
    │             │               │               │                 │
    │             │               │               │ESC/POS commands │
    │             │               │               │- INIT           │
    │             │               │               │- QR Code        │
    │             │               │               │- Barcode        │
    │             │               │               │- Text           │
    │             │               │               │- CUT            │
    │             │               │               │                 │
    │             │               │               │device.write()   │
    │             │               │               ├────────────────>│
    │             │               │               │                 │
    │             │               │               │                 │ Impression
    │             │               │               │                 │ physique
    │             │               │               │                 │ ✂️ Coupe
    │             │               │               │                 │
    │             │               │               │Success          │
    │             │               │               │<────────────────│
    │             │               │               │                 │
    │             │               │<───────────────────────────────│
    │             │               │               │                 │
    │             │               │PrintJob.save()│                 │
    │             │               │status=success │                 │
    │             │               │               │                 │
    │             │JSON response  │               │                 │
    │             │{status:ok}    │               │                 │
    │             │<──────────────│               │                 │
    │             │               │               │                 │
    │             │Toast "Succès" │               │                 │
    │             │               │               │                 │
    │<────────────│               │               │                 │
    │             │               │               │                 │
    │ Étiquette imprimée ✅       │               │                 │
```

---

## 8. Configuration & Déploiement

### 8.1 Prérequis Système

```bash
# Système d'exploitation
Debian 12 (Bookworm)

# Python
Python 3.11+

# Packages système
sudo apt install python3-pip libusb-1.0-0-dev pkg-config

# Permissions USB
sudo usermod -a -G lp,plugdev $USER
sudo usermod -a -G lp,plugdev www-data
```

---

### 8.2 Règles udev

```bash
# /etc/udev/rules.d/99-bixolon-srp350.rules
ATTR{idVendor}=="0419", ATTR{idProduct}=="3c00", MODE="0666", GROUP="lp", SYMLINK+="bixolon_srp350"

# Recharger les règles
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

### 8.3 Blacklist usblp

```bash
# /etc/modprobe.d/blacklist-usblp.conf
blacklist usblp
install usblp /bin/true

# Mettre à jour initramfs
sudo update-initramfs -u

# Redémarrer
sudo reboot
```

---

### 8.4 Installation Python

```bash
# Virtualenv
cd /home/django/Depots/www/projets/envCMDBIventory
source bin/activate

# Installer dépendances
pip install django djangorestframework pyusb pillow

# Ou via requirements.txt
pip install -r requirements.txt
```

**requirements.txt:**
```
Django>=4.2,<5.0
djangorestframework>=3.14
pyusb>=1.2
Pillow>=10.0
psycopg2-binary>=2.9
```

---

### 8.5 Configuration Django

```python
# backend/settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'inventory',
    'printer',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# URL base pour QR Codes
CMDB_BASE_URL = 'http://cmdb.local'  # ou os.getenv('CMDB_BASE_URL')

# Middleware CSRF
MIDDLEWARE = [
    # ...
    'backend.middleware.DisableCSRFForAPIMiddleware',
]
```

---

### 8.6 URLs Configuration

```python
# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # API Inventory
    path('api/v1/', include('inventory.api.urls')),
    
    # API Printer
    path('api/printer/', include('printer.api.urls')),
    
    # Landing page
    path('', include('inventory.urls')),
]
```

---

### 8.7 Tests

```bash
# Tester l'API
curl -X POST http://localhost:8000/api/printer/labels/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d '{"asset_id":"210"}'

# Tester l'impression directe
python3 -c "
from printer.services.bixolon_srp350 import BixolonSRP350
p = BixolonSRP350()
if p.connect():
    p.print_cmdb_label('210', qr_data='http://test/210')
    p.close()
"

# Logs
tail -f /var/log/cmdb/printer.log
```

---

## 📊 Résumé des Composants

| Composant              | Fichier                                | Rôle                         |
| ---------------------- | -------------------------------------- | ---------------------------- |
| **Modèle Asset**       | `inventory/models.py`                  | Stocke les assets IT         |
| **Modèle PrintJob**    | `printer/models.py`                    | Historique impressions       |
| **Serializer**         | `printer/api/serializers.py`           | Validation + auto-génération |
| **ViewSet**            | `printer/api/viewsets.py`              | Endpoints API REST           |
| **Driver USB**         | `printer/services/bixolon_srp350.py`   | Communication pyusb          |
| **Factory**            | `printer/services/factory.py`          | Instanciation drivers        |
| **Constantes ESC/POS** | `printer/utils/escpos_commands.py`     | Commandes imprimante         |
| **Permissions USB**    | `printer/utils/usb_permissions.py`     | Vérif udev/groups            |
| **UI Landing**         | `inventory/templates/landingpage.html` | Interface Bootstrap          |
| **JavaScript**         | `static/js/printer.js`                 | Appels API AJAX              |

---

## ✅ Workflow Récapitulatif (Asset 210)

1. **UI**: Utilisateur clique sur asset "210" dans landingpage.html
2. **Frontend**: Modal s'ouvre avec détails + bouton "Imprimer"
3. **API Call**: POST `/api/printer/labels/` avec `{asset_id: "210"}`
4. **Backend**: Serializer auto-génère `qr_content` et `barcode_content`
5. **Service**: BixolonSRP350 se connecte via USB (pyusb)
6. **ESC/POS**: Envoi séquence commandes (QR + Barcode + Texte + CUT)
7. **Imprimante**: Génère QR Code natif + Barcode + imprime + coupe
8. **Response**: JSON `{status: "success"}` renvoyé au frontend
9. **UI**: Toast notification "✅ Étiquette imprimée"
10. **Historique**: PrintJob enregistré en base

---

**Document créé le**: 2026-03-30  
**Version**: 1.0  
**Auteur**: Équipe CMDB Inventory