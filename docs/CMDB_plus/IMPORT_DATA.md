# Import de Données - CMDB Inventory

## Commande Django d'Import de Données

La commande `import_sample_data` permet d'importer facilement des données d'exemple ou réelles dans votre application CMDB.

## Utilisation

### 1. Créer un fichier JSON d'exemple

```bash
python manage.py import_sample_data --create-sample
```

Cette commande crée un fichier `sample_inventory_data.json` avec des données d'exemple complètes incluant :
- 6 emplacements (bâtiments, bureaux, stock, atelier)
- 6 catégories (PC, écrans, périphériques, réseau, imprimantes)
- 8 marques (Dell, HP, Lenovo, Samsung, LG, Logitech, Cisco, Canon)
- 5 étiquettes (Urgent, Nouveau, VIP, Critique, Test)
- 11 équipements variés avec toutes leurs informations

### 2. Importer les données d'exemple

```bash
# Import des données par défaut
python manage.py import_sample_data

# Ou import depuis un fichier spécifique
python manage.py import_sample_data --file sample_inventory_data.json
```

### 3. Nettoyer et réimporter

```bash
# Supprimer toutes les données existantes et importer
python manage.py import_sample_data --clear
```

## Format du Fichier JSON

Le fichier JSON doit respecter la structure suivante :

```json
{
  "locations": [
    {
      "name": "Bureau 101",
      "type": "bureau",
      "description": "Bureau du directeur",
      "parent": "Bâtiment Principal"
    }
  ],
  "categories": [
    {
      "name": "PC",
      "slug": "pc",
      "description": "Ordinateurs de bureau et portables",
      "parent": "Informatique",
      "icon": "bi-pc-display"
    }
  ],
  "brands": [
    {
      "name": "Dell",
      "website": "https://www.dell.com"
    }
  ],
  "tags": [
    {
      "name": "Urgent",
      "color": "#dc3545",
      "description": "Équipement nécessitant une attention urgente"
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
      "description": "PC de bureau haute performance",
      "purchase_date": "2023-01-15",
      "purchase_price": 1200.00,
      "warranty_end": "2026-01-15",
      "status": "use",
      "current_location": "Bureau 102",
      "tags": ["Critique", "Nouveau"],
      "notes": "Équipement principal du développeur"
    }
  ]
}
```

## Champs Obligatoires et Optionnels

### Locations
- **Obligatoires** : `name`, `type`
- **Optionnels** : `description`, `parent`
- **Types valides** : `bureau`, `salle`, `entrepot`, `placard`, `externe`, `vehicule`

### Categories
- **Obligatoires** : `name`, `slug`
- **Optionnels** : `description`, `parent`, `icon`

### Brands
- **Obligatoires** : `name`
- **Optionnels** : `website`

### Tags
- **Obligatoires** : `name`
- **Optionnels** : `color` (défaut: #007bff), `description`

### Assets
- **Obligatoires** : `name`
- **Optionnels** : `internal_code`, `category`, `brand`, `model`, `serial_number`, `description`, `purchase_date`, `purchase_price`, `warranty_end`, `status`, `current_location`, `tags`, `notes`
- **Statuts valides** : `stock`, `use`, `broken`, `maintenance`, `sold`, `disposed`, `lost`

## Exemples d'Utilisation

### Import initial avec données d'exemple
```bash
# 1. Créer le fichier d'exemple
python manage.py import_sample_data --create-sample

# 2. Importer les données
python manage.py import_sample_data --file sample_inventory_data.json
```

### Mise à jour avec nouvelles données
```bash
# Créer votre fichier custom_data.json puis :
python manage.py import_sample_data --file custom_data.json
```

### Reset complet
```bash
# Attention : supprime TOUTES les données !
python manage.py import_sample_data --clear --file sample_inventory_data.json
```

## Gestion des Erreurs

La commande gère automatiquement :
- **Relations hiérarchiques** : Les parents sont créés avant les enfants
- **Références** : Les catégories, marques, emplacements et tags sont liés automatiquement
- **Transactions** : Tout l'import est dans une transaction (rollback en cas d'erreur)
- **Validation** : Les données sont validées selon les modèles Django

## Conseils

1. **Testez d'abord** : Utilisez `--create-sample` pour voir le format attendu
2. **Sauvegardez** : Faites une sauvegarde avant `--clear`
3. **Vérifiez les relations** : Assurez-vous que les noms des parents existent
4. **Dates au format ISO** : Utilisez le format `YYYY-MM-DD` pour les dates
5. **Codes uniques** : Les `internal_code` doivent être uniques

## Données d'Exemple Incluses

Le fichier d'exemple contient :
- **PC** : Dell OptiPlex, HP EliteDesk, Lenovo ThinkPad, Dell Precision
- **Écrans** : Samsung 4K, LG UltraWide
- **Périphériques** : Clavier et souris Logitech
- **Réseau** : Switch Cisco
- **Imprimante** : Canon PIXMA (en panne pour test)

Tous avec des informations réalistes : dates d'achat, garanties, emplacements, etc.

## Intégration Docker

Dans l'environnement Docker :
```bash
# Entrer dans le container backend
docker-compose exec backend bash

# Puis exécuter la commande
python manage.py import_sample_data --create-sample
python manage.py import_sample_data