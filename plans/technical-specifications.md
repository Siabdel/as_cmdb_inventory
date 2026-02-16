# Spécifications Techniques - CMDB Application

## Structure du Projet

```
inventory_app/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── inventory_project/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── inventory/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── tests.py
│   │   ├── permissions.py
│   │   ├── utils.py
│   │   └── migrations/
│   ├── media/
│   │   └── qr_codes/
│   └── static/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   ├── DataTable.vue
│   │   │   │   ├── LoadingSpinner.vue
│   │   │   │   └── ConfirmModal.vue
│   │   │   ├── assets/
│   │   │   │   ├── AssetCard.vue
│   │   │   │   ├── AssetForm.vue
│   │   │   │   ├── AssetDetail.vue
│   │   │   │   └── QRDisplay.vue
│   │   │   ├── scan/
│   │   │   │   ├── QRScanner.vue
│   │   │   │   ├── ScanResult.vue
│   │   │   │   └── MoveModal.vue
│   │   │   └── dashboard/
│   │   │       ├── StatsCard.vue
│   │   │       ├── ChartWidget.vue
│   │   │       └── RecentActivity.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Assets.vue
│   │   │   ├── AssetDetail.vue
│   │   │   ├── ScanQR.vue
│   │   │   ├── Locations.vue
│   │   │   ├── Categories.vue
│   │   │   ├── Brands.vue
│   │   │   └── Tags.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── store/
│   │   │   ├── index.js
│   │   │   ├── modules/
│   │   │   │   ├── assets.js
│   │   │   │   ├── locations.js
│   │   │   │   ├── categories.js
│   │   │   │   ├── auth.js
│   │   │   │   └── dashboard.js
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   ├── assets.js
│   │   │   ├── locations.js
│   │   │   ├── categories.js
│   │   │   ├── brands.js
│   │   │   ├── tags.js
│   │   │   └── dashboard.js
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   └── validators.js
│   │   └── assets/
│   │       ├── css/
│   │       │   └── custom.css
│   │       └── images/
│   └── public/
│       └── favicon.ico
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .gitignore
└── README.md
```

## Backend Django - Spécifications Détaillées

### Requirements.txt
```
Django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
qrcode[pil]==7.4.2
django-filter==23.5
python-decouple==3.8
Pillow==10.2.0
django-extensions==3.2.3
```

### Modèles Django Détaillés

#### Location Model
```python
class Location(models.Model):
    LOCATION_TYPES = [
        ('placard', 'Placard'),
        ('salle', 'Salle'),
        ('bureau', 'Bureau'),
        ('entrepot', 'Entrepôt'),
        ('externe', 'Externe'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    type = models.CharField(max_length=50, choices=LOCATION_TYPES, verbose_name="Type")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Parent")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Asset Model Complet
```python
class Asset(models.Model):
    STATUS_CHOICES = [
        ('stock', 'En stock'),
        ('use', 'En utilisation'),
        ('broken', 'En panne'),
        ('maintenance', 'En maintenance'),
        ('sold', 'Vendu'),
        ('disposed', 'Mis au rebut'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    internal_code = models.CharField(max_length=20, unique=True, verbose_name="Code interne")
    name = models.CharField(max_length=200, verbose_name="Nom")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Catégorie")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, verbose_name="Marque")
    model = models.CharField(max_length=100, blank=True, verbose_name="Modèle")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de série")
    description = models.TextField(blank=True, verbose_name="Description")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Date d'achat")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix d'achat")
    warranty_end = models.DateField(null=True, blank=True, verbose_name="Fin de garantie")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stock', verbose_name="Statut")
    current_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, verbose_name="Emplacement actuel")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assigné à")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Étiquettes")
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### API Endpoints Détaillés

#### Assets API
```python
# GET /api/assets/
# Filtres: ?search=, ?category=, ?location=, ?status=, ?tags=, ?assigned_to=
# Pagination: ?page=, ?page_size=
# Tri: ?ordering=name, ?ordering=-created_at

# POST /api/assets/
# PUT /api/assets/{id}/
# DELETE /api/assets/{id}/
# GET /api/assets/{id}/qr_image/ → Retourne PNG du QR code
# POST /api/assets/move-from-scan/ → {code: "uuid", target_location_id: 1}
# GET /api/assets/{id}/movements/ → Historique des mouvements
```

#### Dashboard API
```python
# GET /api/dashboard/summary/
{
    "total_assets": 150,
    "assets_by_status": {
        "stock": 45,
        "use": 80,
        "broken": 15,
        "maintenance": 10
    },
    "assets_by_location": {
        "Salle 1": 30,
        "Placard A": 25,
        "Bureau": 40
    },
    "assets_by_category": {
        "PC": 50,
        "Écran": 45,
        "Clavier": 30
    },
    "recent_movements": [...],
    "assets_needing_maintenance": [...],
    "warranty_expiring_soon": [...]
}
```

## Frontend Vue.js - Spécifications Détaillées

### Package.json
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "bootstrap": "^5.3.2",
    "bootstrap-icons": "^1.11.2",
    "axios": "^1.6.2",
    "html5-qrcode": "^2.3.8",
    "chart.js": "^4.4.1",
    "vue-chartjs": "^5.3.0",
    "date-fns": "^3.0.6",
    "vue-toastification": "^2.0.0-rc.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "sass": "^1.69.5"
  }
}
```

### Composants Clés

#### QRScanner.vue
```vue
<template>
  <div class="qr-scanner">
    <div id="qr-reader" style="width: 100%"></div>
    <div class="scanner-controls">
      <button @click="startScanning" :disabled="isScanning">Démarrer</button>
      <button @click="stopScanning" :disabled="!isScanning">Arrêter</button>
    </div>
  </div>
</template>

<script>
import { Html5QrcodeScanner } from 'html5-qrcode'

export default {
  name: 'QRScanner',
  emits: ['scan-success', 'scan-error'],
  data() {
    return {
      scanner: null,
      isScanning: false
    }
  },
  methods: {
    startScanning() {
      // Configuration du scanner
      const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      }
      
      this.scanner = new Html5QrcodeScanner("qr-reader", config)
      this.scanner.render(this.onScanSuccess, this.onScanError)
      this.isScanning = true
    },
    
    onScanSuccess(decodedText) {
      this.$emit('scan-success', decodedText)
      this.stopScanning()
    },
    
    onScanError(error) {
      this.$emit('scan-error', error)
    }
  }
}
</script>
```

### Store Pinia - Assets Module
```javascript
import { defineStore } from 'pinia'
import { assetsApi } from '@/api/assets'

export const useAssetsStore = defineStore('assets', {
  state: () => ({
    assets: [],
    currentAsset: null,
    loading: false,
    filters: {
      search: '',
      category: null,
      location: null,
      status: null,
      tags: []
    },
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0
    }
  }),
  
  actions: {
    async fetchAssets() {
      this.loading = true
      try {
        const response = await assetsApi.getAssets({
          ...this.filters,
          page: this.pagination.page,
          page_size: this.pagination.pageSize
        })
        this.assets = response.data.results
        this.pagination.total = response.data.count
      } catch (error) {
        console.error('Erreur lors du chargement des assets:', error)
      } finally {
        this.loading = false
      }
    },
    
    async moveAssetFromScan(assetId, locationId) {
      try {
        await assetsApi.moveFromScan(assetId, locationId)
        await this.fetchAssets() // Refresh list
      } catch (error) {
        throw error
      }
    }
  }
})
```

## Configuration Docker

### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: inventory_db
      POSTGRES_USER: inventory_user
      POSTGRES_PASSWORD: inventory_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://inventory_user:inventory_pass@db:5432/inventory_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
      - media_files:/app/media

  celery:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    command: celery -A inventory_project worker -l info
    environment:
      - DATABASE_URL=postgresql://inventory_user:inventory_pass@db:5432/inventory_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  media_files:
```

## Fonctionnalités Avancées

### Système de QR Code
- Génération automatique lors de la création d'un asset
- Format URL: `https://app.domain.com/assets/{uuid}/`
- Impression en lot possible
- Scan mobile optimisé

### Recherche et Filtres
- Recherche full-text sur nom, description, code interne, numéro de série
- Filtres combinables par catégorie, emplacement, statut, étiquettes
- Sauvegarde des filtres en localStorage
- Export des résultats en CSV/Excel

### Notifications et Alertes
- Garanties expirant bientôt
- Équipements nécessitant une maintenance
- Mouvements suspects ou non autorisés
- Notifications push pour actions critiques

### Rapports et Analytics
- Tableau de bord avec métriques clés
- Graphiques de répartition par catégorie/emplacement
- Historique des mouvements avec timeline
- Rapports d'inventaire périodiques
- Analyse des coûts et amortissements