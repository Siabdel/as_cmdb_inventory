# Cheat Sheet : Commandes curl pour tester les URLs du module Stock

Cette cheat-sheet récapitule les commandes curl utilisées pour vérifier la validité des URLs sur la page `http://localhost:8300/admin/stock/`.

## Vérification basique du serveur

```bash
# Vérifier si le serveur répond (code HTTP uniquement)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/admin/stock/

# Afficher les en‑têtes de réponse
curl -s -I http://localhost:8300/admin/stock/ | head -10

# Vérifier la présence d'erreurs dans le contenu HTML
curl -s http://localhost:8300/admin/stock/ | grep -i "error\|exception\|traceback\|not found" | head -5
```

## Tests des différentes URLs du module Stock

### Page principale du stock
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/admin/stock/ && echo " - /admin/stock/"
```

### Liste du stock (alias)
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/admin/stock/list/ && echo " - /admin/stock/list/"
```

### Détail d'un article (avec ID)
```bash
# Tester avec un ID existant (ex: 1)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/admin/stock/1/ && echo " - /admin/stock/1/"

# Récupérer le contenu HTML en cas d'erreur 500
curl -s http://localhost:8300/admin/stock/1/ | head -30

# Filtrer l'erreur TemplateSyntaxError
curl -s http://localhost:8300/admin/stock/1/ | grep -A 10 "TemplateSyntaxError"
```

### Page des mouvements de stock (TODO)
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/admin/stock/movement/ && echo " - /admin/stock/movement/"
```

## Commandes utiles pour le débogage

### Afficher le code HTTP et l'URL en une ligne
```bash
curl -s -o /dev/null -w "%{http_code} - %{url_effective}\n" http://localhost:8300/admin/stock/
```

### Vérifier le type de contenu
```bash
curl -s -I http://localhost:8300/admin/stock/ | grep -i "content-type"
```

### Tester plusieurs URLs en une seule commande (avec xargs)
```bash
echo "http://localhost:8300/admin/stock/ http://localhost:8300/admin/stock/list/" | xargs -n1 -I {} curl -s -o /dev/null -w "%{http_code} - {}\n" {}
```

## Exemple de sortie attendue

- `200 - /admin/stock/` → OK
- `200 - /admin/stock/list/` → OK
- `200 - /admin/stock/1/` → OK (après correction)
- `200 - /admin/stock/movement/` → OK (template générique)

## Notes

- Le port `8300` est celui utilisé par le serveur Django dans ce projet.
- Les commandes utilisent l'option `-s` (silencieux) pour supprimer la progression.
- L'option `-o /dev/null` redirige le corps de la réponse vers `/dev/null`.
- L'option `-w` permet de formater la sortie (ici le code HTTP).
- En cas d'erreur 500, il est utile de récupérer le contenu HTML pour analyser la trace Django.

## Correction appliquée

Une erreur `TemplateSyntaxError` sur `/admin/stock/1/` a été corrigée en modifiant `backend/templates/admin/stock/detail.html` :

- Remplacement de `{{ item.category.name if item.category else '' }}` par `{{ item.category.name|default:'' }}`
- Remplacement de `{{ item.photo.url if item.photo else '' }}` par `{% if item.photo %}{{ item.photo.url }}{% endif %}`

Après correction, la page retourne un code 200.

## Tests des endpoints API (cette tâche)

### Vérification de l'endpoint `/api/v1/stock/categories/`

```bash
# Test simple (sans authentification) – attendu 401 (Unauthorized) au lieu de 404 (Not Found)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/api/v1/stock/categories/

# Avec authentification par token (remplacez TOKEN par un token valide)
curl -H "Authorization: Token YOUR_TOKEN" -s http://localhost:8300/api/v1/stock/categories/ | jq .
```

### Commandes shell Django (manage.py) pour tester la vue

```bash
# Se placer dans le répertoire backend
cd backend

# Lancer un shell Django et exécuter un test rapide
python manage.py shell -c "
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Créer un utilisateur de test (si inexistant)
try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create_user('testuser', password='testpass')
    user.save()

# Créer un token
token, created = Token.objects.get_or_create(user=user)

# Client API
client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

# Requête GET
response = client.get('/api/v1/stock/categories/')
print('Status:', response.status_code)
print('Data:', response.data)
"
```

### Commandes utiles pour inspecter les routes

```bash
# Lister les URLs enregistrées dans le module stock
python manage.py shell -c "
from django.urls import get_resolver
resolver = get_resolver()
for url_pattern in resolver.url_patterns:
    if hasattr(url_pattern, 'url_patterns'):
        for sub in url_pattern.url_patterns:
            if 'stock' in str(sub.pattern):
                print(sub.pattern, sub.callback.__module__ if hasattr(sub, 'callback') else '')
"

# Vérifier que la vue CategoryViewSet est bien enregistrée
python manage.py shell -c "
from stock.urls import router
for prefix, viewset, basename in router.registry:
    print(f'{prefix} -> {viewset.__name__}')
"
```

## Résolution de l'erreur 404 sur `/api/v1/stock/categories/`

1. **Cause** : L'endpoint n'existait pas dans `stock/urls.py`.
2. **Solution** : Ajout d'une vue `CategoryViewSet` dans `stock/views.py` et enregistrement via `router.register('categories', ...)`.
3. **Vérification** : Après correction, l'endpoint retourne 401 (authentification requise) au lieu de 404.

## Références

- [Documentation DRF ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Gestion des tokens d'authentification](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)