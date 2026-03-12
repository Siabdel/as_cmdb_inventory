### la commande suivante pour vérifier la connexion à la base de données :
$ docker-compose exec backend python manage.py check
## Je vais exécuter la commande suivante pour vérifier la connexion à la base de données :
$ docker-compose run --rm backend python manage.py check
## Je vais exécuter la commande suivante pour installer le module django-environ :
$ docker-compose run --rm backend pip install django-environ
#" Je vais exécuter la commande suivante pour reconstruire l'image Docker :
$ docker-compose build backend
## Je vais exécuter la commande suivante pour corriger le fichier requirements.txt :
sed -i 's/faker==20.1.0django-environ==0.10.0/faker==20.1.0\ndjango-environ==0.10.0/' backend/requirements.txt
## je vais exécuter la commande suivante pour redémarrer les services :

## docker-compose restart backend celery-beat celery
## Je vais exécuter la commande suivante pour tester la connexion à la base de données :

$ docker-compose exec backend python manage.py shell -c "import django; django.setup(); from django.db import connection; connection.connect()"

docker compose down
docker compose up -d db
python manage.py migrate
###
## Celery-beat utilise localhost:5432 au lieu de db:5432 ! DATABASE_URL pas passée ou override local.
##​ Diagnostic Celery-beat
docker compose logs celery-beat  # Config utilisée ?
docker compose exec celery-beat env | grep DB  # Vars réelles
docker compose exec celery-beat python manage.py shell -c "
from django.conf import settings
print(settings.DATABASES['default']['HOST'])
###
docker compose up -d  # Stack complète
docker compose ps    # Status services
docker compose logs celery-beat  # Logs erreur
docker compose exec celery-beat env | grep DB  # Vars réelles
docker compose restart celery-beat  # Restart rapide
### Mise a jour version moteur docker 
# Purge ancien
sudo apt purge docker.io docker-ce docker-ce-cli containerd runc

# Docker officiel 27+ (API 1.53)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

docker --version  # 27.x API 1.53
docker compose up -d  # No error
### Le db est OK, mais backend / celery crashent à chaque start → il faut lire leurs logs pour voir la vraie erreur (probablement encore la DB ou une variable manquante).

docker compose logs backend --tail=50
docker compose logs celery --tail=50
docker compose logs celery-beat --tail=50
###
docker compose down
docker compose up -d db redis
sleep 5
docker compose up -d backend celery celery-beat frontend
docker compose logs backend  # No crash !

### err socket 
# 1. Connecte explicitement Docker DB
docker compose exec db psql -U inventory_user -d inventory_db

# 2. Ou backend → DB interne
docker compose exec backend python manage.py dbshell

# 3. Test connexion Python
docker compose exec backend python manage.py shell -c "
from django.db import connection
connection.ensure_connection()
print('✅ DB OK')
"
docker compose ps  # db healthy ?
docker compose logs db  # "ready to accept" ?
docker compose exec db psql -U inventory_user -d inventory_db -c "\dt"  # Tables ?
✅ Backend DB OK ! ALLOWED_HOSTS et connexion PostgreSQL fonctionnent parfaitement dans le conteneur.
​

# Prochaines étapes as_cmdb_inventory
# Stack saine → migre et teste :

# 1. Migrations
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# 2. Superuser (prod)
docker compose exec backend python manage.py createsuperuser

# 3. Collect static + QR codes
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py generate_qr_codes  # Si custom cmd

# 4. Celery test
docker compose exec celery python manage.py shell -c "
from celery import current_app
print('✅ Celery broker OK:', current_app.broker_connection().ensure_connection())
"

# 5. Status complet
docker compose ps
##
docker compose exec backend python manage.py flush --no-input
## 
rm -rf backend/inventory/migrations/00*
##
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py generate_fake_data
###
# Vider et recréer proprement
# Reset propre (si env de dev, données non critiques)
docker compose exec db psql -U inventory_user -d inventory_db -c "DROP TABLE IF EXISTS inventory_asset CASCADE;"
docker compose exec backend python manage.py migrate inventory zero
docker compose exec backend python manage.py makemigrations inventory
docker compose exec backend python manage.py migrate inventory
## 
# 1. Supprimer TOUTES les anciennes migrations (garder __init__.py)
find inventory/migrations/ -name "0*.py" -delete

# 2. Recréer une migration initiale propre
docker compose exec backend python manage.py makemigrations inventory

# 3. Appliquer les migrations (crée les tables)
docker compose exec backend python manage.py migrate

# 4. Vérifier que les tables existent
docker compose exec db psql -U inventory_user -d inventory_db -c "\dt inventory_*"

# 5. Générer les données fake
docker compose exec backend python manage.py generate_fake_data --assets 100 --movements 200
La colonne description existe déjà → Cas A, faker la migration.

Fix — 1 commande
bash
docker compose exec backend python manage.py migrate inventory 0002 --fake
Puis lancer le script
bash
docker compose exec backend python manage.py generate_fake_data --assets 100 --movements 200
Vérif finale
bash
docker compose exec backend python manage.py showmigrations inventory
# Doit afficher :
# [X] 0001_initial
# [X] 0002_location_description
C'est tout — la colonne existe, Django n'a pas besoin de la recréer. --fake synchronise juste l'état. 🚀
# Ajouter la colonne manuellement sur inventory_tag
docker compose exec db psql -U inventory_user -d inventory_db -c "
ALTER TABLE inventory_tag ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;
UPDATE inventory_tag SET updated_at = created_at WHERE updated_at IS NULL;
ALTER TABLE inventory_tag ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE inventory_tag ALTER COLUMN updated_at SET DEFAULT NOW();
"
docker compose exec db psql -U inventory_user -d inventory_db -c "
SELECT table_name FROM information_schema.tables 
WHERE table_schema='public' 
ORDER BY table_name;"



