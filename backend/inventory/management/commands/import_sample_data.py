"""
Commande Django pour importer des données d'exemple de matériels informatiques
Usage: python manage.py import_sample_data [--file path/to/file.json] [--clear]
"""

import json
import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from inventory.models import Location, Category, Brand, Tag, Asset, AssetMovement


class Command(BaseCommand):
    help = 'Importe des données d\'exemple de matériels informatiques depuis un fichier JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Chemin vers le fichier JSON à importer',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant l\'import',
        )
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Crée un fichier JSON d\'exemple avec des données de démonstration',
        )

    def handle(self, *args, **options):
        if options['create_sample']:
            self.create_sample_file()
            return

        if options['clear']:
            self.clear_existing_data()

        file_path = options.get('file')
        if file_path:
            self.import_from_file(file_path)
        else:
            self.import_default_data()

    def create_sample_file(self):
        """Crée un fichier JSON d'exemple avec des données de démonstration"""
        sample_data = {
            "locations": [
                {
                    "name": "Bâtiment Principal",
                    "type": "salle",
                    "description": "Bâtiment principal de l'entreprise",
                    "parent": None
                },
                {
                    "name": "Bureau 101",
                    "type": "bureau",
                    "description": "Bureau du directeur",
                    "parent": "Bâtiment Principal"
                },
                {
                    "name": "Bureau 102",
                    "type": "bureau",
                    "description": "Bureau des développeurs",
                    "parent": "Bâtiment Principal"
                },
                {
                    "name": "Salle de réunion A",
                    "type": "salle",
                    "description": "Grande salle de réunion",
                    "parent": "Bâtiment Principal"
                },
                {
                    "name": "Stock principal",
                    "type": "entrepot",
                    "description": "Entrepôt de stockage principal",
                    "parent": None
                },
                {
                    "name": "Atelier maintenance",
                    "type": "entrepot",
                    "description": "Atelier de réparation",
                    "parent": None
                }
            ],
            "categories": [
                {
                    "name": "Informatique",
                    "slug": "informatique",
                    "description": "Équipements informatiques",
                    "parent": None,
                    "icon": "bi-laptop"
                },
                {
                    "name": "PC",
                    "slug": "pc",
                    "description": "Ordinateurs de bureau et portables",
                    "parent": "Informatique",
                    "icon": "bi-pc-display"
                },
                {
                    "name": "Écrans",
                    "slug": "ecrans",
                    "description": "Moniteurs et écrans",
                    "parent": "Informatique",
                    "icon": "bi-display"
                },
                {
                    "name": "Périphériques",
                    "slug": "peripheriques",
                    "description": "Claviers, souris, etc.",
                    "parent": "Informatique",
                    "icon": "bi-keyboard"
                },
                {
                    "name": "Réseau",
                    "slug": "reseau",
                    "description": "Équipements réseau",
                    "parent": "Informatique",
                    "icon": "bi-router"
                },
                {
                    "name": "Imprimantes",
                    "slug": "imprimantes",
                    "description": "Imprimantes et scanners",
                    "parent": "Informatique",
                    "icon": "bi-printer"
                }
            ],
            "brands": [
                {
                    "name": "Dell",
                    "website": "https://www.dell.com"
                },
                {
                    "name": "HP",
                    "website": "https://www.hp.com"
                },
                {
                    "name": "Lenovo",
                    "website": "https://www.lenovo.com"
                },
                {
                    "name": "Samsung",
                    "website": "https://www.samsung.com"
                },
                {
                    "name": "LG",
                    "website": "https://www.lg.com"
                },
                {
                    "name": "Logitech",
                    "website": "https://www.logitech.com"
                },
                {
                    "name": "Cisco",
                    "website": "https://www.cisco.com"
                },
                {
                    "name": "Canon",
                    "website": "https://www.canon.com"
                }
            ],
            "tags": [
                {
                    "name": "Urgent",
                    "color": "#dc3545",
                    "description": "Équipement nécessitant une attention urgente"
                },
                {
                    "name": "Nouveau",
                    "color": "#28a745",
                    "description": "Équipement récemment acquis"
                },
                {
                    "name": "VIP",
                    "color": "#ffc107",
                    "description": "Équipement pour personnel VIP"
                },
                {
                    "name": "Critique",
                    "color": "#fd7e14",
                    "description": "Équipement critique pour l'activité"
                },
                {
                    "name": "Test",
                    "color": "#6f42c1",
                    "description": "Équipement de test"
                }
            ],
            "assets": [
                {
                    "internal_code": "PC-001",
                    "name": "Dell OptiPlex 7090",
                    "category": "PC",
                    "brand": "Dell",
                    "model": "OptiPlex 7090",
                    "serial_number": "DL7090001",
                    "description": "PC de bureau haute performance pour développement",
                    "purchase_date": "2023-01-15",
                    "purchase_price": 1200.00,
                    "warranty_end": "2026-01-15",
                    "status": "use",
                    "current_location": "Bureau 102",
                    "tags": ["Critique", "Nouveau"],
                    "notes": "Équipement principal du développeur senior"
                },
                {
                    "internal_code": "PC-002",
                    "name": "HP EliteDesk 800",
                    "category": "PC",
                    "brand": "HP",
                    "model": "EliteDesk 800 G9",
                    "serial_number": "HP800002",
                    "description": "PC de bureau pour usage bureautique",
                    "purchase_date": "2023-02-20",
                    "purchase_price": 950.00,
                    "warranty_end": "2026-02-20",
                    "status": "use",
                    "current_location": "Bureau 101",
                    "tags": ["VIP"],
                    "notes": "PC du directeur"
                },
                {
                    "internal_code": "LAP-001",
                    "name": "Lenovo ThinkPad X1",
                    "category": "PC",
                    "brand": "Lenovo",
                    "model": "ThinkPad X1 Carbon",
                    "serial_number": "LN001X1C",
                    "description": "Ordinateur portable professionnel",
                    "purchase_date": "2023-03-10",
                    "purchase_price": 1800.00,
                    "warranty_end": "2026-03-10",
                    "status": "stock",
                    "current_location": "Stock principal",
                    "tags": ["Nouveau"],
                    "notes": "En attente d'attribution"
                },
                {
                    "internal_code": "ECR-001",
                    "name": "Samsung 27\" 4K",
                    "category": "Écrans",
                    "brand": "Samsung",
                    "model": "U28E590D",
                    "serial_number": "SM28E001",
                    "description": "Écran 27 pouces 4K UHD",
                    "purchase_date": "2023-01-20",
                    "purchase_price": 350.00,
                    "warranty_end": "2025-01-20",
                    "status": "use",
                    "current_location": "Bureau 102",
                    "tags": [],
                    "notes": "Écran principal développeur"
                },
                {
                    "internal_code": "ECR-002",
                    "name": "LG UltraWide 34\"",
                    "category": "Écrans",
                    "brand": "LG",
                    "model": "34WN80C-B",
                    "serial_number": "LG34WN002",
                    "description": "Écran ultra-large 34 pouces",
                    "purchase_date": "2023-02-25",
                    "purchase_price": 450.00,
                    "warranty_end": "2025-02-25",
                    "status": "use",
                    "current_location": "Bureau 101",
                    "tags": ["VIP"],
                    "notes": "Écran du directeur"
                },
                {
                    "internal_code": "CLV-001",
                    "name": "Logitech MX Keys",
                    "category": "Périphériques",
                    "brand": "Logitech",
                    "model": "MX Keys",
                    "serial_number": "LG920009",
                    "description": "Clavier sans fil professionnel",
                    "purchase_date": "2023-01-25",
                    "purchase_price": 120.00,
                    "warranty_end": "2025-01-25",
                    "status": "use",
                    "current_location": "Bureau 102",
                    "tags": [],
                    "notes": "Clavier développeur"
                },
                {
                    "internal_code": "SOU-001",
                    "name": "Logitech MX Master 3",
                    "category": "Périphériques",
                    "brand": "Logitech",
                    "model": "MX Master 3",
                    "serial_number": "LG910013",
                    "description": "Souris sans fil ergonomique",
                    "purchase_date": "2023-01-25",
                    "purchase_price": 100.00,
                    "warranty_end": "2025-01-25",
                    "status": "use",
                    "current_location": "Bureau 102",
                    "tags": [],
                    "notes": "Souris développeur"
                },
                {
                    "internal_code": "IMP-001",
                    "name": "Canon PIXMA Pro-200",
                    "category": "Imprimantes",
                    "brand": "Canon",
                    "model": "PIXMA Pro-200",
                    "serial_number": "CN200001",
                    "description": "Imprimante photo professionnelle",
                    "purchase_date": "2023-04-01",
                    "purchase_price": 600.00,
                    "warranty_end": "2025-04-01",
                    "status": "broken",
                    "current_location": "Atelier maintenance",
                    "tags": ["Urgent"],
                    "notes": "Problème d'alimentation papier"
                },
                {
                    "internal_code": "RTR-001",
                    "name": "Cisco Catalyst 2960",
                    "category": "Réseau",
                    "brand": "Cisco",
                    "model": "Catalyst 2960-X",
                    "serial_number": "CS2960001",
                    "description": "Switch réseau 24 ports",
                    "purchase_date": "2022-12-15",
                    "purchase_price": 800.00,
                    "warranty_end": "2025-12-15",
                    "status": "use",
                    "current_location": "Salle de réunion A",
                    "tags": ["Critique"],
                    "notes": "Switch principal salle de réunion"
                },
                {
                    "internal_code": "PC-003",
                    "name": "Dell Precision 5570",
                    "category": "PC",
                    "brand": "Dell",
                    "model": "Precision 5570",
                    "serial_number": "DL5570003",
                    "description": "Station de travail mobile",
                    "purchase_date": "2023-05-10",
                    "purchase_price": 2200.00,
                    "warranty_end": "2026-05-10",
                    "status": "maintenance",
                    "current_location": "Atelier maintenance",
                    "tags": ["Test", "Critique"],
                    "notes": "Maintenance préventive programmée"
                }
            ]
        }

        file_path = 'sample_inventory_data.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Fichier d\'exemple créé : {file_path}')
        )

    def clear_existing_data(self):
        """Supprime toutes les données existantes"""
        self.stdout.write('Suppression des données existantes...')
        
        with transaction.atomic():
            AssetMovement.objects.all().delete()
            Asset.objects.all().delete()
            Tag.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()
            Location.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS('Données existantes supprimées')
        )

    def import_from_file(self, file_path):
        """Importe les données depuis un fichier JSON"""
        if not os.path.exists(file_path):
            raise CommandError(f'Le fichier {file_path} n\'existe pas')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Erreur de format JSON : {e}')

        self.import_data(data)

    def import_default_data(self):
        """Importe les données par défaut"""
        self.stdout.write('Import des données par défaut...')
        # Créer d'abord le fichier d'exemple puis l'importer
        self.create_sample_file()
        self.import_from_file('sample_inventory_data.json')

    def import_data(self, data):
        """Importe les données depuis un dictionnaire"""
        self.stdout.write('Début de l\'import des données...')

        with transaction.atomic():
            # Import des emplacements
            locations_map = self.import_locations(data.get('locations', []))
            
            # Import des catégories
            categories_map = self.import_categories(data.get('categories', []))
            
            # Import des marques
            brands_map = self.import_brands(data.get('brands', []))
            
            # Import des tags
            tags_map = self.import_tags(data.get('tags', []))
            
            # Import des assets
            self.import_assets(
                data.get('assets', []),
                locations_map,
                categories_map,
                brands_map,
                tags_map
            )

        self.stdout.write(
            self.style.SUCCESS('Import terminé avec succès !')
        )

    def import_locations(self, locations_data):
        """Importe les emplacements"""
        self.stdout.write('Import des emplacements...')
        locations_map = {}
        
        # Premier passage : créer les emplacements sans parent
        for loc_data in locations_data:
            if not loc_data.get('parent'):
                location = Location.objects.create(
                    name=loc_data['name'],
                    type=loc_data['type'],
                    description=loc_data.get('description', '')
                )
                locations_map[loc_data['name']] = location
                self.stdout.write(f'  ✓ {location.name}')

        # Deuxième passage : créer les emplacements avec parent
        for loc_data in locations_data:
            if loc_data.get('parent'):
                parent = locations_map.get(loc_data['parent'])
                if parent:
                    location = Location.objects.create(
                        name=loc_data['name'],
                        type=loc_data['type'],
                        description=loc_data.get('description', ''),
                        parent=parent
                    )
                    locations_map[loc_data['name']] = location
                    self.stdout.write(f'  ✓ {location.name} (parent: {parent.name})')

        return locations_map

    def import_categories(self, categories_data):
        """Importe les catégories"""
        self.stdout.write('Import des catégories...')
        categories_map = {}
        
        # Premier passage : créer les catégories sans parent
        for cat_data in categories_data:
            if not cat_data.get('parent'):
                category = Category.objects.create(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    description=cat_data.get('description', ''),
                    icon=cat_data.get('icon', '')
                )
                categories_map[cat_data['name']] = category
                self.stdout.write(f'  ✓ {category.name}')

        # Deuxième passage : créer les catégories avec parent
        for cat_data in categories_data:
            if cat_data.get('parent'):
                parent = categories_map.get(cat_data['parent'])
                if parent:
                    category = Category.objects.create(
                        name=cat_data['name'],
                        slug=cat_data['slug'],
                        description=cat_data.get('description', ''),
                        icon=cat_data.get('icon', ''),
                        parent=parent
                    )
                    categories_map[cat_data['name']] = category
                    self.stdout.write(f'  ✓ {category.name} (parent: {parent.name})')

        return categories_map

    def import_brands(self, brands_data):
        """Importe les marques"""
        self.stdout.write('Import des marques...')
        brands_map = {}
        
        for brand_data in brands_data:
            brand = Brand.objects.create(
                name=brand_data['name'],
                website=brand_data.get('website', '')
            )
            brands_map[brand_data['name']] = brand
            self.stdout.write(f'  ✓ {brand.name}')

        return brands_map

    def import_tags(self, tags_data):
        """Importe les tags"""
        self.stdout.write('Import des étiquettes...')
        tags_map = {}
        
        for tag_data in tags_data:
            tag = Tag.objects.create(
                name=tag_data['name'],
                color=tag_data.get('color', '#007bff'),
                description=tag_data.get('description', '')
            )
            tags_map[tag_data['name']] = tag
            self.stdout.write(f'  ✓ {tag.name}')

        return tags_map

    def import_assets(self, assets_data, locations_map, categories_map, brands_map, tags_map):
        """Importe les assets"""
        self.stdout.write('Import des équipements...')
        
        for asset_data in assets_data:
            # Récupérer les objets liés
            category = categories_map.get(asset_data.get('category'))
            brand = brands_map.get(asset_data.get('brand'))
            location = locations_map.get(asset_data.get('current_location'))
            
            # Convertir les dates
            purchase_date = None
            if asset_data.get('purchase_date'):
                purchase_date = date.fromisoformat(asset_data['purchase_date'])
            
            warranty_end = None
            if asset_data.get('warranty_end'):
                warranty_end = date.fromisoformat(asset_data['warranty_end'])

            # Créer l'asset
            asset = Asset.objects.create(
                internal_code=asset_data.get('internal_code', ''),
                name=asset_data['name'],
                category=category,
                brand=brand,
                model=asset_data.get('model', ''),
                serial_number=asset_data.get('serial_number', ''),
                description=asset_data.get('description', ''),
                purchase_date=purchase_date,
                purchase_price=asset_data.get('purchase_price'),
                warranty_end=warranty_end,
                status=asset_data.get('status', 'stock'),
                current_location=location,
                notes=asset_data.get('notes', '')
            )

            # Ajouter les tags
            tag_names = asset_data.get('tags', [])
            for tag_name in tag_names:
                tag = tags_map.get(tag_name)
                if tag:
                    asset.tags.add(tag)

            self.stdout.write(f'  ✓ {asset.internal_code} - {asset.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Import de {len(assets_data)} équipements terminé')
        )