

# Gestion de la rétractabilité par code-barres et QR code pour votre application CMDB

> Created : 16 mars 2026
>
> Author : AS 

J'ai implémenté avec succès la fonctionnalité complète de gestion de la rétractabilité par code-barres et QR code pour votre application CMDB. Voici un résumé des réalisations :

## Backend Django/DRF

1. **Modèles** (`backend/models.py`) :
   - `Asset` avec champs : UUID, nom, code unique, localisation, QR code, code-barres, dates
   - `AssetScan` avec champs : asset, date/heure, scanné par, lieu, source, notes
   - Génération automatique des QR codes et code-barres via les méthodes `save()`

2. **Serializers** (`backend/serializers.py`) :
   - `AssetSerializer` avec URLs des images et compteur de scans
   - `AssetScanSerializer` pour les enregistrements de scans
   - `AssetCreateSerializer` pour la création avec génération automatique de code
   - `ScanCreateSerializer` pour l'enregistrement des scans via API
   - `AssetHistorySerializer` pour l'historique de rétractabilité

3. **ViewSets et vues** (`backend/views.py`) :
   - `AssetViewSet` avec actions CRUD, historique, impression d'étiquette
   - `AssetScanViewSet` pour la gestion des scans
   - `ScanAPIView` pour l'enregistrement des scans via code
   - Vues spécifiques pour les images QR code et code-barres

4. **Routes API** (`backend/urls.py`) :
   - `/api/assets/` - CRUD des assets
   - `/api/assets/<id>/history/` - Historique des scans
   - `/api/assets/<id>/print-label/` - Impression d'étiquette
   - `/api/scans/` - Enregistrement de scans
   - `/api/assets/by-code/<code>/` - Recherche par code

5. **Service de génération** (`backend/barcode_service.py`) :
   - Fonctions pour générer QR codes et code-barres
   - Génération de PDF d'étiquettes avec ReportLab
   - Support d'impression thermique (ESC/POS, ZPL, EPL)
   - Gestion des images et URLs

## Frontend Vue.js/Axios/Bootstrap

1. **Service API** (`frontend/src/api/assetScanApi.js`) :
   - Client Axios configuré pour tous les endpoints
   - Méthodes pour assets, scans, historique, impression

2. **Composants Vue.js** :
   - `AssetScanComponent.vue` : Simulation de scan avec capture automatique des entrées scanner
   - `AssetHistoryComponent.vue` : Historique de rétractabilité avec statistiques et visualisation
   - Intégration Bootstrap complète avec tables, badges, modales

3. **Fonctionnalités frontend** :
   - Capture automatique des codes via scanners USB (émulation clavier)
   - Affichage des images QR code et code-barres
   - Tableaux paginés avec filtres
   - Notifications toast pour feedback utilisateur
   - Statistiques et visualisation des données de scan

## Architecture et intégration

- **Traçabilité complète** : Chaque scan enregistre date, heure, agent, localisation et source
- **Rétractabilité** : Historique chronologique permettant de retracer le parcours de chaque asset
- **Support matériel** : Douchettes USB, smartphones, scanners Bluetooth, imprimantes thermiques
- **Génération d'images** : QR codes (python-qrcode) et code-barres (python-barcode)
- **Impression** : PDF étiquette et commandes directes vers imprimantes thermiques

L'implémentation suit les meilleures pratiques Django/DRF et Vue.js 3 (Composition API), avec une architecture modulaire et extensible. Tous les endpoints API sont documentés et prêts à l'utilisation, et les composants frontend sont entièrement fonctionnels avec gestion d'erreur et états de chargement.

-----

J'ai mis à jour le formulaire backend de Django Admin pour l'asset avec les améliorations suivantes :

1. **Admin enrichi** (`backend/inventory/admin.py`) :
   - Ajout de champs en lecture seule (`internal_code`, `created_at`, `updated_at`)
   - Organisation des champs en sections (`fieldsets`) pour une meilleure lisibilité
   - Ajout d'une prévisualisation du QR code et d'un bouton d'impression dans l'interface d'administration
   - Intégration d'un template personnalisé (`change_form_template`)

2. **Template personnalisé** (`backend/templates/admin/inventory/asset/change_form.html`) :
   - Extension du template admin standard avec une section dédiée au QR code et à l'impression
   - Affichage conditionnel du QR code existant ou d'un lien pour en générer un nouveau
   - Bouton pour imprimer une étiquette PDF avec les informations de l'asset
   - Styles CSS intégrés pour une intégration harmonieuse

3. **Vues de génération QR code et impression** (`backend/inventory/views.py`) :
   - `generate_qrcode_view` : génère un QR code pour l'asset et le sauvegarde dans le modèle `QRCode`
   - `print_label_view` : produit un PDF d'étiquette prêt à imprimer avec les données de l'asset
   - Protection par décorateur `@staff_member_required` pour un accès réservé aux administrateurs

4. **URLs dédiées** (`backend/inventory_project/urls.py`) :
   - Routes `admin_generate_qrcode` et `admin_print_label` accessibles sous `/django-admin/inventory/asset/<id>/...`
   - Intégration transparente avec l'interface d'administration Django

5. **Adaptation aux modifications récentes du modèle** :
   - Prise en compte des nouveaux champs `internal_code` et des choix étendus de statut/condition
   - Utilisation de la relation `OneToOne` avec le modèle `QRCode` du module `scanner`

Le formulaire admin est maintenant "version pro" : structuré, fonctionnel, avec intégration du QR code et de l'impression. Les dépendances manquantes (`python-barcode`, `qrcode[pil]`, `reportlab`) ont été installées. Le serveur Django redémarre correctement et les nouvelles fonctionnalités sont opérationnelles.