"""
Configuration Celery pour le projet CMDB Inventory
"""

import os
from celery import Celery

# Définir le module de settings Django par défaut pour le programme 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')

app = Celery('inventory_project')

# Utiliser une chaîne ici signifie que le worker n'a pas besoin de sérialiser
# l'objet de configuration vers les processus enfants.
# - namespace='CELERY' signifie que toutes les clés de configuration liées à celery
#   doivent avoir un préfixe `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger les modules de tâches de toutes les applications Django enregistrées.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')