// backend/static/admin_cmdb/js/search.js
// ============================================================================
// IMPORTANT : Cette ligne DOIT être la PREMIÈRE ligne du fichier
// ============================================================================
// backend/static/admin_cmdb/js/search.js
// DEBUG - À supprimer après résolution
console.log('=== search.js chargé ===');
console.log('Vue:', typeof Vue);
console.log('Vue.createApp:', typeof Vue.createApp);
console.log('window.VueCreateApp:', typeof window.VueCreateApp);
console.log('window.apiClient:', typeof window.apiClient);

const { createApp } = Vue

/// Vérification que createApp est une fonction
if (typeof createApp !== 'function') {
    console.error('❌ createApp n\'est pas une fonction !');
    console.log('Vue:', typeof Vue);
    console.log('Vue.createApp:', typeof Vue.createApp);
    console.log('window.VueCreateApp:', typeof window.VueCreateApp);
}

// ============================================================================
// === APP SEARCH DROPDOWN (NAVBAR) ===
// ============================================================================

//window.VueCreateApp = Vue.createApp;

function initSearchDropdown() {
    const searchInput = document.getElementById('global-search-input');
    if (!searchInput) return;

    // Create dropdown element
    const dropdown = document.createElement('div');
    dropdown.className = 'search-dropdown';
    dropdown.id = 'search-dropdown';
    searchInput.parentElement.style.position = 'relative';
    searchInput.parentElement.appendChild(dropdown);

    const app = createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                query: '',
                results: {
                    assets: [],
                    tickets: [],
                    stock: []
                },
                loading: false,
                showDropdown: false,
                selectedIndex: -1,
                searchTimeout: null,
                totalResults: 0
            }
        },
        // ... reste du code inchangé


        computed: {
            allResults() {
                return [
                    ...this.results.assets.map(r => ({ ...r, type: 'asset' })),
                    ...this.results.tickets.map(r => ({ ...r, type: 'ticket' })),
                    ...this.results.stock.map(r => ({ ...r, type: 'stock' }))
                ].slice(0, 10);
            }
        },
        mounted() {
            // Focus handler
            searchInput.addEventListener('focus', () => {
                if (this.query.trim()) {
                    this.showDropdown = true;
                }
            });

            // Blur handler with delay
            searchInput.addEventListener('blur', () => {
                setTimeout(() => {
                    this.showDropdown = false;
                }, 200);
            });

            // Keyboard navigation
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.selectedIndex = Math.min(this.selectedIndex + 1, this.allResults.length - 1);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                } else if (e.key === 'Enter' && this.selectedIndex >= 0) {
                    e.preventDefault();
                    this.selectResult(this.allResults[this.selectedIndex]);
                } else if (e.key === 'Escape') {
                    this.showDropdown = false;
                    searchInput.blur();
                }
            });

            // Input handler with debounce
            searchInput.addEventListener('input', (e) => {
                this.query = e.target.value;
                this.debounceSearch();
            });
        },
        methods: {
            debounceSearch() {
                clearTimeout(this.searchTimeout);
                
                if (this.query.trim().length < 2) {
                    this.results = { assets: [], tickets: [], stock: [] };
                    this.totalResults = 0;
                    this.showDropdown = false;
                    return;
                }

                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 300);
            },
            async performSearch() {
                if (this.query.trim().length < 2) return;

                this.loading = true;
                this.showDropdown = true;

                try {
                    // 3 parallel requests
                    const [assetsRes, ticketsRes, stockRes] = await Promise.all([
                        window.apiClient.get('api/v1/inventory/assets/', {
                            params: { search: this.query, page_size: 3 }
                        }),
                        window.apiClient.get('api/v1/maintenance/tickets/', {
                            params: { search: this.query, page_size: 3 }
                        }),
                        window.apiClient.get('api/v1/stock/items/', {
                            params: { search: this.query, page_size: 3 }
                        })
                    ]);

                    this.results = {
                        assets: assetsRes.data.results || assetsRes.data || [],
                        tickets: ticketsRes.data.results || ticketsRes.data || [],
                        stock: stockRes.data.results || stockRes.data || []
                    };

                    this.totalResults = this.results.assets.length + 
                                       this.results.tickets.length + 
                                       this.results.stock.length;
                } catch (error) {
                    console.error('Erreur recherche:', error);
                    this.results = { assets: [], tickets: [], stock: [] };
                } finally {
                    this.loading = false;
                }
            },
            selectResult(result) {
                if (!result) return;
                
                const urls = {
                    'asset': 'api/v1/inventory/assets/',
                    'ticket': 'api/v1/maintenance/tickets/',
                    'stock': 'api/v1/stock/items/'
                };
                
                window.location.href = `${urls[result.type]}${result.id}/`;
            },
            getIcon(type) {
                const map = {
                    'asset': '💻',
                    'ticket': '🔧',
                    'stock': '📦'
                };
                return map[type] || '📄';
            },
            getIconClass(type) {
                const map = {
                    'asset': 'asset',
                    'ticket': 'ticket',
                    'stock': 'stock'
                };
                return map[type] || '';
            },
            highlightText(text) {
                if (!this.query) return text;
                const regex = new RegExp(`(${this.query})`, 'gi');
                return text.replace(regex, '<span class="search-result-highlight">$1</span>');
            }
        },
        watch: {
            results: {
                handler() {
                    this.$nextTick(() => {
                        dropdown.innerHTML = this.renderDropdown();
                        dropdown.classList.toggle('show', this.showDropdown && this.query.trim().length >= 2);
                    });
                },
                deep: true
            },
            loading() {
                this.$nextTick(() => {
                    dropdown.innerHTML = this.renderDropdown();
                    dropdown.classList.toggle('show', this.showDropdown && this.query.trim().length >= 2);
                });
            }
        },
        template: `
            <div class="search-dropdown-header">
                <h6>Résultats</h6>
                <span class="search-shortcut">Ctrl+K</span>
            </div>
            <div class="search-results-list" v-if="!loading && totalResults > 0">
                <div v-if="results.assets.length > 0" class="search-result-group">
                    <div class="search-result-group-title">
                        Assets <span class="badge bg-primary">[[ results.assets.length ]]</span>
                    </div>
                    <a v-for="(asset, idx) in results.assets" :key="'asset-'+asset.id"
                       class="search-result-item" :class="{ active: selectedIndex === idx }"
                       @click="selectResult({...asset, type: 'asset'})">
                        <div class="search-result-icon asset">💻</div>
                        <div class="search-result-content">
                            <div class="search-result-title" v-html="highlightText(asset.name)"></div>
                            <div class="search-result-meta">S/N: [[ asset.serial_number ]]</div>
                        </div>
                    </a>
                </div>
                <div v-if="results.tickets.length > 0" class="search-result-group">
                    <div class="search-result-group-title">
                        Tickets <span class="badge bg-purple">[[ results.tickets.length ]]</span>
                    </div>
                    <a v-for="(ticket, idx) in results.tickets" :key="'ticket-'+ticket.id"
                       class="search-result-item" :class="{ active: selectedIndex === idx }"
                       @click="selectResult({...ticket, type: 'ticket'})">
                        <div class="search-result-icon ticket">🔧</div>
                        <div class="search-result-content">
                            <div class="search-result-title" v-html="highlightText(ticket.subject)"></div>
                            <div class="search-result-meta">#[[ ticket.id ]] • [[ ticket.status ]]</div>
                        </div>
                    </a>
                </div>
                <div v-if="results.stock.length > 0" class="search-result-group">
                    <div class="search-result-group-title">
                        Stock <span class="badge bg-success">[[ results.stock.length ]]</span>
                    </div>
                    <a v-for="(item, idx) in results.stock" :key="'stock-'+item.id"
                       class="search-result-item" :class="{ active: selectedIndex === idx }"
                       @click="selectResult({...item, type: 'stock'})">
                        <div class="search-result-icon stock">📦</div>
                        <div class="search-result-content">
                            <div class="search-result-title" v-html="highlightText(item.name)"></div>
                            <div class="search-result-meta">[[ item.reference ]] • Stock: [[ item.quantity ]]</div>
                        </div>
                    </a>
                </div>
            </div>
            <div class="search-loading" v-else-if="loading">
                <div class="search-spinner"></div>
                <p class="text-muted small">Recherche...</p>
            </div>
            <div class="search-empty" v-else-if="query.trim().length >= 2">
                <i>🔍</i>
                <p class="mb-0">Aucun résultat</p>
            </div>
            <div class="search-empty" v-else>
                <i>⌨️</i>
                <p class="mb-0">Tapez pour rechercher...</p>
            </div>
        `
    });

    app.mount(dropdown);
}

// === APP SEARCH RESULTS PAGE ===
function initSearchResults() {
    const app = document.getElementById('search-app');
    if (!app) return;

    const initialQuery = app.dataset.initialQuery || '';

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                query: initialQuery,
                assets: [],
                tickets: [],
                stock: [],
                loading: false,
                activeTab: 'all'
            }
        },
        computed: {
            totalCount() {
                return this.assets.length + this.tickets.length + this.stock.length;
            }
        },
        mounted() {
            if (this.query) {
                this.performSearch();
                console.log('Recherche initiale pour:', this.query);
            }
            
            // Update input on mount
            const input = document.getElementById('search-input');
            if (input) {
                input.addEventListener('keyup', (e) => {
                    if (e.key === 'Enter') {
                        this.query = e.target.value;
                        this.performSearch();
                    }
                });
            }
        },
        methods: {
            async performSearch() {
                if (!this.query.trim()) return;
                
                this.loading = true;
                
                try {
                    const [assetsRes, ticketsRes, stockRes] = await Promise.all([
                        window.apiClient.get('api/v1/inventory/assets/', {
                            params: { search: this.query, page_size: 10 }
                        }),
                        window.apiClient.get('api/v1/maintenance/tickets/', {
                            params: { search: this.query, page_size: 10 }
                        }),
                        window.apiClient.get('api/v1/stock/items/', {
                            params: { search: this.query, page_size: 10 }
                        })
                    ]);

                    this.assets = assetsRes.data.results || assetsRes.data || [];
                    this.tickets = ticketsRes.data.results || ticketsRes.data || [];
                    this.stock = stockRes.data.results || stockRes.data || [];
                } catch (error) {
                    console.error('Erreur recherche:', error);
                } finally {
                    this.loading = false;
                }
            },
            highlightText(text) {
                if (!this.query) return text;
                const regex = new RegExp(`(${this.query})`, 'gi');
                return text.replace(regex, '<span class="search-result-highlight">$1</span>');
            },
            getStatusClass(status) {
                const map = {
                    'active': 'status-active',
                    'maintenance': 'status-maintenance',
                    'retired': 'status-retired',
                    'stock': 'status-stock',
                    'repair': 'status-repair'
                };
                return map[status] || 'status-stock';
            },
            getPriorityClass(priority) {
                const map = {
                    'critique': 'priority-critique',
                    'eleve': 'priority-eleve',
                    'moyen': 'priority-moyen',
                    'bas': 'priority-bas'
                };
                return map[priority] || 'priority-bas';
            },
            getStockLevelClass(item) {
                if (item.quantity <= 0) return 'stock-critical';
                if (item.quantity <= item.min_stock) return 'stock-low';
                return 'stock-ok';
            },
            formatCurrency(amount) {
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount);
            }
        }
    }).mount('#search-app');
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    initSearchDropdown();
    initSearchResults();
});