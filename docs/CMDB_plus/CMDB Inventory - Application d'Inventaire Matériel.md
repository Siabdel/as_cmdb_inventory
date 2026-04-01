# CMDB Inventory - Application d'Inventaire Matériel

Une application complète de gestion d'inventaire matériel informatique avec QR codes, développée avec Django et Vue.js.

## 🚀 Fonctionnalités

### ✅ Backend Django 5.x

- **API REST complète** avec Django REST Framework
- **Modèles complets** : Location, Category, Brand, Tag, Asset, AssetMovement
- **Génération automatique de QR codes** avec qrcode[pil]
- **Authentification Token** sécurisée
- **Endpoints spécialisés** pour scan, dashboard, mouvements
- **Filtres avancés** et recherche full-text
- **Celery** pour tâches asynchrones
- **PostgreSQL** comme base de données

### ✅ Frontend Vue.js 3

- **Interface moderne** avec Bootstrap 5
- **Scan QR mobile-first** avec html5-qrcode
- **Dashboard interactif** avec graphiques Chart.js
- **Gestion d'état** avec Pinia
- **Routage** avec Vue Router
- **Composants réutilisables** et modulaires
- **Interface responsive** optimisée mobile

### ✅ Fonctionnalités Avancées

- **Scan QR instantané** → actions en 2 clics maximum
- **Historique complet** des mouvements
- **Tableaux de bord** avec statistiques en temps réel
- **Recherche globale** multi-champs
- **Exports** CSV/Excel
- **Notifications** pour maintenance et garanties
- **Interface d'administration** Django complète

## 🏗️ Architecture

```
inventory_app/
├── backend/              # Django + DRF + Celery
│   ├── inventory_project/    # Configuration Django
│   ├── inventory/           # Application principale
│   ├── media/              # Fichiers uploadés (QR codes)
│   ├── static/             # Fichiers statiques
│   └── requirements.txt    # Dépendances Python
├── frontend/             # Vue.js 3 + Vite
│   ├── src/
│   │   ├── components/     # Composants Vue
│   │   ├── views/         # Pages principales
│   │   ├── router/        # Configuration routage
│   │   ├── store/         # Gestion d'état Pinia
│   │   └── api/           # Services API
│   └── package.json       # Dépendances Node.js
├── plans/                # Documentation d'architecture
├── docker-compose.yml    # Configuration Docker
└── README.md
```

## 🛠️ Stack Technologique

- **Backend** : Django 5.x, DRF, PostgreSQL, Celery, Redis
- **Frontend** : Vue.js 3, Vite, Pinia, Bootstrap 5, Chart.js
- **QR** : qrcode[pil] (backend) + html5-qrcode (frontend)
- **Déploiement** : Docker, NGINX, SSL/HTTPS ready

## 🚀 Installation Rapide

### Prérequis

- Docker et Docker Compose
- Git

### Installation en 5 minutes

```bash
# 1. Cloner le projet
git clone <repository-url>
cd inventory_app

# 2. Copier les fichiers d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Démarrer tous les services
docker-compose up -d

# 4. Attendre que les services démarrent (2-3 minutes)
docker-compose logs -f backend

# 5. L'application est prête !
```

### Accès aux services

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000/api
- **Admin Django** : http://localhost:8000/admin
- **Credentials admin** : `admin` / `admin123`

## 📱 Utilisation

### Workflow Principal

1. **Créer un équipement** → QR code généré automatiquement
2. **Imprimer le QR code** → Coller sur l'équipement
3. **Scanner avec mobile** → Actions instantanées disponibles
4. **Gérer les mouvements** → Historique complet automatique

### Scan QR Mobile

1. Ouvrir l'app sur mobile
2. Aller sur "Scan QR"
3. Scanner le code
4. Choisir l'action :
   - Voir la fiche
   - Déplacer vers...
   - Marquer en panne

## 🔧 Développement

### Backend Django

```bash
# Entrer dans le container backend
docker-compose exec backend bash

# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer les tests
python manage.py test
```

### Frontend Vue.js

```bash
# Entrer dans le container frontend
docker-compose exec frontend sh

# Installer les dépendances
npm install

# Lancer en mode développement
npm run dev

# Build pour production
npm run build
```

## 📊 API Endpoints

### Assets

- `GET /api/assets/` - Liste des équipements
- `POST /api/assets/` - Créer un équipement
- `GET /api/assets/{id}/` - Détail d'un équipement
- `PUT /api/assets/{id}/` - Modifier un équipement
- `DELETE /api/assets/{id}/` - Supprimer un équipement
- `GET /api/assets/{id}/qr_image/` - Image QR code
- `POST /api/assets/move-from-scan/` - Déplacer via scan
- `GET /api/assets/{id}/movements/` - Historique mouvements

### Dashboard

- `GET /api/dashboard/summary/` - Résumé statistiques
- `GET /api/dashboard/stats/` - Statistiques détaillées

Voici le fichier complet . Il ne reste qu'à le brancher dans Django.

------

## Ce que fait le dashboard

| Fonctionnalité            | Détail                                       |
| ------------------------- | -------------------------------------------- |
| **KPIs live**             | Total assets, actifs, garanties, valeur parc |
| **Barres de progression** | Statuts + états équipements animées          |
| **Mouvements récents**    | 8 derniers avec from→to + timestamp relatif  |
| **Grille catégories**     | Icônes + compteurs par catégorie             |
| **Alertes garanties**     | Bloc rouge si assets expirant < 30j          |
| **Mode démo**             | Données fictives si API non joignable        |
| **Auto-refresh**          | Actualisation automatique toutes les 60s     |
| **Bouton rafraîchir**     | Avec animation spinner                       |

> 🔑 Pour l'authentification Token, le dashboard lit `localStorage.getItem('cmdb_token')`. Tu peux ajouter un mini-formulaire de login ou injecter le token via Django template : `<script>localStorage.setItem('cmdb_token', '{{ request.auth.key }}')</script>`.

### Autres

- `GET /api/locations/` - Emplacements
- `GET /api/categories/` - Catégories
- `GET /api/brands/` - Marques
- `GET /api/tags/` - Étiquettes
- `GET /api/movements/` - Mouvements

## 🔒 Sécurité

- **Authentification Token** Django
- **HTTPS** obligatoire pour scan caméra
- **Permissions** granulaires
- **Variables d'environnement** sécurisées
- **Headers de sécurité** configurés

## 📈 Performance

- **Pagination** automatique
- **Cache Redis** pour Celery
- **Optimisation** des requêtes Django
- **Lazy loading** des composants Vue
- **Compression** des assets

## 🧪 Tests

```bash
# Tests backend
docker-compose exec backend python manage.py test

# Tests frontend (à implémenter)
docker-compose exec frontend npm run test
```

## 📦 Production

### Variables d'environnement importantes

```env
# Backend
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
ALLOWED_HOSTS=your-domain.com

# Frontend
VITE_API_BASE_URL=https://your-domain.com/api
```

### Déploiement

1. Configurer les variables d'environnement
2. Utiliser `docker-compose.prod.yml`
3. Configurer NGINX/reverse proxy
4. Activer SSL/HTTPS
5. Configurer les sauvegardes

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation** : Voir le dossier `/plans/`
- **Issues** : Utiliser GitHub Issues
- **Email** : support@example.com

## 🎯 Roadmap

- [ ] Application mobile native (React Native/Flutter)
- [ ] Intégrations ERP/LDAP
- [ ] IoT capteurs pour localisation automatique
- [ ] IA reconnaissance d'images pour inventaire
- [ ] Multi-tenant pour plusieurs organisations

---

**Développé avec ❤️ pour simplifier la gestion d'inventaire matériel**