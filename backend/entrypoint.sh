#!/bin/bash
set -e

# Créer le répertoire de logs
echo "Creating logs directory..."
mkdir -p /app/logs

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U inventory_user; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Exécuter les migrations
echo "Running migrations..."
python manage.py migrate
python manage.py makemigrations inventory maintenance scanner stock --noinput
python manage.py migrate

# Collecter les fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Créer un superutilisateur si il n'existe pas
echo "Creating superuser if not exists..."
python manage.py shell << PYEOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
PYEOF

# Démarrer le serveur
exec "$@"
