# Algorithme du Processus de Scan QR Code

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