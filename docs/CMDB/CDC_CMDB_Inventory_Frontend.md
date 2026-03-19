# Cahier des Charges — CMDB Inventory Frontend
**Société de Reconditionnement IT**
Version 1.0 — Mars 2026

---

## 1. Contexte & Objectifs

### 1.1 Contexte

Société de reconditionnement IT gérant un parc matériel (laptops, serveurs, switches, imprimantes, NAS, onduleurs…) avec des flux de réception, diagnostic, réparation, réaffectation et expédition.

Le backend Django 5 / DRF est opérationnel avec les apps suivantes :

| App | Responsabilité |
|---|---|
| `inventory` | Assets, catégories, marques, localisations, tags, mouvements |
| `maintenance` | Tickets, historique statuts, pièces, commentaires |
| `scanner` | QR codes, scan logs |
| `stock` | Articles atelier, mouvements de stock |

### 1.2 Objectifs

| Zone | URL | Audience |
|---|---|---|
| Dashboard vitrine | `/` | Public / lecture seule |
| Interface métier | `/admin/` | Techniciens, gestionnaires IT |
| Admin système | `/django-admin/` | Superusers uniquement |
| Page scan publique | `/scan/<uuid>/` | Techniciens terrain sans compte |

### 1.3 Contraintes Techniques

- **Stack** : HTML5 + Bootstrap 5.3 + Vue 3 (CDN) + Axios + jQuery
- **Consomme** exclusivement les API DRF existantes sur `/api/v1/`
- **Responsive** : desktop prioritaire, mobile optimisé pour scan QR
- **Auth** : DRF `TokenAuthentication` → `localStorage['cmdb_token']`
- **Délimiteurs Vue** : `[[ ]]` pour cohabitation Django templates
- **Pas de build tool** (Webpack/Vite) — fichiers statiques servis par Django

---

## 2. Architecture des URLs

```
/                           → Dashboard vitrine (Vue.js, lecture seule)
/admin/                     → Interface métier CMDB (intervenants IT)
/admin/login/               → Authentification Token
/admin/assets/              → Gestion du parc
/admin/tickets/             → Maintenance (Kanban)
/admin/scanner/             → Scan QR Code / Code-barres
/admin/stock/               → Stock atelier
/admin/search/              → Recherche globale
/django-admin/              → Django Admin système (superusers)
/scan/<uuid>/               → Résolution QR publique (sans auth)
/api/v1/inventory/          → API REST
/api/v1/maintenance/        → API REST
/api/v1/scanner/            → API REST
/api/v1/stock/              → API REST
/media/qr_codes/            → Images QR générées
```

### Séparation Django Admin

```python
# core/admin.py
from django.contrib.admin import AdminSite

class CMDBAdminSite(AdminSite):
    site_header = "CMDB Inventory — Administration"
    site_title  = "CMDB Admin"
    index_title = "Panneau de gestion IT"

cmdb_admin = CMDBAdminSite(name='cmdb_admin')
# Enregistre : inventory, maintenance, stock, scanner

# config/urls.py
path('django-admin/', admin.site.urls),  # users, groups, tokens, auth
path('admin/',        cmdb_admin.urls),  # métier IT uniquement
```

---

## 3. Modules Frontend — `/admin/`

### Module 1 — Assets (Gestion du Parc)

**Pages**

| URL | Description |
|---|---|
| `/admin/assets/` | Liste paginée + filtres |
| `/admin/assets/new/` | Formulaire création |
| `/admin/assets/<id>/` | Fiche détail (4 onglets) |
| `/admin/assets/<id>/edit/` | Édition |

**Fonctionnalités**

- Tableau : photo miniature, nom, S/N, catégorie, marque, localisation, statut (badge couleur), assigné à
- Filtres sidebar réactifs : catégorie, marque, statut, état, localisation
- Recherche fulltext : nom, S/N, modèle, assigné
- Tri colonnes + pagination 25 par page
- Actions bulk : archiver, changer localisation, assigner
- Fiche détail — 4 onglets :
  - **Infos** : tous les champs + photo
  - **Mouvements** : historique déplacements
  - **Tickets** : tickets maintenance liés
  - **QR Code** : image + download + impression étiquette
- Bouton "Générer QR" → `POST /api/v1/scanner/assets/<id>/regen-qr/`

**APIs consommées**

```
GET    /api/v1/inventory/assets/
POST   /api/v1/inventory/assets/
GET    /api/v1/inventory/assets/<id>/
PUT    /api/v1/inventory/assets/<id>/
POST   /api/v1/inventory/assets/<id>/move/
POST   /api/v1/inventory/assets/<id>/assign/
POST   /api/v1/inventory/assets/<id>/retire/
POST   /api/v1/scanner/assets/<id>/regen-qr/
```

---

### Module 2 — Scanner QR Code / Code-Barres

**Pages**

| URL | Description |
|---|---|
| `/admin/scanner/` | Interface scan (desktop + mobile) |
| `/scan/<uuid>/` | Résolution QR publique (sans auth) |

**Workflow complet**

```
Scan mobile (ZXing-js)
    │
    ├── Décode QR → UUID extrait
    │
    ▼
GET /api/v1/scanner/scan/<uuid>/
    │
    ├── ScanLog enregistré automatiquement
    │
    ▼
Fiche asset affichée
    ├── Bouton → Créer ticket maintenance (modal rapide)
    ├── Bouton → Déplacer asset (select location)
    └── Bouton → Voir historique mouvements

Page publique /scan/<uuid>/  (sans auth)
    → nom, S/N, photo, statut, localisation
    → assigné, garantie, tickets ouverts
    → QR image downloadable (impression étiquette)
```

**Flux génération QR**

```
POST /api/v1/inventory/assets/   →  Asset créé
         ↓ signal post_save
     QRCode créé → _generate_qr_image()
         ↓
     media/qr_codes/qr_asset_<id>_<uuid>.png
```

**APIs consommées**

```
GET  /api/v1/scanner/scan/<uuid>/
POST /api/v1/scanner/assets/<id>/regen-qr/
GET  /api/v1/inventory/assets/?search=<sn>
```

---

### Module 3 — Maintenance Tickets

**Pages**

| URL | Description |
|---|---|
| `/admin/tickets/` | Liste Kanban + vue tableau |
| `/admin/tickets/new/` | Création ticket |
| `/admin/tickets/<id>/` | Détail + workflow |

**Vue Kanban — colonnes**

```
[Ouvert] → [Assigné] → [En cours] → [Attente pièces] → [Résolu] → [Fermé]
```

**Fonctionnalités**

- Kanban drag-and-drop → `PATCH /api/v1/maintenance/tickets/<id>/transition/`
- Badge priorité coloré : 🔴 Critique / 🟠 Élevé / 🔵 Moyen / ⚪ Bas
- Indicateur "En retard" (due_date dépassée)
- Détail ticket :
  - Boutons workflow selon `ALLOWED_TRANSITIONS`
  - Assignation technicien
  - Commentaires internes / publics
  - Pièces consommées (lien stock)
  - Historique complet des transitions
  - Coût total (main d'œuvre + pièces)

**APIs consommées**

```
GET    /api/v1/maintenance/tickets/
POST   /api/v1/maintenance/tickets/
GET    /api/v1/maintenance/tickets/<id>/
PATCH  /api/v1/maintenance/tickets/<id>/
POST   /api/v1/maintenance/tickets/<id>/transition/
POST   /api/v1/maintenance/tickets/<id>/assign/
GET/POST /api/v1/maintenance/tickets/<id>/comments/
GET/POST /api/v1/maintenance/tickets/<id>/parts/
GET    /api/v1/maintenance/tickets/overdue/
GET    /api/v1/maintenance/tickets/stats/
```

---

### Module 4 — Stock Atelier

**Pages**

| URL | Description |
|---|---|
| `/admin/stock/` | Liste articles + alertes rupture |
| `/admin/stock/<id>/` | Fiche article + mouvements |
| `/admin/stock/movement/` | Saisie entrée/sortie rapide |

**Fonctionnalités**

- Tableau : référence, nom, type, stock actuel, seuil min, valeur totale
- Badge stock : 🔴 Rupture / 🟠 Critique / 🟢 OK
- Alertes en haut de page si rupture ou critique
- Entrée rapide : `POST /api/v1/stock/items/<id>/add-stock/`
- Sortie liée optionnellement à un ticket maintenance
- Timeline mouvements par article
- KPIs : total articles, ruptures, valeur totale

**APIs consommées**

```
GET    /api/v1/stock/items/
GET    /api/v1/stock/items/low-stock/
GET    /api/v1/stock/items/stats/
POST   /api/v1/stock/items/<id>/add-stock/
POST   /api/v1/stock/items/<id>/remove-stock/
GET    /api/v1/stock/movements/
```

---

### Module 5 — Moteur de Recherche Global

**URL** : `/admin/search/?q=<query>`

**Fonctionnalités**

- Barre persistante dans la navbar (shortcut **Ctrl+K** / **Cmd+K**)
- Debounce 300ms → 3 requêtes Axios parallèles
- Résultats groupés par type : Assets / Tickets / Stock
- Mise en surbrillance des termes trouvés
- Autocomplete dropdown pendant la frappe
- Raccourci "Rechercher par S/N" → redirect scanner

**APIs consommées**

```
GET /api/v1/inventory/assets/?search=<q>
GET /api/v1/maintenance/tickets/?search=<q>
GET /api/v1/stock/items/?search=<q>
```

---

## 4. Authentification & Rôles

```
/admin/login/  →  POST /api/v1/auth/token/
               →  Token stocké dans localStorage['cmdb_token']
               →  Axios interceptor global : Authorization: Token <token>
               →  401 → redirect automatique /admin/login/
```

| Rôle | Assets | Tickets | Stock | Scanner | Django-Admin |
|---|---|---|---|---|---|
| `technicien` | R/W | R/W | R | ✓ | ✗ |
| `gestionnaire` | R/W | R/W | R/W | ✓ | ✗ |
| `admin_cmdb` | R/W | R/W | R/W | ✓ | ✗ |
| `superuser` | R/W | R/W | R/W | ✓ | ✓ |

---

## 5. Structure Fichiers Statiques

```
backend/
├── templates/
│   ├── dashboard.html              → vitrine /
│   ├── admin_base.html             → layout /admin/ (sidebar + navbar)
│   ├── admin_login.html            → /admin/login/
│   ├── admin/
│   │   ├── assets/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── form.html
│   │   ├── tickets/
│   │   │   ├── list.html           → kanban + tableau
│   │   │   └── detail.html
│   │   ├── scanner/
│   │   │   └── index.html          → caméra + résultat
│   │   ├── stock/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   └── search/
│   │       └── results.html
│   └── public/
│       └── scan_result.html        → /scan/<uuid>/ sans auth
│
└── static/
    ├── dashboard/                  → vitrine (existant)
    │   ├── css/style.css
    │   └── js/main.js
    └── admin_cmdb/
        ├── css/
        │   ├── admin_base.css      → sidebar 260px + navbar
        │   ├── assets.css
        │   ├── tickets.css         → kanban colonnes
        │   ├── scanner.css         → caméra + résultat scan
        │   └── stock.css
        └── js/
            ├── api.js              → Axios instance + interceptors
            ├── assets.js           → Vue app parc
            ├── tickets.js          → Vue app kanban
            ├── scanner.js          → ZXing-js + Vue scan
            ├── stock.js            → Vue app stock
            └── search.js           → Recherche globale + autocomplete
```

---

## 6. Charte Graphique `/admin/`

Cohérence avec le dashboard existant :

| Élément | Valeur |
|---|---|
| Fond | `#0f172a` (dark navy) |
| Cards | `rgba(15,23,42,0.75)` + `backdrop-filter: blur(16px)` |
| Accent | `#2563eb` |
| Police | Inter (Google Fonts) |
| Border radius | 14–16px |
| Sidebar | 260px fixe, collapsible mobile |
| Navbar | Sticky, 60px hauteur |

**Badges statuts tickets**

| Statut | Couleur |
|---|---|
| `open` | 🔵 Bleu |
| `assigned` | 🟣 Violet |
| `in_progress` | 🟠 Orange |
| `waiting_parts` | 🟡 Ambre |
| `resolved` | 🟢 Vert |
| `closed` | ⚫ Gris |
| `cancelled` | 🔴 Rouge |

---

## 7. Ordre de Développement Recommandé

```
Étape 1  →  Layout admin_base.html + api.js (Axios + auth)
Étape 2  →  Module Assets (liste + détail + QR)
Étape 3  →  Scanner QR (caméra + page publique /scan/)
Étape 4  →  Tickets Maintenance (Kanban + workflow)
Étape 5  →  Stock Atelier (entrées/sorties)
Étape 6  →  Moteur de recherche global
```

---

*CMDB Inventory — Cahier des charges frontend v1.0 — Mars 2026*

---

# Prompt developpment 

Tu es un développeur fullstack senior Django/Vue.js.

Contexte :
- Backend Django 5 + DRF opérationnel avec apps :
  inventory, maintenance, scanner, stock
- API REST disponibles sur /api/v1/
- Stack frontend : HTML5, Bootstrap 5.3, Vue 3 (CDN),
  Axios, jQuery, delimiters ['[[',']]']
- Auth : DRF TokenAuthentication → localStorage['cmdb_token']

Objectif : Implémenter le frontend /admin/ (interface métier IT)
avec les modules suivants dans l'ordre :

ÉTAPE 1 — Layout de base
  Fichier : templates/admin_base.html

  - Sidebar 260px collapsible avec navigation modules
  - Navbar sticky : logo, recherche globale (Ctrl+K),
    notifications, user menu (logout)
  - Axios interceptor global (api.js) :
    ajouter Authorization header + gérer 401 → redirect /admin/login/

ÉTAPE 2 — Module Assets (/admin/assets/)
  - Tableau Bootstrap paginé avec filtres sidebar Vue réactifs
  - Appel GET /api/v1/inventory/assets/ avec params filtres
  - Fiche détail : 4 onglets (Infos / Mouvements / Tickets / QR Code)
  - Onglet QR Code : afficher image PNG + bouton download + imprimer

ÉTAPE 3 — Scanner QR (/admin/scanner/)
  - Intégrer ZXing-js (CDN) pour accès caméra
  - Décode QR → appelle GET /api/v1/scanner/scan/<uuid>/
  - Affiche résultat : fiche asset + actions (ticket / déplacer)
  - Page publique /scan/<uuid>/ sans auth (TemplateView)

ÉTAPE 4 — Tickets Maintenance (/admin/tickets/)
  - Vue Kanban : colonnes drag-and-drop par statut
    [Ouvert / Assigné / En cours / Attente pièces / Résolu / Fermé]
  - PATCH /api/v1/maintenance/tickets/<id>/transition/
    au drag d'une colonne à une autre
  - Détail ticket : commentaires + pièces + historique statuts

ÉTAPE 5 — Stock Atelier (/admin/stock/)
  - Tableau articles avec badges stock 🔴/🟠/🟢
  - Modal entrée rapide : POST /api/v1/stock/items/<id>/add-stock/
  - Modal sortie : sélection ticket optionnel

ÉTAPE 6 — Moteur de recherche global
  - Barre search dans navbar (search.js)
  - Debounce 300ms → 3 requêtes parallèles Axios
    assets + tickets + stock
  - Dropdown résultats groupés par type

Contraintes importantes :
  1. Chaque module = fichier JS Vue séparé (assets.js, tickets.js…)
  2. api.js centralisé pour tous les appels Axios
  3. delimiters: ['[[',']]'] dans chaque createApp()
  4. Tous les {{ }} Django dans les templates utilisent
     le contexte Python, pas Vue (pas de conflit)
  5. Responsive : sidebar collapse sur < 768px
  6. Mode démo si API retourne 401/403

Produire fichier par fichier dans l'ordre des étapes.

----

# Prompt Qwen3.5 plus :



Société de reconditionnement IT gérant un parc matériel (laptops, serveurs, switches, imprimantes, NAS, onduleurs…) avec des flux de réception, diagnostic, réparation, réaffectation et expédition.

Le backend Django 5 / DRF est opérationnel avec les apps suivantes :

| App           | Responsabilité                                               |
| ------------- | ------------------------------------------------------------ |
| `inventory`   | Assets, catégories, marques, localisations, tags, mouvements |
| `maintenance` | Tickets, historique statuts, pièces, commentaires            |
| `scanner`     | QR codes, scan logs                                          |
| `stock`       | Articles atelier, mouvements de stock                        |
# Analyse des endpoints backend dispos et ceux consommé par frontend 

> created 13 mars 2026 



J'ai répertorié les endpoints disponibles dans le backend et ceux consommés côté frontend par Vue.js. Voici la synthèse des endpoints :

### Endpoints Disponibles (Backend)

| Endpoint                                             | Méthode          | Description                                          |
| ---------------------------------------------------- | ---------------- | ---------------------------------------------------- |
| `/api/v1/inventory/category/`                        | GET, POST        | Liste et création des catégories                     |
| `/api/v1/inventory/category/{id}/`                   | GET, PUT, DELETE | Détails, mise à jour et suppression d'une catégorie  |
| `/api/v1/inventory/brand/`                           | GET, POST        | Liste et création des marques                        |
| `/api/v1/inventory/brand/{id}/`                      | GET, PUT, DELETE | Détails, mise à jour et suppression d'une marque     |
| `/api/v1/inventory/location/`                        | GET, POST        | Liste et création des emplacements                   |
| `/api/v1/inventory/location/{id}/`                   | GET, PUT, DELETE | Détails, mise à jour et suppression d'un emplacement |
| `/api/v1/inventory/tag/`                             | GET, POST        | Liste et création des tags                           |
| `/api/v1/inventory/tag/{id}/`                        | GET, PUT, DELETE | Détails, mise à jour et suppression d'un tag         |
| `/api/v1/inventory/asset/`                           | GET, POST        | Liste et création des actifs                         |
| `/api/v1/inventory/asset/{id}/`                      | GET, PUT, DELETE | Détails, mise à jour et suppression d'un actif       |
| `/api/v1/inventory/asset/{id}/move/`                 | POST             | Déplacer un actif                                    |
| `/api/v1/inventory/asset/{id}/assign/`               | POST             | Assigner un actif                                    |
| `/api/v1/inventory/asset/{id}/retire/`               | POST             | Archiver un actif                                    |
| `/api/v1/inventory/asset/warranty-expiring/`         | GET              | Actifs dont la garantie expire bientôt               |
| `/api/v1/inventory/asset/by-status/`                 | GET              | Répartition des actifs par statut                    |
| `/api/v1/inventory/asset/by-category/`               | GET              | Répartition des actifs par catégorie                 |
| `/api/v1/inventory/asset-movement/`                  | GET, POST        | Liste et création des mouvements d'actifs            |
| `/api/v1/inventory/asset-movement/{id}/`             | GET, DELETE      | Détails et suppression d'un mouvement d'actif        |
| `/api/v1/inventory/dashboard/stats/`                 | GET              | Statistiques pour le tableau de bord                 |
| Tu es un développeur fullstack senior Django/Vue.js. |                  |                                                      |

Contexte :

- Backend Django 5 + DRF opérationnel avec apps :
  inventory, maintenance, scanner, stock
- API REST disponibles sur /api/v1/
- Stack frontend : HTML5, Bootstrap 5.3, Vue 3 (CDN),
  Axios, jQuery, delimiters ['[[',']]']
- Auth : DRF TokenAuthentication → localStorage['cmdb_token']

Objectif : Implémenter le frontend /admin/ (interface métier IT)
avec les modules suivants dans l'ordre :

ÉTAPE 1 — Layout de base
  Fichier : templates/admin_base.html

  - Sidebar 260px collapsible avec navigation modules
  - Navbar sticky : logo, recherche globale (Ctrl+K),
    notifications, user menu (logout)
  - Axios interceptor global (api.js) :
    ajouter Authorization header + gérer 401 → redirect /admin/login/

ÉTAPE 2 — Module Assets (/admin/assets/)

  - Tableau Bootstrap paginé avec filtres sidebar Vue réactifs
  - Appel GET /api/v1/inventory/assets/ avec params filtres
  - Fiche détail : 4 onglets (Infos / Mouvements / Tickets / QR Code)
  - Onglet QR Code : afficher image PNG + bouton download + imprimer

ÉTAPE 3 — Scanner QR (/admin/scanner/)

  - Intégrer ZXing-js (CDN) pour accès caméra
  - Décode QR → appelle GET /api/v1/scanner/scan/<uuid>/
  - Affiche résultat : fiche asset + actions (ticket / déplacer)
  - Page publique /scan/<uuid>/ sans auth (TemplateView)

ÉTAPE 4 — Tickets Maintenance (/admin/tickets/)

  - Vue Kanban : colonnes drag-and-drop par statut
    [Ouvert / Assigné / En cours / Attente pièces / Résolu / Fermé]
  - PATCH /api/v1/maintenance/tickets/<id>/transition/
    au drag d'une colonne à une autre
  - Détail ticket : commentaires + pièces + historique statuts

ÉTAPE 5 — Stock Atelier (/admin/stock/)

  - Tableau articles avec badges stock 🔴/🟠/🟢
  - Modal entrée rapide : POST /api/v1/stock/items/<id>/add-stock/
  - Modal sortie : sélection ticket optionnel

ÉTAPE 6 — Moteur de recherche global

  - Barre search dans navbar (search.js)
  - Debounce 300ms → 3 requêtes parallèles Axios
    assets + tickets + stock
  - Dropdown résultats groupés par type

Contraintes importantes :

    1. Chaque module = fichier JS Vue séparé (assets.js, tickets.js…)
    2. api.js centralisé pour tous les appels Axios
    3. delimiters: ['[[',']]'] dans chaque createApp()
    4. Tous les {{ }} Django dans les templates utilisent
       le contexte Python, pas Vue (pas de conflit)
    5. Responsive : sidebar collapse sur < 768px
    6. Mode démo si API retourne 401/403

Produire fichier par fichier dans l'ordre des étapes.
