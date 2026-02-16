"""
Modèles de maintenance et valorisation pour l'application CMDB Inventory
"""

from django.db import models
from django.contrib.auth.models import User


class MaintenanceType(models.Model):
    """Types de maintenance (Réparation, Préventive, Upgrade)"""
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    is_preventive = models.BooleanField(default=False, verbose_name="Est préventive")
    estimated_duration_hours = models.FloatField(null=True, blank=True, verbose_name="Durée estimée (heures)")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Type de maintenance"
        verbose_name_plural = "Types de maintenance"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MaintenanceTicket(models.Model):
    """Tickets de maintenance pour les équipements"""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Basse'),
        ('MED', 'Moyenne'),
        ('HIGH', 'Haute'),
        ('URGENT', 'Urgente')
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Ouvert'),
        ('IN_PROGRESS', 'En cours'),
        ('CLOSED', 'Fermé'),
        ('CANCELLED', 'Annulé')
    ]
    
    asset = models.ForeignKey(
        'inventory.Asset',
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name="Équipement"
    )
    maintenance_type = models.ForeignKey(
        MaintenanceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Type de maintenance"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MED',
        verbose_name="Priorité"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN',
        verbose_name="Statut"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets',
        verbose_name="Créé par"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name="Assigné à"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    due_date = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fermé le")
    
    class Meta:
        verbose_name = "Ticket de maintenance"
        verbose_name_plural = "Tickets de maintenance"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', '-created_at']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"#{self.id} - {self.asset.internal_code} - {self.title}"
    
    @property
    def total_cost(self):
        """Coût total des actions de maintenance"""
        return sum(action.cost_euros for action in self.actions.all())
    
    @property
    def duration_hours(self):
        """Durée totale des actions de maintenance"""
        return sum(action.duration_hours or 0 for action in self.actions.all())


class MaintenanceAction(models.Model):
    """Actions de maintenance réalisées"""
    
    ACTION_CHOICES = [
        ('INSTALLED', 'Installé'),
        ('REPAIRED', 'Réparé'),
        ('MAINTENANCE', 'Maintenance'),
        ('BROKEN', 'Panne déclarée'),
        ('SOLD', 'Vendu'),
        ('UPGRADED', 'Amélioré/Upgradé'),
        ('INSPECTED', 'Inspecté'),
        ('CLEANED', 'Nettoyé'),
        ('REPLACED', 'Remplacé')
    ]
    
    ticket = models.ForeignKey(
        MaintenanceTicket,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="Ticket"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Type d'action"
    )
    description = models.TextField(verbose_name="Description")
    cost_euros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Coût (€)"
    )
    duration_hours = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Durée (heures)"
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='maintenance_actions',
        verbose_name="Réalisé par"
    )
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de réalisation")
    before_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Statut avant"
    )
    after_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Statut après"
    )
    parts_used = models.TextField(
        blank=True,
        verbose_name="Pièces utilisées"
    )
    
    class Meta:
        verbose_name = "Action de maintenance"
        verbose_name_plural = "Actions de maintenance"
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.ticket.asset.internal_code} - {self.get_action_type_display()} - {self.performed_at.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Sauvegarder l'ancien statut avant modification
        if not self.before_status:
            self.before_status = self.ticket.asset.status
        
        super().save(*args, **kwargs)
        
        # Auto-mise à jour du statut de l'asset
        if self.after_status:
            self.ticket.asset.status = self.after_status
            self.ticket.asset.save(update_fields=['status'])
        
        # Mettre à jour le statut du ticket si fermé
        if self.action_type in ['SOLD', 'REPLACED'] and self.ticket.status == 'OPEN':
            self.ticket.status = 'CLOSED'
            self.ticket.save(update_fields=['status'])
