// static/admin_cmdb/js/assets.js

// backend/static/admin_cmdb/js/search.js
// backend/static/admin_cmdb/js/assets.js

// Utiliser window.VueCreateApp (défini dans api.js)
//const createApp = window.VueCreateApp;
const { createApp } = Vue


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
        async mounted() {
            await this.fetchFilters();  // ← attendre d'abord
            await this.fetchAssets();   // ← puis les assets
            this.fetchStatusStats();    // ← celui-là peut être async
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
                    const rawAssets = res.data.results || res.data;
                    console.log('Raw assets:', rawAssets);
                    // Filtrer les assets null/undefined et sans id pour éviter l'erreur "Cannot read properties of null"
                    const filteredAssets = rawAssets.filter(asset => asset && asset.id != null && asset.id !== undefined);
                    console.log('Filtered assets ####:', filteredAssets);
                    this.assets = filteredAssets;
                    this.pagination.count = res.data.count || this.assets.length;
                    this.pagination.totalPages = Math.ceil(this.pagination.count / 25);
                } catch (error) {
                    console.error('Erreur fetch assets:', error);
                }
            },
        
            //L'erreur (cats.data || []).filter is not a function prouve que cats.data n'est pas un array !
            //// ❌ BUG - cats.data est un objet {count, results, next, previous}
            // this.categories = cats.data;  // ← assigne l'objet, pas l'array !
            // ❌ BUG - .filter() sur un objet = crash
            //this.categories = (cats.data || []).filter(c => c && c.id != null);
            async fetchFilters() {
                try {
                    const [cats, brands, locs] = await Promise.all([
                        window.apiClient.get('/inventory/category/'),
                        window.apiClient.get('/inventory/brand/'),
                        window.apiClient.get('/inventory/location/')
                    ]);
                    
                    // ✅ EXTRAIRE .results (format paginé Django REST)
                    this.categories = (cats.data?.results || []).filter(c => c && c.id != null);
                    this.brands = (brands.data?.results || []).filter(b => b && b.id != null);
                    this.locations = (locs.data?.results || []).filter(l => l && l.id != null);
                    
                } catch (error) {
                    console.error('Erreur fetch filters:', error);
                    this.categories = [];
                    this.brands = [];
                    this.locations = [];
                }
            },


            async fetchStatusStats() {
                try {
                    const res = await window.apiClient.get('/inventory/assets/by-status/');
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
                this.sortOrder[field] = this.sortOrder[field] === 'asc' ? 'desc' : 'asc';
            },
            toggleSelectAll(e) {
                this.selectAll = e.target.checked;
                if (this.selectAll) {
                    this.selectedAssets = this.assets.filter(a => a != null && a.id != null).map(a => a.id);
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
                    await window.apiClient.post(`/inventory/assets/${id}/retire/`);
                }
                this.fetchAssets();
                this.selectedAssets = [];
            },
            async bulkMove() {
                if (!this.moveLocation) return;
                for (const id of this.selectedAssets) {
                    await window.apiClient.post(`/inventory/assets/${id}/move/`, {
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
    if (!assetId) {
        console.error('assetId manquant dans dataset');
        return;
    }

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
                    const res = await window.apiClient.get(`/inventory/assets/${this.assetId}/`);
                    this.asset = { ...this.asset, ...res.data };
                } catch (error) {
                    console.error('Erreur fetch asset:', error);
                }
            },
            async fetchMovements() {
                try {
                    const res = await window.apiClient.get(`/inventory/assets/${this.assetId}/movements/`);
                    this.movements = res.data.results || res.data;
                } catch (error) {
                    console.error('Erreur fetch movements:', error);
                    // Si l'API n'existe pas, on peut simplement ne rien faire ou afficher un message
                    this.movements = [];
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
                    await window.apiClient.post(`/inventory/assets/${this.assetId}/retire/`);
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

// === APP FORMULAIRE ASSET ===
function initAssetForm() {
    const app = document.getElementById('asset-form-app');
    if (!app) return;

    const formMode = app.dataset.mode || 'create';
    const assetId = app.dataset.assetId || null;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                formMode: formMode,
                assetId: assetId,
                submitting: false,
                lastModified: '',
                form: {
                    name: '',
                    model: '',
                    serial_number: '',
                    inventory_number: '',
                    description: '',
                    category: '',
                    brand: '',
                    status: 'stock',
                    tags: [],
                    location: '',
                    assigned_to: '',
                    purchase_date: '',
                    warranty_end: '',
                    purchase_price: '',
                    vendor: '',
                    specs: { cpu: '', ram: '', storage: '', screen: '' },
                    photo: null
                },
                newTag: '',
                photoFile: null,
                photoPreview: null,
                categories: [],
                brands: [],
                locations: [],
                users: [],
                qrCodeUrl: ''
            }
        },
        mounted() {
            this.fetchFilters();
            this.fetchUsers();
            if (this.formMode === 'edit' && this.assetId) {
                this.fetchAsset();
            }
        },
        methods: {
            async fetchFilters() {
                try {
                    const [cats, brands, locs] = await Promise.all([
                        window.apiClient.get('/inventory/category/'),
                        window.apiClient.get('/inventory/brand/'),
                        window.apiClient.get('/inventory/location/')
                    ]);
                    this.categories = (cats.data?.results || []).filter(c => c && c.id != null);
                    this.brands = (brands.data?.results || []).filter(b => b && b.id != null);
                    this.locations = (locs.data?.results || []).filter(l => l && l.id != null);
                } catch (error) {
                    console.error('Erreur fetch filters:', error);
                }
            },
            async fetchUsers() {
                try {
                    const res = await window.apiClient.get('/staff/auth/users/');
                    this.users = res.data;
                } catch (error) {
                    this.users = [];
                }
            },
            async fetchAsset() {
                try {
                    const res = await window.apiClient.get(`/inventory/assets/${this.assetId}/`);
                    const data = res.data;
                    this.form = {
                        ...this.form,
                        name: data.name || '',
                        model: data.model || '',
                        serial_number: data.serial_number || '',
                        inventory_number: data.inventory_number || '',
                        description: data.description || '',
                        category: data.category || '',
                        brand: data.brand || '',
                        status: data.status || 'stock',
                        tags: data.tags || [],
                        location: data.location || '',
                        assigned_to: data.assigned_to || '',
                        purchase_date: data.purchase_date || '',
                        warranty_end: data.warranty_end || '',
                        purchase_price: data.purchase_price || '',
                        vendor: data.vendor || '',
                        specs: data.specs || {},
                        photo: data.photo || ''
                    };
                    this.photoPreview = data.photo;
                    this.qrCodeUrl = `/media/qr_codes/qr_asset_${this.assetId}.png`;
                    this.lastModified = new Date(data.updated_at).toLocaleString('fr-FR');
                } catch (error) {
                    console.error('Erreur fetch asset:', error);
                }
            },
            addTag() {
                if (this.newTag.trim()) {
                    this.form.tags.push({ name: this.newTag.trim() });
                    this.newTag = '';
                }
            },
            removeTag(index) {
                this.form.tags.splice(index, 1);
            },
            handlePhotoUpload(event) {
                const file = event.target.files[0];
                if (file) {
                    if (file.size > 5 * 1024 * 1024) {
                        alert('La photo ne doit pas dépasser 5MB');
                        return;
                    }
                    this.photoFile = file;
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        this.photoPreview = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            },
            removePhoto() {
                this.photoFile = null;
                this.photoPreview = null;
                this.form.photo = null;
            },
            async regenerateQR() {
                try {
                    await window.apiClient.post(`/scanner/assets/${this.assetId}/regen-qr/`);
                    this.qrCodeUrl = `/media/qr_codes/qr_asset_${this.assetId}.png?t=${Date.now()}`;
                    alert('QR Code régénéré');
                } catch (error) {
                    alert('Erreur lors de la régénération');
                }
            },
            async submitForm() {
                this.submitting = true;
                try {
                    const formData = new FormData();
                    Object.keys(this.form).forEach(key => {
                        if (key === 'specs') {
                            formData.append('specs', JSON.stringify(this.form.specs));
                        } else if (key === 'tags') {
                            formData.append('tags', JSON.stringify(this.form.tags.map(t => t.name)));
                        } else if (this.form[key]) {
                            formData.append(key, this.form[key]);
                        }
                    });
                    if (this.photoFile) {
                        formData.append('photo', this.photoFile);
                    }

                    let response;
                    if (this.formMode === 'create') {
                        response = await window.apiClient.post('/inventory/assets/', formData, {
                            headers: { 'Content-Type': 'multipart/form-data' }
                        });
                    } else {
                        response = await window.apiClient.put(`/inventory/assets/${this.assetId}/`, formData, {
                            headers: { 'Content-Type': 'multipart/form-data' }
                        });
                    }

                    alert(this.formMode === 'create' ? 'Asset créé avec succès' : 'Asset mis à jour');
                    window.location.href = `/admin/assets/${response.data.id}/`;
                } catch (error) {
                    console.error('Erreur submit:', error);
                    const errors = error.response?.data;
                    if (errors) {
                        Object.keys(errors).forEach(key => {
                            alert(`${key}: ${errors[key].join(', ')}`);
                        });
                    } else {
                        alert('Erreur lors de l\'enregistrement');
                    }
                } finally {
                    this.submitting = false;
                }
            },
            async saveDraft() {
                try {
                    await window.apiClient.post('/inventory/assets/draft/', this.form);
                    alert('Brouillon sauvegardé');
                } catch (error) {
                    alert('Erreur sauvegarde brouillon');
                }
            }
        }
    }).mount('#asset-form-app');
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    initAssetsList();
    initAssetDetail();
    initAssetForm();
});