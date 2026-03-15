"""
Configuration de l'application cmdb_admin
"""
from django.apps import AppConfig

class CmdbAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb_admin'
    verbose_name = 'CMDB Admin'
