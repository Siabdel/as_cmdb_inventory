-- docker/init-db.sql
GRANT USAGE ON SCHEMA public TO inventory_user;
GRANT CREATE ON SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_user;
### # Bonne syntaxe
sudo -u postgres psql -d inventory_db -c "GRANT ALL ON SCHEMA public TO inventory_user;"
sudo -u postgres psql -d inventory_db -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO inventory_user;"
sudo -u postgres psql -d inventory_db -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO inventory_user;"
sudo -u postgres psql -d inventory_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_user;"
sudo -u postgres psql -d inventory_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_user;"
# Bonne syntaxe
sudo -u postgres psql -d inventory_db -c "GRANT ALL ON SCHEMA public TO inventory_user;"
## createdb -U inventory_user recrée la DB avec lui comme owner automatiquement. Aucun GRANT nécessaire.
##
## sous docker ADMINER, la DB est créée avec inventory_user comme owner, donc pas besoin de GRANT.
# 1. Supprimer les fichiers de migration
find . -path "*/inventory/migrations/0*.py" -delete

# 2. Ouvrir le dbshell
docker compose exec backend python manage.py dbshell

# 3. Dans psql — reset schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO inventory_user;
\q

# 4. Recréer les migrations et migrer
docker compose exec backend python manage.py makemigrations inventory
docker compose exec backend python manage.py migrate

# 5. Recréer le superuser (déjà dans entrypoint mais manuellement si besoin)
docker compose exec backend python manage.py createsuperuser

Oui, l'ordre est **exactement correct** et voici pourquoi :

***

## Graphe des dépendances FK

```
django (contenttypes, auth, admin, sessions)
         │
         ▼
    inventory          ← aucune dépendance projet
    ├── Category
    ├── Brand
    ├── Location
    ├── Tag
    ├── Asset          ← FK vers Category, Brand, Location, Tag
    └── AssetMovement  ← FK vers Asset, Location
         │
         ├──────────────────────┐
         ▼                      ▼
    maintenance            scanner
    ├── MaintenanceTicket   ├── QRCode      ← OneToOne vers Asset
    │   └── FK → Asset      └── ScanLog     ← FK vers QRCode
    ├── TicketPart
    ├── TicketComment
    └── StatusHistory
         │
         ▼
       stock
       ├── StockItem       ← FK vers Brand, Location (inventory)
       └── StockMovement   ← FK vers StockItem
                           ← FK vers MaintenanceTicket (maintenance)
```

***

## Ordre final confirmé ✅

| Ordre | App | Dépend de |
|-------|-----|-----------|
| 1 | `contenttypes` | — |
| 2 | `auth` | contenttypes |
| 3 | `admin` | auth, contenttypes |
| 4 | `sessions` | — |
| 5 | `inventory` | auth |
| 6 | `maintenance` | inventory |
| 7 | `scanner` | inventory |
| 8 | `stock` | inventory + maintenance |

> ⚠️ **`stock` doit être en dernier** car `StockMovement` a une FK vers `maintenance.MaintenanceTicket` — si tu mets `stock` avant `maintenance`, la migration plantera sur cette FK.