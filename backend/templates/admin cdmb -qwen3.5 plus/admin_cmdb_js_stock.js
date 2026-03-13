// static/admin_cmdb/js/stock.js

const { createApp } = Vue;

// === APP LISTE DU STOCK ===
function initStockList() {
    const app = document.getElementById('stock-app');
    if (!app) return;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                items: [],
                categories: [],
                openTickets: [],
                filters: {
                    search: '',
                    category: '',
                    stockLevel: '',
                    type: ''
                },
                pagination: {
                    count: 0,
                    currentPage: 1,
                    totalPages: 1
                },
                selectedItems: [],
                selectAll: false,
                sortOrder: { reference: '', name: '', quantity: '' },
                searchTimeout: null,
                
                // Modals
                showEntryModal: false,
                showExitModal: false,
                showAddItemModal: false,
                showInventoryModal: false,
                
                // Entry
                entryItem: null,
                entryItemId: '',
                entryQuantity: 1,
                entryComment: '',
                
                // Exit
                exitItem: null,
                exitItemId: '',
                exitQuantity: 1,
                exitTicketId: '',
                exitComment: '',
                
                // New Item
                newItem: {
                    reference: '',
                    name: '',
                    category: '',
                    type: 'component',
                    quantity: 0,
                    min_stock: 5,
                    unit_price: 0
                },
                
                // Stats
                totalItems: 0,
                totalValue: 0,
                okStockCount: 0,
                lowStockCount: 0,
                criticalStockCount: 0
            }
        },
        computed: {
            filteredItems() {
                return this.items.filter(item => {
                    if (this.filters.search && !this.matchesSearch(item)) return false;
                    if (this.filters.category && item.category_id !== this.filters.category) return false;
                    if (this.filters.type && item.type !== this.filters.type) return false;
                    if (this.filters.stockLevel && this.getStockLevel(item) !== this.filters.stockLevel) return false;
                    return true;
                });
            },
            currentPage() {
                return this.pagination.currentPage;
            },
            totalPages() {
                return this.pagination.totalPages;
            },
            visiblePages() {
                const pages = [];
                const maxVisible = 5;
                let start = Math.max(1, this.currentPage - 2);
                let end = Math.min(this.totalPages, start + maxVisible - 1);
                for (let i = start; i <= end; i++) {
                    pages.push(i);
                }
                return pages;
            }
        },
        mounted() {
            this.fetchItems();
            this.fetchCategories();
            this.fetchOpenTickets();
            this.fetchStats();
        },
        methods: {
            async fetchItems() {
                try {
                    const params = new URLSearchParams();
                    if (this.filters.search) params.append('search', this.filters.search);
                    if (this.filters.category) params.append('category', this.filters.category);
                    if (this.filters.type) params.append('type', this.filters.type);
                    params.append('page', this.currentPage);
                    params.append('page_size', 25);

                    const res = await window.apiClient.get(`/stock/items/?${params.toString()}`);
                    this.items = res.data.results || res.data;
                    this.pagination.count = res.data.count || this.items.length;
                    this.pagination.totalPages = Math.ceil(this.pagination.count / 25);
                } catch (error) {
                    console.error('Erreur fetch items:', error);
                }
            },
            async fetchCategories() {
                try {
                    const res = await window.apiClient.get('/stock/categories/');
                    this.categories = res.data;
                } catch (error) {
                    this.categories = [];
                }
            },
            async fetchOpenTickets() {
                try {
                    const res = await window.apiClient.get('/maintenance/tickets/', {
                        params: { status__in: ['open', 'assigned', 'in_progress'] }
                    });
                    this.openTickets = res.data.results || res.data;
                } catch (error) {
                    this.openTickets = [];
                }
            },
            async fetchStats() {
                try {
                    const res = await window.apiClient.get('/stock/items/stats/');
                    this.totalItems = res.data.total_items || this.items.length;
                    this.totalValue = res.data.total_value || 0;
                    this.okStockCount = res.data.ok_stock || 0;
                    this.lowStockCount = res.data.low_stock || 0;
                    this.criticalStockCount = res.data.critical_stock || 0;
                } catch (error) {
                    this.calculateStats();
                }
            },
            calculateStats() {
                this.totalItems = this.items.length;
                this.totalValue = this.items.reduce((sum, i) => sum + (i.total_value || 0), 0);
                this.okStockCount = this.items.filter(i => this.getStockLevel(i) === 'ok').length;
                this.lowStockCount = this.items.filter(i => this.getStockLevel(i) === 'low').length;
                this.criticalStockCount = this.items.filter(i => this.getStockLevel(i) === 'critical').length;
            },
            matchesSearch(item) {
                const query = this.filters.search.toLowerCase();
                return item.name.toLowerCase().includes(query) ||
                       item.reference.toLowerCase().includes(query) ||
                       (item.manufacturer && item.manufacturer.toLowerCase().includes(query));
            },
            getStockLevel(item) {
                if (item.quantity <= 0) return 'critical';
                if (item.quantity <= item.min_stock) return 'low';
                return 'ok';
            },
            isLowStock(item) {
                const level = this.getStockLevel(item);
                return level === 'critical' || level === 'low';
            },
            getStockLevelClass(item) {
                const level = this.getStockLevel(item);
                const map = {
                    'ok': 'stock-ok',
                    'low': 'stock-low',
                    'critical': 'stock-critical'
                };
                return map[level] || 'stock-ok';
            },
            getStockLevelIconClass(item) {
                const level = this.getStockLevel(item);
                const map = {
                    'ok': 'green',
                    'low': 'amber',
                    'critical': 'red'
                };
                return map[level] || 'blue';
            },
            getStockLevelColorClass(item) {
                const level = this.getStockLevel(item);
                const map = {
                    'ok': 'text-success',
                    'low': 'text-warning',
                    'critical': 'text-danger'
                };
                return map[level] || 'text-white';
            },
            getStockLevelGradient() {
                const level = this.getStockLevel(this.items[0] || { quantity: 10, min_stock: 5 });
                const map = {
                    'ok': 'linear-gradient(90deg, #22c55e, #86efac)',
                    'low': 'linear-gradient(90deg, #f97316, #fdba74)',
                    'critical': 'linear-gradient(90deg, #ef4444, #fca5a5)'
                };
                return map[level] || 'linear-gradient(90deg, #3b82f6, #93c5fd)';
            },
            getStockPercentage() {
                const item = this.items[0] || { quantity: 10, min_stock: 5 };
                if (item.min_stock === 0) return 100;
                return Math.min(100, Math.round((item.quantity / (item.min_stock * 2)) * 100));
            },
            getStockValuePercent(item) {
                const maxValue = Math.max(...this.items.map(i => i.total_value || 0), 1);
                return Math.min(100, ((item.total_value || 0) / maxValue) * 100);
            },
            getTypeLabel(type) {
                const map = {
                    'component': 'Composant',
                    'accessory': 'Accessoire',
                    'consumable': 'Consommable',
                    'tool': 'Outillage'
                };
                return map[type] || type;
            },
            getMovementTypeLabel(type) {
                const map = {
                    'entry': 'Entrée',
                    'exit': 'Sortie',
                    'adjustment': 'Ajustement'
                };
                return map[type] || type;
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            },
            formatCurrency(amount) {
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount);
            },
            debounceSearch() {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.pagination.currentPage = 1;
                    this.fetchItems();
                }, 300);
            },
            resetFilters() {
                this.filters = { search: '', category: '', stockLevel: '', type: '' };
                this.pagination.currentPage = 1;
                this.fetchItems();
            },
            filterByStockLevel(level) {
                this.filters.stockLevel = level;
                this.fetchItems();
            },
            changePage(page) {
                if (page < 1 || page > this.totalPages) return;
                this.pagination.currentPage = page;
                this.fetchItems();
            },
            sortBy(field) {
                this.sortOrder[field] = this.sortOrder[field] === 'asc' ? 'desc' : 'asc';
                // Implement sorting logic
            },
            toggleSelectAll(e) {
                this.selectAll = e.target.checked;
                if (this.selectAll) {
                    this.selectedItems = this.filteredItems.map(i => i.id);
                } else {
                    this.selectedItems = [];
                }
            },
            // Entry Modal
            openEntryModal(item) {
                this.entryItem = item;
                this.entryItemId = item.id;
                this.entryQuantity = 1;
                this.entryComment = '';
                this.showEntryModal = true;
            },
            async submitEntry() {
                const itemId = this.entryItemId || this.entryItem?.id;
                if (!itemId || this.entryQuantity < 1) return;

                try {
                    await window.apiClient.post(`/stock/items/${itemId}/add-stock/`, {
                        quantity: this.entryQuantity,
                        comment: this.entryComment
                    });
                    alert('Entrée de stock enregistrée');
                    this.showEntryModal = false;
                    this.fetchItems();
                    this.fetchStats();
                } catch (error) {
                    alert('Erreur lors de l\'entrée de stock');
                }
            },
            // Exit Modal
            openExitModal(item) {
                this.exitItem = item;
                this.exitItemId = item.id;
                this.exitQuantity = 1;
                this.exitTicketId = '';
                this.exitComment = '';
                this.showExitModal = true;
            },
            async submitExit() {
                const itemId = this.exitItemId || this.exitItem?.id;
                if (!itemId || this.exitQuantity < 1) return;

                try {
                    await window.apiClient.post(`/stock/items/${itemId}/remove-stock/`, {
                        quantity: this.exitQuantity,
                        ticket_id: this.exitTicketId || null,
                        comment: this.exitComment
                    });
                    alert('Sortie de stock enregistrée');
                    this.showExitModal = false;
                    this.fetchItems();
                    this.fetchStats();
                } catch (error) {
                    alert('Erreur lors de la sortie de stock');
                }
            },
            // New Item
            async submitNewItem() {
                if (!this.newItem.reference || !this.newItem.name) {
                    alert('Référence et nom requis');
                    return;
                }

                try {
                    await window.apiClient.post('/stock/items/', this.newItem);
                    alert('Article créé avec succès');
                    this.showAddItemModal = false;
                    this.newItem = { reference: '', name: '', category: '', type: 'component', quantity: 0, min_stock: 5, unit_price: 0 };
                    this.fetchItems();
                    this.fetchStats();
                } catch (error) {
                    alert('Erreur lors de la création');
                }
            },
            exportStock() {
                window.location.href = '/api/v1/stock/items/export/csv/';
            }
        }
    }).mount('#stock-app');
}

// === APP DÉTAIL STOCK ===
function initStockDetail() {
    const app = document.getElementById('stock-detail-app');
    if (!app) return;

    const itemId = app.dataset.itemId;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                itemId: itemId,
                item: window.stockItemInitialData || {},
                movements: [],
                stats: { entries30d: 0, exits30d: 0, ticketsLinked: 0 },
                showEntryModal: false,
                showExitModal: false,
                showReorderModal: false,
                entryQuantity: 1,
                entryComment: '',
                exitQuantity: 1,
                exitTicketId: '',
                exitComment: ''
            }
        },
        computed: {
            isCritical() {
                return this.item.quantity <= 0;
            },
            isLow() {
                return this.item.quantity > 0 && this.item.quantity <= this.item.min_stock;
            }
        },
        mounted() {
            this.fetchItemDetail();
            this.fetchMovements();
            this.fetchStats();
        },
        methods: {
            async fetchItemDetail() {
                try {
                    const res = await window.apiClient.get(`/stock/items/${this.itemId}/`);
                    this.item = { ...this.item, ...res.data };
                } catch (error) {
                    console.error('Erreur fetch item:', error);
                }
            },
            async fetchMovements() {
                try {
                    const res = await window.apiClient.get('/stock/movements/', {
                        params: { item: this.itemId }
                    });
                    this.movements = res.data.results || res.data;
                } catch (error) {
                    this.movements = [];
                }
            },
            async fetchStats() {
                try {
                    const res = await window.apiClient.get(`/stock/items/${this.itemId}/stats/`);
                    this.stats = res.data;
                } catch (error) {
                    // Calculate from movements
                    const now = new Date();
                    const thirtyDaysAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);
                    this.stats.entries30d = this.movements.filter(m => 
                        m.movement_type === 'entry' && new Date(m.created_at) > thirtyDaysAgo
                    ).reduce((sum, m) => sum + m.quantity, 0);
                    this.stats.exits30d = this.movements.filter(m => 
                        m.movement_type === 'exit' && new Date(m.created_at) > thirtyDaysAgo
                    ).reduce((sum, m) => sum + m.quantity, 0);
                    this.stats.ticketsLinked = this.movements.filter(m => m.ticket).length;
                }
            },
            getStockLevel(item) {
                if (item.quantity <= 0) return 'critical';
                if (item.quantity <= item.min_stock) return 'low';
                return 'ok';
            },
            getStockLevelClass(item) {
                const level = this.getStockLevel(item);
                const map = { 'ok': 'stock-ok', 'low': 'stock-low', 'critical': 'stock-critical' };
                return map[level] || 'stock-ok';
            },
            getStockLevelIconClass(item) {
                const level = this.getStockLevel(item);
                const map = { 'ok': 'green', 'low': 'amber', 'critical': 'red' };
                return map[level] || 'blue';
            },
            getStockPercentage() {
                if (this.item.min_stock === 0) return 100;
                return Math.min(100, Math.round((this.item.quantity / (this.item.min_stock * 2)) * 100));
            },
            getStockLevelGradient() {
                const level = this.getStockLevel(this.item);
                const map = {
                    'ok': 'linear-gradient(90deg, #22c55e, #86efac)',
                    'low': 'linear-gradient(90deg, #f97316, #fdba74)',
                    'critical': 'linear-gradient(90deg, #ef4444, #fca5a5)'
                };
                return map[level] || 'linear-gradient(90deg, #3b82f6, #93c5fd)';
            },
            getTypeLabel(type) {
                const map = {
                    'component': 'Composant',
                    'accessory': 'Accessoire',
                    'consumable': 'Consommable',
                    'tool': 'Outillage'
                };
                return map[type] || type;
            },
            getMovementTypeLabel(type) {
                const map = { 'entry': 'Entrée', 'exit': 'Sortie', 'adjustment': 'Ajustement' };
                return map[type] || type;
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR', {
                    day: '2-digit', month: '2-digit', year: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                });
            },
            formatCurrency(amount) {
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount);
            },
            async submitEntry() {
                try {
                    await window.apiClient.post(`/stock/items/${this.itemId}/add-stock/`, {
                        quantity: this.entryQuantity,
                        comment: this.entryComment
                    });
                    alert('Entrée enregistrée');
                    this.showEntryModal = false;
                    this.fetchItemDetail();
                    this.fetchMovements();
                } catch (error) {
                    alert('Erreur');
                }
            },
            async submitExit() {
                try {
                    await window.apiClient.post(`/stock/items/${this.itemId}/remove-stock/`, {
                        quantity: this.exitQuantity,
                        ticket_id: this.exitTicketId || null,
                        comment: this.exitComment
                    });
                    alert('Sortie enregistrée');
                    this.showExitModal = false;
                    this.fetchItemDetail();
                    this.fetchMovements();
                } catch (error) {
                    alert('Erreur');
                }
            },
            exportMovements() {
                window.location.href = `/api/v1/stock/movements/export/csv/?item=${this.itemId}`;
            }
        }
    }).mount('#stock-detail-app');
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    initStockList();
    initStockDetail();
});