// static/admin_cmdb/js/main.js

const createApp = window.VueCreateApp || Vue.createApp;

createApp({
    delimiters: ['[[', ']]'], // Délimiteurs Vue pour éviter conflit Django
    data() {
        return {
            sidebarCollapsed: false,
            mobileOpen: false,
            user: {
                username: 'Chargement...',
                role: 'technicien'
            },
            searchQuery: ''
        }
    },
    mounted() {
        this.fetchUser();
        // Shortcut Ctrl+K pour la recherche
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('global-search-input').focus();
            }
        });
    },
    methods: {
        toggleSidebar() {
            if (window.innerWidth < 768) {
                this.mobileOpen = !this.mobileOpen;
            } else {
                this.sidebarCollapsed = !this.sidebarCollapsed;
            }
        },
        async fetchUser() {
            // Appel API pour récupérer les infos utilisateur courantes
            // Fallback sur localStorage si besoin pour éviter une requête supplémentaire
            try {
                const res = await window.apiClient.get('/auth/user/'); // Endpoint supposé standard
                this.user = res.data || res.data.user || [];
            } catch (e) {
                // Si échec, on garde les données en session ou default
                this.user.username = "Utilisateur";
            }
        },
        logout() {
            localStorage.removeItem('cmdb_token');
            window.location.href = '/admin/login/';
        }
    }
}).mount('#layout-app');