Voici le script **exact** pour créer ta DB PostgreSQL sous Debian 12 :

## Script complet

```bash
#!/bin/bash
# Create inventory_db avec user/password

sudo -u postgres psql << EOF
CREATE DATABASE inventory_db;
CREATE USER inventory_user WITH ENCRYPTED PASSWORD 'inventory_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
ALTER USER inventory_user CREATEDB;
\q
EOF
```

## Ou en 4 commandes

```bash
# 1. Connecte-toi en tant que postgres
sudo -u postgres psql

# 2. Dans psql :
CREATE DATABASE inventory_db;
CREATE USER inventory_user WITH ENCRYPTED PASSWORD 'inventory_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
ALTER USER inventory_user CREATEDB;
\q

# 3. Test connexion
psql -h localhost -U inventory_user -d inventory_db
```

## Variables d’environnement

Ajoute dans ton `.env` :

```
DB_NAME=inventory_db
DB_USER=inventory_user
DB_PASSWORD=inventory_password
DB_HOST=localhost
DB_PORT=5432
```

## Test final

```bash
psql -h localhost -U inventory_user -d inventory_db -c "\dt"
```

## Sécurité (optionnel)

Pour production, limite l’accès :

```sql
-- Dans psql (postgres)
ALTER USER inventory_user NOSUPERUSER;
REVOKE ALL PRIVILEGES ON DATABASE postgres FROM inventory_user;
```

**DB prête !** Connecte ton Django dessus.  🚀 [atlassian](https://www.atlassian.com/data/admin/how-to-set-the-default-user-password-in-postgresql)
# 1. Connecte-toi à inventory_db en tant que postgres
sudo -u postgres psql -d inventory_db

# 2. Dans psql, donne les droits complets :
GRANT ALL ON SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_user;

# 3. Quitte
\q

