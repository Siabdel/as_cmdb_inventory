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


### DashboardVoici l'architecture API complète pour une **société de reconditionnement IT**  : [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/71803920/dd3513f6-da42-4507-af82-ea6a1b5f4ee1/models.py)

***

## 1. `inventory/serializers.py`

```python
from rest_framework import serializers
from .models import Category, Brand, Location, Tag, Asset, AssetMovement


# ── Serializers de référence (lecture légère) ──────────────

class CategoryMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']


class BrandMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo']


class LocationMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'type']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'description']


# ── Category ───────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon',
                  'asset_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        from django.utils.text import slugify
        qs = Category.objects.filter(slug=slugify(value))
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Une catégorie avec ce nom existe déjà.")
        return value

    def create(self, validated_data):
        from django.utils.text import slugify
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


# ── Brand ──────────────────────────────────────────────────

class BrandSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'website', 'logo',
                  'asset_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ── Location ───────────────────────────────────────────────

class LocationSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'type', 'description',
                  'parent', 'parent_name', 'asset_count',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ── AssetMovement ──────────────────────────────────────────

class AssetMovementSerializer(serializers.ModelSerializer):
    from_location_detail = LocationMinSerializer(source='from_location', read_only=True)
    to_location_detail   = LocationMinSerializer(source='to_location', read_only=True)

    class Meta:
        model = AssetMovement
        fields = ['id', 'asset', 'from_location', 'from_location_detail',
                  'to_location', 'to_location_detail',
                  'moved_by', 'moved_at', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ── Asset List (léger pour dashboard/tableaux) ─────────────

class AssetListSerializer(serializers.ModelSerializer):
    category = CategoryMinSerializer(read_only=True)
    brand    = BrandMinSerializer(read_only=True)
    location = LocationMinSerializer(source='current_location', read_only=True)
    tags     = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'model', 'serial_number',
            'category', 'brand', 'location',
            'status', 'condition_state',
            'assigned_to', 'tags', 'photo',
            'purchase_date', 'warranty_end',
            'created_at', 'updated_at',
        ]


# ── Asset Detail (complet pour fiche individuelle) ─────────

class AssetDetailSerializer(serializers.ModelSerializer):
    category         = CategoryMinSerializer(read_only=True)
    brand            = BrandMinSerializer(read_only=True)
    current_location = LocationMinSerializer(read_only=True)
    tags             = TagSerializer(many=True, read_only=True)
    movements        = AssetMovementSerializer(many=True, read_only=True)

    # Champs write-only pour create/update
    category_id         = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True)
    brand_id            = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source='brand', write_only=True)
    current_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='current_location', write_only=True)
    tag_ids             = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags',
        many=True, write_only=True, required=False)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'model', 'serial_number', 'description',
            'category', 'category_id',
            'brand', 'brand_id',
            'current_location', 'current_location_id',
            'assigned_to', 'status', 'condition_state',
            'purchase_date', 'purchase_price', 'warranty_end',
            'tags', 'tag_ids', 'photo', 'movements',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        asset = super().create(validated_data)
        asset.tags.set(tags)
        return asset

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        asset = super().update(instance, validated_data)
        if tags is not None:
            asset.tags.set(tags)
        return asset


# ── Dashboard Stats (lecture seule) ───────────────────────

class DashboardStatsSerializer(serializers.Serializer):
    total_assets      = serializers.IntegerField()
    active_assets     = serializers.IntegerField()
    inactive_assets   = serializers.IntegerField()
    archived_assets   = serializers.IntegerField()
    assets_new        = serializers.IntegerField()
    assets_used       = serializers.IntegerField()
    assets_damaged    = serializers.IntegerField()
    total_value       = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_warranty      = serializers.IntegerField()  # warranty < 30 jours
    recent_movements  = AssetMovementSerializer(many=True)
```

***

## 2. `inventory/views.py`

```python
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import Category, Brand, Location, Tag, Asset, AssetMovement
from .serializers import (
    CategorySerializer, BrandSerializer, LocationSerializer,
    TagSerializer, AssetListSerializer, AssetDetailSerializer,
    AssetMovementSerializer, DashboardStatsSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.annotate(asset_count=Count('assets')).order_by('name')
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['type']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'condition_state', 'category', 'brand', 'current_location']
    search_fields = ['name', 'serial_number', 'model', 'assigned_to']
    ordering_fields = ['name', 'purchase_date', 'purchase_price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Asset.objects.select_related(
            'category', 'brand', 'current_location'
        ).prefetch_related('tags', 'movements').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetDetailSerializer

    # ── Actions custom ──────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='move')
    def move(self, request, pk=None):
        """Déplacer un asset vers un nouvel emplacement."""
        asset = self.get_object()
        to_location_id = request.data.get('to_location_id')
        moved_by = request.data.get('moved_by', request.user.username)
        notes = request.data.get('notes', '')

        try:
            to_location = Location.objects.get(pk=to_location_id)
        except Location.DoesNotExist:
            return Response({'error': 'Location introuvable.'}, status=400)

        movement = AssetMovement.objects.create(
            asset=asset,
            from_location=asset.current_location,
            to_location=to_location,
            moved_by=moved_by,
            notes=notes,
        )
        asset.current_location = to_location
        asset.save()

        return Response(AssetMovementSerializer(movement).data, status=201)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        """Assigner un asset à un employé."""
        asset = self.get_object()
        assigned_to = request.data.get('assigned_to')
        if not assigned_to:
            return Response({'error': 'assigned_to requis.'}, status=400)
        asset.assigned_to = assigned_to
        asset.status = 'active'
        asset.save()
        return Response(AssetDetailSerializer(asset).data)

    @action(detail=True, methods=['post'], url_path='retire')
    def retire(self, request, pk=None):
        """Archiver/retirer un asset du stock."""
        asset = self.get_object()
        asset.status = 'archived'
        asset.assigned_to = None
        asset.save()
        return Response({'status': 'archived', 'asset': asset.name})

    @action(detail=False, methods=['get'], url_path='warranty-expiring')
    def warranty_expiring(self, request):
        """Assets dont la garantie expire dans 30 jours."""
        soon = timezone.now().date() + timedelta(days=30)
        qs = Asset.objects.filter(
            warranty_end__lte=soon,
            warranty_end__gte=timezone.now().date(),
            status='active'
        ).select_related('category', 'brand', 'current_location')
        return Response(AssetListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='by-status')
    def by_status(self, request):
        """Répartition des assets par statut (pour graphiques dashboard)."""
        data = Asset.objects.values('status').annotate(count=Count('id'))
        return Response(data)

    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        """Répartition par catégorie."""
        data = Asset.objects.values(
            'category__name', 'category__icon'
        ).annotate(count=Count('id')).order_by('-count')
        return Response(data)


class AssetMovementViewSet(viewsets.ModelViewSet):
    queryset = AssetMovement.objects.select_related(
        'asset', 'from_location', 'to_location'
    ).order_by('-moved_at')
    serializer_class = AssetMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'from_location', 'to_location']
    ordering_fields = ['moved_at']
    http_method_names = ['get', 'post', 'head', 'options']  # pas de PUT/DELETE


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        soon = timezone.now().date() + timedelta(days=30)
        data = {
            'total_assets':    Asset.objects.count(),
            'active_assets':   Asset.objects.filter(status='active').count(),
            'inactive_assets': Asset.objects.filter(status='inactive').count(),
            'archived_assets': Asset.objects.filter(status='archived').count(),
            'assets_new':      Asset.objects.filter(condition_state='new').count(),
            'assets_used':     Asset.objects.filter(condition_state='used').count(),
            'assets_damaged':  Asset.objects.filter(condition_state='damaged').count(),
            'total_value':     Asset.objects.aggregate(
                                   v=Sum('purchase_price'))['v'] or 0,
            'low_warranty':    Asset.objects.filter(
                                   warranty_end__lte=soon,
                                   warranty_end__gte=timezone.now().date()).count(),
            'recent_movements': AssetMovement.objects.select_related(
                                   'asset', 'from_location', 'to_location'
                                ).order_by('-moved_at')[:10],
        }
        return Response(DashboardStatsSerializer(data).data)
```

***

## 3. `inventory/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories',  views.CategoryViewSet,      basename='category')
router.register('brands',      views.BrandViewSet,         basename='brand')
router.register('locations',   views.LocationViewSet,      basename='location')
router.register('tags',        views.TagViewSet,           basename='tag')
router.register('assets',      views.AssetViewSet,         basename='asset')
router.register('movements',   views.AssetMovementViewSet, basename='movement')
router.register('dashboard',   views.DashboardViewSet,     basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
```

## 4. `config/urls.py` — ajouter le prefix

```python
path('api/v1/inventory/', include('inventory.urls')),
```

## 5. Install django-filter

```bash
pip install django-filter
# settings.py → INSTALLED_APPS
'django_filters',
# settings.py → REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}
```

***

## Endpoints générés

| Méthode | URL | Usage |
|---------|-----|-------|
| `GET` | `/api/v1/inventory/assets/` | Liste assets (dashboard) |
| `GET` | `/api/v1/inventory/assets/{id}/` | Fiche asset complète |
| `POST` | `/api/v1/inventory/assets/{id}/move/` | Déplacer un asset |
| `POST` | `/api/v1/inventory/assets/{id}/assign/` | Assigner à un employé |
| `POST` | `/api/v1/inventory/assets/{id}/retire/` | Archiver |
| `GET` | `/api/v1/inventory/assets/warranty-expiring/` | Garanties expirant |
| `GET` | `/api/v1/inventory/assets/by-status/` | Stats par statut |
| `GET` | `/api/v1/inventory/assets/by-category/` | Stats par catégorie |
| `GET` | `/api/v1/inventory/dashboard/stats/` | KPIs dashboard complet |
| `GET` | `/api/v1/inventory/movements/` | Historique mouvements |
- `GET /api/dashboard/summary/` - Résumé statistiques
- `GET /api/dashboard/stats/` - Statistiques détaillées

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