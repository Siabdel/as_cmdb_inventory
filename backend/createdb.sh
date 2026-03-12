#!/bin/bash
# Create inventory_db avec user/password

sudo -u postgres psql << EOF
CREATE DATABASE inventory_db;
CREATE USER inventory_user WITH ENCRYPTED PASSWORD 'inventory_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
ALTER USER inventory_user CREATEDB;
\q
EOF
