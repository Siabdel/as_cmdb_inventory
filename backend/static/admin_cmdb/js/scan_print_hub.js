// static/admin_cmdb/js/scan_print_hub.js


if (typeof window.VueCreateApp === 'undefined') {
    console.error('❌ window.VueCreateApp non défini !');
    if (typeof Vue !== 'undefined') {
        window.VueCreateApp = Vue.createApp;
    }
}

const createApp = window.VueCreateApp;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            stats: {
                scans_today: 0,
                prints_today: 0,
                total_assets: 0,
                printers_active: 0
            },
            recentActivity: []
        }
    },
    mounted() {
        this.fetchStats();
        this.fetchRecentActivity();
    },
    methods: {
        async fetchStats() {
            try {
                const [assetsRes, printersRes] = await Promise.all([
                    window.apiClient.get('inventory/assets/', { params: { page_size: 1 } }),
                    window.apiClient.get('scanner/printers/', { params: { is_active: true } })
                ]);
                
                this.stats.total_assets = assetsRes.data.count || 0;
                this.stats.printers_active = printersRes.data.length || 0;
                
                // Stats scans/prints today (endpoints à créer)
                const today = new Date().toISOString().split('T')[0];
                const [scansRes, printsRes] = await Promise.all([
                    window.apiClient.get('scanner/logs/', { params: { date: today } }),
                    window.apiClient.get('scanner/print-logs/', { params: { date: today } })
                ]);
                
                this.stats.scans_today = scansRes.data.count || 0;
                this.stats.prints_today = printsRes.data.count || 0;
                
            } catch (error) {
                console.error('Erreur fetch stats:', error);
            }
        },
        async fetchRecentActivity() {
            try {
                const [scansRes, printsRes] = await Promise.all([
                    window.apiClient.get('scanner/logs/', { params: { page_size: 5 } }),
                    window.apiClient.get('scanner/print-logs/', { params: { page_size: 5 } })
                ]);
                
                const scans = (scansRes.data.results || scansRes.data || []).map(s => ({
                    id: `scan-${s.id}`,
                    type: 'scan',
                    title: `📷 Scan: ${s.asset_name || 'Asset inconnu'}`,
                    meta: `Par: ${s.scanned_by || 'Inconnu'} • IP: ${s.ip_address || 'N/A'}`,
                    time: this.formatTime(s.created_at)
                }));
                
                const prints = (printsRes.data.results || printsRes.data || []).map(p => ({
                    id: `print-${p.id}`,
                    type: 'print',
                    title: `🖨️ Impression: ${p.asset_name || 'Asset inconnu'}`,
                    meta: `Par: ${p.printed_by || 'Inconnu'} • ${p.printer_name}`,
                    time: this.formatTime(p.printed_at)
                }));
                
                this.recentActivity = [...scans, ...prints]
                    .sort((a, b) => new Date(b.time) - new Date(a.time))
                    .slice(0, 10);
                    
            } catch (error) {
                console.error('Erreur fetch activity:', error);
            }
        },
        formatTime(dateStr) {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) return 'À l\'instant';
            if (diff < 3600000) return `Il y a ${Math.floor(diff / 60000)} min`;
            if (diff < 86400000) return `Il y a ${Math.floor(diff / 3600000)} h`;
            return date.toLocaleDateString('fr-FR');
        }
    }
}).mount('#scan-print-hub');
