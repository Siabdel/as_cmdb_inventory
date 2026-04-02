// static/admin_cmdb/js/print.js
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
            printers: [],
            templates: [],
            assetIds: [],
            selectedPrinter: null,
            selectedTemplate: null,
            copies: 1,
            printing: false
        }
    },
    mounted() {
        this.fetchPrinters();
        this.fetchTemplates();
        this.getAssetIdsFromURL();
    },
    methods: {
        async fetchPrinters() {
            try {
                const res = await window.apiClient.get('/scanner/printers/');
                this.printers = res.data.results;
                if (this.printers.length > 0) {
                    this.selectedPrinter = this.printers.find(p => p.is_default)?.id || this.printers[0].id;
                }
            } catch (error) {
                console.error('Erreur fetch printers:', error);
            }
        },
        async fetchTemplates() {
            try {
                const res = await window.apiClient.get('/scanner/templates/');
                this.templates = res.data.results;
                if (this.templates.length > 0) {
                    this.selectedTemplate = this.templates.find(t => t.is_default)?.id || this.templates[0].id;
                }
            } catch (error) {
                console.error('Erreur fetch templates:', error);
            }
        },
        getAssetIdsFromURL() {
            const params = new URLSearchParams(window.location.search);
            const ids = params.get('assets');
            if (ids) {
                this.assetIds = ids.split(',').map(id => parseInt(id));
            }
        },
        async testPrint() {
            if (!this.selectedPrinter) return;
            
            try {
                const res = await window.apiClient.post(`/scanner/printers/${this.selectedPrinter}/test/`, {}, {
                    responseType: 'blob'
                });
                
                const url = window.URL.createObjectURL(res);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'test_print.pdf';
                link.click();
                window.URL.revokeObjectURL(url);
                
                alert('✅ Test impression lancé');
            } catch (error) {
                alert('❌ Erreur test impression: ' + error.message);
            }
        },
        async printLabels() {
            if (!this.selectedPrinter || this.assetIds.length === 0) return;
            
            this.printing = true;
            
            try {
                const res = await window.apiClient.post('/scanner/print-labels/', {
                    asset_ids: this.assetIds,
                    printer_id: this.selectedPrinter,
                    template_id: this.selectedTemplate,
                    copies: this.copies
                }, {
                    responseType: 'blob'
                });
                
                const url = window.URL.createObjectURL(res);
                const link = document.createElement('a');
                link.href = url;
                link.download = `labels_${Date.now()}.pdf`;
                link.click();
                window.URL.revokeObjectURL(url);
                
                alert('✅ Impression lancée');
            } catch (error) {
                alert('❌ Erreur impression: ' + error.message);
            } finally {
                this.printing = false;
            }
        },
        async downloadPDF() {
            await this.printLabels();
        }
    }
}).mount('#print-app');