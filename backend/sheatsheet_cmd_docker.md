## Tableau de synthèse des commandes Docker utilisées

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
