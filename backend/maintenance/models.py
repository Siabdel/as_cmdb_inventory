"""
Modèles de maintenance et valorisation pour l'application CMDB Inventory
"""
from django.db import models
from django.utils import timezone
from inventory.models import Asset, TimeStampMixin


class MaintenanceTicket(TimeStampMixin):

    PRIORITY_CHOICES = [
        ('low',      'Faible'),
        ('medium',   'Moyen'),
        ('high',     'Élevé'),
        ('critical', 'Critique'),
    ]

    STATUS_CHOICES = [
        ('open',           'Ouvert'),
        ('assigned',       'Assigné'),
        ('in_progress',    'En cours'),
        ('waiting_parts',  'Attente pièces'),
        ('pending_review', 'En attente validation'),
        ('resolved',       'Résolu'),
        ('closed',         'Fermé'),
        ('cancelled',      'Annulé'),
    ]

    TYPE_CHOICES = [
        ('repair',      'Réparation'),
        ('diagnostic',  'Diagnostic'),
        ('upgrade',     'Upgrade'),
        ('preventive',  'Préventif'),
        ('cleaning',    'Nettoyage'),
    ]

    # Transitions autorisées : {statut_actuel: [statuts_suivants]}
    ALLOWED_TRANSITIONS = {
        'open':           ['assigned', 'cancelled'],
        'assigned':       ['in_progress', 'cancelled'],
        'in_progress':    ['waiting_parts', 'pending_review', 'cancelled'],
        'waiting_parts':  ['in_progress', 'cancelled'],
        'pending_review': ['resolved', 'in_progress'],
        'resolved':       ['closed', 'in_progress'],  # réouverture possible
        'closed':         [],
        'cancelled':      [],
    }

    ticket_number    = models.CharField(max_length=20, unique=True, blank=True)
    asset            = models.ForeignKey(Asset, on_delete=models.CASCADE,
                                         related_name='tickets')
    title            = models.CharField(max_length=200)
    description      = models.TextField()
    ticket_type      = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                        default='repair')
    priority         = models.CharField(max_length=10, choices=PRIORITY_CHOICES,
                                        default='medium')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                        default='open')
    assigned_tech    = models.CharField(max_length=100, blank=True)
    reported_by      = models.CharField(max_length=100, blank=True)
    due_date         = models.DateField(null=True, blank=True)
    resolved_at      = models.DateTimeField(null=True, blank=True)
    closed_at        = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    labor_cost       = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket de maintenance'
        verbose_name_plural = 'Tickets de maintenance'

    def __str__(self):
        return f"[{self.ticket_number}] {self.title} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # Auto-génération du numéro de ticket
        if not self.ticket_number:
            year = timezone.now().year
            last = MaintenanceTicket.objects.filter(
                ticket_number__startswith=f"TKT-{year}-"
            ).count()
            self.ticket_number = f"TKT-{year}-{last + 1:04d}"
        super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status, user='', notes=''):
        """Effectue la transition avec validation + timestamps automatiques."""
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Transition '{self.status}' → '{new_status}' non autorisée."
            )
        old_status = self.status
        self.status = new_status

        # Timestamps automatiques
        if new_status == 'resolved':
            self.resolved_at = timezone.now()
        if new_status == 'closed':
            self.closed_at = timezone.now()
        # Réouverture : reset resolved_at
        if old_status in ('resolved', 'closed') and new_status == 'in_progress':
            self.resolved_at = None
            self.closed_at = None

        self.save(update_fields=['status', 'resolved_at', 'closed_at', 'updated_at'])

        # Enregistrer dans l'historique
        StatusHistory.objects.create(
            ticket=self,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            notes=notes,
        )
        return self

    @property
    def total_cost(self):
        parts_cost = sum(p.total_cost for p in self.parts.all())
        return self.labor_cost + parts_cost

    @property
    def is_overdue(self):
        if self.due_date and self.status not in ('resolved', 'closed', 'cancelled'):
            return timezone.now().date() > self.due_date
        return False


class StatusHistory(TimeStampMixin):
    """Historique complet des transitions de statut."""
    ticket      = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE,
                                    related_name='status_history')
    from_status = models.CharField(max_length=20)
    to_status   = models.CharField(max_length=20)
    changed_by  = models.CharField(max_length=100, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historique statut'

    def __str__(self):
        return f"{self.ticket.ticket_number}: {self.from_status} → {self.to_status}"


class TicketPart(TimeStampMixin):
    """Pièces détachées consommées pour un ticket."""
    ticket    = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE,
                                  related_name='parts')
    part_name = models.CharField(max_length=200)
    part_ref  = models.CharField(max_length=100, blank=True)
    quantity  = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Pièce utilisée'

    def __str__(self):
        return f"{self.part_name} x{self.quantity}"

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost


class TicketComment(TimeStampMixin):
    """Journal d'activité / commentaires technicien."""
    ticket      = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE,
                                    related_name='comments')
    author      = models.CharField(max_length=100)
    content     = models.TextField()
    is_internal = models.BooleanField(default=False)  # note interne technicien

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Commentaire ticket'

    def __str__(self):
        return f"{self.ticket.ticket_number} — {self.author}"
