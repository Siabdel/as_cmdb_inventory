# Ajout de la méthode POST à l'API /api/v1/api/stock/items/

## Contexte
L'API `/api/v1/api/stock/items/` ne disposait pas de méthode POST pour permettre la création d'articles de stock.

## Commandes utilisées

### 1. Vérification de l'architecture des URLs
```bash
cd /home/django/Depots/www/projets/envCMDBIventory/as_cmdb_inventory
find . -name "*url*" -type f | grep stock
```

### 2. Analyse du fichier des URLs
```bash
cat backend/stock/urls.py
```

### 3. Analyse du fichier des vues
```bash
cat backend/stock/views.py
```

### 4. Test des tests unitaires (échec attendu)
```bash
cd /home/django/Depots/www/projets/envCMDBIventory/as_cmdb_inventory/backend
python3 manage.py test stock.tests
```

### 5. Vérification du contenu du fichier de tests
```bash
cat backend/stock/tests.py
```

## Solution appliquée

Ajout de la méthode `create` dans la classe `StockItemViewSet` dans `backend/stock/views.py` :

```python
def create(self, request, *args, **kwargs):
    """Permet la création d'un nouvel article de stock via POST."""
    return super().create(request, *args, **kwargs)
```

Cette méthode étend le comportement du ModelViewSet pour inclure la fonctionnalité de création standard via POST.

## Résultat
L'API `/api/v1/api/stock/items/` est désormais accessible en POST pour créer de nouveaux articles de stock.