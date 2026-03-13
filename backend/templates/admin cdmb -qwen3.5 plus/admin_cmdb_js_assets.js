// static/admin_cmdb/js/assets.js

const { createApp } = Vue;

// === APP LISTE DES ASSETS ===
function initAssetsList() {
    const app = document.getElementById('assets-app');
    if (!app) return;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                assets: [],
                categories: [],
                brands: [],
                locations: [],
                statusStats: [],
                filters: {
                    search: '',
                    category: '',
                    brand: '',
                    status: '',
                    location: ''
                },
                pagination: {
                    count: 0,
                    next: null,
                    previous: null,
                    currentPage: 1,
                    totalPages: 1
                },
                selectedAssets: [],
                selectAll: false,
                sortOrder: { name: '', serial_number: '' },
                showMoveModal: false,
                showAssignModal: false,
                moveLocation: '',
                searchTimeout: null
            }
        },
        computed: {
            totalAssets() {
                return this.pagination.count;
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
            this.fetchFilters();
            this.fetchAssets();
            this.fetchStatusStats();
        },
        methods: {
            async fetchAssets() {
                try {
                    const params = new URLSearchParams();
                    if (this.filters.search) params.append('search', this.filters.search);
                    if (this.filters.category) params.append('category', this.filters.category);
                    if (this.filters.brand) params.append('brand', this.filters.brand);
                    if (this.filters.status) params.append('status', this.filters.status);
                    if (this.filters.location) params.append('location', this.filters.location);
                    params.append('page', this.currentPage);
                    params.append('page_size', 25);

                    const res = await window.apiClient.get(`/inventory/assets/?${params.toString()}`);
                    this.assets = res.data.results || res.data;
                    this.pagination.count = res.data.count || this.assets.length;
                    this.pagination.totalPages = Math.ceil(this.pagination.count / 25);
                } catch (error) {
                    console.error('Erreur fetch assets:', error);
                }
            },
            async fetchFilters() {
                try {
                    const [cats, brands, locs] = await Promise.all([
                        window.apiClient.get('/inventory/category/'),
                        window.apiClient.get('/inventory/brand/'),
                        window.apiClient.get('/inventory/location/')
                    ]);
                    this.categories = cats.data;
                    this.brands = brands.data;
                    this.locations = locs.data;
                } catch (error) {
                    console.error('Erreur fetch filters:', error);
                }
            },
            async fetchStatusStats() {
                try {
                    const res = await window.apiClient.get('/inventory/asset/by-status/');
                    this.statusStats = res.data.map(stat => ({
                        status: stat.status,
                        count: stat.count,
                        label: this.getStatusLabel(stat.status)
                    }));
                } catch (error) {
                    console.error('Erreur fetch stats:', error);
                }
            },
            debounceSearch() {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.currentPage = 1;
                    this.fetchAssets();
                }, 300);
            },
            resetFilters() {
                this.filters = { search: '', category: '', brand: '', status: '', location: '' };
                this.currentPage = 1;
                this.fetchAssets();
            },
            changePage(page) {
                if (page < 1 || page > this.totalPages) return;
                this.currentPage = page;
                this.fetchAssets();
            },
            sortBy(field) {
                // Implementation du tri
                this.sortOrder[field] = this.sortOrder[field] === 'asc' ? 'desc' : 'asc';
            },
            toggleSelectAll(e) {
                this.selectAll = e.target.checked;
                if (this.selectAll) {
                    this.selectedAssets = this.assets.map(a => a.id);
                } else {
                    this.selectedAssets = [];
                }
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
            getStatusBadgeClass(status) {
                const map = {
                    'active': 'bg-success',
                    'maintenance': 'bg-warning',
                    'retired': 'bg-secondary',
                    'stock': 'bg-primary',
                    'repair': 'bg-danger'
                };
                return map[status] || 'bg-secondary';
            },
            getStatusLabel(status) {
                const map = {
                    'active': 'Actif',
                    'maintenance': 'Maintenance',
                    'retired': 'Retiré',
                    'stock': 'En Stock',
                    'repair': 'En Réparation'
                };
                return map[status] || status;
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR');
            },
            async bulkRetire() {
                if (!confirm(`Archiver ${this.selectedAssets.length} asset(s) ?`)) return;
                for (const id of this.selectedAssets) {
                    await window.apiClient.post(`/inventory/asset/${id}/retire/`);
                }
                this.fetchAssets();
                this.selectedAssets = [];
            },
            async bulkMove() {
                if (!this.moveLocation) return;
                for (const id of this.selectedAssets) {
                    await window.apiClient.post(`/inventory/asset/${id}/move/`, {
                        location_id: this.moveLocation
                    });
                }
                this.showMoveModal = false;
                this.moveLocation = '';
                this.fetchAssets();
            },
            exportCSV() {
                window.location.href = '/api/v1/inventory/assets/export/csv/';
            }
        }
    }).mount('#assets-app');
}

// === APP DÉTAIL ASSET ===
function initAssetDetail() {
    const app = document.getElementById('asset-detail-app');
    if (!app) return;

    const assetId = app.dataset.assetId;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                assetId: assetId,
                asset: window.assetInitialData || {},
                movements: [],
                tickets: [],
                qrCodeUrl: '',
                activeTab: 'info'
            }
        },
        mounted() {
            this.fetchAssetDetail();
            this.fetchMovements();
            this.fetchTickets();
            this.generateQRUrl();
        },
        methods: {
            async fetchAssetDetail() {
                try {
                    const res = await window.apiClient.get(`/inventory/asset/${this.assetId}/`);
                    this.asset = { ...this.asset, ...res.data };
                } catch (error) {
                    console.error('Erreur fetch asset:', error);
                }
            },
            async fetchMovements() {
                try {
                    const res = await window.apiClient.get('/inventory/asset-movement/', {
                        params: { asset: this.assetId }
                    });
                    this.movements = res.data.results || res.data;
                } catch (error) {
                    console.error('Erreur fetch movements:', error);
                }
            },
            async fetchTickets() {
                try {
                    const res = await window.apiClient.get('/maintenance/tickets/', {
                        params: { asset: this.assetId }
                    });
                    this.tickets = res.data.results || res.data;
                } catch (error) {
                    console.error('Erreur fetch tickets:', error);
                }
            },
            generateQRUrl() {
                this.qrCodeUrl = `/media/qr_codes/qr_asset_${this.assetId}.png`;
            },
            async regenerateQR() {
                try {
                    await window.apiClient.post(`/scanner/assets/${this.assetId}/regen-qr/`);
                    this.generateQRUrl();
                    alert('QR Code régénéré avec succès');
                } catch (error) {
                    console.error('Erreur regen QR:', error);
                }
            },
            printQR() {
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <html><head><title>QR Code Asset ${this.assetId}</title></head>
                    <body style="display:flex;justify-content:center;align-items:center;height:100vh;">
                        <img src="${this.qrCodeUrl}" style="max-width:300px;">
                    </body></html>
                `);
                printWindow.document.close();
                printWindow.print();
            },
            async retireAsset() {
                if (!confirm('Archiver cet asset ?')) return;
                try {
                    await window.apiClient.post(`/inventory/asset/${this.assetId}/retire/`);
                    window.location.reload();
                } catch (error) {
                    console.error('Erreur retire:', error);
                }
            },
            createTicket() {
                window.location.href = `/admin/tickets/new/?asset=${this.assetId}`;
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
            getTicketStatusClass(status) {
                const map = {
                    'open': 'bg-primary',
                    'assigned': 'bg-purple',
                    'in_progress': 'bg-warning',
                    'waiting_parts': 'bg-amber',
                    'resolved': 'bg-success',
                    'closed': 'bg-secondary'
                };
                return map[status] || 'bg-secondary';
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR');
            }
        }
    }).mount('#asset-detail-app');
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    initAssetsList();
    initAssetDetail();
});