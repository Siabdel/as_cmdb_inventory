pip list | grep drf-spectacular
##
cd /home/django/Depots/www/projets/envCMDBIventory && bash -c 'source venv/bin/activate && pip install dj-database-url && cd as_cmdb_inventory/backend && python manage.py runserver'
## 
curl -s http://localhost:3001/ | grep -i 'Bienvenue sur notre Application de Gestion d'Inventaire'
