Waiting for PostgreSQL...
db:5432 - accepting connections
PostgreSQL is ready!
Running migrations...
Waiting for PostgreSQL...
db:5432 - accepting connections
PostgreSQL is ready!
Running migrations...
docker logs as_cmdb_inventory_backend_1
docker logs 0f35a248d0c6 --tail 10
docker exec -it as_cmdb_inventory_backend_1 mkdir -p /app/logs
docker exec as_cmdb_inventory_backend_1 mkdir -p /app/logs
docker-compose logs frontend
chmod -R 755 ../backend/logs
sudo systemctl restart postgresql
psql -U postgres -c SELECT usename, passwd FROM pg_shadow WHERE usename = 'inventory_user';
sudo -u postgres psql -c CREATE USER inventory_user WITH PASSWORD 'inventory_password';
sudo -u postgres psql -c CREATE DATABASE inventory_db OWNER inventory_user;
sudo -u postgres psql -c GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
psql -U postgres -c "SELECT usename, datname FROM pg_database db JOIN pg_user u ON db.datdba = u.usesysid WHERE usename = 'inventory_user';"

