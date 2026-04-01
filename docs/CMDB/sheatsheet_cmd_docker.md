## Tableau de synthèse des commandes Docker utilisées

> created 18 mars 2026
>
> prompt: ecrire un cheat-sheet  MD une synthezes des cmd curl passer dans cette tache 



| Commande | Explication | But |
|----------|-------------|------|
| `docker compose ps` | Liste les conteneurs en cours d'exécution du projet. | Vérifier l'état des services (backend, db, redis) et s'assurer que le backend est opérationnel. |
| `docker compose exec backend python manage.py collectstatic --noinput` | Exécute la commande Django `collectstatic` dans le conteneur backend sans interaction. | Copier les fichiers statiques depuis `STATICFILES_DIRS` vers `STATIC_ROOT` (initialement échoué car les fichiers sources n'étaient pas montés). |
| `docker compose exec backend python manage.py collectstatic --noinput --clear` | Idem avec l'option `--clear` qui supprime les fichiers existants dans `STATIC_ROOT` avant la copie. | Forcer une recopie complète après correction du montage des volumes. |
| `docker compose exec backend python manage.py findstatic admin_cmdb/css/admin_base.css` | Recherche le chemin d'un fichier statique spécifique via les finders Django. | Diagnostiquer pourquoi les fichiers `admin_cmdb` n'étaient pas trouvés par Django. |
| `docker compose exec backend python manage.py findstatic admin_cmdb/css/admin_base.css -v 2` | Version verbeuse (`-v 2`) qui affiche les emplacements scrutés par les finders. | Comprendre quels répertoires Django inspecte et identifier l'absence du dossier `admin_cmdb`. |
| `docker compose exec backend ls -la /app/static/` | Liste le contenu du répertoire `/app/static` dans le conteneur. | Vérifier la présence (ou l'absence) des dossiers `admin_cmdb` dans le volume monté. |
| `docker compose exec backend ls -la /app/static/admin_cmdb/css/` | Liste les fichiers CSS dans le sous‑dossier `admin_cmdb/css`. | Confirmer que les fichiers sources sont bien accessibles après correction du montage. |
| `docker compose exec backend find /app -type d -name admin_cmdb` | Recherche récursive du dossier `admin_cmdb` dans `/app`. | S'assurer que le dossier n'existe nulle part ailleurs dans le conteneur. |
| `docker compose exec backend mount \| grep /app` | Affiche les points de montage concernant `/app`. | Comprendre la structure des volumes (bind mounts vs volumes nommés) et identifier que `/app/static` était un volume nommé `static_files`. |
| `docker compose restart backend` | Redémarre le service backend. | Appliquer les modifications de configuration (settings.py) et rafraîchir l'environnement. |
| `docker compose up -d backend` | Recrée et relance le service backend en mode détaché. | Appliquer la modification du volume dans `docker-compose.yml` (remplacement de `static_files:/app/static` par `./backend/static:/app/static`). |
| `curl -I http://localhost:8300/static/admin_cmdb/css/admin_base.css` | Test HTTP HEAD sur l'URL du fichier statique depuis l'hôte. | Vérifier que le serveur Django sert correctement le fichier (réponse 200 OK) après les corrections. |

**Résultat** : Ces commandes ont permis d'identifier et de corriger la cause racine des erreurs 404 (fichiers statiques non montés dans le conteneur) et de valider que les fichiers sont désormais accessibles.



## Les commandes Curl pour debuguer 

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
