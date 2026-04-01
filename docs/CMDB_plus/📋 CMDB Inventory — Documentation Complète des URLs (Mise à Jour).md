# 📋 CMDB Inventory — Documentation Complète des URLs (Mise à Jour)

**Version:** 3.0  
**Date:** 26 Mars 2026  
**Projet:** CMDB Inventory — Société de Reconditionnement IT  
**Stack:** Django 5 + DRF + Vue 3 (CDN) + Bootstrap 5.3  
**Nouveau Module:** Printer (Impression Étiquettes QR)

---

## 📑 Table des Matières

1. [Vue d'Ensemble des Modules](#1-vue-densemble-des-modules)
2. [URLs Publiques (Sans Authentication)](#2-urls-publiques-sans-authentication)
3. [URLs Interface Métier (/admin/)](#3-urls-interface-métier-admin)
4. [API REST Inventory](#4-api-rest-inventory)
5. [API REST Maintenance](#5-api-rest-maintenance)
6. [API REST Scanner](#6-api-rest-scanner)
7. [API REST Stock](#7-api-rest-stock)
8. [API REST Printer ⭐ NOUVEAU](#8-api-rest-printer--nouveau)
9. [API REST Authentication](#9-api-rest-authentication)
10. [Django Admin Système](#10-django-admin-système)
11. [Fichiers Statiques](#11-fichiers-statiques)
12. [Workflows Complets](#12-workflows-complets)

---

## 1. Vue d'Ensemble des Modules

| Module              | Base URL               | Description                         | Auth Requise |
| ------------------- | ---------------------- | ----------------------------------- | ------------ |
| **Dashboard**       | `/`                    | Vitrine publique, statistiques      | ❌ Non        |
| **Admin Métier**    | `/admin/`              | Interface techniciens/gestionnaires | ✅ Oui        |
| **Scanner**         | `/admin/scanner/`      | Scan QR/Code-barres                 | ✅ Oui        |
| **Printer**         | `/admin/printer/`      | Impression étiquettes QR            | ✅ Oui        |
| **Scan Public**     | `/scan/<uuid>/`        | Fiche asset publique (terrain)      | ❌ Non        |
| **API Inventory**   | `/api/v1/inventory/`   | Gestion assets                      | ✅ Oui        |
| **API Maintenance** | `/api/v1/maintenance/` | Tickets, réparations                | ✅ Oui        |
| **API Scanner**     | `/api/v1/scanner/`     | Résolution QR, logs                 | ⚠️ Mixte      |
| **API Stock**       | `/api/v1/stock/`       | Articles atelier, mouvements        | ✅ Oui        |
| **API Printer**     | `/api/printer/`        | **Impression, templates, printers** | ✅ Oui        |
| **API Auth**        | `/api/v1/auth/`        | Token, utilisateurs                 | ✅ Oui        |
| **Django Admin**    | `/django-admin/`       | Administration système              | ✅ Superuser  |

---

## 8. API REST Printer ⭐ NOUVEAU

### 8.1 Vue d'Ensemble Module Printer

| Composant         | Description                             | Usage                           |
| ----------------- | --------------------------------------- | ------------------------------- |
| **PrintTemplate** | Modèles d'étiquettes (formats, layouts) | 30x20mm, 50x30mm, 70x40mm, etc. |
| **Printer**       | Configuration imprimantes (USB/BT/WiFi) | MUNBYN, Samsung, Zebra          |
| **PrintJob**      | Jobs d'impression batch (PDF)           | Multi-assets, tracking          |
| **PrintLog**      | Audit des impressions (traçabilité)     | Qui, quand, quoi                |
| **PrintLabel**    | Génération étiquettes unitaires         | Single asset                    |

---

### 8.2 Endpoints API Printer

| Endpoint                                              | Méthode | View/ViewSet           | Description              | Params                                                 | Response                                    | Auth    |
| ----------------------------------------------------- | ------- | ---------------------- | ------------------------ | ------------------------------------------------------ | ------------------------------------------- | ------- |
| `/api/printer/`                                       | GET     | `APIRootView`          | Racine API Printer       | -                                                      | `{endpoints}`                               | ✅ Token |
| `/api/printer/printers/`                              | GET     | `PrinterViewSet`       | Liste imprimantes        | `is_active`, `connection_type`                         | `[{id, name, connection_type, ...}]`        | ✅ Token |
| `/api/printer/printers/`                              | POST    | `PrinterViewSet`       | Créer imprimante         | `name`, `connection_type`, `ip_address`, `device_path` | `{id, name, ...}`                           | ✅ Admin |
| `/api/printer/printers/<id>/`                         | GET     | `PrinterViewSet`       | Détail imprimante        | -                                                      | `{id, name, connection_type, config, ...}`  | ✅ Token |
| `/api/printer/printers/<id>/`                         | PUT     | `PrinterViewSet`       | Mettre à jour imprimante | Champs partiels                                        | `{id, name, ...}`                           | ✅ Admin |
| `/api/printer/printers/<id>/`                         | DELETE  | `PrinterViewSet`       | Supprimer imprimante     | -                                                      | `204 No Content`                            | ✅ Admin |
| `/api/printer/templates/`                             | GET     | `PrintTemplateViewSet` | Liste templates          | `format`, `is_default`                                 | `[{id, name, format, width_mm, height_mm}]` | ✅ Token |
| `/api/printer/templates/`                             | POST    | `PrintTemplateViewSet` | Créer template           | `name`, `format`, `width_mm`, `height_mm`, `layout`    | `{id, name, ...}`                           | ✅ Admin |
| `/api/printer/templates/<id>/`                        | GET     | `PrintTemplateViewSet` | Détail template          | -                                                      | `{id, name, format, layout_config}`         | ✅ Token |
| `/api/printer/templates/<id>/`                        | PUT     | `PrintTemplateViewSet` | Mettre à jour template   | Champs partiels                                        | `{id, name, ...}`                           | ✅ Admin |
| `/api/printer/templates/<id>/`                        | DELETE  | `PrintTemplateViewSet` | Supprimer template       | -                                                      | `204 No Content`                            | ✅ Admin |
| `/api/printer/jobs/`                                  | GET     | `PrintJobViewSet`      | Liste jobs impression    | `status`, `created_by`, `date_from`, `date_to`         | `[{id, status, asset_count, pdf_url}]`      | ✅ Token |
| `/api/printer/jobs/`                                  | POST    | `PrintJobViewSet`      | Créer job impression     | `asset_ids[]`, `template_id`, `printer_id`, `copies`   | `{id, status, uuid}`                        | ✅ Token |
| `/api/printer/jobs/<id>/`                             | GET     | `PrintJobViewSet`      | Détail job               | -                                                      | `{id, status, pdf_url, completed_at}`       | ✅ Token |
| `/api/printer/jobs/<id>/download/`                    | GET     | `PrintJobViewSet`      | Télécharger PDF          | -                                                      | `application/pdf`                           | ✅ Token |
| `/api/printer/jobs/<id>/cancel/`                      | POST    | `PrintJobViewSet`      | Annuler job              | -                                                      | `{status: cancelled}`                       | ✅ Token |
| `/api/printer/labels/`                                | GET     | `PrintLabelViewSet`    | Liste étiquettes         | `asset_id`, `status`                                   | `[{id, asset, qr_code, status}]`            | ✅ Token |
| `/api/printer/labels/`                                | POST    | `PrintLabelViewSet`    | Générer étiquette        | `asset_id`, `template_id`, `copies`                    | `{id, pdf_url, status}`                     | ✅ Token |
| `/api/printer/labels/status/`                         | GET     | `PrintLabelViewSet`    | Statut imprimantes       | -                                                      | `{printers: [{name, status, online}]}`      | ✅ Token |
| `/api/printer/print-labels/`                          | POST    | `print_labels`         | Impression directe       | `asset_ids[]`, `template_id`, `copies`                 | `application/pdf`                           | ✅ Token |
| `/django-admin/inventory/asset/<id>/generate_qrcode/` | POST    | `generate_qrcode_view` | Générer QR Code asset    | `asset_id` (URL)                                       | `{uuid, qr_url, image}`                     | ✅ Admin |
| `/django-admin/inventory/asset/<id>/print_label/`     | GET     | `print_label_pdf_view` | PDF étiquette single     | `asset_id` (URL), `format`, `copies`                   | `application/pdf`                           | ✅ Admin |

---

### 8.3 Modèles Printer

#### **PrintTemplate**

| Champ              | Type      | Description           | Exemple                   |
| ------------------ | --------- | --------------------- | ------------------------- |
| `name`             | CharField | Nom du template       | "Standard Laptop 50x30"   |
| `format`           | CharField | Format étiquette      | "50x30", "70x40", "80x50" |
| `width_mm`         | Integer   | Largeur (mm)          | 50                        |
| `height_mm`        | Integer   | Hauteur (mm)          | 30                        |
| `qr_size_mm`       | Integer   | Taille QR Code (mm)   | 20                        |
| `qr_position_x_mm` | Integer   | Position X QR (mm)    | 5                         |
| `qr_position_y_mm` | Integer   | Position Y QR (mm)    | 5                         |
| `font_size_title`  | Integer   | Taille police titre   | 10                        |
| `font_size_text`   | Integer   | Taille police texte   | 8                         |
| `show_serial`      | Boolean   | Afficher S/N          | True                      |
| `show_category`    | Boolean   | Afficher catégorie    | True                      |
| `show_location`    | Boolean   | Afficher localisation | True                      |
| `is_default`       | Boolean   | Template par défaut   | False                     |
| `is_active`        | Boolean   | Template actif        | True                      |

---

#### **Printer**

| Champ             | Type      | Description                | Exemple                               |
| ----------------- | --------- | -------------------------- | ------------------------------------- |
| `name`            | CharField | Nom imprimante             | "MUNBYN RW403B - Atelier"             |
| `connection_type` | CharField | Type connexion             | "usb", "bluetooth", "wifi", "network" |
| `ip_address`      | GenericIP | Adresse IP (WiFi/Ethernet) | "192.168.1.100"                       |
| `port`            | Integer   | Port réseau                | 9100                                  |
| `mac_address`     | CharField | Adresse MAC (Bluetooth)    | "00:11:22:33:44:55"                   |
| `device_path`     | CharField | Chemin device (USB)        | "/dev/usb/lp0"                        |
| `dpi`             | Integer   | Résolution                 | 203                                   |
| `speed`           | Integer   | Vitesse (1-5)              | 3                                     |
| `density`         | Integer   | Densité (1-15)             | 10                                    |
| `paper_width_mm`  | Integer   | Largeur papier (mm)        | 50                                    |
| `paper_height_mm` | Integer   | Hauteur papier (mm)        | 30                                    |
| `is_active`       | Boolean   | Imprimante active          | True                                  |
| `is_default`      | Boolean   | Imprimante par défaut      | True                                  |
| `last_used_at`    | DateTime  | Dernière utilisation       | 2026-03-26 14:30                      |

---

#### **PrintJob**

| Champ           | Type       | Description            | Exemple                                        |
| --------------- | ---------- | ---------------------- | ---------------------------------------------- |
| `uuid`          | UUID       | Identifiant unique job | "abc123-def456-789"                            |
| `created_by`    | ForeignKey | Utilisateur créateur   | User #5                                        |
| `asset_ids`     | JSONField  | Liste IDs assets       | "[210, 211, 212]"                              |
| `template`      | ForeignKey | Template utilisé       | PrintTemplate #1                               |
| `printer`       | ForeignKey | Imprimante cible       | Printer #1                                     |
| `copies`        | Integer    | Nombre de copies       | 1                                              |
| `status`        | CharField  | Statut job             | "pending", "processing", "completed", "failed" |
| `pdf_file`      | FileField  | Fichier PDF généré     | "print_jobs/2026/03/job_abc.pdf"               |
| `error_message` | TextField  | Erreur (si failed)     | "Printer offline"                              |
| `started_at`    | DateTime   | Début traitement       | 2026-03-26 14:30                               |
| `completed_at`  | DateTime   | Fin traitement         | 2026-03-26 14:31                               |
| `created_at`    | DateTime   | Création job           | 2026-03-26 14:30                               |

---

#### **PrintLog**

| Champ           | Type       | Description           | Exemple          |
| --------------- | ---------- | --------------------- | ---------------- |
| `job`           | ForeignKey | Job associé           | PrintJob #12     |
| `asset`         | ForeignKey | Asset imprimé         | Asset #210       |
| `printed_by`    | ForeignKey | Utilisateur (qui)     | User #5          |
| `printer_name`  | CharField  | Nom imprimante        | "MUNBYN RW403B"  |
| `template_name` | CharField  | Nom template          | "Standard 50x30" |
| `printed_at`    | DateTime   | Timestamp impression  | 2026-03-26 14:31 |
| `ip_address`    | GenericIP  | IP utilisateur        | "192.168.1.50"   |
| `user_agent`    | TextField  | User agent navigateur | "Mozilla/5.0..." |

---

### 8.4 Formats d'Étiquettes Supportés

| Format   | Dimensions (mm) | Usage Recommandé                     | QR Size |
| -------- | --------------- | ------------------------------------ | ------- |
| `30x20`  | 30 × 20         | Petit matériel (câbles, adaptateurs) | 15mm    |
| `50x30`  | 50 × 30         | **Standard** (laptops, écrans)       | 20mm    |
| `70x40`  | 70 × 40         | Grand matériel (serveurs, baies)     | 25mm    |
| `80x50`  | 80 × 50         | Rack, armoires, équipements          | 30mm    |
| `100x50` | 100 × 50        | Étiquettes industrielles             | 35mm    |

---

### 8.5 Statuts PrintJob

| Statut     | Code         | Couleur | Description                  | Transitions             |
| ---------- | ------------ | ------- | ---------------------------- | ----------------------- |
| En attente | `pending`    | ⚪ Gris  | Job créé, pas encore traité  | → processing, cancelled |
| En cours   | `processing` | 🔵 Bleu  | Génération PDF en cours      | → completed, failed     |
| Terminé    | `completed`  | 🟢 Vert  | PDF généré, prêt à imprimer  | -                       |
| Échoué     | `failed`     | 🔴 Rouge | Erreur génération/impression | → pending (retry)       |
| Annulé     | `cancelled`  | ⚫ Noir  | Job annulé par utilisateur   | -                       |

---

### 8.6 Workflow Impression

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKFLOW IMPRESSION ÉTIQUETTES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. POST /api/printer/jobs/                                    │
│     Body: {                                                    │
│       "asset_ids": [210, 211, 212],                           │
│       "template_id": 1,                                        │
│       "printer_id": 1,                                         │
│       "copies": 1                                              │
│     }                                                          │
│         │                                                       │
│         ▼                                                       │
│  2. PrintJob créé (status: pending)                            │
│     └── UUID généré                                            │
│         │                                                       │
│         ▼                                                       │
│  3. Celery task: generate_print_job_pdf.delay(job_id)          │
│     └── Status: processing                                     │
│         │                                                       │
│         ▼                                                       │
│  4. PDF généré (ReportLab)                                     │
│     └── media/print_jobs/YYYY/MM/job_<uuid>.pdf               │
│         │                                                       │
│         ▼                                                       │
│  5. PrintLog enregistré (par asset)                            │
│     └── Audit: qui, quand, quelle imprimante                   │
│         │                                                       │
│         ▼                                                       │
│  6. Status: completed                                          │
│     └── PDF prêt à télécharger/imprimer                        │
│         │                                                       │
│         ▼                                                       │
│  7. GET /api/printer/jobs/<id>/download/                       │
│     └── application/pdf                                        │
│         │                                                       │
│         ▼                                                       │
│  8. Impression physique (MUNBYN/Samsung)                       │
│     └── Étiquettes collées sur assets                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 8.7 Exemples de Requêtes

#### **Créer Imprimante**

```bash
curl -X POST http://localhost:8000/api/printer/printers/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MUNBYN RW403B - Atelier",
    "connection_type": "usb",
    "device_path": "/dev/usb/lp0",
    "dpi": 203,
    "speed": 3,
    "density": 10,
    "paper_width_mm": 50,
    "paper_height_mm": 30,
    "is_default": true
  }'
```

#### **Créer Template**

```bash
curl -X POST http://localhost:8000/api/printer/templates/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Standard Laptop 50x30",
    "format": "50x30",
    "width_mm": 50,
    "height_mm": 30,
    "qr_size_mm": 20,
    "qr_position_x_mm": 5,
    "qr_position_y_mm": 5,
    "font_size_title": 10,
    "font_size_text": 8,
    "show_serial": true,
    "show_category": true,
    "show_location": true,
    "is_default": true
  }'
```

#### **Créer Job Impression**

```bash
curl -X POST http://localhost:8000/api/printer/jobs/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_ids": [210, 211, 212, 213, 214],
    "template_id": 1,
    "printer_id": 1,
    "copies": 1
  }'

# Response:
{
  "id": 45,
  "uuid": "abc123-def456-789",
  "status": "pending",
  "asset_count": 5,
  "message": "Job en cours de traitement"
}
```

#### **Télécharger PDF**

```bash
curl -X GET http://localhost:8000/api/printer/jobs/45/download/ \
  -H "Authorization: Token YOUR_TOKEN" \
  --output labels_20260326.pdf
```

#### **Générer QR Code Single Asset**

```bash
curl -X POST http://localhost:8000/api/printer/django-admin/inventory/asset/210/generate_qrcode/ \
  -H "Authorization: Token YOUR_TOKEN"

# Response:
{
  "uuid": "abc123-def456",
  "qr_url": "/media/qr_codes/2026/03/qr_asset_210_abc.png",
  "image": "http://localhost:8000/media/qr_codes/2026/03/qr_asset_210_abc.png"
}
```

#### **Imprimer Étiquette Single Asset**

```bash
curl -X GET "http://localhost:8000/api/printer/django-admin/inventory/asset/210/print_label/?format=50x30&copies=1" \
  -H "Authorization: Token YOUR_TOKEN" \
  --output label_210.pdf
```

---

### 8.8 Intégration Frontend

#### **Vue.js — Impression Batch**

```javascript
// static/admin_cmdb/js/printer.js
const { createApp } = window.VueCreateApp || Vue.createApp;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            printers: [],
            templates: [],
            selectedAssets: [],
            selectedPrinter: null,
            selectedTemplate: null,
            copies: 1,
            printing: false
        }
    },
    mounted() {
        this.fetchPrinters();
        this.fetchTemplates();
    },
    methods: {
        async fetchPrinters() {
            const res = await window.apiClient.get('/api/printer/printers/', {
                params: { is_active: true }
            });
            this.printers = res.data;
            this.selectedPrinter = this.printers.find(p => p.is_default)?.id;
        },
        async fetchTemplates() {
            const res = await window.apiClient.get('/api/printer/templates/', {
                params: { is_default: true }
            });
            this.templates = res.data;
            this.selectedTemplate = this.templates.find(t => t.is_default)?.id;
        },
        async printLabels() {
            this.printing = true;
            try {
                const res = await window.apiClient.post('/api/printer/jobs/', {
                    asset_ids: this.selectedAssets,
                    template_id: this.selectedTemplate,
                    printer_id: this.selectedPrinter,
                    copies: this.copies
                }, {
                    responseType: 'blob'
                });
                
                const url = window.URL.createObjectURL(res);
                const link = document.createElement('a');
                link.href = url;
                link.download = `labels_${Date.now()}.pdf`;
                link.click();
                window.URL.revokeObjectURL(url);
                
                alert('✅ Impression lancée');
            } catch (error) {
                alert('❌ Erreur impression: ' + error.message);
            } finally {
                this.printing = false;
            }
        }
    }
}).mount('#printer-app');
```

---

## 12. Workflows Complets (Mise à Jour)

### 12.1 Workflow Réception & Étiquetage (Avec Printer)

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKFLOW RÉCEPTION & ÉTIQUETAGE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. POST /api/v1/inventory/assets/                             │
│     └── Asset créé (ex: HP Elitebook G4)                       │
│         │                                                       │
│         ▼                                                       │
│  2. Signal post_save → QRCode.objects.create()                 │
│     └── UUID généré automatiquement                            │
│         │                                                       │
│         ▼                                                       │
│  3. POST /api/printer/django-admin/asset/<id>/generate_qrcode/ │
│     └── _generate_qr_image() → media/qr_codes/                 │
│         └── PNG 300x300px généré                               │
│         │                                                       │
│         ▼                                                       │
│  4. /admin/assets/ → Sélectionner assets                       │
│     └── Action: "Imprimer Étiquettes"                          │
│         │                                                       │
│         ▼                                                       │
│  5. POST /api/printer/jobs/                                    │
│     └── PrintJob créé (status: pending)                        │
│         │                                                       │
│         ▼                                                       │
│  6. Celery: generate_print_job_pdf.delay(job_id)               │
│     └── PDF batch généré (ReportLab)                           │
│         └── media/print_jobs/YYYY/MM/job_<uuid>.pdf           │
│         │                                                       │
│         ▼                                                       │
│  7. PrintLog enregistré (par asset)                            │
│     └── Audit: qui, quand, quelle imprimante                   │
│         │                                                       │
│         ▼                                                       │
│  8. GET /api/printer/jobs/<id>/download/                       │
│     └── PDF téléchargé → Impression MUNBYN                     │
│         │                                                       │
│         ▼                                                       │
│  9. Étiquettes collées sur assets                              │
│     └── Scan vérification → /admin/scanner/                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Finale (Mise à Jour)

| Module           | URLs   | API Endpoints | Templates | Static Files | Statut |
| ---------------- | ------ | ------------- | --------- | ------------ | ------ |
| **Dashboard**    | 1      | 0             | 1         | 2            | ✅      |
| **Admin Layout** | 1      | 0             | 1         | 2            | ✅      |
| **Assets**       | 7      | 12            | 3         | 2            | ✅      |
| **Tickets**      | 4      | 14            | 3         | 2            | ✅      |
| **Scanner**      | 7      | 15            | 6         | 2            | ✅      |
| **Stock**        | 4      | 13            | 3         | 2            | ✅      |
| **Printer ⭐**    | **12** | **18**        | **4**     | **2**        | ✅      |
| **Search**       | 1      | 3             | 1         | 2            | ✅      |
| **Auth**         | 5      | 7             | 1         | 0            | ✅      |
| **Public**       | 2      | 1             | 1         | 0            | ✅      |
| **TOTAL**        | **44** | **83**        | **24**    | **16**       | ✅      |

---

## 📊 Résumé Module Printer

| Composant         | Count | Description                                          |
| ----------------- | ----- | ---------------------------------------------------- |
| **API Endpoints** | 18    | CRUD Printers, Templates, Jobs, Labels               |
| **URLs Web**      | 12    | Admin views, print pages                             |
| **Modèles**       | 4     | PrintTemplate, Printer, PrintJob, PrintLog           |
| **Templates**     | 4     | print.html, templates.html, printers.html, jobs.html |
| **Formats**       | 5     | 30x20, 50x30, 70x40, 80x50, 100x50                   |
| **Statuts Job**   | 5     | pending, processing, completed, failed, cancelled    |
| **Imprimantes**   | ∞     | USB, Bluetooth, WiFi, Network (CUPS)                 |

---

**Documentation complète des URLs CMDB Inventory v3.0 — Mars 2026** 🎉  
**Module Printer intégré avec 18 endpoints API et 12 URLs web**