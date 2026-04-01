# 📋 Rapport Technique — Module Scanner : Analyse Complète Scan & Print

**Version:** 3.0  
**Date:** 26 Mars 2026  
**Contexte:** CMDB Inventory — Tracabilité Assets

---

## 1. Analyse Algorithmique — Workflow Scan & Print

### 1.1 Cycle de Vie Complet d'un Asset

```
┌─────────────────────────────────────────────────────────────────┐
│              CYCLE DE VIE ASSET — SCAN & PRINT                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. RÉCEPTION                                                   │
│     └── Asset créé → QR Code généré automatiquement            │
│                                                                 │
│  2. ÉTIQUETAGE                                                  │
│     └── PrintJob créé → Étiquette imprimée → Collée sur asset  │
│                                                                 │
│  3. UTILISATION                                                 │
│     └── Scan régulier → Vérification existence/localisation    │
│                                                                 │
│  4. MAINTENANCE                                                 │
│     └── Scan → Ticket créé → Pièces stock consommées           │
│                                                                 │
│  5. MOUVEMENT                                                   │
│     └── Scan → Localisation mise à jour → PrintLog enregistré  │
│                                                                 │
│  6. RETRAITE                                                    │
│     └── Scan → Statut "retired" → Historique complet           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1.2 Rôle des 4 Nouveaux Modèles

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODÈLES SCAN & PRINT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │ PrintTemplate│        │   Printer   │                       │
│  │             │        │             │                       │
│  │ - Format    │        │ - USB/BT/WiFi│                      │
│  │ - Layout    │        │ - IP/MAC    │                       │
│  │ - Taille    │        │ - Config    │                       │
│  └──────┬──────┘        └──────┬──────┘                       │
│         │                      │                                │
│         │                      │                                │
│         └──────────┬───────────┘                                │
│                    │                                            │
│                    ▼                                            │
│            ┌─────────────┐                                     │
│            │  PrintJob   │                                     │
│            │             │                                     │
│            │ - Assets[]  │                                     │
│            │ - Template  │                                     │
│            │ - Printer   │                                     │
│            │ - Status    │                                     │
│            │ - PDF File  │                                     │
│            └──────┬──────┘                                     │
│                   │                                             │
│                   │ 1-to-Many                                   │
│                   ▼                                             │
│            ┌─────────────┐                                     │
│            │  PrintLog   │                                     │
│            │             │                                     │
│            │ - Asset     │                                     │
│            │ - PrintedBy │                                     │
│            │ - Timestamp │                                     │
│            │ - Audit     │                                     │
│            └─────────────┘                                     │
│                                                                 │
│  FLUX COMPLET:                                                  │
│  ───────────                                                    │
│  Template + Printer → PrintJob → PDF → PrintLog (audit)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1.3 Détail des 4 Modèles

#### **PrintTemplate — Configuration Étiquette**

| Champ                           | Type                       | Usage                        |
| ------------------------------- | -------------------------- | ---------------------------- |
| `format`                        | 30x20, 50x30, 70x40, 80x50 | Taille physique étiquette    |
| `width_mm`, `height_mm`         | Integer                    | Dimensions exactes           |
| `qr_size_mm`                    | Integer                    | Taille QR Code sur étiquette |
| `qr_position_x/y_mm`            | Integer                    | Position QR (coordonnées)    |
| `font_size_title/text`          | Integer                    | Tailles police               |
| `show_serial/category/location` | Boolean                    | Champs à afficher            |

**Exemple d'Usage:**
```python
# Template standard pour laptops
template = PrintTemplate.objects.create(
    name='Standard Laptop 50x30',
    format='50x30',
    width_mm=50,
    height_mm=30,
    qr_size_mm=20,
    qr_position_x_mm=5,
    qr_position_y_mm=5,
    font_size_title=10,
    font_size_text=8,
    show_serial=True,
    show_category=True,
    show_location=True,
    is_default=True
)
```

---

#### **Printer — Configuration Imprimante**

| Champ                     | Type                          | Usage                   |
| ------------------------- | ----------------------------- | ----------------------- |
| `connection_type`         | usb, bluetooth, wifi, network | Type de connexion       |
| `ip_address`, `port`      | IP, Integer                   | Pour WiFi/Ethernet      |
| `mac_address`             | String                        | Pour Bluetooth          |
| `device_path`             | String                        | Pour USB (/dev/usb/lp0) |
| `dpi`, `speed`, `density` | Integer                       | Qualité impression      |
| `paper_width/height_mm`   | Integer                       | Format papier           |
| `is_default`              | Boolean                       | Imprimante par défaut   |

**Exemple d'Usage:**
```python
# Imprimante USB atelier
printer = Printer.objects.create(
    name='MUNBYN RW403B - Atelier',
    connection_type='usb',
    device_path='/dev/usb/lp0',
    dpi=203,
    speed=3,
    density=10,
    paper_width_mm=50,
    paper_height_mm=30,
    is_default=True
)

# Imprimante WiFi bureau
printer = Printer.objects.create(
    name='Samsung SP350 - Bureau',
    connection_type='wifi',
    ip_address='192.168.1.100',
    port=9100,
    dpi=203,
    speed=3,
    density=12,
    paper_width_mm=70,
    paper_height_mm=40,
    is_default=False
)
```

---

#### **PrintJob — Job d'Impression (Batch)**

| Champ                 | Type                                   | Usage                       |
| --------------------- | -------------------------------------- | --------------------------- |
| `uuid`                | UUID                                   | Identifiant unique du job   |
| `asset_ids`           | JSONField                              | Liste des assets à imprimer |
| `template`, `printer` | ForeignKey                             | Configuration utilisée      |
| `copies`              | Integer                                | Nombre de copies par asset  |
| `status`              | pending, processing, completed, failed | Statut du job               |
| `pdf_file`            | FileField                              | PDF généré (stocké)         |
| `error_message`       | Text                                   | Erreur si failed            |
| `created_by`          | ForeignKey                             | Technicien qui a lancé      |

**Exemple d'Usage:**
```python
# Job batch pour 50 laptops
job = PrintJob.objects.create(
    created_by=request.user,
    asset_ids=[210, 211, 212, ..., 260],  # 50 assets
    template=template_50x30,
    printer=printer_munbyn,
    copies=1,
    status='pending'
)

# Task Celery génère le PDF
generate_print_job_pdf.delay(job.id)

# Après génération
job.status = 'completed'
job.pdf_file = 'print_jobs/2026/03/job_abc123.pdf'
job.completed_at = timezone.now()
job.save()
```

---

#### **PrintLog — Audit & Traçabilité**

| Champ                           | Type       | Usage                      |
| ------------------------------- | ---------- | -------------------------- |
| `job`                           | ForeignKey | PrintJob associé           |
| `asset`                         | ForeignKey | Asset imprimé              |
| `printed_by`                    | ForeignKey | Technicien (qui a imprimé) |
| `printer_name`, `template_name` | String     | Snapshot configuration     |
| `printed_at`                    | DateTime   | Timestamp exact            |
| `ip_address`, `user_agent`      | String     | Contexte technique         |

**Exemple d'Usage:**
```python
# Log créé automatiquement après impression
for asset_id in job.asset_ids:
    PrintLog.objects.create(
        job=job,
        asset_id=asset_id,
        printed_by=request.user,
        printer_name=job.printer.name,
        template_name=job.template.name,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )

# Requête audit : qui a imprimé quoi ?
PrintLog.objects.filter(
    printed_at__gte=timezone.now() - timedelta(days=30)
).select_related('asset', 'printed_by')
```

---

### 1.4 Relations entre Modèles

```
┌─────────────────────────────────────────────────────────────────┐
│                 DIAGRAMME DE RELATIONS COMPLET                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │   Asset     │         │  QRCode     │                       │
│  │  (210)      │◄────────│             │                       │
│  │             │  1-to-1 │ - uuid      │                       │
│  │ - S/N       │         │ - image     │                       │
│  └──────┬──────┘         └─────────────┘                       │
│         │                       │                               │
│         │ 1-to-Many           │ 1-to-Many                       │
│         │                       │                               │
│         ▼                       ▼                               │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │ ScanLog     │         │  PrintLog   │                       │
│  │             │         │             │                       │
│  │ - scanned   │         │ - printed   │                       │
│  │ - timestamp │         │ - timestamp │                       │
│  └─────────────┘         └──────┬──────┘                       │
│                                 │                               │
│                          1-to-Many                              │
│                                 │                               │
│                                 ▼                               │
│                         ┌─────────────┐                        │
│                         │  PrintJob   │                        │
│                         │             │                        │
│                         │ - batch     │                        │
│                         │ - PDF       │                        │
│                         └──────┬──────┘                        │
│                                │                                │
│                    ┌───────────┴───────────┐                   │
│                    │                       │                   │
│                    ▼                       ▼                   │
│            ┌─────────────┐         ┌─────────────┐             │
│            │PrintTemplate│         │   Printer   │             │
│            │             │         │             │             │
│            │ - layout    │         │ - config    │             │
│            └─────────────┘         └─────────────┘             │
│                                                                 │
│  TRACABILITÉ COMPLÈTE:                                          │
│  ──────────────────                                             │
│  Asset → QR Code → Scan (ScanLog) + Print (PrintLog)           │
│  Chaque action est enregistrée avec timestamp + user           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Pages UI à Modifier/Créer

### 2.1 Pages Existantes à Modifier

| Page                  | Modifications                                  | Priorité  |
| --------------------- | ---------------------------------------------- | --------- |
| `/admin/scanner/`     | ✅ Ajouter section Print + Templates + Printers | 🔴 Haute   |
| `/admin/assets/`      | ✅ Bouton "Imprimer Étiquette" (single/batch)   | 🔴 Haute   |
| `/admin/assets/<id>/` | ✅ Onglet "Étiquette" + Preview QR              | 🔴 Haute   |
| `/admin/stock/`       | ⚠️ Lien vers impression étiquettes stock        | 🟠 Moyenne |

### 2.2 Nouvelles Pages à Créer

| Page                   | URL                         | Description             | Priorité  |
| ---------------------- | --------------------------- | ----------------------- | --------- |
| **Landing Scan/Print** | `/admin/scan-print/`        | Hub central techniciens | 🔴 Haute   |
| **Templates**          | `/admin/scanner/templates/` | CRUD PrintTemplate      | 🟠 Moyenne |
| **Printers**           | `/admin/scanner/printers/`  | CRUD Printer config     | 🟠 Moyenne |
| **Print Jobs**         | `/admin/scanner/jobs/`      | Historique jobs         | 🟠 Moyenne |
| **Print Logs**         | `/admin/scanner/logs/`      | Audit impressions       | 🟢 Basse   |

---

## 3. Landing Page — Scan & Print Hub

### 3.1 Concept

```
┌─────────────────────────────────────────────────────────────────┐
│                    LANDING PAGE TECHNICIENS                     │
│                    /admin/scan-print/                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🎯 CENTRE DE TRACABILITÉ ASSETS                        │   │
│  │     Scanner + Imprimer + Auditer                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   📷 SCAN   │  │   🖨️ PRINT  │  │   📊 AUDIT  │             │
│  │             │  │             │  │             │             │
│  │ Scanner QR  │  │ Étiquettes  │  │ Historique  │             │
│  │ Code-Barres │  │ Batch/Single│  │ Complet     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ⚡ ACTIONS RAPIDES                                      │   │
│  │  [Scanner Asset] [Imprimer Étiquette] [Voir Historique] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📊 STATISTIQUES EN TEMPS RÉEL                          │   │
│  │  Scans today: 145  |  Prints today: 89  |  Assets: 210  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Code Complet — `templates/admin/scan_print/landing.html`

```html
<!-- templates/admin/scan_print/landing.html -->
{% extends 'admin_base.html' %}
{% load static %}

{% block title %}Scan & Print Hub — CMDB Inventory{% endblock %}

{% block extra_css %}
<link href="{% static 'admin_cmdb/css/scan_print_hub.css' %}" rel="stylesheet">
<style>
    :root {
        --bg-dark: #0f172a;
        --bg-card: rgba(15, 23, 42, 0.75);
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }
    
    body {
        background: var(--bg-dark);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }
    
    .hub-hero {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 40px;
        text-align: center;
    }
    
    .hub-hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 16px;
        background: linear-gradient(135deg, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hub-hero p {
        color: var(--text-muted);
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .hub-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 24px;
        margin-bottom: 40px;
    }
    
    .hub-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 32px;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        color: inherit;
    }
    
    .hub-card:hover {
        transform: translateY(-4px);
        border-color: var(--accent);
        box-shadow: 0 20px 40px rgba(37, 99, 235, 0.2);
    }
    
    .hub-card-icon {
        width: 80px;
        height: 80px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin-bottom: 24px;
    }
    
    .hub-card-icon.scan { background: rgba(37, 99, 235, 0.2); color: #3b82f6; }
    .hub-card-icon.print { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
    .hub-card-icon.audit { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
    
    .hub-card h3 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    .hub-card p {
        color: var(--text-muted);
        line-height: 1.6;
        margin-bottom: 20px;
    }
    
    .hub-card-features {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 16px;
    }
    
    .hub-feature {
        padding: 6px 12px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    .quick-actions {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 40px;
    }
    
    .quick-actions h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .quick-actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
    }
    
    .quick-action-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 24px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        text-decoration: none;
        color: var(--text-main);
        transition: all 0.2s;
    }
    
    .quick-action-btn:hover {
        background: rgba(37, 99, 235, 0.1);
        border-color: var(--accent);
        transform: translateY(-2px);
    }
    
    .quick-action-btn i {
        font-size: 2rem;
        margin-bottom: 12px;
    }
    
    .quick-action-btn span {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stats-bar {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 40px;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 24px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--accent);
        line-height: 1.2;
    }
    
    .stat-label {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    .recent-activity {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 32px;
    }
    
    .recent-activity h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 24px;
    }
    
    .activity-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .activity-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        transition: background 0.2s;
    }
    
    .activity-item:hover {
        background: rgba(255, 255, 255, 0.06);
    }
    
    .activity-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .activity-icon.scan { background: rgba(37, 99, 235, 0.2); color: #3b82f6; }
    .activity-icon.print { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
    
    .activity-content {
        flex-grow: 1;
    }
    
    .activity-title {
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .activity-meta {
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    
    .activity-time {
        font-size: 0.85rem;
        color: var(--text-muted);
        white-space: nowrap;
    }
    
    @media (max-width: 768px) {
        .hub-hero h1 { font-size: 1.8rem; }
        .hub-cards { grid-template-columns: 1fr; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        .quick-actions-grid { grid-template-columns: repeat(2, 1fr); }
    }
</style>
{% endblock %}

{% block content %}
<div id="scan-print-hub" class="container-fluid py-4">
    
    <!-- Hero Section -->
    <div class="hub-hero">
        <h1>🎯 Centre de Tracabilité Assets</h1>
        <p>Scanner, imprimer et auditer tous vos assets IT en un seul endroit. Traçabilité complète du cycle de vie.</p>
    </div>
    
    <!-- Main Cards -->
    <div class="hub-cards">
        <!-- Scan Card -->
        <a href="/admin/scanner/" class="hub-card">
            <div class="hub-card-icon scan">📷</div>
            <h3>Scanner QR / Code-Barres</h3>
            <p>Identifiez instantanément n'importe quel asset avec votre scanner USB, douchette Bluetooth ou caméra smartphone.</p>
            <div class="hub-card-features">
                <span class="hub-feature">USB HoneyWell</span>
                <span class="hub-feature">Bluetooth</span>
                <span class="hub-feature">Webcam</span>
                <span class="hub-feature">Smartphone</span>
            </div>
        </a>
        
        <!-- Print Card -->
        <a href="/admin/scanner/print/" class="hub-card">
            <div class="hub-card-icon print">🖨️</div>
            <h3>Imprimer Étiquettes QR</h3>
            <p>Générez et imprimez des étiquettes QR Code professionnelles pour tous vos assets. Supporte impression batch.</p>
            <div class="hub-card-features">
                <span class="hub-feature">Single/Batch</span>
                <span class="hub-feature">USB/BT/WiFi</span>
                <span class="hub-feature">Templates</span>
                <span class="hub-feature">PDF Export</span>
            </div>
        </a>
        
        <!-- Audit Card -->
        <a href="/admin/scanner/logs/" class="hub-card">
            <div class="hub-card-icon audit">📊</div>
            <h3>Audit & Historique</h3>
            <p>Consultez l'historique complet des scans et impressions. Traçabilité conforme pour audit et compliance.</p>
            <div class="hub-card-features">
                <span class="hub-feature">ScanLog</span>
                <span class="hub-feature">PrintLog</span>
                <span class="hub-feature">Export CSV</span>
                <span class="hub-feature">Rapports</span>
            </div>
        </a>
    </div>
    
    <!-- Stats Bar -->
    <div class="stats-bar">
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">[[ stats.scans_today ]]</div>
                <div class="stat-label">📷 Scans aujourd'hui</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">[[ stats.prints_today ]]</div>
                <div class="stat-label">🖨️ Impressions aujourd'hui</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">[[ stats.total_assets ]]</div>
                <div class="stat-label">💻 Assets totaux</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">[[ stats.printers_active ]]</div>
                <div class="stat-label">🖨️ Imprimantes actives</div>
            </div>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="quick-actions">
        <h2>⚡ Actions Rapides</h2>
        <div class="quick-actions-grid">
            <a href="/admin/scanner/" class="quick-action-btn">
                <i>📷</i>
                <span>Scanner Asset</span>
            </a>
            <a href="/admin/assets/" class="quick-action-btn">
                <i>📋</i>
                <span>Sélectionner Assets</span>
            </a>
            <a href="/admin/scanner/print/" class="quick-action-btn">
                <i>🖨️</i>
                <span>Imprimer Étiquettes</span>
            </a>
            <a href="/admin/scanner/templates/" class="quick-action-btn">
                <i>🎨</i>
                <span>Templates</span>
            </a>
            <a href="/admin/scanner/printers/" class="quick-action-btn">
                <i>⚙️</i>
                <span>Imprimantes</span>
            </a>
            <a href="/admin/scanner/jobs/" class="quick-action-btn">
                <i>📜</i>
                <span>Jobs d'Impression</span>
            </a>
            <a href="/admin/scanner/logs/" class="quick-action-btn">
                <i>🔍</i>
                <span>Historique</span>
            </a>
            <a href="/admin/search/" class="quick-action-btn">
                <i>🔎</i>
                <span>Recherche</span>
            </a>
        </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="recent-activity">
        <h2>🕐 Activité Récente</h2>
        <div class="activity-list" v-if="recentActivity.length > 0">
            <div class="activity-item" v-for="activity in recentActivity" :key="activity.id">
                <div class="activity-icon" :class="activity.type">
                    [[ activity.type === 'scan' ? '📷' : '🖨️' ]]
                </div>
                <div class="activity-content">
                    <div class="activity-title">[[ activity.title ]]</div>
                    <div class="activity-meta">[[ activity.meta ]]</div>
                </div>
                <div class="activity-time">[[ activity.time ]]</div>
            </div>
        </div>
        <div v-else class="text-center text-muted py-5">
            <i style="font-size: 3rem; opacity: 0.3;">📊</i>
            <p class="mt-3">Aucune activité récente</p>
        </div>
    </div>
    
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'admin_cmdb/js/scan_print_hub.js' %}"></script>
{% endblock %}
```

---

### 3.3 Code JavaScript — `static/admin_cmdb/js/scan_print_hub.js`

```javascript
// static/admin_cmdb/js/scan_print_hub.js
const { createApp } = window.VueCreateApp || Vue.createApp;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            stats: {
                scans_today: 0,
                prints_today: 0,
                total_assets: 0,
                printers_active: 0
            },
            recentActivity: []
        }
    },
    mounted() {
        this.fetchStats();
        this.fetchRecentActivity();
    },
    methods: {
        async fetchStats() {
            try {
                const [assetsRes, printersRes] = await Promise.all([
                    window.apiClient.get('/inventory/assets/', { params: { page_size: 1 } }),
                    window.apiClient.get('/scanner/printers/', { params: { is_active: true } })
                ]);
                
                this.stats.total_assets = assetsRes.data.count || 0;
                this.stats.printers_active = printersRes.data.length || 0;
                
                // Stats scans/prints today (endpoints à créer)
                const today = new Date().toISOString().split('T')[0];
                const [scansRes, printsRes] = await Promise.all([
                    window.apiClient.get('/scanner/logs/', { params: { date: today } }),
                    window.apiClient.get('/scanner/print-logs/', { params: { date: today } })
                ]);
                
                this.stats.scans_today = scansRes.data.count || 0;
                this.stats.prints_today = printsRes.data.count || 0;
                
            } catch (error) {
                console.error('Erreur fetch stats:', error);
            }
        },
        async fetchRecentActivity() {
            try {
                const [scansRes, printsRes] = await Promise.all([
                    window.apiClient.get('/scanner/logs/', { params: { page_size: 5 } }),
                    window.apiClient.get('/scanner/print-logs/', { params: { page_size: 5 } })
                ]);
                
                const scans = (scansRes.data.results || scansRes.data || []).map(s => ({
                    id: `scan-${s.id}`,
                    type: 'scan',
                    title: `📷 Scan: ${s.asset_name || 'Asset inconnu'}`,
                    meta: `Par: ${s.scanned_by || 'Inconnu'} • IP: ${s.ip_address || 'N/A'}`,
                    time: this.formatTime(s.created_at)
                }));
                
                const prints = (printsRes.data.results || printsRes.data || []).map(p => ({
                    id: `print-${p.id}`,
                    type: 'print',
                    title: `🖨️ Impression: ${p.asset_name || 'Asset inconnu'}`,
                    meta: `Par: ${p.printed_by || 'Inconnu'} • ${p.printer_name}`,
                    time: this.formatTime(p.printed_at)
                }));
                
                this.recentActivity = [...scans, ...prints]
                    .sort((a, b) => new Date(b.time) - new Date(a.time))
                    .slice(0, 10);
                    
            } catch (error) {
                console.error('Erreur fetch activity:', error);
            }
        },
        formatTime(dateStr) {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) return 'À l\'instant';
            if (diff < 3600000) return `Il y a ${Math.floor(diff / 60000)} min`;
            if (diff < 86400000) return `Il y a ${Math.floor(diff / 3600000)} h`;
            return date.toLocaleDateString('fr-FR');
        }
    }
}).mount('#scan-print-hub');
```

---

## 4. URLs à Ajouter

```python
# backend/scanner/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... existing URLs
    
    # Landing Page Scan & Print
    path('scan-print/', views.scan_print_landing, name='scan-print-landing'),
    
    # Print Management
    path('print/', views.print_labels_view, name='print-labels'),
    path('templates/', views.PrintTemplateViewSet.as_view({'get': 'list', 'post': 'create'}), name='print-templates'),
    path('templates/<int:pk>/', views.PrintTemplateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='print-template-detail'),
    path('printers/', views.PrinterViewSet.as_view({'get': 'list', 'post': 'create'}), name='printers'),
    path('printers/<int:pk>/', views.PrinterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='printer-detail'),
    path('jobs/', views.PrintJobViewSet.as_view({'get': 'list', 'post': 'create'}), name='print-jobs'),
    path('jobs/<int:pk>/', views.PrintJobViewSet.as_view({'get': 'retrieve'}), name='print-job-detail'),
    path('logs/', views.PrintLogViewSet.as_view({'get': 'list'}), name='print-logs'),
]
```

---

## 5. Workflow Complet — Exemple Technicien

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKFLOW TECHNICIEN COMPLET                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. ARRIVÉE MATIN                                               │
│     └── /admin/scan-print/ → Vue statistiques jour              │
│                                                                 │
│  2. RÉCEPTION 10 LAPTOPS                                        │
│     └── /admin/assets/new/ → Créer 10 assets                    │
│     └── QR Codes générés automatiquement                        │
│                                                                 │
│  3. ÉTIQUETAGE                                                  │
│     └── /admin/assets/ → Sélectionner 10 laptops                │
│     └── Action: "Imprimer Étiquettes"                           │
│     └── PrintJob créé → PDF généré → Impression MUNBYN          │
│     └── Coller étiquettes sur laptops                           │
│                                                                 │
│  4. SCAN CONTRÔLE                                               │
│     └── /admin/scanner/ → Scanner chaque laptop                 │
│     └── Vérifier fiche asset correcte                           │
│     └── ScanLog enregistré automatiquement                      │
│                                                                 │
│  5. MAINTENANCE LAPTOP #215                                     │
│     └── Scan laptop → Fiche asset                               │
│     └── Bouton: "Créer Ticket"                                  │
│     └── Ticket créé → Pièces consommées (StockMovement)         │
│     └── PrintLog: Étiquette de maintenance imprimée             │
│                                                                 │
│  6. FIN JOURNÉE                                                 │
│     └── /admin/scan-print/ → Vérifier activité jour             │
│     └── Scans: 45 | Prints: 23 | Assets: 210                    │
│     └── Export CSV pour rapport                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Finale

| Élément           | Statut | Fichier                                    |
| ----------------- | ------ | ------------------------------------------ |
| **Modèles Print** | ✅      | `scanner/models.py`                        |
| **Landing Page**  | ✅      | `templates/admin/scan_print/landing.html`  |
| **JS Hub**        | ✅      | `static/admin_cmdb/js/scan_print_hub.js`   |
| **URLs**          | ✅      | `scanner/urls.py`                          |
| **Views**         | ⚠️      | `scanner/views.py` (à compléter)           |
| **API Endpoints** | ⚠️      | `scanner/api/views.py` (à compléter)       |
| **CSS Hub**       | ⚠️      | `static/admin_cmdb/css/scan_print_hub.css` |

---

**Cette landing page est le hub central pour toutes les opérations Scan & Print de vos techniciens !** 🎉