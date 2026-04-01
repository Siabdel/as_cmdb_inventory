# 📋 Manuel d'Utilisation — Écran d'Étiquetage QR Code

**URL:** `http://localhost:8000/admin/scanner/print/`  
**Version:** 1.0 — Mars 2026  
**Public:** Techniciens, Gestionnaires IT

---

## 1. 🎯 Objectif de l'Écran

Cet écran permet de **générer et imprimer des étiquettes QR Code** pour identifier physiquement vos assets (laptops, serveurs, équipements IT).

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ÉTIQUETAGE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Sélectionner assets → 2. Générer PDF → 3. Imprimer         │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │  Assets  │───→│   PDF    │───→│Imprimante│                 │
│  │  (10x)   │    │Étiquettes│    │  MUNBYN  │                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│                                                                 │
│  Résultat: 10 étiquettes QR Code collées sur les laptops       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 📸 Capture d'Écran de l'Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  🖨️ Impression Étiquettes QR Code                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Assets Sélectionnés: 10                                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  CONFIGURATION                                          │   │
│  │                                                         │   │
│  │  Template: [Standard Laptop 50x30mm ▼]                 │   │
│  │                                                         │   │
│  │  Imprimante: [MUNBYN RW403B - Atelier ▼]               │   │
│  │                                                         │   │
│  │  Copies: [1 ▼]                                         │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  APERÇU DES ASSETS                                      │   │
│  │                                                         │   │
│  │  ☑ HP Elitebook G4 - S/N: 200932322210011              │   │
│  │  ☑ HP Elitebook G4 - S/N: 200932322210012              │   │
│  │  ☑ HP Elitebook G4 - S/N: 200932322210013              │   │
│  │  ... (7 autres)                                         │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [🧪 Tester Imprimante]  [🖨️ Générer & Imprimer]  [📥 PDF]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 📖 Procédure Pas à Pas

### Étape 1 — Sélectionner les Assets

**Option A: Depuis la liste des assets**

```
1. Naviguer vers: /admin/assets/
2. Cocher les assets à étiqueter (checkbox)
   ☑ HP Elitebook #210
   ☑ HP Elitebook #211
   ☑ HP Elitebook #212
   ...
3. Menu Actions → "Imprimer Étiquettes"
4. Redirection automatique vers /admin/scanner/print/?assets=210,211,212
```

**Option B: Directement sur la page Print**

```
1. Naviguer vers: /admin/scanner/print/
2. Cliquer "Sélectionner Assets"
3. Rechercher par:
   - Nom (ex: "HP Elitebook")
   - Numéro de série
   - Catégorie (ex: "Laptop")
   - Statut (ex: "En Stock")
4. Cocher les assets désirés
5. Cliquer "Valider Sélection"
```

---

### Étape 2 — Configurer l'Impression

| Champ          | Options                            | Recommandation              |
| -------------- | ---------------------------------- | --------------------------- |
| **Template**   | 30x20mm, 50x30mm, 70x40mm, 80x50mm | **50x30mm** pour laptops    |
| **Imprimante** | USB, Bluetooth, WiFi               | Selon votre configuration   |
| **Copies**     | 1-10                               | **1** (sauf besoin spécial) |

**Exemple de Configuration:**

```
┌────────────────────────────────────────┐
│  Template: Standard Laptop 50x30mm    │
│  ─────────────────────────────────    │
│  • Format: 50mm x 30mm                │
│  • QR Code: 20mm x 20mm               │
│  • Texte: Nom, S/N, Catégorie         │
│  • Barcode: Serial Number (Code 128)  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Imprimante: MUNBYN RW403B            │
│  ─────────────────────────────────    │
│  • Type: Bluetooth                    │
│  • IP/MAC: 00:11:22:33:44:55          │
│  • DPI: 203                           │
│  • Papier: 50mm x 30mm                │
└────────────────────────────────────────┘
```

---

### Étape 3 — Tester l'Imprimante (Optionnel)

```
1. Cliquer bouton: [🧪 Tester Imprimante]
2. PDF test généré automatiquement
3. Vérifier dans l'imprimante:
   ✓ Qualité d'impression
   ✓ Alignement du QR Code
   ✓ Lisibilité du texte
4. Si OK → Passer à l'étape 4
5. Si NOK → Ajuster settings imprimante
```

**Paramètres Imprimante MUNBYN:**

| Paramètre      | Valeur        | Comment                        |
| -------------- | ------------- | ------------------------------ |
| **Density**    | 10-12         | Plus foncé = meilleure lecture |
| **Speed**      | 3 (Normal)    | Trop rapide = qualité réduite  |
| **Paper Type** | Thermal Label | IMPORTANT                      |
| **Tear Bar**   | Activé        | Pour découper étiquettes       |

---

### Étape 4 — Générer et Imprimer

```
1. Cliquer bouton: [🖨️ Générer & Imprimer]
2. Progression affichée:
   ⏳ Génération PDF en cours...
   ✓ 10 assets traités
   ✓ PDF prêt (245 KB)
3. Deux options:
   
   Option A: Impression directe
   └── Dialogue impression navigateur s'ouvre
   └── Sélectionner imprimante (MUNBYN RW403B)
   └── Paramètres:
       • Taille: Réelle (100%)
       • Marges: Aucune
       • Noir & Blanc: Oui
   └── Cliquer "Imprimer"
   
   Option B: Télécharger PDF
   └── Fichier: labels_20260326_143022.pdf
   └── Ouvrir avec lecteur PDF
   └── Imprimer ultérieurement
```

---

### Étape 5 — Coller les Étiquettes

```
1. Découper les étiquettes (si nécessaire)
2. Pour CHAQUE laptop:
   
   a. Scanner l'étiquette (vérification)
      └── /admin/scanner/
      └── Vérifier fiche asset correcte
   
   b. Nettoyer surface (alcool isopropylique)
   
   c. Coller étiquette:
      ─────────────────
      Emplacement recommandé:
      • Dessous du laptop (près du S/N constructeur)
      • OU sur le bord arrière (visible quand fermé)
      • ÉVITER: Zones de chaleur, charnières
      
   d. Appuyer fermement 5 secondes
   
   e. Vérifier dans CMDB:
      └── Asset #210 → Statut: "Étiqueté"
      └── PrintLog enregistré
```

**Positionnement Recommandé:**

```
┌─────────────────────────────────────────┐
│           DESSUS LAPTOP (FERMÉ)         │
│                                         │
│    ┌─────────────────────────────┐     │
│    │                             │     │
│    │         [ÉCRAN]             │     │
│    │                             │     │
│    └─────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│          DESSOUS LAPTOP (RETOUR)        │
│                                         │
│    ┌─────────────────────────────┐     │
│    │  [ÉTIQUETTE QR]  [S/N MFG]  │     │
│    │  █████████████   HP123456   │     │
│    │  █████████████              │     │
│    └─────────────────────────────┘     │
│                                         │
│    ← Zone recommandée pour étiquette   │
└─────────────────────────────────────────┘
```

---

## 4. 📊 Exemple d'Étiquette Générée

```
┌─────────────────────────────────────────────┐
│  50mm × 30mm                                │
│  ┌───────────┐                             │
│  │           │  HP Elitebook G4            │
│  │   █████   │  S/N: 200932322210011      │
│  │   █████   │  ID: CI-20260001-001        │
│  │   █████   │  Cat: Laptop                │
│  │   █████   │  Loc: Paris - Atelier       │
│  │           │  Statut: EN STOCK           │
│  └───────────┘                             │
│  ||| ||| ||| ||| ||| ||| ||| ||| |||      │
│  200932322210011  (Code 128 Barcode)       │
└─────────────────────────────────────────────┘

Contenu QR Code: qr_asset_210_abc123-def456
Format: PNG 300 DPI
Error Correction: M (15% récupération)
```

---

## 5. 🔧 Dépannage

| Problème                    | Cause                 | Solution                             |
| --------------------------- | --------------------- | ------------------------------------ |
| **QR Code illisible**       | Density trop faible   | Augmenter à 12-14                    |
| **Étiquette mal alignée**   | Template incorrect    | Vérifier format (50x30mm)            |
| **Imprimante non détectée** | Bluetooth non appairé | `bluetoothctl` → pair/connect        |
| **PDF trop grand**          | Scale navigateur      | Mettre à 100% (pas "Ajuster")        |
| **QR Code manquant**        | Asset sans QRCode     | Bouton "Générer QR" dans fiche asset |
| **Impression blanche**      | Papier inversé        | Vérifier sens du rouleau thermique   |

---

## 6. 📋 Checklist de Validation

Après étiquetage, vérifier:

```
☐ 10 assets sélectionnés
☐ 10 étiquettes imprimées
☐ QR Code lisible (test scan)
☐ Texte lisible (nom, S/N)
☐ Étiquettes collées correctement
☐ PrintLog enregistré (audit)
☐ Statut asset mis à jour
☐ Rapport généré (optionnel)
```

---

## 7. 📊 Audit & Traçabilité

Chaque impression est enregistrée dans `PrintLog`:

```python
# Exemple d'entrée PrintLog
{
    "id": 45,
    "job": 12,
    "asset": 210,
    "printed_by": "jean.technicien",
    "printer_name": "MUNBYN RW403B - Atelier",
    "template_name": "Standard Laptop 50x30mm",
    "printed_at": "2026-03-26 14:30:22",
    "ip_address": "192.168.1.50",
    "user_agent": "Mozilla/5.0..."
}
```

**Consultation:** `/admin/scanner/logs/`

---

## 8. ⚡ Raccourcis & Astuces

| Action                | Raccourci                            |
| --------------------- | ------------------------------------ |
| **Sélection rapide**  | Ctrl+A (tous)                        |
| **Recherche asset**   | Ctrl+F dans liste                    |
| **Test imprimante**   | Bouton 🧪 avant batch                 |
| **Export PDF**        | Toujours garder copie                |
| **Scan vérification** | Scanner 1ère étiquette avant collage |

---

## 9. 📞 Support & Questions Fréquentes

### Q: "Combien d'étiquettes par page PDF ?"

**R:** 1 étiquette = 1 page PDF. Pour 10 assets → 10 pages PDF. L'imprimante thermique découpe automatiquement.

### Q: "Peut-on imprimer sans sélectionner d'assets ?"

**R:** Non. Minimum 1 asset requis. Maximum recommandé: 100 assets par batch (performance).

### Q: "Le QR Code ne scanne pas ?"

**R:** Vérifier:
1. Density imprimante (10-12)
2. Taille QR (min 20mm x 20mm)
3. Surface de collage (plane, propre)
4. Scanner (distance 10-20cm)

### Q: "Comment annuler un PrintJob ?"

**R:** `/admin/scanner/jobs/` → Sélectionner job → Action "Annuler". Seul statut "pending" annulable.

---

## ✅ Résumé — Workflow Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW ÉTIQUETAGE COMPLET                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. /admin/assets/ → Cocher 10 laptops                         │
│         │                                                       │
│         ▼                                                       │
│  2. Action: "Imprimer Étiquettes"                              │
│         │                                                       │
│         ▼                                                       │
│  3. /admin/scanner/print/ → Configurer                         │
│         │   • Template: 50x30mm                                │
│         │   • Imprimante: MUNBYN                               │
│         │   • Copies: 1                                        │
│         │                                                       │
│         ▼                                                       │
│  4. [🖨️ Générer & Imprimer]                                   │
│         │                                                       │
│         ▼                                                       │
│  5. PDF téléchargé/imprimé                                     │
│         │                                                       │
│         ▼                                                       │
│  6. Découper + Coller sur laptops                              │
│         │                                                       │
│         ▼                                                       │
│  7. Scanner vérification (1er laptop)                          │
│         │                                                       │
│         ▼                                                       │
│  8. PrintLog enregistré (audit)                                │
│         │                                                       │
│         ▼                                                       │
│  9. ✅ TERMINÉ — 10 laptops étiquetés                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**Temps estimé:** 15-20 minutes pour 10 laptops  
**Gain vs manuel:** 2 heures → 20 minutes (✅ 85% de gain)

**Ce manuel couvre 100% du processus d'étiquetage QR Code dans CMDB Inventory !** 🎉