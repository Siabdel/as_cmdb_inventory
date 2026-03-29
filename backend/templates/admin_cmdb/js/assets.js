// assets.js - Vue Composition API
const { createApp, ref, onMounted } = Vue;

// Initialisation des données
const defaultAsset = {
    id: 0,
    name: '',
    serial_number: '',
    category_name: '',
    brand_name: '',
    location_name: '',
    status: '',
    photo: ''
};

// Helper pour les notifications
export function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    new bootstrap.Toast(toast, { delay: 3000 }).show();
}

createApp({
    setup() {
        const loading = ref(false);
        const assets = ref([]);
        const categories = ref([]);
        const brands = ref([]);
        const locations = ref([]);
        const totalAssets = ref(0);
        
        // Initialisation des filtres
        const filters = ref({
            search: '',
            category: '',
            brand: '',
            status: '',
            location: ''
        });
        
        // Exemple de méthode avec gestion du loader
        const fetchAssets = async () => {
            loading.value = true;
            try {
                const response = await axios.get('/api/assets/');
                assets.value = response.data.results.map(asset => ({
                    ...defaultAsset,
                    ...asset
                }));
                totalAssets.value = response.data.count;
            } catch (error) {
                console.error('Erreur:', error);
                showToast('Erreur lors du chargement des assets', 'error');
            } finally {
                loading.value = false;
            }
        };

        const exportCSV = async () => {
            loading.value = true;
            try {
                const response = await axios.get('/api/assets/export/', {
                    responseType: 'blob'
                });
                // Gestion du téléchargement...
            } finally {
                loading.value = false;
            }
        };

        onMounted(() => {
            fetchAssets();
        });

        return {
            loading,
            assets,
            categories,
            brands,
            locations,
            totalAssets,
            filters,
            fetchAssets,
            exportCSV
        };
    }
}).mount('#assets-app');