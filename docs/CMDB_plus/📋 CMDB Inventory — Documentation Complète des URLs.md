# 📋 CMDB Inventory — Documentation Complète des URLs

**Version:** 2.0  
**Date:** 26 Mars 2026  
**Projet:** CMDB Inventory — Société de Reconditionnement IT  
**Stack:** Django 5 + DRF + Vue 3 (CDN) + Bootstrap 5.3

---

## 📑 Table des Matières

1. [Vue d'Ensemble des Modules](#1-vue-densemble-des-modules)
2. [URLs Publiques (Sans Authentication)](#2-urls-publiques-sans-authentication)
3. [URLs Interface Métier (/admin/)](#3-urls-interface-métier-admin)
4. [API REST Inventory](#4-api-rest-inventory)
5. [API REST Maintenance](#5-api-rest-maintenance)
6. [API REST Scanner](#6-api-rest-scanner)
7. [API REST Stock](#7-api-rest-stock)
8. [API REST Printer ⭐ NOUVEAU](https://chat.qwen.ai/c/aa64ddbf-1b84-412e-9eaa-be5af298305b#8-api-rest-printer--nouveau)
9. [API REST Authentication](#8-api-rest-authentication)
10. [Django Admin Système](#9-django-admin-système)
11. [Fichiers Statiques](#10-fichiers-statiques)
12. [Workflows Complets](#11-workflows-complets)

---

## 1. Vue d'Ensemble des Modules

| Module              | Base URL               | Description                         | Auth Requise |
| ------------------- | ---------------------- | ----------------------------------- | ------------ |
| **Dashboard**       | `/`                    | Vitrine publique, statistiques      | ❌ Non        |
| **Admin Métier**    | `/admin/`              | Interface techniciens/gestionnaires | ✅ Oui        |
| **Scanner**         | `/admin/scanner/`      | Scan QR/Code-barres                 | ✅ Oui        |
| **Scan Public**     | `/scan/<uuid>/`        | Fiche asset publique (terrain)      | ❌ Non        |
| **API Inventory**   | `/api/v1/inventory/`   | Gestion assets                      | ✅ Oui        |
| **API Maintenance** | `/api/v1/maintenance/` | Tickets, réparations                | ✅ Oui        |
| **API Scanner**     | `/api/v1/scanner/`     | Résolution QR, logs                 | ⚠️ Mixte      |
| **API Printer**     | /api/printer/          | Impression, templates, printers<    | ✅ Oui        |
| **API Stock**       | `/api/v1/stock/`       | Articles atelier, mouvements        | ✅ Oui        |
| **API Auth**        | `/api/v1/auth/`        | Token, utilisateurs                 | ✅ Oui        |
| **Django Admin**    | `/django-admin/`       | Administration système              | ✅ Superuser  |

---

## 2. URLs Publiques (Sans Authentication)

### 2.1 Dashboard & Pages Publiques

| URL                      | Méthode  | Vue/Template              | Description                    | Usage                           |
| ------------------------ | -------- | ------------------------- | ------------------------------ | ------------------------------- |
| `/`                      | GET      | `dashboard.html`          | Dashboard vitrine publique     | Stats, KPIs, navigation         |
| `/scan/<uuid>/`          | GET      | `public/scan_result.html` | Fiche asset publique (QR scan) | Techniciens terrain sans compte |
| `/admin/login/`          | GET/POST | `admin_login.html`        | Authentification Token         | Login techniciens               |
| `/media/qr_codes/<file>` | GET      | -                         | Images QR Code (static)        | Téléchargement étiquettes       |

### 2.2 Détails — `/scan/<uuid>/`

| Élément               | Détail                                                       |
| --------------------- | ------------------------------------------------------------ |
| **Paramètre**         | `uuid` = UUID du QR Code ou Serial Number                    |
| **Template**          | `public/scan_result.html`                                    |
| **View**              | `scanner.views.public_scan_result`                           |
| **Données affichées** | Nom, S/N, photo, statut, localisation, assigné, garantie, tickets ouverts |
| **Actions**           | Télécharger QR, voir tickets                                 |
| **Auth**              | ❌ Aucune (accessible sans compte)                            |
| **Use Case**          | Technicien terrain scanne QR avec smartphone → fiche asset sans login |

---

## 3. URLs Interface Métier (/admin/)

### 3.1 Layout & Navigation

| URL                         | Méthode  | Template                        | Description                    | Composants                                 |
| --------------------------- | -------- | ------------------------------- | ------------------------------ | ------------------------------------------ |
| `/admin/`                   | GET      | `admin_base.html` + dashboard   | Dashboard métier (après login) | Sidebar, Navbar, KPIs                      |
| `/admin/assets/`            | GET      | `admin/assets/list.html`        | Liste assets + filtres         | Tableau, filtres, pagination               |
| `/admin/assets/new/`        | GET/POST | `admin/assets/form.html`        | Création asset                 | Formulaire complet                         |
| `/admin/assets/<id>/`       | GET      | `admin/assets/detail.html`      | Fiche détail asset             | 4 onglets (Infos, Mouvements, Tickets, QR) |
| `/admin/assets/<id>/edit/`  | GET/PUT  | `admin/assets/form.html`        | Édition asset                  | Formulaire pré-rempli                      |
| `/admin/tickets/`           | GET      | `admin/tickets/list.html`       | Tickets Kanban + tableau       | Drag-drop, statuts                         |
| `/admin/tickets/new/`       | GET/POST | `admin/tickets/form.html`       | Création ticket                | Formulaire + sélection asset               |
| `/admin/tickets/<id>/`      | GET      | `admin/tickets/detail.html`     | Détail ticket                  | Workflow, commentaires, pièces             |
| `/admin/scanner/`           | GET      | `admin/scanner/index.html`      | Interface scan (USB/Webcam)    | ZXing, buffer USB, historique              |
| `/admin/stock/`             | GET      | `admin/stock/list.html`         | Stock atelier + alertes        | Tableau, badges stock                      |
| `/admin/stock/<id>/`        | GET      | `admin/stock/detail.html`       | Fiche article + mouvements     | Timeline, stats                            |
| `/admin/stock/movement/`    | GET/POST | `admin/stock/movement.html`     | Entrée/Sortie rapide           | Modal, lien ticket                         |
| `/admin/search/`            | GET      | `admin/search/results.html`     | Recherche globale              | Assets + Tickets + Stock                   |
| `/admin/scan-print/`        | GET      | `admin/scan_print/landing.html` | Hub Scan & Print               | Stats, activité récente, actions rapides   |
| `/admin/scanner/print/`     | GET/POST | `admin/scanner/print.html`      | Impression étiquettes          | Templates, imprimantes, PDF batch          |
| `/admin/scanner/templates/` | GET/POST | `admin/scanner/templates.html`  | Gestion templates              | CRUD PrintTemplate                         |
| `/admin/scanner/printers/`  | GET/POST | `admin/scanner/printers.html`   | Gestion imprimantes            | CRUD Printer (USB/BT/WiFi)                 |
| `/admin/scanner/jobs/`      | GET      | `admin/scanner/jobs.html`       | Historique jobs                | PrintJob status, download PDF              |
| `/admin/scanner/logs/`      | GET      | `admin/scanner/logs.html`       | Logs audit impressions         | PrintLog, filtres, export                  |

### 3.2 Détails — Module Assets

| URL                          | Méthode  | API Consommée                                | Description             | Permissions   |
| ---------------------------- | -------- | -------------------------------------------- | ----------------------- | ------------- |
| `/admin/assets/`             | GET      | `GET /api/v1/inventory/assets/`              | Liste paginée + filtres | Technicien+   |
| `/admin/assets/new/`         | GET/POST | `POST /api/v1/inventory/assets/`             | Création + QR auto      | Gestionnaire+ |
| `/admin/assets/<id>/`        | GET      | `GET /api/v1/inventory/assets/<id>/`         | Fiche détail 4 onglets  | Technicien+   |
| `/admin/assets/<id>/edit/`   | GET/PUT  | `PUT /api/v1/inventory/assets/<id>/`         | Édition asset           | Gestionnaire+ |
| `/admin/assets/<id>/move/`   | POST     | `POST /api/v1/inventory/assets/<id>/move/`   | Changer localisation    | Technicien+   |
| `/admin/assets/<id>/assign/` | POST     | `POST /api/v1/inventory/assets/<id>/assign/` | Assigner utilisateur    | Gestionnaire+ |
| `/admin/assets/<id>/retire/` | POST     | `POST /api/v1/inventory/assets/<id>/retire/` | Archiver asset          | Gestionnaire+ |

### 3.3 Détails — Module Scanner

| URL                         | Méthode  | API Consommée                        | Description                 | Permissions |
| --------------------------- | -------- | ------------------------------------ | --------------------------- | ----------- |
| `/admin/scanner/`           | GET      | `GET /api/v1/scanner/scan/<uuid>/`   | Interface scan USB/Webcam   | Technicien+ |
| `/admin/scanner/print/`     | GET/POST | `POST /api/v1/scanner/print-labels/` | Impression étiquettes batch | Technicien+ |
| `/admin/scanner/templates/` | GET/POST | API PrintTemplate                    | Gestion templates           | Admin+      |
| `/admin/scanner/printers/`  | GET/POST | API Printer                          | Configuration imprimantes   | Admin+      |
| `/admin/scanner/jobs/`      | GET      | API PrintJob                         | Historique jobs             | Technicien+ |
| `/admin/scanner/logs/`      | GET      | API PrintLog                         | Audit impressions           | Admin+      |

---



## 4. API REST Inventory

### 4.1 Assets

| Endpoint                                      | Méthode | Description                | Params                                                       | Response                                                     | Auth    |
| --------------------------------------------- | ------- | -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------- |
| `/api/v1/inventory/assets/`                   | GET     | Liste assets paginée       | `page`, `page_size`, `search`, `category`, `brand`, `status`, `location` | `{count, next, previous, results[]}`                         | ✅ Token |
| `/api/v1/inventory/assets/`                   | POST    | Créer asset                | `name`, `serial_number`, `category`, `brand`, `status`       | `{id, uuid, name, ...}`                                      | ✅ Token |
| `/api/v1/inventory/assets/<id>/`              | GET     | Détail asset               | -                                                            | `{id, name, serial_number, category, brand, location, assigned_to, status, ...}` | ✅ Token |
| `/api/v1/inventory/assets/<id>/`              | PUT     | Mettre à jour asset        | Tous champs                                                  | `{id, name, ...}`                                            | ✅ Token |
| `/api/v1/inventory/assets/<id>/`              | DELETE  | Supprimer asset            | -                                                            | `204 No Content`                                             | ✅ Admin |
| `/api/v1/inventory/assets/<id>/move/`         | POST    | Déplacer asset             | `location_id`                                                | `{status, new_location}`                                     | ✅ Token |
| `/api/v1/inventory/assets/<id>/assign/`       | POST    | Assigner asset             | `user_id`                                                    | `{status, assigned_to}`                                      | ✅ Token |
| `/api/v1/inventory/assets/<id>/retire/`       | POST    | Archiver asset             | -                                                            | `{status, retired_at}`                                       | ✅ Token |
| `/api/v1/inventory/assets/warranty-expiring/` | GET     | Garanties expirant bientôt | `days` (default 30)                                          | `[{asset, warranty_end}]`                                    | ✅ Token |
| `/api/v1/inventory/assets/by-status/`         | GET     | Répartition par statut     | -                                                            | `[{status, count}]`                                          | ✅ Token |
| `/api/v1/inventory/assets/by-category/`       | GET     | Répartition par catégorie  | -                                                            | `[{category, count}]`                                        | ✅ Token |
| `/api/v1/inventory/assets/export/csv/`        | GET     | Export CSV                 | Filtres                                                      | `text/csv`                                                   | ✅ Token |

### 4.2 Catégories, Marques, Locations, Tags

| Endpoint                           | Méthode        | Description                | Auth    |
| ---------------------------------- | -------------- | -------------------------- | ------- |
| `/api/v1/inventory/category/`      | GET/POST       | Liste/Créer catégories     | ✅ Token |
| `/api/v1/inventory/category/<id>/` | GET/PUT/DELETE | Détail/Maj/Suppr catégorie | ✅ Token |
| `/api/v1/inventory/brand/`         | GET/POST       | Liste/Créer marques        | ✅ Token |
| `/api/v1/inventory/brand/<id>/`    | GET/PUT/DELETE | Détail/Maj/Suppr marque    | ✅ Token |
| `/api/v1/inventory/location/`      | GET/POST       | Liste/Créer localisations  | ✅ Token |
| `/api/v1/inventory/location/<id>/` | GET/PUT/DELETE | Détail/Maj/Suppr location  | ✅ Token |
| `/api/v1/inventory/tag/`           | GET/POST       | Liste/Créer tags           | ✅ Token |
| `/api/v1/inventory/tag/<id>/`      | GET/PUT/DELETE | Détail/Maj/Suppr tag       | ✅ Token |

### 4.3 Mouvements Assets

| Endpoint                                 | Méthode | Description           | Params                                                      | Auth    |
| ---------------------------------------- | ------- | --------------------- | ----------------------------------------------------------- | ------- |
| `/api/v1/inventory/asset-movement/`      | GET     | Historique mouvements | `asset`, `location`, `date_from`, `date_to`                 | ✅ Token |
| `/api/v1/inventory/asset-movement/`      | POST    | Créer mouvement       | `asset_id`, `from_location`, `to_location`, `movement_type` | ✅ Token |
| `/api/v1/inventory/asset-movement/<id>/` | GET     | Détail mouvement      | -                                                           | ✅ Token |
| `/api/v1/inventory/asset-movement/<id>/` | DELETE  | Supprimer mouvement   | -                                                           | ✅ Admin |

---

## 5. API REST Maintenance

### 5.1 Tickets

| Endpoint                                       | Méthode | Description          | Params                                                       | Response                                                     | Auth    |
| ---------------------------------------------- | ------- | -------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------- |
| `/api/v1/maintenance/tickets/`                 | GET     | Liste tickets        | `page`, `status`, `priority`, `assignee`, `asset`            | `{count, results[]}`                                         | ✅ Token |
| `/api/v1/maintenance/tickets/`                 | POST    | Créer ticket         | `subject`, `description`, `asset_id`, `priority`, `category` | `{id, subject, status}`                                      | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/`            | GET     | Détail ticket        | -                                                            | `{id, subject, description, status, priority, asset, assignee, ...}` | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/`            | PATCH   | Mettre à jour ticket | Champs partiels                                              | `{id, ...}`                                                  | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/`            | DELETE  | Supprimer ticket     | -                                                            | `204 No Content`                                             | ✅ Admin |
| `/api/v1/maintenance/tickets/<id>/transition/` | PATCH   | Changer statut       | `to_status`                                                  | `{status, history}`                                          | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/assign/`     | POST    | Assigner ticket      | `assignee_id`                                                | `{assignee, status}`                                         | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/comments/`   | GET     | Liste commentaires   | -                                                            | `[{id, content, author, created_at, is_internal}]`           | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/comments/`   | POST    | Ajouter commentaire  | `content`, `is_internal`                                     | `{id, content, author}`                                      | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/parts/`      | GET     | Pièces consommées    | -                                                            | `[{item, quantity, unit_price, total_price}]`                | ✅ Token |
| `/api/v1/maintenance/tickets/<id>/parts/`      | POST    | Ajouter pièce        | `item_id`, `quantity`                                        | `{item, quantity, total}`                                    | ✅ Token |
| `/api/v1/maintenance/tickets/overdue/`         | GET     | Tickets en retard    | -                                                            | `[{id, subject, due_date}]`                                  | ✅ Token |
| `/api/v1/maintenance/tickets/stats/`           | GET     | Statistiques tickets | -                                                            | `{open, in_progress, resolved_30d, overdue}`                 | ✅ Token |
| `/api/v1/maintenance/tickets/export/csv/`      | GET     | Export CSV           | Filtres                                                      | `text/csv`                                                   | ✅ Token |

### 5.2 Workflows & Statuts

| Statut         | Code            | Couleur  | Transitions Autorisées              |
| -------------- | --------------- | -------- | ----------------------------------- |
| Ouvert         | `open`          | 🔵 Bleu   | → assigned, in_progress, closed     |
| Assigné        | `assigned`      | 🟣 Violet | → in_progress, open, closed         |
| En cours       | `in_progress`   | 🟠 Orange | → waiting_parts, resolved, assigned |
| Attente pièces | `waiting_parts` | 🟡 Ambre  | → in_progress, resolved             |
| Résolu         | `resolved`      | 🟢 Vert   | → closed, in_progress               |
| Fermé          | `closed`        | ⚫ Gris   | → open (réouverture)                |
| Annulé         | `cancelled`     | 🔴 Rouge  | -                                   |

---

## 6. API REST Scanner

### 6.1 Scan & Résolution

| Endpoint                           | Méthode | Description             | Params                                  | Response                                           | Auth     |
| ---------------------------------- | ------- | ----------------------- | --------------------------------------- | -------------------------------------------------- | -------- |
| `/api/v1/scanner/scan/<uuid>/`     | GET     | Résoudre QR/Code-barres | `uuid` = UUID, S/N, ou code interne     | `{id, name, serial_number, status, location, ...}` | ❌ Public |
| `/api/v1/scanner/stats/`           | GET     | Statistiques scans      | `date_from`, `date_to`                  | `{scans_today, scans_week, top_assets}`            | ✅ Token  |
| `/api/v1/scanner/recent-activity/` | GET     | Activité récente        | `limit` (default 10)                    | `[{type, asset, user, timestamp}]`                 | ✅ Token  |
| `/api/v1/scanner/logs/`            | GET     | Historique scans        | `asset`, `user`, `date_from`, `date_to` | `[{id, asset, scanned_by, timestamp, ip}]`         | ✅ Token  |

### 6.2 QR Code Management

| Endpoint                                | Méthode | Description       | Params           | Response                                 | Auth    |
| --------------------------------------- | ------- | ----------------- | ---------------- | ---------------------------------------- | ------- |
| `/api/v1/scanner/assets/<id>/regen-qr/` | POST    | Régénérer QR Code | `asset_id` (URL) | `{uuid, url, image}`                     | ✅ Token |
| `/api/v1/scanner/assets/<id>/qr/`       | GET     | Récupérer QR info | `asset_id` (URL) | `{uuid, code, image_url, scanned_count}` | ✅ Token |
| `/api/v1/scanner/batch-generate/`       | POST    | Générer QR batch  | `asset_ids[]`    | `{success, failed, count}`               | ✅ Token |

### 6.3 Impression Étiquettes

| Endpoint                                    | Méthode        | Description       | Params                                               | Response                               | Auth    |
| ------------------------------------------- | -------------- | ----------------- | ---------------------------------------------------- | -------------------------------------- | ------- |
| `/api/v1/scanner/print-label/`              | GET            | PDF single asset  | `asset_id`, `format`, `copies`                       | `application/pdf`                      | ✅ Token |
| `/api/v1/scanner/print-labels/`             | POST           | PDF batch assets  | `asset_ids[]`, `template_id`, `printer_id`, `copies` | `application/pdf`                      | ✅ Token |
| `/api/v1/scanner/templates/`                | GET/POST       | CRUD templates    | -                                                    | `[{id, name, format, ...}]`            | ✅ Token |
| `/api/v1/scanner/templates/<id>/`           | GET/PUT/DELETE | Détail template   | -                                                    | `{id, name, format, ...}`              | ✅ Token |
| `/api/v1/scanner/printers/`                 | GET/POST       | CRUD imprimantes  | -                                                    | `[{id, name, connection_type, ...}]`   | ✅ Token |
| `/api/v1/scanner/printers/<id>/`            | GET/PUT/DELETE | Détail imprimante | -                                                    | `{id, name, connection_type, ...}`     | ✅ Token |
| `/api/v1/scanner/printers/<id>/test/`       | POST           | Tester imprimante | -                                                    | `application/pdf` (test)               | ✅ Token |
| `/api/v1/scanner/print-jobs/`               | GET/POST       | CRUD jobs         | `status`, `created_by`                               | `[{id, status, asset_count, ...}]`     | ✅ Token |
| `/api/v1/scanner/print-jobs/<id>/`          | GET            | Détail job        | -                                                    | `{id, status, pdf_url, ...}`           | ✅ Token |
| `/api/v1/scanner/print-jobs/<id>/download/` | GET            | Télécharger PDF   | -                                                    | `application/pdf`                      | ✅ Token |
| `/api/v1/scanner/print-jobs/<id>/cancel/`   | POST           | Annuler job       | -                                                    | `{status: cancelled}`                  | ✅ Token |
| `/api/v1/scanner/print-logs/`               | GET            | Logs audit        | `asset`, `user`, `date_from`, `date_to`              | `[{id, asset, printed_by, timestamp}]` | ✅ Token |

---



## 7. API REST Printer ⭐ NOUVEAU

### 7.1 Vue d'Ensemble Module Printer

| Composant         | Description                             | Usage                           |
| ----------------- | --------------------------------------- | ------------------------------- |
| **PrintTemplate** | Modèles d'étiquettes (formats, layouts) | 30x20mm, 50x30mm, 70x40mm, etc. |
| **Printer**       | Configuration imprimantes (USB/BT/WiFi) | MUNBYN, Samsung, Zebra          |
| **PrintJob**      | Jobs d'impression batch (PDF)           | Multi-assets, tracking          |
| **PrintLog**      | Audit des impressions (traçabilité)     | Qui, quand, quoi                |
| **PrintLabel**    | Génération étiquettes unitaires         | Single asset                    |

---

### 7.2 Endpoints API Printer

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

### 7.3 Modèles Printer

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

### 7.4 Formats d'Étiquettes Supportés

| Format   | Dimensions (mm) | Usage Recommandé                     | QR Size |
| -------- | --------------- | ------------------------------------ | ------- |
| `30x20`  | 30 × 20         | Petit matériel (câbles, adaptateurs) | 15mm    |
| `50x30`  | 50 × 30         | **Standard** (laptops, écrans)       | 20mm    |
| `70x40`  | 70 × 40         | Grand matériel (serveurs, baies)     | 25mm    |
| `80x50`  | 80 × 50         | Rack, armoires, équipements          | 30mm    |
| `100x50` | 100 × 50        | Étiquettes industrielles             | 35mm    |

---

### 7.5 Statuts PrintJob

| Statut     | Code         | Couleur | Description                  | Transitions             |
| ---------- | ------------ | ------- | ---------------------------- | ----------------------- |
| En attente | `pending`    | ⚪ Gris  | Job créé, pas encore traité  | → processing, cancelled |
| En cours   | `processing` | 🔵 Bleu  | Génération PDF en cours      | → completed, failed     |
| Terminé    | `completed`  | 🟢 Vert  | PDF généré, prêt à imprimer  | -                       |
| Échoué     | `failed`     | 🔴 Rouge | Erreur génération/impression | → pending (retry)       |
| Annulé     | `cancelled`  | ⚫ Noir  | Job annulé par utilisateur   | -                       |

---

### 7.6 Workflow Impression

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

### 7.7 Exemples de Requêtes

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

### 

---



## 8. API REST Stock

### 8.1 Articles Stock

| Endpoint                                 | Méthode | Description           | Params                                                     | Response                                              | Auth    |
| ---------------------------------------- | ------- | --------------------- | ---------------------------------------------------------- | ----------------------------------------------------- | ------- |
| `/api/v1/stock/items/`                   | GET     | Liste articles        | `page`, `search`, `type`, `category`                       | `{count, results[]}`                                  | ✅ Token |
| `/api/v1/stock/items/`                   | POST    | Créer article         | `reference`, `name`, `item_type`, `quantity`, `unit_price` | `{id, reference, ...}`                                | ✅ Token |
| `/api/v1/stock/items/<id>/`              | GET     | Détail article        | -                                                          | `{id, reference, name, quantity, min_quantity, ...}`  | ✅ Token |
| `/api/v1/stock/items/<id>/`              | PUT     | Mettre à jour article | Champs partiels                                            | `{id, ...}`                                           | ✅ Token |
| `/api/v1/stock/items/<id>/`              | DELETE  | Supprimer article     | -                                                          | `204 No Content`                                      | ✅ Admin |
| `/api/v1/stock/items/low-stock/`         | GET     | Alertes rupture       | -                                                          | `[{id, name, quantity, min_quantity}]`                | ✅ Token |
| `/api/v1/stock/items/stats/`             | GET     | Statistiques stock    | -                                                          | `{total_items, total_value, low_stock, out_of_stock}` | ✅ Token |
| `/api/v1/stock/items/<id>/add-stock/`    | POST    | Entrée stock          | `quantity`, `reason`, `reference_doc`                      | `{status, new_quantity}`                              | ✅ Token |
| `/api/v1/stock/items/<id>/remove-stock/` | POST    | Sortie stock          | `quantity`, `reason`, `ticket_id`                          | `{status, new_quantity}`                              | ✅ Token |
| `/api/v1/stock/items/export/csv/`        | GET     | Export CSV            | Filtres                                                    | `text/csv`                                            | ✅ Token |

### 8.2 Mouvements Stock

| Endpoint                              | Méthode | Description           | Params                                                       | Response                                    | Auth    |
| ------------------------------------- | ------- | --------------------- | ------------------------------------------------------------ | ------------------------------------------- | ------- |
| `/api/v1/stock/movements/`            | GET     | Historique mouvements | `item`, `type`, `ticket`, `date_from`, `date_to`             | `[{id, item, type, quantity, reason, ...}]` | ✅ Token |
| `/api/v1/stock/movements/`            | POST    | Créer mouvement       | `item_id`, `movement_type`, `quantity`, `reason`, `ticket_id` | `{id, item, quantity}`                      | ✅ Token |
| `/api/v1/stock/movements/<id>/`       | GET     | Détail mouvement      | -                                                            | `{id, item, type, quantity, ...}`           | ✅ Token |
| `/api/v1/stock/movements/<id>/`       | DELETE  | Supprimer mouvement   | -                                                            | `204 No Content`                            | ✅ Admin |
| `/api/v1/stock/movements/export/csv/` | GET     | Export CSV            | Filtres                                                      | `text/csv`                                  | ✅ Token |

### 8.3 Types d'Articles

| Type           | Code         | Description          | Exemples                       |
| -------------- | ------------ | -------------------- | ------------------------------ |
| Pièce détachée | `spare_part` | Pièces de rechange   | RAM, SSD, Batteries, Écrans    |
| Consommable    | `consumable` | Consommables atelier | Vis, Pâte thermique, Adhésifs  |
| Accessoire     | `accessory`  | Accessoires          | Câbles, Adaptateurs, Housses   |
| Outil          | `tool`       | Outillage            | Tournevis, Pinces, Multimètres |

---

## 9. API REST Authentication

### 9.1 Token & Utilisateurs

| Endpoint                   | Méthode        | Description          | Params                                  | Response                        | Auth     |
| -------------------------- | -------------- | -------------------- | --------------------------------------- | ------------------------------- | -------- |
| `/api/v1/auth/token/`      | POST           | Obtenir token        | `username`, `password`                  | `{token, user}`                 | ❌ Public |
| `/api/v1/auth/token/`      | DELETE         | Révoquer token       | -                                       | `204 No Content`                | ✅ Token  |
| `/api/v1/auth/user/`       | GET            | Utilisateur courant  | -                                       | `{id, username, email, role}`   | ✅ Token  |
| `/api/v1/auth/user/`       | PUT            | Mettre à jour profil | `email`, `password`                     | `{id, username, ...}`           | ✅ Token  |
| `/api/v1/auth/users/`      | GET            | Liste utilisateurs   | `role`, `is_active`                     | `[{id, username, email, role}]` | ✅ Admin  |
| `/api/v1/auth/users/`      | POST           | Créer utilisateur    | `username`, `email`, `password`, `role` | `{id, username, ...}`           | ✅ Admin  |
| `/api/v1/auth/users/<id>/` | GET/PUT/DELETE | CRUD utilisateur     | -                                       | `{id, username, ...}`           | ✅ Admin  |

### 9.2 Rôles & Permissions

| Rôle         | Code           | Assets | Tickets | Stock | Scanner | Django-Admin |
| ------------ | -------------- | ------ | ------- | ----- | ------- | ------------ |
| Technicien   | `technicien`   | R/W    | R/W     | R     | ✅       | ❌            |
| Gestionnaire | `gestionnaire` | R/W    | R/W     | R/W   | ✅       | ❌            |
| Admin CMDB   | `admin_cmdb`   | R/W    | R/W     | R/W   | ✅       | ❌            |
| Superuser    | `superuser`    | R/W    | R/W     | R/W   | ✅       | ✅            |

---

## 10. Django Admin Système

### 10.1 URLs Système

| URL                              | Description                                  | Accès     |
| -------------------------------- | -------------------------------------------- | --------- |
| `/django-admin/`                 | Admin Django système (users, groups, tokens) | Superuser |
| `/django-admin/auth/user/`       | Gestion utilisateurs Django                  | Superuser |
| `/django-admin/auth/group/`      | Gestion groupes/permissions                  | Superuser |
| `/django-admin/authtoken/token/` | Tokens DRF                                   | Superuser |
| `/django-admin/admin/logentry/`  | Logs admin Django                            | Superuser |

### 10.2 Séparation Admin

```python
# config/urls.py
urlpatterns = [
    path('django-admin/', admin.site.urls),      # Système (superusers)
    path('admin/', cmdb_admin.urls),             # Métier IT (techniciens, gestionnaires)
]
```

| Admin       | URL              | Scope                                  | Utilisateurs                       |
| ----------- | ---------------- | -------------------------------------- | ---------------------------------- |
| **Système** | `/django-admin/` | Auth, Users, Groups, Tokens, Logs      | Superusers uniquement              |
| **Métier**  | `/admin/`        | Inventory, Maintenance, Stock, Scanner | Techniciens, Gestionnaires, Admins |

---

## 11. Fichiers Statiques

### 11.1 CSS

| Fichier              | Chemin                    | Description             |
| -------------------- | ------------------------- | ----------------------- |
| `admin_base.css`     | `/static/admin_cmdb/css/` | Layout, Sidebar, Navbar |
| `assets.css`         | `/static/admin_cmdb/css/` | Module Assets           |
| `tickets.css`        | `/static/admin_cmdb/css/` | Module Tickets (Kanban) |
| `scanner.css`        | `/static/admin_cmdb/css/` | Module Scanner          |
| `stock.css`          | `/static/admin_cmdb/css/` | Module Stock            |
| `search.css`         | `/static/admin_cmdb/css/` | Recherche globale       |
| `scan_print_hub.css` | `/static/admin_cmdb/css/` | Landing Scan & Print    |

### 11.2 JavaScript

| Fichier             | Chemin                   | Description                      |
| ------------------- | ------------------------ | -------------------------------- |
| `api.js`            | `/static/admin_cmdb/js/` | Axios instance + interceptors    |
| `main.js`           | `/static/admin_cmdb/js/` | Layout Vue app (sidebar/navbar)  |
| `assets.js`         | `/static/admin_cmdb/js/` | Vue app Assets                   |
| `tickets.js`        | `/static/admin_cmdb/js/` | Vue app Tickets                  |
| `scanner.js`        | `/static/admin_cmdb/js/` | Vue app Scanner (ZXing + USB)    |
| `stock.js`          | `/static/admin_cmdb/js/` | Vue app Stock                    |
| `search.js`         | `/static/admin_cmdb/js/` | Recherche globale + autocomplete |
| `scan_print_hub.js` | `/static/admin_cmdb/js/` | Landing Scan & Print             |

### 11.3 Templates

| Module      | Templates                                                    |
| ----------- | ------------------------------------------------------------ |
| **Base**    | `admin_base.html`, `admin_login.html`, `dashboard.html`      |
| **Assets**  | `admin/assets/list.html`, `detail.html`, `form.html`         |
| **Tickets** | `admin/tickets/list.html`, `detail.html`, `form.html`        |
| **Scanner** | `admin/scanner/index.html`, `print.html`, `templates.html`, `printers.html`, `jobs.html`, `logs.html` |
| **Stock**   | `admin/stock/list.html`, `detail.html`, `movement.html`      |
| **Search**  | `admin/search/results.html`                                  |
| **Hub**     | `admin/scan_print/landing.html`                              |
| **Public**  | `public/scan_result.html`                                    |

### 11.4 Media

| Type           | Chemin                       | Description            |
| -------------- | ---------------------------- | ---------------------- |
| QR Codes       | `/media/qr_codes/YYYY/MM/`   | Images QR générées     |
| Assets Photos  | `/media/assets/YYYY/MM/`     | Photos assets          |
| Stock Photos   | `/media/stock/YYYY/MM/`      | Photos articles        |
| Print Jobs PDF | `/media/print_jobs/YYYY/MM/` | PDFs impressions batch |

---

## 12. Workflows Complets

### 12.1 Workflow Réception & Étiquetage

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
│  3. _generate_qr_image() → media/qr_codes/                     │
│     └── PNG 300x300px généré                                   │
│         │                                                       │
│         ▼                                                       │
│  4. /admin/assets/ → Sélectionner assets                       │
│     └── Action: "Imprimer Étiquettes"                          │
│         │                                                       │
│         ▼                                                       │
│  5. POST /api/v1/scanner/print-labels/                         │
│     └── PDF batch généré (ReportLab)                           │
│         │                                                       │
│         ▼                                                       │
│  6. PrintJob créé → Celery task                                │
│     └── PDF sauvegardé dans media/print_jobs/                  │
│         │                                                       │
│         ▼                                                       │
│  7. GET /api/v1/scanner/print-jobs/<id>/download/              │
│     └── PDF téléchargé → Impression MUNBYN                     │
│         │                                                       │
│         ▼                                                       │
│  8. PrintLog enregistré (audit)                                │
│     └── Qui, quand, quelle imprimante                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 Workflow Scan & Maintenance

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKFLOW SCAN & MAINTENANCE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. /admin/scanner/ → Scanner USB/Webcam                       │
│     └── QR Code scanné → UUID extrait                          │
│         │                                                       │
│         ▼                                                       │
│  2. GET /api/v1/scanner/scan/<uuid>/                           │
│     └── Asset résolu (QR, S/N, ou code interne)                │
│         │                                                       │
│         ▼                                                       │
│  3. ScanLog enregistré                                         │
│     └── Qui, quand, IP, user_agent                             │
│         │                                                       │
│         ▼                                                       │
│  4. Fiche asset affichée                                       │
│     └── Nom, S/N, statut, localisation, assigné                │
│         │                                                       │
│         ▼                                                       │
│  5. Bouton "Créer Ticket"                                      │
│     └── POST /api/v1/maintenance/tickets/                      │
│         │                                                       │
│         ▼                                                       │
│  6. Technicien intervient                                      │
│     └── PATCH /api/v1/maintenance/tickets/<id>/transition/     │
│         │                                                       │
│         ▼                                                       │
│  7. Pièces consommées                                          │
│     └── POST /api/v1/maintenance/tickets/<id>/parts/           │
│         │                                                       │
│         ▼                                                       │
│  8. Stock décrémenté (signal)                                  │
│     └── POST /api/v1/stock/items/<id>/remove-stock/            │
│         │                                                       │
│         ▼                                                       │
│  9. Ticket résolu → Fermé                                      │
│     └── Historique complet                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.3 Workflow Entrée/Sortie Stock

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKFLOW ENTRÉE/SORTIE STOCK                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ENTRÉE STOCK                                                   │
│  ─────────────                                                  │
│  1. POST /api/v1/stock/items/<id>/add-stock/                   │
│     └── quantity: +50, reason: "Commande fournisseur"          │
│         │                                                       │
│         ▼                                                       │
│  2. StockMovement créé (type: 'in')                            │
│     └── quantity: +50, quantity_before: 20, quantity_after: 70 │
│         │                                                       │
│         ▼                                                       │
│  3. StockItem.quantity mis à jour (signal)                     │
│     └── 20 → 70                                                │
│                                                                 │
│  SORTIE STOCK                                                   │
│  ─────────────                                                  │
│  1. POST /api/v1/stock/items/<id>/remove-stock/                │
│     └── quantity: -5, reason: "Réparation", ticket_id: 45      │
│         │                                                       │
│         ▼                                                       │
│  2. StockMovement créé (type: 'out')                           │
│     └── quantity: -5, ticket: #45                              │
│         │                                                       │
│         ▼                                                       │
│  3. StockItem.quantity mis à jour (signal)                     │
│     └── 70 → 65                                                │
│         │                                                       │
│         ▼                                                       │
│  4. PrintLog enregistré (si étiquette imprimée)                │
│     └── Audit complet                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Finale

| Module           | URLs   | API Endpoints | Templates | Static Files | Statut |
| ---------------- | ------ | ------------- | --------- | ------------ | ------ |
| **Dashboard**    | 1      | 0             | 1         | 2            | ✅      |
| **Admin Layout** | 1      | 0             | 1         | 2            | ✅      |
| **Assets**       | 7      | 12            | 3         | 2            | ✅      |
| **Tickets**      | 4      | 14            | 3         | 2            | ✅      |
| **Scanner**      | 7      | 15            | 6         | 2            | ✅      |
| **Stock**        | 4      | 13            | 3         | 2            | ✅      |
| **Search**       | 1      | 3             | 1         | 2            | ✅      |
| **Auth**         | 5      | 7             | 1         | 0            | ✅      |
| **Public**       | 2      | 1             | 1         | 0            | ✅      |
| **TOTAL**        | **32** | **65**        | **20**    | **14**       | ✅      |

---

**Documentation complète des URLs CMDB Inventory v2.0 — Mars 2026** 🎉