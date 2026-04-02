# Analyse et Proposition de Refactorisation des Pages Stock

## État Actuel
- **Templates Django** : `templates/admin/stock/list.html` et `admin/stock/movement` utilisent des filtres personnalisés (`subtract`, `multiply`, etc.) pour gérer les calculs et le formatage.
- **Filtres personnalisés** : Définis dans `cmdb_admin/templatetags/custom_filters.py` (ex: `{{ total_items|subtract:low_stock|subtract:out_of_stock }}`).
- **Limites** :
  - Logique métier dans les templates (anti-pattern Django).
  - Calculs répétitifs et dépendants du contexte.
  - Difficile à tester et à maintenir.

## Proposition : Refactorisation en Vue.js
### Avantages
1. **Séparation des Concerns** :
   - Logique de calcul déplacée vers des composants réutilisables.
   - UI dynamique avec réactivité (Vue 3 + Composition API).
2. **Réutilisation** :
   - Composants réutilisables pour les KPI, tableaux, filtres.
3. **Performance** :
   - Mise en cache des calculs côté client.
4. **Testabilité** :
   - Unit tests pour les composants Vue.

### Implémentation
1. **Structure** : Créer un composant `StockDashboard.vue` avec : 
   ```vue
   <template>
     <div class="kpi-card">
       <div class="kpi-value">{{ stockOK }}</div>
       <div class="kpi-label">Stock OK</div>
     </div>
   </template>

   <script setup>
   import { computed } from 'vue';
   import axios from 'axios';

   const props = defineProps(['totalItems', 'lowStock', 'outOfStock']);

   const stockOK = computed(() => 
     props.totalItems - props.lowStock - props.outOfStock
   );

   // Fetch data via Axios/DRF
   </script>
   ```
2. **Intégration Django** :
   - Exposer des endpoints DRF pour `low_stock`, `out_of_stock`, etc.
   - Remplacer les templates Django par des `div` conteneurs pour Vue.

### Risques et Alternatives
- **Coût initial** : Refactorisation progressive recommandée.
- **Compatibilité** : Conserver les templates Django pour les anciens navigateurs.

## Conclusion
La refactorisation en Vue.js améliorera la maintenabilité et la performance, mais nécessite une planification itérative. Commencer par les composants les plus complexes (ex: calculs de stock) avant de généraliser.