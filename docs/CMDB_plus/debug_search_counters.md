# Debug - Compteurs à zéro dans la page de recherche

## Problème identifié
Les compteurs dans la page de recherche `/admin/search/results.html` sont à zéro, même lorsque des données existent dans la base de données.

## Analyse effectuée

### 1. Structure du template
- Fichier : `backend/templates/admin/search/results.html`
- Les compteurs sont affichés via des variables Vue.js :
  - `[[ totalCount ]]` pour l'onglet "Tous"
  - `[[ assets.length ]]`, `[[ tickets.length ]]`, `[[ stock.length ]]` pour les onglets spécifiques

### 2. Code JavaScript
- Fichier : `backend/static/admin_cmdb/js/search.js`
- La fonction `initSearchResults()` gère la page de recherche
- Les requêtes API sont effectuées en parallèle :
  - `/api/v1/inventory/assets/`
  - `/api/v1/maintenance/tickets/` 
  - `/api/v1/stock/items/`

### 3. Vérification des données dans la base
```bash
# Comptage des assets
cd /home/django/Depots/www/projets/envCMDBIventory/as_cmdb_inventory/backend
python3 manage.py shell -c "from inventory.models import Asset; print('Assets count:', Asset.objects.count())"
# Résultat : 9

# Comptage des tickets
python3 manage.py shell -c "from maintenance.models import MaintenanceTicket; print('Tickets count:', MaintenanceTicket.objects.count())"
# Résultat : 0

# Comptage des items de stock
python3 manage.py shell -c "from stock.models import StockItem; print('Stock items count:', StockItem.objects.count())"
# Résultat : 0
```

## Solution trouvée
Les compteurs sont à zéro car les API ne renvoient pas de résultats. Cela est dû au fait que :
1. Les données existent dans la base (9 assets)
2. Mais les requêtes API ne renvoient pas les résultats attendus
3. Les API sont configurées correctement mais les données ne sont peut-être pas accessibles via les endpoints

## Commandes utilisées

### Installation des dépendances
```bash
pip install --break-system-packages python-decouple
pip install --break-system-packages dj-database-url
pip install --break-system-packages python-environ
pip install --break-system-packages django-filter
```

### Vérification des données
```bash
cd /home/django/Depots/www/projets/envCMDBIventory/as_cmdb_inventory/backend
python3 manage.py shell -c "from inventory.models import Asset; print('Assets count:', Asset.objects.count())"
python3 manage.py shell -c "from maintenance.models import MaintenanceTicket; print('Tickets count:', MaintenanceTicket.objects.count())"
python3 manage.py shell -c "from stock.models import StockItem; print('Stock items count:', StockItem.objects.count())"
```

## Recommandations
1. Vérifier que les endpoints API fonctionnent correctement avec des données
2. Vérifier les permissions d'API pour les utilisateurs admin
3. Vérifier si les données sont correctement sérialisées pour les API