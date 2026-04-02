// Vue.js 3 Stock Management (detail page)
// Appelle endpoint GET /api/v1/stock/items/{id}/

document.addEventListener('DOMContentLoaded', function() {
    const createApp = window.VueCreateApp || Vue.createApp;

    createApp({
        delimiters: ['[[', ']]'],
        
        data() {
            return {
                item: window.stockItemInitialData || {},
                stats: {
                    entries30d: 0,
                    exits30d: 0,
                    ticketsLinked: 0
                },
                movements: [],
                showEntryModal: false,
                showExitModal: false,
                showReorderModal: false,
                loading: false,
                csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                itemMovements: []
            }
        },
        computed: {
            itemId() {
                return this.item.id || 0;
            },
            isCritical() {
                return (this.item.quantity || 0) <= 0;
            },
            isLow() {
                const qty = this.item.quantity || 0;
                const min = this.item.min_stock || 0;
                return qty > 0 && qty <= min;
            }
        },
        mounted() {
            this.loadMovements();
            this.loadStats();
        },
        methods: {
            async loadMovements() {
                try {
                    if (!this.itemId || this.itemId === 0) {
                        this.movements = [];
                        return;
                    }
                    const response = await axios.get(`/api/v1/stock/movements/?item=${this.itemId}`);
                    this.movements = response.data.results || response.data || [];
                } catch (error) {
                    console.error('Erreur chargement mouvements:', error);
                    this.movements = [];
                }
            },
            async loadStats() {
                try {
                    const response = await axios.get('/api/v1/stock/items/stats/');
                    this.stats = response.data;
                } catch (error) {
                    console.error('Erreur chargement stats:', error);
                }
            },
            showError(message) {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                alertDiv.style.position = 'fixed';
                alertDiv.style.top = '20px';
                alertDiv.style.right = '20px';
                alertDiv.style.zIndex = '10000';
                alertDiv.style.maxWidth = '400px';
                alertDiv.innerHTML = `
                    <strong>Erreur API:</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.body.appendChild(alertDiv);
                setTimeout(() => {
                    if (document.body.contains(alertDiv)) {
                        document.body.removeChild(alertDiv);
                    }
                }, 5000);
            },
            formatCurrency(value) {
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
            },
            getStockPercentage() {
                const qty = this.item.quantity || 0;
                const min = this.item.min_stock || 0;
                if (min <= 0) return 100;
                return Math.round((qty / min) * 100);
            },
            getStockLevelClass(item) {
                if (!item) return 'kpi-critical';
                const qty = item.quantity || 0;
                if (qty <= 0) return 'kpi-critical';
                if (qty <= (item.min_stock || 0)) return 'kpi-low';
                return 'kpi-ok';
            },
            getStockLevelIconClass(item) {
                if (!item) return 'icon-critical';
                const qty = item.quantity || 0;
                if (qty <= 0) return 'icon-critical';
                if (qty <= (item.min_stock || 0)) return 'icon-low';
                return 'icon-ok';
            },
            getStockLevelColorClass(item) {
                if (!item) return 'text-muted';
                const qty = item.quantity || 0;
                if (qty <= 0) return 'text-danger';
                if (qty <= (item.min_stock || 0)) return 'text-warning';
                return 'text-success';
            },
            getTypeLabel(type) {
                const types = {
                    'spare_part': 'Pièce détachée',
                    'consumable': 'Consommable',
                    'accessory': 'Accessoire',
                    'tool': 'Outil'
                };
                return types[type] || type || '-';
            },
            getMovementTypeLabel(type) {
                const types = {
                    'in': 'Entrée',
                    'out': 'Sortie',
                    'adjustment': 'Ajustement',
                    'transfer': 'Transfert'
                };
                return types[type] || type || '-';
            },
            exportMovements() {
                alert('Export des mouvements à implémenter');
            },
            showReorder() {
                this.showReorderModal = true;
            }
        }
    }).mount('#stock-detail-app');
});
