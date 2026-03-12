sudo -u postgres psql -d inventory_db << EOF
-- Droits explicites schéma public
GRANT USAGE ON SCHEMA public TO inventory_user;
GRANT CREATE ON SCHEMA public TO inventory_user;

-- Droits sur objets existants (au cas où)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inventory_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inventory_user;

-- Droits FUTURS (essentiel pour Django migrations)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_user;

-- Vérif
SELECT has_schema_privilege('inventory_user', 'public', 'CREATE');
\q
EOF
