# 📋 Rapport Technique — Workflow QR Code & Code-Barres CMDB Inventory

**Version:** 1.0  
**Date:** 26 Mars 2026  
**Auteur:** Équipe Technique CMDB  
**Société:** Reconditionnement IT

---

## 📑 Table des Matières

1. [Génération du QR Code](#1-génération-du-qr-code)
2. [Contenu des Codes](#2-contenu-des-codes)
3. [Stockage en Base de Données](#3-stockage-en-base-de-données)
4. [Impression Thermique](#4-impression-thermique)
5. [Scan des Codes](#5-scan-des-codes)
6. [Vérification Code Actuel](#6-vérification-du-code-actuel)
7. [Endpoints DRF Requis](#7-endpoints-drf-requis)
8. [Procédure Complète](#8-procédure-complète)
9. [Algorithme Complet](#9-algorithme-complet)

---

## 1. Génération du QR Code

### 1.1 Moment de Génération

| Événement              | Déclencheur                                  | Action                                           |
| ---------------------- | -------------------------------------------- | ------------------------------------------------ |
| **Création Asset**     | `POST /api/v1/inventory/assets/`             | ✅ QR généré automatiquement (signal `post_save`) |
| **Modification Asset** | `PUT /api/v1/inventory/assets/<id>/`         | ⚠️ QR régénéré si S/N changé                      |
| **Demande Manuelle**   | `POST /api/v1/scanner/assets/<id>/regen-qr/` | ✅ QR régénéré à la demande                       |

### 1.2 Workflow de Génération

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW GÉNÉRATION QR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Asset créé (POST /inventory/assets/)                        │
│         │                                                       │
│         ▼                                                       │
│  2. Signal Django post_save déclenché                           │
│         │                                                       │
│         ▼                                                       │
│  3. QRCode.objects.create(asset=asset, uuid=uuid4())           │
│         │                                                       │
│         ▼                                                       │
│  4. _generate_qr_image(qr_obj) appelé                           │
│         │                                                       │
│         ▼                                                       │
│  5. Image PNG générée (qrcode library)                          │
│         │                                                       │
│         ▼                                                       │
│  6. Sauvegarde: media/qr_codes/qr_asset_<id>_<uuid>.png        │
│         │                                                       │
│         ▼                                                       │
│  7. URL stockée dans QRCode.image                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Page Dédiée — Generation & Print

**URL:** `/admin/scanner/generate/`

**Fonctionnalités:**
- ✅ Sélection multiple d'assets (checkbox)
- ✅ Aperçu QR Code avant impression
- ✅ Choix du format (QR Code / Code-Barres)
- ✅ Choix de la taille d'étiquette (30x20mm, 50x30mm, 70x40mm)
- ✅ Impression directe (USB/Bluetooth/Ethernet)
- ✅ Export PDF batch (multiple assets)

---

## 2. Contenu des Codes

### 2.1 QR Code (2D)

| Champ              | Format                 | Exemple                             |
| ------------------ | ---------------------- | ----------------------------------- |
| **Préfixe**        | Texte fixe             | `qr_asset_`                         |
| **Asset ID**       | Integer                | `152`                               |
| **UUID Token**     | UUID4                  | `abc123-def456-789ghi`              |
| **Format complet** | `qr_asset_<id>_<uuid>` | `qr_asset_152_abc123-def456-789ghi` |

**Avantages:**
- ✅ 300-500 caractères max
- ✅ Error correction (30% lisible même endommagé)
- ✅ Lisible smartphone natif
- ✅ Contient URL complète pour scan direct

### 2.2 Code-Barres (1D) — Code 128

| Type              | Format            | Exemple           | Usage                |
| ----------------- | ----------------- | ----------------- | -------------------- |
| **Serial Number** | `SR-YYYYNNNN-NNN` | `SR-20260001-001` | Asset constructeur   |
| **Internal Code** | `CI-YYYYNNNN-NNN` | `CI-20260001-001` | Code interne atelier |
| **QR Fallback**   | UUID seul         | `abc123-def456`   | Petit matériel       |

**Avantages:**
- ✅ Compact (petites étiquettes)
- ✅ Universel (toutes douchettes)
- ✅ Rapide à scanner
- ❌ Limité à 20-25 caractères

### 2.3 Comparaison

| Critère              | QR Code                | Code-Barres          |
| -------------------- | ---------------------- | -------------------- |
| **Capacité**         | 300-500 chars          | 20-25 chars          |
| **Taille min**       | 10x10mm                | 25x5mm               |
| **Lecture**          | Smartphone + Douchette | Douchette uniquement |
| **Error correction** | ✅ 30%                  | ❌ Aucun              |
| **Vitesse scan**     | 0.5-1 sec              | 0.2-0.3 sec          |
| **Coût impression**  | Identique              | Identique            |

---

## 3. Stockage en Base de Données

### 3.1 Modèle QRCode

```python
# backend/scanner/models.py
class QRCode(models.Model):
    asset = models.OneToOneField('inventory.Asset', on_delete=models.CASCADE)
    uuid_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    code = models.CharField(max_length=255, unique=True)  # qr_asset_<id>_<uuid>
    
    # Image stockée en filesystem, URL en base
    image = models.ImageField(upload_to='qr_codes/%Y/%m/', blank=True)
    
    # Métadonnées
    format = models.CharField(max_length=20, default='PNG')  # PNG, SVG, PDF
    size = models.PositiveIntegerField(default=300)  # pixels
    error_correction = models.CharField(max_length=10, default='M')  # L, M, Q, H
    
    # Tracking
    is_active = models.BooleanField(default=True)
    scanned_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['uuid_token']),
            models.Index(fields=['code']),
            models.Index(fields=['asset', '-created_at']),
        ]
```

### 3.2 Stockage Image

| Élément           | Emplacement                                   | Format                                  |
| ----------------- | --------------------------------------------- | --------------------------------------- |
| **Fichier image** | `media/qr_codes/2026/03/qr_asset_152_abc.png` | PNG (300 DPI)                           |
| **URL en base**   | `QRCode.image`                                | `qr_codes/2026/03/qr_asset_152_abc.png` |
| **URL absolue**   | `settings.MEDIA_URL + QRCode.image`           | `https://domain.com/media/...`          |

### 3.3 Backup & Migration

```bash
# Backup des QR Codes
python manage.py dumpdata scanner.QRCode --format json > backup_qr.json
rsync -av media/qr_codes/ backup-server:/qr_backup/

# Restoration
python manage.py loaddata backup_qr.json
rsync -av backup-server:/qr_backup/ media/qr_codes/
```

---

## 4. Impression Thermique

### 4.1 Imprimantes Supportées

| Modèle               | Type      | Connectique              | Résolution | Vitesse |
| -------------------- | --------- | ------------------------ | ---------- | ------- |
| **Samsung SP350/T1** | Thermique | USB, Ethernet            | 203 DPI    | 150mm/s |
| **Munbyn P42B**      | Thermique | USB, Bluetooth           | 203 DPI    | 127mm/s |
| **Itari PM 246S**    | Thermique | USB, Bluetooth, Ethernet | 203 DPI    | 152mm/s |

### 4.2 Formats d'Étiquettes

| Format       | Dimensions   | Usage                            |
| ------------ | ------------ | -------------------------------- |
| **30x20mm**  | 30mm x 20mm  | Petit matériel (souris, câbles)  |
| **50x30mm**  | 50mm x 30mm  | Standard (laptops, écrans)       |
| **70x40mm**  | 70mm x 40mm  | Grand matériel (serveurs, baies) |
| **100x50mm** | 100mm x 50mm | Rack, armoires                   |

### 4.3 Processus d'Impression

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW IMPRESSION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Utilisateur sélectionne assets (checkbox)                   │
│         │                                                       │
│         ▼                                                       │
│  2. Clic "Imprimer Étiquettes"                                  │
│         │                                                       │
│         ▼                                                       │
│  3. Frontend appelle POST /api/v1/scanner/print-labels/        │
│         Body: {asset_ids: [152, 153, 154], format: '50x30'}    │
│         │                                                       │
│         ▼                                                       │
│  4. Backend génère PDF avec ReportLab                           │
│         - QR Code image intégrée                                │
│         - Texte: Nom, S/N, Date                                 │
│         │                                                       │
│         ▼                                                       │
│  5. PDF retourné en binaire                                     │
│         │                                                       │
│         ▼                                                       │
│  6. Navigateur ouvre dialogue impression                        │
│         │                                                       │
│         ▼                                                       │
│  7. Utilisateur sélectionne imprimante thermique                │
│         - USB: Détectée automatiquement                         │
│         - Bluetooth: Appairage préalable requis                 │
│         - Ethernet: IP configurée dans navigateur               │
│         │                                                       │
│         ▼                                                       │
│  8. Impression lancée (paramètres: 203 DPI, noir seul)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Configuration par Imprimante

#### **USB (Samsung SP350/T1)**
```javascript
// Configuration navigateur
{
    printer: 'Samsung_SP350',
    connection: 'usb',
    paperSize: '50x30mm',
    density: 'high',
    speed: 'normal'
}
```

#### **Bluetooth (Munbyn P42B)**
```javascript
// Appairage préalable requis
// Windows: Paramètres → Périphériques → Bluetooth
// macOS: Préférences → Bluetooth
{
    printer: 'Munbyn_P42B',
    connection: 'bluetooth',
    paperSize: '50x30mm',
    density: 'medium',
    speed: 'fast'
}
```

#### **Ethernet (Itari PM 246S)**
```javascript
// Configuration IP statique recommandée
{
    printer: 'Itari_PM246S',
    connection: 'ethernet',
    ip: '192.168.1.100',
    port: 9100,
    paperSize: '70x40mm',
    density: 'high',
    speed: 'normal'
}
```

### 4.5 Exemple d'Étiquette

```
┌─────────────────────────────────────────────┐
│                                             │
│   ██████████████████████████████████████   │
│   ██  ██  ████  ██  ██  ████  ██  ██   │
│   ██  ██████  ██  ██  ██  ██████  ██   │
│   ██  ██  ████  ██  ██  ████  ██  ██   │
│   ██████████████████████████████████████   │
│                                             │
│   Dell Latitude 5420                        │
│   S/N: ABC123XYZ                            │
│   ID: 152 | 26/03/2026                     │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 5. Scan des Codes

### 5.1 Matériel Supporté

| Type                    | Modèle                  | Connectique    | Portée  |
| ----------------------- | ----------------------- | -------------- | ------- |
| **Douchette USB**       | HoneyWell Voyager 1450g | USB            | Filaire |
| **Douchette Bluetooth** | HoneyWell Granit 1911i  | Bluetooth      | 100m    |
| **Smartphone**          | Android/iOS             | Caméra         | 5-30cm  |
| **Mobile Industriel**   | Zebra TC52              | Caméra + Laser | 5-50cm  |

### 5.2 Workflow de Scan

```
┌─────────────────────────────────────────────────────────────────┐
│                      WORKFLOW SCAN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Utilisateur scanne code (USB/Bluetooth/Smartphone)         │
│         │                                                       │
│         ▼                                                       │
│  2. Scanner émule clavier (USB/Bluetooth)                      │
│     OU                                                          │
│     ZXing decode (Smartphone)                                   │
│         │                                                       │
│         ▼                                                       │
│  3. Texte capturé: qr_asset_152_abc123-def456                  │
│         │                                                       │
│         ▼                                                       │
│  4. Frontend extrait UUID: abc123-def456                       │
│         │                                                       │
│         ▼                                                       │
│  5. Appel API: GET /api/v1/scanner/scan/<uuid>/                │
│         │                                                       │
│         ▼                                                       │
│  6. Backend résout:                                            │
│     - QR Code UUID → Asset                                      │
│     - Serial Number → Asset                                     │
│     - Internal Code → Asset                                     │
│         │                                                       │
│         ▼                                                       │
│  7. ScanLog enregistré (IP, user_agent, timestamp)             │
│         │                                                       │
│         ▼                                                       │
│  8. Réponse JSON avec données asset                            │
│         │                                                       │
│         ▼                                                       │
│  9. Frontend affiche fiche asset                               │
│         - Nom, S/N, Photo                                       │
│         - Statut, Localisation                                  │
│         - Actions: Ticket, Déplacer, Voir                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Configuration Scanner USB (HoneyWell)

| Paramètre      | Valeur        | Code Configuration  |
| -------------- | ------------- | ------------------- |
| **Mode**       | USB Keyboard  | Scanner dans manuel |
| **Suffix**     | Enter (CR+LF) | Scanner dans manuel |
| **Langue**     | French AZERTY | Scanner dans manuel |
| **Batch Mode** | OFF           | Scanner dans manuel |
| **Beep**       | ON            | Scanner dans manuel |

### 5.4 Affichage Résultat

**Asset Connu:**
```
✅ Scan réussi

Dell Latitude 5420
S/N: ABC123XYZ • Laptop
📍 Paris - Bureau 204

Statut: ✅ Actif
Assigné à: Jean Dupont
Garantie: 15/06/2027

[🔧 Créer Ticket] [📍 Déplacer] [👁️ Voir Fiche]
```

**Asset Inconnu:**
```
❌ Code non reconnu

Code scanné: qr_asset_999_xyz789

Aucun asset trouvé dans le système.

[🔍 Recherche manuelle] [➕ Créer Asset]
```

---

## 6. Vérification du Code Actuel

### 6.1 Backend (`views.py`)

| Élément                 | État           | Correction Requise                               |
| ----------------------- | -------------- | ------------------------------------------------ |
| **Endpoint GET**        | ⚠️ Partiel      | ✅ Changer en POST pour `/api/v1/scanner/scan/`   |
| **QRCode.uuid_token**   | ✅ Correct      | -                                                |
| **Asset.qr_uuid**       | ❌ N'existe pas | ✅ Utiliser `QRCode.objects.get(uuid_token=uuid)` |
| **ScanLog créé**        | ✅ Correct      | -                                                |
| **Compteur incrémenté** | ✅ Correct      | -                                                |
| **Signal post_save**    | ⚠️ Non visible  | ✅ Vérifier `scanner/signals.py`                  |

### 6.2 Frontend (`scanner.js`)

| Élément                   | État             | Correction Requise               |
| ------------------------- | ---------------- | -------------------------------- |
| **createApp declaration** | ❌ Double         | ✅ Utiliser `window.VueCreateApp` |
| **handleKeyboardInput**   | ❌ Double méthode | ✅ Fusionner en 1 seule           |
| **Buffer USB**            | ⚠️ Partiel        | ✅ Ajouter timeout + validation   |
| **Appel API GET**         | ⚠️ GET            | ✅ Changer en POST                |
| **Erreur handling**       | ✅ Correct        | -                                |

### 6.3 Template (`index.html`)

| Élément                | État       | Correction Requise          |
| ---------------------- | ---------- | --------------------------- |
| **id="scanner-app"**   | ⚠️ Manquant | ✅ Ajouter pour mount Vue    |
| **ZXing CDN**          | ⚠️ Manquant | ✅ Ajouter `<script>` ZXing  |
| **Camera preview**     | ⚠️ Manquant | ✅ Ajouter `<video>` element |
| **USB buffer display** | ⚠️ Manquant | ✅ Ajouter debug display     |

---

## 7. Endpoints DRF Requis

### 7.1 Endpoints Existants

| Méthode | Endpoint                                | Description               | Statut   |
| ------- | --------------------------------------- | ------------------------- | -------- |
| GET     | `/api/v1/scanner/scan/<uuid>/`          | Résolution QR/Code-barres | ⚠️ → POST |
| POST    | `/api/v1/scanner/assets/<id>/regen-qr/` | Régénérer QR              | ✅        |

### 7.2 Endpoints à Créer

| Méthode | Endpoint                          | Description                      | Priority  |
| ------- | --------------------------------- | -------------------------------- | --------- |
| POST    | `/api/v1/scanner/scan/`           | Scan avec body `{"uuid": "..."}` | 🔴 Haute   |
| POST    | `/api/v1/scanner/print-labels/`   | Impression batch PDF             | 🔴 Haute   |
| GET     | `/api/v1/scanner/assets/<id>/qr/` | Récupérer QR image URL           | 🟠 Moyenne |
| POST    | `/api/v1/scanner/batch-generate/` | Générer QR multiple assets       | 🟠 Moyenne |
| GET     | `/api/v1/scanner/history/`        | Historique des scans             | 🟢 Basse   |
| DELETE  | `/api/v1/scanner/assets/<id>/qr/` | Supprimer QR (révoquer)          | 🟢 Basse   |

### 7.3 Spécifications Endpoints

```python
# POST /api/v1/scanner/scan/
Request:
{
    "uuid": "abc123-def456",
    "scanner_type": "usb|bluetooth|webcam|mobile",
    "user_id": 42  # Optionnel
}

Response (200):
{
    "id": 152,
    "name": "Dell Latitude 5420",
    "serial_number": "ABC123XYZ",
    "status": "active",
    "location_name": "Paris - Bureau 204",
    "assigned_to": "Jean Dupont",
    "code_type": "qr_code|barcode_serial|barcode_internal",
    "scanned_code": "qr_asset_152_abc123-def456"
}

# POST /api/v1/scanner/print-labels/
Request:
{
    "asset_ids": [152, 153, 154],
    "format": "qr|barcode",
    "label_size": "30x20|50x30|70x40",
    "copies": 1
}

Response (200):
Content-Type: application/pdf
Binary PDF data
```

---

## 8. Procédure Complète — Cas Exemple

### 8.1 Scénario : Réception et Marquage de 10 Laptops

**Matériel:**
- 1 PC Fixe (Windows 11, Chrome/Firefox)
- 1 Scanner USB HoneyWell Voyager 1450g
- 1 Imprimante Thermique Samsung SP350/T1 (USB)
- 1 Smartphone Android (scan mobile terrain)

**Connectique:**
```
┌──────────────┐     USB      ┌──────────────┐
│   HoneyWell  │──────────────│              │
│   Scanner    │              │              │
└──────────────┘              │   PC Fixe    │
                              │   (CMDB)     │
┌──────────────┐     USB      │              │
│   Samsung    │──────────────│              │
│   SP350/T1   │              │              │
└──────────────┘              └──────────────┘
                                       │
                                    Ethernet
                                       │
                              ┌──────────────┐
                              │  Smartphone  │
                              │   (WiFi)     │
                              └──────────────┘
```

### 8.2 Étapes Détaillées

#### **Étape 1: Réception Matériel** (15 min)

```
1.1 Déballer 10 laptops Dell Latitude 5420
1.2 Noter numéros de série constructeur:
    - ABC123XYZ001 à ABC123XYZ010
1.3 Vérifier état physique (grille de contrôle)
1.4 Allumer et tester boot (OK/NOK)
```

#### **Étape 2: Création Assets dans CMDB** (20 min)

```
2.1 Ouvrir navigateur → https://cmdb.company.com/admin/
2.2 Login: technicien / motdepasse
2.3 Naviguer: Assets → Nouvel Asset
2.4 Remplir formulaire (x10):
    ┌────────────────────────────────────────┐
    │ Nom: Dell Latitude 5420                │
    │ S/N: ABC123XYZ001                      │
    │ Catégorie: Laptop                      │
    │ Marque: Dell                           │
    │ Statut: En Stock                       │
    │ Localisation: Paris - Atelier          │
    │ Prix achat: 450.00 €                   │
    │ Garantie: 15/06/2027                   │
    └────────────────────────────────────────┘
2.5 Valider → QR Code généré automatiquement
2.6 Répéter pour 9 autres laptops
```

#### **Étape 3: Impression Étiquettes QR** (10 min)

```
3.1 Naviguer: Assets → Liste
3.2 Cocher 10 laptops (checkbox)
3.3 Action: "Imprimer Étiquettes"
3.4 Choisir format: 50x30mm
3.5 Choisir type: QR Code + Texte
3.6 Imprimante: Samsung SP350/T1 (USB)
3.7 Lancer impression
3.8 Vérifier qualité (10 étiquettes)
3.9 Coller étiquettes sur chaque laptop (dessous)
```

**Exemple Étiquette:**
```
┌─────────────────────────────────────────────┐
│  ████████████████████████████████████████  │
│  ██  ██  ████  ██  ██  ████  ██  ██  ██  │
│  ██  ██████  ██  ██  ██  ██████  ██  ██  │
│  ██  ██  ████  ██  ██  ████  ██  ██  ██  │
│  ████████████████████████████████████████  │
│                                            │
│  Dell Latitude 5420                        │
│  S/N: ABC123XYZ001                         │
│  ID: 152 | 26/03/2026                     │
│  Paris - Atelier                           │
└─────────────────────────────────────────────┘
```

#### **Étape 4: Scan de Contrôle** (5 min)

```
4.1 Prendre scanner USB HoneyWell
4.2 Scanner étiquette laptop #1
4.3 Vérifier affichage écran:
    ✅ Nom: Dell Latitude 5420
    ✅ S/N: ABC123XYZ001
    ✅ Statut: En Stock
    ✅ Localisation: Paris - Atelier
4.4 Si OK → Passer au suivant
4.5 Si NOK → Vérifier collage étiquette
4.6 Répéter pour 10 laptops
```

#### **Étape 5: Scan Mobile Terrain** (Variable)

```
5.1 Technicien terrain prend smartphone
5.2 Ouvrir navigateur → https://cmdb.company.com/scan/
5.3 Scanner QR code laptop (caméra smartphone)
5.4 Vérifier affichage:
    ✅ Fiche asset complète
    ✅ Boutons: Ticket / Déplacer / Voir
5.5 Si maintenance requise → Créer ticket directement
5.6 Si déplacement → Changer localisation
```

#### **Étape 6: Traçabilité et Reporting** (5 min)

```
6.1 Naviguer: Scanner → Historique
6.2 Vérifier 10 scans enregistrés
6.3 Exporter rapport CSV (date, user, asset, location)
6.4 Archiver dans dossier: /rapports/reception/2026-03/
6.5 Clôturer réception dans CMDB
```

### 8.3 Timeline Totale

| Étape                 | Durée      | Personnel        |
| --------------------- | ---------- | ---------------- |
| Réception             | 15 min     | 1 technicien     |
| Création Assets       | 20 min     | 1 technicien     |
| Impression Étiquettes | 10 min     | 1 technicien     |
| Scan de Contrôle      | 5 min      | 1 technicien     |
| **Total**             | **50 min** | **1 technicien** |

**Gain vs Manuel:** 2 heures → 50 minutes (✅ 60% de gain)

---

## 9. Algorithme Complet

### 9.1 Algorithme de Génération QR

```
┌─────────────────────────────────────────────────────────────────┐
│  ALGORITHME: GÉNÉRATION QR CODE                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DÉBUT                                                          │
│    │                                                            │
│    ▼                                                            │
│  [Asset créé via POST /inventory/assets/]                      │
│    │                                                            │
│    ▼                                                            │
│  [Signal post_save déclenché]                                  │
│    │                                                            │
│    ▼                                                            │
│  [QRCode.objects.create()]                                     │
│    ├── asset = asset                                           │
│    ├── uuid_token = uuid4()                                    │
│    └── code = f"qr_asset_{asset.id}_{uuid_token}"             │
│    │                                                            │
│    ▼                                                            │
│  [_generate_qr_image(qr_obj)]                                  │
│    ├── qr = QRCode(version=1, error_correction=M)             │
│    ├── qr.add_data(qr_obj.code)                                │
│    ├── img = qr.make_image(fill_color="black", back="white")  │
│    └── img.save(buffer, format="PNG")                          │
│    │                                                            │
│    ▼                                                            │
│  [Sauvegarde fichier]                                          │
│    └── media/qr_codes/YYYY/MM/qr_asset_<id>_<uuid>.png        │
│    │                                                            │
│    ▼                                                            │
│  [Mise à jour QRCode.image]                                    │
│    └── qr_obj.image = filename                                 │
│    │                                                            │
│    ▼                                                            │
│  FIN                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Algorithme de Scan

```
┌─────────────────────────────────────────────────────────────────┐
│  ALGORITHME: SCAN QR/BARCODE                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DÉBUT                                                          │
│    │                                                            │
│    ▼                                                            │
│  [Scan déclenché (USB/Webcam/Mobile)]                          │
│    │                                                            │
│    ▼                                                            │
│  [Code texte capturé]                                          │
│    └── ex: "qr_asset_152_abc123-def456"                       │
│    │                                                            │
│    ▼                                                            │
│  [Extraction UUID]                                             │
│    ├── Si format QR: parts = code.split('_')                  │
│    │   └── uuid = parts[-1]                                    │
│    └── Si barcode: uuid = code (serial/internal)              │
│    │                                                            │
│    ▼                                                            │
│  [Appel API POST /scanner/scan/]                               │
│    └── Body: {"uuid": uuid}                                    │
│    │                                                            │
│    ▼                                                            │
│  [Backend résolution]                                          │
│    ├── Essai 1: QRCode.objects.get(uuid_token=uuid)           │
│    │   └── Si OK → asset = qr_obj.asset                        │
│    ├── Essai 2: Asset.objects.get(serial_number=uuid)         │
│    │   └── Si OK → qr_obj, _ = QRCode.objects.get_or_create() │
│    └── Essai 3: Asset.objects.get(internal_code=uuid)         │
│        └── Si OK → qr_obj, _ = QRCode.objects.get_or_create() │
│    │                                                            │
│    ▼                                                            │
│  [Si asset trouvé]                                             │
│    ├── ScanLog.objects.create(...)                            │
│    ├── QRCode.scanned_count += 1                              │
│    └── Retourner AssetDetailSerializer(asset)                 │
│    │                                                            │
│    ▼                                                            │
│  [Si asset NON trouvé]                                         │
│    └── Retourner 404 {"error": "Code invalide"}               │
│    │                                                            │
│    ▼                                                            │
│  [Frontend affichage]                                          │
│    ├── Si 200: Afficher fiche asset + actions                 │
│    └── Si 404: Afficher erreur + recherche manuelle           │
│    │                                                            │
│    ▼                                                            │
│  FIN                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Algorithme d'Impression

```
┌─────────────────────────────────────────────────────────────────┐
│  ALGORITHME: IMPRESSION ÉTIQUETTES                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DÉBUT                                                          │
│    │                                                            │
│    ▼                                                            │
│  [Sélection assets (checkbox)]                                 │
│    └── asset_ids = [152, 153, 154, ...]                       │
│    │                                                            │
│    ▼                                                            │
│  [Choix paramètres]                                            │
│    ├── format = "qr" | "barcode"                              │
│    ├── label_size = "30x20" | "50x30" | "70x40"               │
│    └── copies = 1 | 2 | 3                                      │
│    │                                                            │
│    ▼                                                            │
│  [Appel API POST /scanner/print-labels/]                       │
│    └── Body: {asset_ids, format, label_size, copies}          │
│    │                                                            │
│    ▼                                                            │
│  [Backend génération PDF]                                      │
│    ├── Pour chaque asset_id:                                  │
│    │   ├── asset = Asset.objects.get(id=asset_id)             │
│    │   ├── qr_obj = QRCode.objects.get(asset=asset)           │
│    │   ├── img = Image.open(qr_obj.image.path)                │
│    │   └── draw.text(nom, s/n, date)                          │
│    │                                                            │
│    ├── pdf = ReportLab PDF()                                  │
│    ├── pdf.setSize(label_size)                                │
│    └── pdf.save(buffer)                                       │
│    │                                                            │
│    ▼                                                            │
│  [Retour PDF binaire]                                          │
│    └── Content-Type: application/pdf                          │
│    │                                                            │
│    ▼                                                            │
│  [Navigateur dialogue impression]                              │
│    ├── Sélection imprimante (USB/BT/Ethernet)                 │
│    ├── Paramètres: 203 DPI, noir seul, density high           │
│    └── Lancer impression                                      │
│    │                                                            │
│    ▼                                                            │
│  FIN                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Finale

| Élément                               | Statut        | Action                           |
| ------------------------------------- | ------------- | -------------------------------- |
| **Génération QR automatique**         | ⚠️ À vérifier  | Vérifier `scanner/signals.py`    |
| **Endpoint POST /scanner/scan/**      | ❌ Manquant    | Créer endpoint POST              |
| **Correction views.py (qr_uuid)**     | ❌ Erreur      | Utiliser `QRCode.objects.get()`  |
| **Correction scanner.js (createApp)** | ❌ Erreur      | Utiliser `window.VueCreateApp`   |
| **Page impression dédiée**            | ❌ Manquante   | Créer `/admin/scanner/generate/` |
| **Support imprimantes thermiques**    | ⚠️ Partiel     | Ajouter config par modèle        |
| **Historique des scans**              | ✅ Existant    | Vérifier `ScanLog` model         |
| **Documentation procédure**           | ✅ Ce document | À diffuser équipe                |

---

## 📎 Annexes

### A. Exemple de Code QR Généré

```
Contenu: qr_asset_152_abc123-def456-789ghi
Format: PNG 300x300 pixels
Error Correction: M (15%)
URL: /media/qr_codes/2026/03/qr_asset_152_abc.png
```

### B. Configuration Imprimante Samsung SP350/T1

```
Driver: Samsung SP350 Series
Port: USB001
Resolution: 203 DPI
Density: 10 (High)
Speed: 3 (Normal)
Paper: 50x30mm Thermal Label
```

### C. Configuration Scanner HoneyWell

```
Model: Voyager 1450g
Interface: USB Keyboard
Suffix: Enter (CR+LF)
Language: French AZERTY
Beep: ON (Good Read)
```

---

**Fin du Rapport — Version 1.0 — 26 Mars 2026**