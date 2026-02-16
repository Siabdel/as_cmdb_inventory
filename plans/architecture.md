# Architecture CMDB - Application d'Inventaire Matériel

## Vue d'ensemble du projet

Application complète d'inventaire matériel informatique personnel avec QR codes, développée avec Django/Vue.js.

### Stack technique
- **Backend** : Django 5.x + Django REST Framework + Celery + PostgreSQL + qrcode[pil]
- **Frontend** : Vue.js 3 + Vue Router + Pinia + Bootstrap 5 + html5-qrcode
- **Architecture** : API REST + SPA frontend

## Modèles de données

### Entités principales
1. **Location** - Emplacements physiques (placards, salles, etc.)
2. **Category** - Catégories d'équipements (PC, écran, clavier, etc.)
3. **Brand** - Marques d'équipements
4. **Tag** - Étiquettes pour classification
5. **Asset** - Équipements/matériel principal
6. **AssetMovement** - Historique des déplacements

### Relations clés
- Asset → Category (Many-to-One)
- Asset → Location (Many-to-One)
- Asset → Tags (Many-to-Many)
- AssetMovement → Asset (Many-to-One)
- Location → Location (Self-referencing pour hiérarchie)

## API REST Endpoints

### CRUD Standard
- `/api/assets/` - Gestion complète des équipements
- `/api/locations/` - Gestion des emplacements
- `/api/categories/` - Gestion des catégories
- `/api/brands/` - Gestion des marques
- `/api/tags/` - Gestion des étiquettes

### Endpoints spécialisés
- `/api/assets/{id}/qr_image/` - Génération QR code
- `/api/assets/move-from-scan/` - Déplacement via scan
- `/api/dashboard/summary/` - Statistiques dashboard
- `/api/assets/{id}/movements/` - Historique mouvements

## Frontend Vue.js

### Pages principales
1. **Dashboard** - Vue d'ensemble avec statistiques
2. **Liste Assets** - Table filtrable des équipements
3. **Détail Asset** - Fiche complète + QR code
4. **Scan QR** - Interface mobile pour scan caméra
5. **Forms CRUD** - Création/édition des entités

### Composants clés
- **Scan.vue** - Composant de scan QR avec caméra
- **AssetCard.vue** - Carte d'affichage équipement
- **DataTable.vue** - Table avec filtres et pagination
- **Dashboard widgets** - Graphiques et statistiques

## Fonctionnalités avancées

### QR Code System
- Génération automatique QR pour chaque asset
- Scan mobile → actions instantanées
- URL format : `https://app.com/assets/{uuid}/`

### Recherche et filtres
- Recherche full-text multi-champs
- Filtres par catégorie, localisation, statut, tags
- Pagination et tri

### Historique et traçabilité
- Suivi complet des mouvements
- Historique des modifications
- Audit trail

## Architecture technique

### Backend Django
```
backend/
├── manage.py
├── requirements.txt
├── inventory_project/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
└── inventory/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    └── tests.py
```

### Frontend Vue.js
```
frontend/
├── package.json
├── vite.config.js
├── src/
│   ├── components/
│   ├── views/
│   ├── router/
│   ├── store/
│   ├── api/
│   └── App.vue
└── public/
```

## Sécurité et authentification
- TokenAuthentication Django simple
- HTTPS ready pour scan caméra
- Permissions basiques par utilisateur

## Déploiement
- Configuration Docker/docker-compose
- Variables d'environnement
- Setup PostgreSQL
- Configuration NGINX pour production