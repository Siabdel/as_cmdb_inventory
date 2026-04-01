# Algorithme du Processus de Scan QR Code ou Code a barre

> created le 25 mars 2026 
>
> author : AS 





## 1. Initialisation du Scanner

### 1.1. Montage du composant
- Le composant Vue.js est monté dans le DOM
- Les données initiales sont définies :
  - `cameraActive: false` (caméra désactivée)
  - `scanResult: null` (pas de résultat de scan)
  - `locations: []` (liste des emplacements vide)
  - `scanHistory: []` (historique des scans vide)
  - `scannerType: 'webcam'` (type de scanner par défaut)

### 1.2. Initialisation des services
- Initialisation de ZXing BrowserMultiFormatReader (pour les scanners web)
- Chargement de l'historique des scans depuis localStorage
- Récupération de la liste des emplacements via API
- Détection automatique des scanners USB connectés

## 2. Démarrage du Scanner

### 2.1. Détection du type de scanner
- Vérifie la présence de scanners USB connectés
- Si des scanners USB sont détectés, utilise le mode "scanner USB"
- Sinon, utilise le mode "caméra web" par défaut

### 2.2. Initialisation du scanner
- Pour les scanners USB :
  - Attend les entrées clavier des scanners
  - Configure un écouteur d'événements sur le champ de saisie
- Pour les caméras web :
  - Liste les dispositifs vidéo disponibles
  - Sélectionne la caméra arrière si disponible
  - Démarre le décodeur de QR code à partir de la caméra

### 2.3. Détection des QR Codes
- Pour les scanners USB :
  - Attend les entrées clavier (les scanners émulent le clavier)
  - Lorsqu'une entrée est reçue :
    - Extrait le texte du QR code
    - Appelle `handleScanResult()` avec le texte extrait
- Pour les caméras web :
  - Le décodeur surveille en continu les images de la caméra
  - Lorsqu'un QR code est détecté :
    - Extrait le texte du QR code
    - Appelle `handleScanResult()` avec le texte extrait

## 3. Traitement du Résultat du Scan

### 3.1. Extraction de l'UUID
- Analyse le texte du QR code pour extraire l'UUID
- Supporte les formats :
  - `qr_asset_<id>_<uuid>`
  - `<uuid>` direct
  - Code-barres standards (format spécifique Honeywell)

### 3.2. Récupération des Données de l'Asset
- Appel API vers `/scanner/scan/{uuid}/`
- Récupère les données de l'asset correspondant à l'UUID
- Stocke les données dans `scanResult`

### 3.3. Mise à Jour de l'Interface
- Affiche les détails de l'asset dans l'interface
- Ajoute l'entrée à l'historique des scans
- Joue un feedback sonore

### 3.4. Gestion des scanners spécifiques
- Pour les scanners Honeywell USB :
  - Détection automatique du type de scanner
  - Configuration spécifique pour les scanners Honeywell
  - Gestion des codes spécifiques (ex: préfixes, suffixes)

## 4. Gestion des Actions

### 4.1. Création de Ticket
- Lien vers `/admin/tickets/new/?asset={asset_id}`

### 4.2. Voir la Fiche de l'Asset
- Lien vers `/admin/assets/list/{asset_id}/`

### 4.3. Déplacement de l'Asset
- Ouvre le modal de déplacement
- Permet de déplacer l'asset vers un nouvel emplacement

### 4.4. Gestion des scanners spécifiques
- Pour les scanners Honeywell :
  - Support des codes spécifiques (préfixes/suffixes)
  - Configuration de l'entrée clavier
  - Gestion des erreurs spécifiques aux scanners

## 5. Cycle de Vie du Composant

### 5.1. Montage
- Initialisation des services
- Chargement des données initiales
- Détection automatique des scanners USB
- Démarrage du scanner (selon le type détecté)

### 5.2. Démontage
- Arrêt du scanner
- Nettoyage des ressources
- Désactivation des écouteurs d'événements

## 6. Gestion des Erreurs

### 6.1. Erreurs de Scanner
- Gestion des scanners USB non détectés
- Gestion des permissions d'accès aux périphériques
- Gestion des scanners déconnectés

### 6.2. Erreurs de Scan
- Gestion des QR codes non reconnus
- Gestion des codes-barres non valides
- Gestion des erreurs réseau

### 6.3. Erreurs de Données
- Gestion des réponses API vides
- Gestion des assets non trouvés
- Gestion des codes spécifiques Honeywell incorrects

----





# Analyse du workflow du scanner

Après avoir examiné le code, j'ai identifié que le module scanner est actuellement conçu uniquement pour gérer les QR codes. Voici les éléments clés :

1. **Structure du module scanner** : Le module scanner utilise uniquement des QR codes (modèle QRCode) et ne gère pas les codes à barres.

2. **Interface admin** : La page d'administration du scanner (`backend/templates/admin/scanner/index.html`) affiche clairement "Scanner QR Code" et utilise des composants spécifiques à la détection de QR codes.

3. **Frontend** : Le composant Vue.js `QRScanner.vue` utilise la bibliothèque `html5-qrcode` qui est spécifiquement conçue pour la détection de QR codes.

4. **Backend** : Les vues du scanner (`scanner/views.py`) sont configurées pour traiter uniquement les QR codes via leur UUID token.

## Problème identifié

Le module ne supporte pas les codes à barres, bien que la demande indique qu'il devrait le faire. Le problème vient du fait que :
- Le frontend est configuré pour scanner uniquement des QR codes
- Le backend ne gère que les QR codes
- Le nom de la page et les éléments de l'interface indiquent clairement "QR Code"

## Solution proposée

Pour ajouter le support des codes à barres, il faudrait :
1. Modifier le frontend pour permettre le scan de codes à barres
2. Mettre à jour le backend pour gérer les codes à barres
3. Adapter l'interface admin pour indiquer le support des deux types de codes

Je vais maintenant modifier le frontend pour ajouter le support des codes à barres.

----



J'ai analysé le workflow du module scanner et identifié que le système ne supportait actuellement que les QR codes. Voici les modifications effectuées pour ajouter le support des codes à barres :

1. **Frontend (Vue.js)** :
   - Mis à jour le template pour indiquer clairement le support des QR codes et codes à barres
   - Ajout de la configuration pour activer le support des différents formats de codes à barres dans la bibliothèque html5-qrcode
   - Amélioration de la gestion des différents types de codes scannés
   - Ajout d'une fonction d'extraction pour les codes à barres (numéros de série, codes internes)

2. **Backend (Django)** :
   - Modification de la vue `resolve_qr` pour permettre le traitement des codes à barres en plus des QR codes
   - Ajout de la logique pour gérer les codes à barres en recherchant l'asset par son numéro de série
   - Création automatique d'un QR code pour les assets scannés via code à barres

3. **Interface Admin** :
   - Mise à jour du texte pour indiquer clairement le support des deux types de codes

Ces modifications permettent maintenant au module scanner de traiter à la fois les QR codes et les codes à barres, répondant ainsi à la demande initiale. Le système est maintenant plus flexible et peut gérer les deux types de codes d'identification utilisés dans l'inventaire.

---

## Résumé des modifications apportées

J'ai effectué les modifications nécessaires pour permettre au module scanner de gérer à la fois les QR codes et les codes à barres. Voici les principales modifications :

1. **Frontend (Vue.js)** :
   - Mis à jour les templates pour indiquer clairement le support des QR codes et codes à barres
   - Ajout de la configuration pour activer le support des différents formats de codes à barres dans la bibliothèque html5-qrcode
   - Amélioration de la gestion des différents types de codes scannés
   - Ajout d'une fonction d'extraction pour les codes à barres (numéros de série, codes internes)

2. **Backend (Django)** :
   - Modification de la vue `resolve_qr` pour permettre le traitement des codes à barres en plus des QR codes
   - Ajout de la logique pour gérer les codes à barres en recherchant l'asset par son numéro de série ou code interne
   - Création automatique d'un QR code pour les assets scannés via code à barres

3. **Interface Admin** :
   - Mise à jour des textes pour indiquer clairement le support des deux types de codes
   - Adaptation du JavaScript de l'interface admin pour gérer les codes à barres

Les codes à barres sont maintenant correctement pris en charge dans l'interface admin à la page "http://localhost:8000/admin/scanner/". Lorsqu'un code à barres est scanné, le système recherche l'asset correspondant par son numéro de série ou code interne, puis affiche les informations de l'équipement comme il le faisait pour les QR codes.

Ces modifications permettent au module scanner de traiter à la fois les QR codes et les codes à barres, répondant ainsi à la demande initiale. Le système est maintenant plus flexible et peut gérer les deux types de codes d'identification utilisés dans l'inventaire.



```python
def public_scan_result(request, uuid):
    """Page publique de résultat de scan - sans authentification"""
    # Résoudre l'UUID vers l'asset
    asset = get_object_or_404(Asset, qr_uuid=uuid)
    
    # Enregistrer le scan (optionnel, pour stats)
    # ScanLog.objects.create(asset=asset, scanned_by='public', scanned_at=timezone.now())
    
    # Tickets ouverts liés
    open_tickets = Ticket.objects.filter(asset=asset, status__in=['open', 'assigned', 'in_progress'])
    
    context = {
        'asset': asset,
        'open_tickets': open_tickets,
        'scan_date': timezone.now()
    }
    return render(request, 'public/scan_result.html', context)


```

J'ai analysé comment les résultats du scan sont affichés dans la page publique. Voici la réponse détaillée :

La fonction `public_scan_result` est bien définie dans le fichier views.py et est utilisée correctement dans les URLs. Voici comment cela fonctionne :

1. **Page publique pour les résultats de scan** :
   - La page publique est accessible via l'URL `/scanner/scan/<uuid>/` 
   - Elle utilise la fonction `public_scan_result` définie dans `views.py`
   - Elle affiche les détails de l'asset scanné

2. **Fonctionnement pour les deux types de codes** :
   - Pour les QR codes : L'UUID est directement celui du QR code
   - Pour les codes à barres : Le système trouve l'asset correspondant, crée un QR code pour lui si nécessaire, puis redirige vers la page publique avec l'UUID du QR code

3. **Structure de la page publique** :
   - Le fichier `backend/templates/public/scan_result.html` contient le template
   - Il affiche les informations de l'asset (nom, numéro de série, catégorie, etc.)
   - Il affiche le QR code généré pour cet asset
   - Il montre les tickets ouverts liés à l'asset

La page publique est donc bien configurée et fonctionne pour les deux types de codes. Lorsqu'un code à barres est scanné :
1. Le backend trouve l'asset correspondant par son numéro de série ou code interne
2. Il crée un QR code pour cet asset s'il n'existe pas
3. Il redirige vers l'URL publique avec l'UUID du QR code
4. La page publique affiche les détails de l'asset avec son QR code

Les modifications apportées permettent donc de gérer à la fois les QR codes et les codes à barres de manière transparente, avec l'affichage des résultats dans la page publique comme prévu.