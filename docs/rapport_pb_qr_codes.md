# Rapport Technique - Problème de Génération de QR Codes

## 1. Analyse du Problème

### 1.1 Description du problème
Les boutons "télécharger", "imprimer" et "regénérer" dans l'interface d'administration ne fonctionnent pas correctement pour la génération des QR codes. Les fichiers générés ne sont pas retrouvés dans le dossier `/media/qr_codes`.

### 1.2 Analyse du workflow actuel

#### Workflow actuel pour la génération de QR codes :
1. Lors de la création d'un asset, les QR codes sont générés automatiquement via la méthode `save()` du modèle `Asset`
2. Les QR codes sont sauvegardés dans le dossier `media/qr_codes/` avec le format `asset_{id}_qrcode.png`
3. Les URLs des QR codes sont accessibles via `asset.qr_code.url`

#### Problèmes identifiés :
1. **Mauvaise gestion des chemins de fichiers** : Le service `barcode_service.py` utilise des chemins relatifs incorrects
2. **Problème de sauvegarde des fichiers** : Les méthodes `save_qrcode_to_asset` et `save_barcode_to_asset` ne sauvegardent pas correctement les fichiers
3. **Incohérence dans les chemins de stockage** : Le code utilise `qrcodes` et `barcodes` comme sous-dossiers, mais les fichiers sont créés dans `media/qr_codes/`

## 2. Analyse du Code

### 2.1 Problème dans `barcode_service.py` (lignes 91-92 et 116-117)
```python
# Ligne 91-92
filename = f'asset_{asset.id}_qrcode.png'
file_path = os.path.join('qrcodes', filename)  # ❌ Problème ici

# Ligne 116-117
filename = f'asset_{asset.id}_barcode.png'
file_path = os.path.join('barcodes', filename)  # ❌ Problème ici
```

### 2.2 Problème dans `models.py` (lignes 20-21)
```python
qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, verbose_name="QR Code")
barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True, verbose_name="Code-barres")
```

## 3. Solutions Proposées

### 3.1 Correction de la gestion des chemins
- Utiliser les chemins de stockage définis dans les modèles (`upload_to`)
- Corriger les méthodes de génération pour utiliser les bonnes conventions

### 3.2 Améliorations de traçabilité
- Ajouter des logs détaillés lors de la génération des QR codes
- Améliorer la gestion des erreurs
- Ajouter des vérifications de chemin de fichier

### 3.3 Sécurité et robustesse
- Vérifier l'existence des dossiers de stockage avant écriture
- Gérer les exceptions lors de la génération des images
- Valider les chemins de fichiers

## 4. Améliorations Proposées

### 4.1 Sécuriser la génération de QR codes
- Ajouter des vérifications de permissions de dossier
- Utiliser des chemins absolus pour éviter les erreurs
- Ajouter des logs d'erreur détaillés

### 4.2 Améliorer la traçabilité
- Ajouter des logs dans les méthodes de génération
- Créer un système de journalisation des actions de génération
- Ajouter des vérifications de succès de sauvegarde

### 4.3 Faciliter la maintenance
- Standardiser les chemins de stockage
- Améliorer la documentation des méthodes
- Ajouter des tests unitaires pour la génération de QR codes

### 4.4 Assurer la compatibilité
- Maintenir la compatibilité avec l'architecture actuelle
- Ne pas modifier les modèles existants
- Respecter les conventions Django

## 5. Actions à Entreprendre

1. **Corriger les chemins dans `barcode_service.py`**
2. **Mettre à jour les méthodes de génération pour utiliser les chemins corrects**
3. **Ajouter des vérifications de chemin et de permissions**
4. **Ajouter des logs pour améliorer la traçabilité**
5. **Vérifier que les dossiers de stockage existent**