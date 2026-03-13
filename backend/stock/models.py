# stock/models.py
from django.db import models
from inventory.models import Brand, Location, TimeStampMixin


class StockItem(TimeStampMixin):

    ITEM_TYPE = [
        ('spare_part',  'Pièce détachée'),
        ('consumable',  'Consommable'),
        ('accessory',   'Accessoire'),
        ('tool',        'Outil'),
    ]

    name         = models.CharField(max_length=200)
    reference    = models.CharField(max_length=100, unique=True)
    item_type    = models.CharField(max_length=20, choices=ITEM_TYPE,
                                    default='spare_part')
    brand        = models.ForeignKey(Brand, null=True, blank=True,
                                     on_delete=models.SET_NULL,
                                     related_name='stock_items')
    description  = models.TextField(blank=True)
    quantity     = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=2)   # seuil alerte
    unit_price   = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    location     = models.ForeignKey(Location, null=True, blank=True,
                                     on_delete=models.SET_NULL,
                                     related_name='stock_items')
    photo        = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Article stock'
        verbose_name_plural = 'Articles stock'

    def __str__(self):
        return f"{self.name} ({self.reference}) — {self.quantity} unités"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity

    @property
    def total_value(self):
        return self.quantity * self.unit_price


class StockMovement(TimeStampMixin):

    MOVEMENT_TYPE = [
        ('in',         'Entrée'),
        ('out',        'Sortie'),
        ('adjustment', 'Ajustement'),
        ('transfer',   'Transfert'),
    ]

    item          = models.ForeignKey(StockItem, on_delete=models.CASCADE,
                                      related_name='movements')
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPE)
    quantity      = models.IntegerField()           # positif ou négatif
    reason        = models.CharField(max_length=200, blank=True)
    done_by       = models.CharField(max_length=100)
    ticket        = models.ForeignKey(
                        'maintenance.MaintenanceTicket',
                        null=True, blank=True,
                        on_delete=models.SET_NULL,
                        related_name='stock_movements'
                    )
    reference_doc = models.CharField(max_length=100, blank=True)  # BL, facture...

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mouvement stock'

    def __str__(self):
        sign = '+' if self.quantity > 0 else ''
        return f"{self.item.name} {sign}{self.quantity} ({self.get_movement_type_display()})"

    def save(self, *args, **kwargs):
        """Met à jour la quantité de l'article automatiquement."""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            StockItem.objects.filter(pk=self.item_id).update(
                quantity=models.F('quantity') + self.quantity
            )
