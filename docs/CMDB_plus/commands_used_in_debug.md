# Commandes utilisées dans le débogage - Rapport technique

## 1. Commande `find` pour localiser les fichiers contenant "QRCode"

### Commande utilisée :
```bash
find backend -name "*.py" -exec grep -l "QRCode" {} \;
```

### Explication :
Cette commande permet de trouver tous les fichiers Python dans le répertoire `backend` qui contiennent le mot "QRCode". Elle utilise :
- `find backend` : recherche dans le répertoire backend
- `-name "*.py"` : filtre uniquement les fichiers avec extension .py
- `-exec grep -l "QRCode" {} \;` : pour chaque fichier trouvé, exécute grep pour vérifier si le mot QRCode est présent et affiche le nom du fichier

### Résultat :
Retourne les fichiers contenant QRCode :
- backend/printer/api/viewsets.py
- backend/inventory_project/tasks.py
- backend/urls.py
- backend/models.py
- backend/views.py
- backend/scanner/admin.py
- backend/scanner/signals.py
- backend/scanner/models.py
- backend/scanner/views.py
- backend/scanner/migrations/0001_initial.py
- backend/scanner/utils.py
- backend/inventory/admin.py
- backend/inventory/views.py
- backend/inventory/management/commands/generate_fake_data copy.py

## 2. Commande `grep` pour rechercher les signaux post_save

### Commande utilisée :
```bash
grep -r "post_save" backend/ --include="*.py" | head -10
```

### Explication :
Cette commande recherche récursivement dans le répertoire `backend` tous les fichiers Python contenant "post_save" et limite les résultats à 10 lignes.

### Résultat :
- backend/scanner/signals.py:from django.db.models.signals import post_save
- backend/scanner/signals.py:@receiver(post_save, sender=QRCode)
- backend/scanner/models.py:    Généré automatiquement à la création d'Asset (signal post_save).

## 3. Commande `grep` pour localiser les fichiers avec "Asset" et "post_save"

### Commande utilisée :
```bash
find backend -name "*.py" -exec grep -l "Asset" {} \; | xargs grep -l "post_save"
```

### Explication :
Cette commande :
1. Trouve tous les fichiers Python contenant "Asset"
2. Puis recherche dans ces fichiers ceux qui contiennent "post_save"

Cela permet de localiser les fichiers qui gèrent les signaux liés aux assets.

## 4. Commande `grep` pour rechercher les routes dans les URLs

### Commande utilisée :
```bash
grep -r "print_label" backend/ --include="*.py"
```

### Explication :
Recherche dans tous les fichiers Python du backend les occurrences de "print_label" pour identifier les routes liées à l'impression d'étiquettes.

## 5. Commande `grep` pour localiser les modèles

### Commande utilisée :
```bash
grep -r "class Asset" backend/ --include="*.py"
```

### Explication :
Recherche la définition de la classe Asset dans tous les fichiers Python du backend pour comprendre la structure du modèle.

## 6. Commande `read_file` pour inspecter les fichiers

### Commande utilisée :
```bash
read_file backend/scanner/models.py
```

### Explication :
Permet de lire le contenu complet du fichier models.py du module scanner pour comprendre la structure du modèle QRCode.

## 7. Commande `read_file` pour inspecter les migrations

### Commande utilisée :
```bash
read_file backend/scanner/migrations/0001_initial.py
```

### Explication :
Permet d'inspecter les migrations pour comprendre comment les modèles sont créés et les relations entre les tables.

## 8. Commande `search_files` pour rechercher dans les fichiers

### Commande utilisée :
```bash
search_files backend/cmdb_admin "*.py" "def generate_label_pdf"
```

### Explication :
Recherche dans le répertoire cmdb_admin tous les fichiers Python contenant la fonction generate_label_pdf.

## 9. Commande `search_files` pour rechercher les routes

### Commande utilisée :
```bash
search_files backend/cmdb_admin "*.py" "print_label"
```

### Explication :
Recherche dans le répertoire cmdb_admin tous les fichiers Python contenant "print_label" pour identifier les routes liées à l'impression.

## 10. Commande `search_files` pour localiser les modèles

### Commande utilisée :
```bash
search_files backend/inventory "*.py" "class Asset"
```

### Explication :
Recherche la définition de la classe Asset dans le module inventory pour comprendre ses attributs et relations.