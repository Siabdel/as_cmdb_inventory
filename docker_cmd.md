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
## se connecter au containe 
docker compose exec -it backend bash 
# ./manage.py dbshell

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

sudo -u postgres psql -d inventory_db << EOF
GRANT USAGE ON SCHEMA public TO inventory_user;
GRANT CREATE ON SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_user;

SELECT has_schema_privilege('inventory_user', 'public', 'CREATE');
EOF
Oui, tu donnes **presque tout** sur `inventory_db` — mais pas les droits dangereux. Voici l'analyse précise :

Très bonne question ! C'est une question de **sécurité et séparation des responsabilités**.
```bash
# Supprimer les containers intermédiaires (stopped)
docker container prune -f

# Supprimer les images intermédiaires (<none>:<none>)
docker image prune -f

# Supprimer les volumes non utilisés
docker volume prune -f

# Supprimer les networks non utilisés
docker network prune -f

# ── TOUT en une seule commande ──────────────
docker system prune -f

# Avec volumes (⚠️ supprime les données PostgreSQL !)
docker system prune -f --volumes
```

## Voir ce qui sera supprimé avant

```bash
# Lister containers stopped
docker ps -a --filter "status=exited"

# Lister images <none>
docker images -f "dangling=true"

# Voir l'espace utilisé
docker system df
```

## Résumé

| Commande | Supprime |
|----------|----------|
| `container prune` | Containers stoppés |
| `image prune` | Images `<none>` orphelines |
| `volume prune` | Volumes non attachés |
| `network prune` | Networks inutilisés |
| `system prune` | Tout sauf volumes |
| `system prune --volumes` | ⚠️ Tout + volumes (reset DB) |

## Analogie — L'immeuble de bureaux

```
postgres        = Le propriétaire de l'immeuble (tout-puissant)
inventory_user  = L'employé locataire (accès limité à son étage)
```

## Rôles distincts

| | `postgres` | `inventory_user` |
|--|-----------|-----------------|
| **Rôle** | Super-administrateur | Utilisateur applicatif |
| **Qui l'utilise** | Toi (DBA/DevOps) | Django (l'application) |
| **Créer des bases** | ✅ | ❌ |
| **Créer des users** | ✅ | ❌ |
| **DROP DATABASE** | ✅ | ❌ |
| **CRUD sur inventory_db** | ✅ | ✅ |

## Pourquoi ne pas utiliser `postgres` directement dans Django ?

### 🔴 Danger si Django utilise `postgres`
```python
# settings.py avec postgres = CATASTROPHIQUE
DATABASES = {
    'default': {
        'USER': 'postgres',  # ← superuser dans l'app !
    }
}
```
Si un attaquant exploite une faille SQL Injection dans ton app → il a accès **superuser** → peut détruire **toutes les bases**, créer des users, exécuter des commandes système.

### ✅ Avec `inventory_user`
```python
# settings.py sécurisé
DATABASES = {
    'default': {
        'USER': 'inventory_user',  # ← accès limité à inventory_db seulement
    }
}
```
Même en cas de faille → l'attaquant est **confiné** à `inventory_db`, ne peut pas toucher aux autres bases ni au système.

## Principe de moindre privilège

```
Ne donne à chaque composant que les droits
dont il a strictement besoin — rien de plus.
```

- `postgres` → utilisé uniquement pour les opérations DBA (créer DB, GRANT, backup)
- `inventory_user` → utilisé uniquement par Django au runtime

## En production, tu aurais même

```
postgres          → superadmin DBA
inventory_user    → Django app (lecture/écriture)
inventory_readonly → Reporting/dashboards (SELECT uniquement)
inventory_backup  → Sauvegarde (pg_dump uniquement)
```

Chaque service a **exactement** ce dont il a besoin — pas plus. 🎯

## Ce que tu donnes ✅

| Droit | Sur quoi | Concrètement |
|-------|----------|-------------|
| `USAGE` | Schéma public | Naviguer dans le schéma |
| `CREATE` | Schéma public | Créer des tables (nécessaire pour `migrate`) |
| `SELECT/INSERT/UPDATE/DELETE` | Toutes les tables | CRUD complet |
| `USAGE/UPDATE` | Toutes les sequences | Générer les IDs auto |

## Ce que tu NE donnes PAS ❌ (les droits dangereux)

| Droit refusé | Conséquence |
|-------------|-------------|
| `SUPERUSER` | Ne peut pas bypasser les sécurités |
| `CREATEDB` | Ne peut pas créer d'autres bases |
| `CREATEROLE` | Ne peut pas créer d'autres users |
| `DROP DATABASE` | Ne peut pas supprimer la base entière |
| `pg_read_server_files` | Ne peut pas lire les fichiers système |

## En pratique pour Django — c'est suffisant et correct ✅

```
inventory_user peut :           inventory_user NE peut PAS :
────────────────────            ────────────────────────────
✅ makemigrations/migrate       ❌ DROP DATABASE inventory_db
✅ SELECT / INSERT / UPDATE     ❌ CREATE DATABASE autre_db
✅ DELETE                       ❌ CREATE USER hacker
✅ Créer tables (migrate)       ❌ accéder à postgres / auth db
✅ Générer IDs auto             ❌ lire fichiers serveur
```

## Version encore plus stricte pour la prod

Si tu veux **retirer le droit CREATE** une fois les migrations appliquées (Django n'en a plus besoin au runtime) :

```sql
-- Après migrate, réduire les droits au strict minimum
REVOKE CREATE ON SCHEMA public FROM inventory_user;
```

Django en production n'a besoin que de **SELECT/INSERT/UPDATE/DELETE** — jamais de CREATE TABLE. Les migrations se font manuellement lors des déploiements avec un user dédié.

```
Développement  →  GRANT CREATE  (migrations fréquentes)
Production     →  REVOKE CREATE (migrations contrôlées)
```

Ton `init-db.sql` est donc **bien calibré pour le développement**. 🎯

La table `maintenance_maintenanceaction` n'existe pas — l'app `maintenance` a des migrations non appliquées.

## Diagnostic

```bash
# Voir l'état des migrations de toutes les apps
./manage.py showmigrations
```

## Fix rapide

```bash
# Appliquer toutes les migrations en attente
./manage.py migrate maintenance
./manage.py migrate
```

## Si erreur "table already exists"

```bash
# Faker les migrations maintenance (tables déjà en base)
./manage.py migrate maintenance --fake-initial
./manage.py migrate
```

## Si erreur "no migrations found"

L'app `maintenance` n'a pas encore de migrations :
```bash
./manage.py makemigrations maintenance
./manage.py migrate maintenance
```

***

## Vérif complète

```bash
# Lister toutes les apps et leur état
./manage.py showmigrations

# Toutes les lignes doivent être [X]
# Les [ ] sont les migrations à appliquer
```

Colle-moi le output de `showmigrations` si ça bloque encore — je verrai exactement quelles apps posent problème. 🎯

**Ta commande a plusieurs erreurs de syntaxe. Voici la correction :**

## ❌ **Ta commande (incorrecte)**
```bash
find .. -path .. -type  f  -exec grep "ashoppy_dev_db" {} \;;
```

## ✅ **Commande corrigée**
```bash
find . -type f -exec grep -l "inventory_db" {} \;
```

**Ou version plus moderne (recommandée) :**
```bash
grep -r --include="*" "inventory_db" .
```

## 🔍 **Explications des corrections**

| Erreur | ❌ Incorrect | ✅ Correct |
|--------|-------------|------------|
| **Répertoire** | `..` (parent) | `.` (courant) |
| **Option inutile** | `-path ..` | Supprimée |
| **Espace avant type** | `-type  f` | `-type f` |
| **Backslash** | `\\;` | `\;` |
| **Chaine de recherche** | `"ashoppy_dev_db"` | `"inventory_db"` |
| **Option utile** | Manquante | `-l` (noms fichiers seulement) |

## 🎯 **Versions selon tes besoins**

### **1. Juste les noms de fichiers**
```bash
find . -type f -exec grep -l "inventory_db" {} \;
```

### **2. Avec numéros de ligne**
```bash
find . -type f -exec grep -n "inventory_db" {} \;
```

### **3. Insensible à la casse**
```bash
find . -type f -exec grep -li "inventory_db" {} \;
```

### **4. Grep récursif (plus rapide)**
```bash
grep -rnl "inventory_db" .
```

### **5. Depuis la racine du projet**
```bash
find /chemin/vers/projet -type f -name "*.py" -exec grep -l "inventory_db" {} \;
```

## 🚀 **Commande idéale pour ton cas**
```bash
# Recherche dans tous les fichiers Python seulement
find . -name "*.py" -exec grep -l "inventory_db" {} \; -print

# Ou plus simple :
grep -rnl --include="*.py" "inventory_db" .
```

**Lance ça depuis la racine de ton projet Django → tu verras tous les fichiers à corriger !** ✅
**Pour chercher `inventory_db` UNIQUEMENT dans les fichiers `.env` :**

## ✅ **Commande corrigée**
```bash
find . -name ".env*" -type f -exec grep -l "inventory_db" {} \;
```

## 🎯 **Versions selon tes besoins**

### **1. Noms des fichiers .env seulement**
```bash
find . -name ".env*" -type f -exec grep -l "inventory_db" {} \;
```

### **2. Avec contexte (lignes + numéros)**
```bash
find . -name ".env*" -type f -exec grep -n "inventory_db" {} \;
```

### **3. Grep moderne (plus rapide)**
```bash
grep -rnl --include="*.env*" "inventory_db" .
```

### **4. Avec affichage des lignes exactes**
```bash
grep -rn --include="*.env*" "inventory_db" .
```

## 🔍 **Explications**
- `-name ".env*"` : **uniquement** les fichiers `.env`, `.env.local`, `.env.prod`, etc.
- `-type f` : fichiers seulement (pas dossiers)
- `-l` : noms des fichiers (pas le contenu)
- `-n` : numéros de ligne

## 🚀 **Commande idéale**
```bash
# Juste les fichiers .env avec inventory_db
grep -rnl --include="*.env*" "inventory_db" .

# OU avec contexte
grep -rn --include="*.env*" "inventory_db" .
```

**Exemple de sortie attendue :**
```
./docker/.env
./backend/.env.local
./.env.example
```

Lance depuis la **racine de ton projet** → tu verras tous tes `.env` à corriger ! ✅