/* ═══════════════════════════════════════════════════════
   CMDB Inventory — Vue.js Dashboard App
   File: static/dashboard/js/main.js
   Requires: Vue 3, Axios
═══════════════════════════════════════════════════════ */

const { createApp } = Vue

// ── Constantes ─────────────────────────────────────────
const API_BASE = '/api/v1/inventory'

const CAT_ICONS = {
  'server':  { icon: 'bi bi-server',          bg: 'rgba(99,102,241,0.15)',  color: '#818cf8' },
  'laptop':  { icon: 'bi bi-laptop',           bg: 'rgba(37,99,235,0.15)',   color: '#60a5fa' },
  'desktop': { icon: 'bi bi-pc-display',       bg: 'rgba(14,165,233,0.15)',  color: '#38bdf8' },
  'router':  { icon: 'bi bi-router',           bg: 'rgba(16,185,129,0.15)', color: '#34d399' },
  'switch':  { icon: 'bi bi-diagram-3',        bg: 'rgba(245,158,11,0.15)', color: '#fbbf24' },
  'monitor': { icon: 'bi bi-display',          bg: 'rgba(139,92,246,0.15)', color: '#a78bfa' },
  'printer': { icon: 'bi bi-printer',          bg: 'rgba(236,72,153,0.15)', color: '#f472b6' },
  'phone':   { icon: 'bi bi-telephone',        bg: 'rgba(20,184,166,0.15)', color: '#2dd4bf' },
  'nas':     { icon: 'bi bi-hdd-stack',        bg: 'rgba(249,115,22,0.15)', color: '#fb923c' },
  'ups':     { icon: 'bi bi-battery-charging', bg: 'rgba(234,179,8,0.15)',  color: '#facc15' },
}

// ── Helpers ────────────────────────────────────────────
function getAuthHeaders() {
  const token = localStorage.getItem('cmdb_token') || ''
  return token ? { Authorization: `Token ${token}` } : {}
}

function formatCurrency(val) {
  if (!val) return '0 €'
  const n = parseFloat(val)
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M €'
  if (n >= 1_000)     return (n / 1_000).toFixed(0) + 'K €'
  return n.toFixed(0) + ' €'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const diff = Math.floor((new Date() - new Date(dateStr)) / 60000)
  if (diff < 60)   return diff + 'm'
  if (diff < 1440) return Math.floor(diff / 60) + 'h'
  return Math.floor(diff / 1440) + 'j'
}

function pct(val, total) {
  if (!total) return '0%'
  return Math.round((val / total) * 100) + '%'
}

// ── Données de démo (API indisponible) ─────────────────
const DEMO_DATA = {
  stats: {
    total_assets: 247, active_assets: 183,
    inactive_assets: 38, archived_assets: 26,
    assets_new: 52, assets_used: 172, assets_damaged: 23,
    total_value: '487320.00', low_warranty: 7,
    recent_movements: [],
  },
  byCategory: [
    { category__name: 'PC Portable',  category__icon: 'laptop',  count: 68 },
    { category__name: 'Serveur',      category__icon: 'server',  count: 24 },
    { category__name: 'PC Fixe',      category__icon: 'desktop', count: 55 },
    { category__name: 'Switch',       category__icon: 'switch',  count: 18 },
    { category__name: 'Écran',        category__icon: 'monitor', count: 42 },
    { category__name: 'Imprimante',   category__icon: 'printer', count: 15 },
    { category__name: 'NAS',          category__icon: 'nas',     count: 8  },
    { category__name: 'Onduleur',     category__icon: 'ups',     count: 17 },
  ],
}

// ── App Vue ────────────────────────────────────────────
createApp({
  delimiters: ['[[', ']]'],

  data() {
    return {
      loading:         true,
      stats:           {},
      byCategory:      [],
      recentMovements: [],
      warrantyAssets:  [],
      lastUpdate:      '—',
      isDemo:          false,
    }
  },

  computed: {
    activePercent() {
      if (!this.stats.total_assets) return 0
      return Math.round((this.stats.active_assets / this.stats.total_assets) * 100)
    }
  },

  mounted() {
    this.loadAll()
    // Auto-refresh toutes les 60s
    this._timer = setInterval(() => this.loadAll(), 60_000)
  },

  beforeUnmount() {
    clearInterval(this._timer)
  },

  methods: {

    // ── Chargement principal ──────────────────────────
    async loadAll() {
      this.loading = true
      try {
        const headers = getAuthHeaders()

        const [statsRes, catRes, warrantyRes, movRes] = await Promise.all([
          axios.get(`${API_BASE}/dashboard/stats/`,          { headers }),
          axios.get(`${API_BASE}/assets/by-category/`,       { headers }),
          axios.get(`${API_BASE}/assets/warranty-expiring/`, { headers }),
          axios.get(`${API_BASE}/movements/?page_size=8`,    { headers }),
        ])

        this.stats           = statsRes.data
        this.byCategory      = catRes.data
        this.warrantyAssets  = warrantyRes.data
        this.recentMovements = this.stats.recent_movements
                               || movRes.data?.results
                               || movRes.data
                               || []
        this.isDemo          = false
        this.lastUpdate      = new Date().toLocaleTimeString('fr-FR')

      } catch (e) {
        console.warn('[CMDB] API non disponible — mode démo:', e.message)
        this.loadDemoData()
      } finally {
        this.loading = false
      }
    },

    // ── Mode démo ─────────────────────────────────────
    loadDemoData() {
      this.stats           = DEMO_DATA.stats
      this.byCategory      = DEMO_DATA.byCategory
      this.warrantyAssets  = []
      this.recentMovements = []
      this.isDemo          = true
      this.lastUpdate      = 'Mode démo'
    },

    // ── Helpers exposés au template ───────────────────
    pct:            pct,
    formatCurrency: formatCurrency,
    formatDate:     formatDate,

    getCatIcon(slug) {
      return CAT_ICONS[slug]?.icon || 'bi bi-box'
    },

    getCatBg(slug) {
      return CAT_ICONS[slug]?.bg || 'rgba(100,116,139,0.15)'
    },
  }

}).mount('#app')
