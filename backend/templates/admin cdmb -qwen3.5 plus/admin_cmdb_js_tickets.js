// static/admin_cmdb/js/tickets.js

const { createApp } = Vue;

// === APP LISTE DES TICKETS (KANBAN) ===
function initTicketsList() {
    const app = document.getElementById('tickets-app');
    if (!app) return;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                tickets: [],
                viewMode: 'kanban',
                filters: {
                    search: '',
                    priority: '',
                    assignee: '',
                    asset: ''
                },
                columns: [
                    { status: 'open', label: 'Ouvert', color: 'rgba(59, 130, 246, 0.2)' },
                    { status: 'assigned', label: 'Assigné', color: 'rgba(168, 85, 247, 0.2)' },
                    { status: 'in_progress', label: 'En cours', color: 'rgba(249, 115, 22, 0.2)' },
                    { status: 'waiting_parts', label: 'Attente pièces', color: 'rgba(234, 179, 8, 0.2)' },
                    { status: 'resolved', label: 'Résolu', color: 'rgba(34, 197, 94, 0.2)' },
                    { status: 'closed', label: 'Fermé', color: 'rgba(107, 114, 128, 0.2)' }
                ],
                technicians: [],
                recentAssets: [],
                stats: { open: 0, in_progress: 0, resolved: 0 },
                overdueCount: 0,
                showOverdueOnly: false,
                draggedTicket: null,
                dragOverColumn: null,
                searchTimeout: null
            }
        },
        computed: {
            totalTickets() {
                return this.tickets.length;
            },
            filteredTickets() {
                return this.tickets.filter(ticket => {
                    if (this.showOverdueOnly && !this.isOverdue(ticket)) return false;
                    if (this.filters.search && !ticket.subject.toLowerCase().includes(this.filters.search.toLowerCase())) return false;
                    if (this.filters.priority && ticket.priority !== this.filters.priority) return false;
                    if (this.filters.assignee && ticket.assignee_id !== this.filters.assignee) return false;
                    if (this.filters.asset && ticket.asset_id !== this.filters.asset) return false;
                    return true;
                });
            }
        },
        mounted() {
            this.fetchTickets();
            this.fetchTechnicians();
            this.fetchRecentAssets();
            this.fetchStats();
        },
        methods: {
            async fetchTickets() {
                try {
                    const res = await window.apiClient.get('/maintenance/tickets/');
                    this.tickets = res.data.results || res.data;
                } catch (error) {
                    console.error('Erreur fetch tickets:', error);
                }
            },
            async fetchTechnicians() {
                try {
                    const res = await window.apiClient.get('/auth/users/', { params: { role: 'technicien' } });
                    this.technicians = res.data;
                } catch (error) {
                    // Fallback
                    this.technicians = [];
                }
            },
            async fetchRecentAssets() {
                try {
                    const res = await window.apiClient.get('/inventory/assets/', { params: { page_size: 50 } });
                    this.recentAssets = res.data.results || res.data;
                } catch (error) {
                    this.recentAssets = [];
                }
            },
            async fetchStats() {
                try {
                    const res = await window.apiClient.get('/maintenance/tickets/stats/');
                    this.stats = res.data;
                    this.overdueCount = res.data.overdue || 0;
                } catch (error) {
                    this.calculateOverdue();
                }
            },
            calculateOverdue() {
                const now = new Date();
                this.overdueCount = this.tickets.filter(t => {
                    if (!t.due_date) return false;
                    return new Date(t.due_date) < now && t.status !== 'closed';
                }).length;
            },
            getTicketsByStatus(status) {
                return this.filteredTickets.filter(t => t.status === status);
            },
            getColumnCount(status) {
                return this.getTicketsByStatus(status).length;
            },
            isOverdue(ticket) {
                if (!ticket.due_date) return false;
                return new Date(ticket.due_date) < new Date() && ticket.status !== 'closed';
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
            getPriorityLabel(priority) {
                const map = {
                    'critique': '🔴 Critique',
                    'eleve': '🟠 Élevée',
                    'moyen': '🔵 Moyenne',
                    'bas': '⚪ Basse'
                };
                return map[priority] || '⚪ Basse';
            },
            getStatusClass(status) {
                const map = {
                    'open': 'status-active',
                    'assigned': 'status-stock',
                    'in_progress': 'status-maintenance',
                    'waiting_parts': 'status-maintenance',
                    'resolved': 'status-active',
                    'closed': 'status-retired'
                };
                return map[status] || 'status-retired';
            },
            getInitials(name) {
                if (!name) return '?';
                return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR');
            },
            debounceSearch() {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.fetchTickets();
                }, 300);
            },
            resetFilters() {
                this.filters = { search: '', priority: '', assignee: '', asset: '' };
                this.showOverdueOnly = false;
            },
            // Drag & Drop
            onDragStart(event, ticket) {
                this.draggedTicket = ticket;
                event.target.classList.add('dragging');
                event.dataTransfer.effectAllowed = 'move';
            },
            onDragEnd(event) {
                event.target.classList.remove('dragging');
                this.draggedTicket = null;
                this.dragOverColumn = null;
            },
            onDragOver(event) {
                event.preventDefault();
                event.dataTransfer.dropEffect = 'move';
            },
            onDragLeave(event) {
                this.dragOverColumn = null;
            },
            async onDrop(event, newStatus) {
                event.preventDefault();
                this.dragOverColumn = null;
                
                if (!this.draggedTicket) return;
                
                const ticket = this.draggedTicket;
                if (ticket.status === newStatus) return;
                
                try {
                    await window.apiClient.patch(`/maintenance/tickets/${ticket.id}/transition/`, {
                        to_status: newStatus
                    });
                    
                    // Update local state
                    ticket.status = newStatus;
                    this.fetchStats();
                    
                    // Feedback visuel
                    this.showNotification(`Ticket #${ticket.id} déplacé vers ${newStatus}`, 'success');
                } catch (error) {
                    console.error('Erreur transition:', error);
                    this.showNotification('Erreur lors du déplacement', 'error');
                }
            },
            showNotification(message, type) {
                // Simple notification (could use a toast library)
                console.log(`[${type}] ${message}`);
            }
        }
    }).mount('#tickets-app');
}

// === APP DÉTAIL TICKET ===
function initTicketDetail() {
    const app = document.getElementById('ticket-detail-app');
    if (!app) return;

    const ticketId = app.dataset.ticketId;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                ticketId: ticketId,
                ticket: window.ticketInitialData || {},
                comments: [],
                parts: [],
                statusHistory: [],
                technicians: [],
                stockItems: [],
                allowedTransitions: [],
                showAssignModal: false,
                showCommentModal: false,
                showPartsModal: false,
                assignTo: '',
                newComment: '',
                commentInternal: false,
                selectedPart: '',
                partQuantity: 1,
                laborRate: 50 // €/hour
            }
        },
        computed: {
            partsCost() {
                return this.parts.reduce((sum, p) => sum + (p.total_price || 0), 0);
            },
            laborCost() {
                return (this.ticket.hours_spent || 0) * this.laborRate;
            },
            totalCost() {
                return this.partsCost + this.laborCost;
            }
        },
        mounted() {
            this.fetchTicketDetail();
            this.fetchComments();
            this.fetchParts();
            this.fetchStatusHistory();
            this.fetchTechnicians();
            this.fetchStockItems();
            this.fetchAllowedTransitions();
        },
        methods: {
            async fetchTicketDetail() {
                try {
                    const res = await window.apiClient.get(`/maintenance/tickets/${this.ticketId}/`);
                    this.ticket = { ...this.ticket, ...res.data };
                } catch (error) {
                    console.error('Erreur fetch ticket:', error);
                }
            },
            async fetchComments() {
                try {
                    const res = await window.apiClient.get(`/maintenance/tickets/${this.ticketId}/comments/`);
                    this.comments = res.data.results || res.data;
                } catch (error) {
                    this.comments = [];
                }
            },
            async fetchParts() {
                try {
                    const res = await window.apiClient.get(`/maintenance/tickets/${this.ticketId}/parts/`);
                    this.parts = res.data.results || res.data;
                } catch (error) {
                    this.parts = [];
                }
            },
            async fetchStatusHistory() {
                try {
                    const res = await window.apiClient.get(`/maintenance/tickets/${this.ticketId}/history/`);
                    this.statusHistory = res.data;
                } catch (error) {
                    this.statusHistory = [];
                }
            },
            async fetchTechnicians() {
                try {
                    const res = await window.apiClient.get('/auth/users/');
                    this.technicians = res.data;
                } catch (error) {
                    this.technicians = [];
                }
            },
            async fetchStockItems() {
                try {
                    const res = await window.apiClient.get('/stock/items/');
                    this.stockItems = res.data.results || res.data;
                } catch (error) {
                    this.stockItems = [];
                }
            },
            async fetchAllowedTransitions() {
                // Transitions autorisées selon le statut actuel
                const transitionsMap = {
                    'open': ['assigned', 'in_progress', 'closed'],
                    'assigned': ['in_progress', 'open', 'closed'],
                    'in_progress': ['waiting_parts', 'resolved', 'assigned'],
                    'waiting_parts': ['in_progress', 'resolved'],
                    'resolved': ['closed', 'in_progress'],
                    'closed': ['open']
                };
                
                const allowed = transitionsMap[this.ticket.status] || [];
                this.allowedTransitions = allowed.map(to => ({ to }));
            },
            async transitionTicket(toStatus) {
                if (!confirm(`Changer le statut vers "${toStatus}" ?`)) return;
                
                try {
                    await window.apiClient.patch(`/maintenance/tickets/${this.ticketId}/transition/`, {
                        to_status: toStatus
                    });
                    this.ticket.status = toStatus;
                    this.fetchAllowedTransitions();
                    this.fetchStatusHistory();
                    alert('Statut mis à jour');
                } catch (error) {
                    alert('Erreur lors de la transition');
                }
            },
            async assignTicket() {
                if (!this.assignTo) return;
                
                try {
                    await window.apiClient.post(`/maintenance/tickets/${this.ticketId}/assign/`, {
                        assignee_id: this.assignTo
                    });
                    this.ticket.assignee = this.technicians.find(t => t.id === this.assignTo)?.username;
                    this.showAssignModal = false;
                    this.assignTo = '';
                    alert('Ticket assigné');
                } catch (error) {
                    alert('Erreur lors de l\'assignation');
                }
            },
            async addComment() {
                if (!this.newComment.trim()) return;
                
                try {
                    await window.apiClient.post(`/maintenance/tickets/${this.ticketId}/comments/`, {
                        content: this.newComment,
                        is_internal: this.commentInternal
                    });
                    this.fetchComments();
                    this.showCommentModal = false;
                    this.newComment = '';
                    this.commentInternal = false;
                } catch (error) {
                    alert('Erreur lors de l\'ajout du commentaire');
                }
            },
            async addPart() {
                if (!this.selectedPart || this.partQuantity < 1) return;
                
                try {
                    await window.apiClient.post(`/maintenance/tickets/${this.ticketId}/parts/`, {
                        item_id: this.selectedPart,
                        quantity: this.partQuantity
                    });
                    this.fetchParts();
                    this.showPartsModal = false;
                    this.selectedPart = '';
                    this.partQuantity = 1;
                } catch (error) {
                    alert('Erreur lors de l\'ajout de la pièce');
                }
            },
            isOverdue() {
                if (!this.ticket.due_date) return false;
                return new Date(this.ticket.due_date) < new Date() && this.ticket.status !== 'closed';
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
            getPriorityLabel(priority) {
                const map = {
                    'critique': '🔴 Critique',
                    'eleve': '🟠 Élevée',
                    'moyen': '🔵 Moyenne',
                    'bas': '⚪ Basse'
                };
                return map[priority] || '⚪ Basse';
            },
            getStatusClass(status) {
                const map = {
                    'open': 'status-active',
                    'assigned': 'status-stock',
                    'in_progress': 'status-maintenance',
                    'waiting_parts': 'status-maintenance',
                    'resolved': 'status-active',
                    'closed': 'status-retired'
                };
                return map[status] || 'status-retired';
            },
            getTransitionButtonClass(status) {
                const map = {
                    'assigned': 'btn-outline-primary',
                    'in_progress': 'btn-outline-warning',
                    'waiting_parts': 'btn-outline-warning',
                    'resolved': 'btn-outline-success',
                    'closed': 'btn-outline-secondary',
                    'open': 'btn-outline-primary'
                };
                return map[status] || 'btn-outline-primary';
            },
            getTransitionLabel(status) {
                const map = {
                    'assigned': '👤 Assigner',
                    'in_progress': '🔧 En cours',
                    'waiting_parts': '📦 Attente pièces',
                    'resolved': '✅ Résoudre',
                    'closed': '🔒 Fermer',
                    'open': '📋 Rouvrir'
                };
                return map[status] || status;
            },
            getInitials(name) {
                if (!name) return '?';
                return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
            },
            formatDate(dateStr) {
                if (!dateStr) return '-';
                return new Date(dateStr).toLocaleDateString('fr-FR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
            },
            formatCurrency(amount) {
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount);
            }
        }
    }).mount('#ticket-detail-app');
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    initTicketsList();
    initTicketDetail();
});