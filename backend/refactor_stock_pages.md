# Fichiers Concernés et Feuille de Route

## Fichiers Impactés
1. **Templates Django**
   - `templates/admin/stock/list.html`
   - `templates/admin/stock/movement.html`
2. **Vue.js Components**
   - `frontend/components/StockDashboard.vue`
   - `frontend/components/StockKPI.vue`
3. **Backend**
   - `stock/views.py` (API DRF)
   - `stock/serializers.py`
   - `stock/urls.py`
4. **Templatetags**
   - `cmdb_admin/templatetags/custom_filters.py` (à déprécié)

## Feuille de Route Itérative
### Phase 1: Préparation Vue.js
- [ ] Créer structure frontend (Vue 3 + Vite)
- [ ] Installer dépendances (axios, vue-router)

### Phase 2: Composants KPI
- [ ] Implémenter `StockKPI.vue` avec calculs réactifs
- [ ] Remplacer logique `subtract` par composants

### Phase 3: API DRF
- [ ] Exposer endpoints `/api/stock/stats/`
- [ ] Créer serializer `StockStatsSerializer`

### Phase 4: Migration Templates
- [ ] Remplacer `list.html` par `StockDashboard.vue`
- [ ] Conserver templates Django pour fallback

### Phase 5: Tests
- [ ] Tests unitaires Vue
- [ ] Tests d'intégration DRF
- [ ] Validation UX/UI

> *Note : Les phases 1-2 peuvent être parallélisées avec la documentation.*