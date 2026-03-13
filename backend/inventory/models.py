from django.db import models
from django.utils import timezone


# ── Mixin abstrait ─────────────────────────────────────────
class TimeStampMixin(models.Model):
    """Mixin réutilisable : created_at + updated_at sur tous les models."""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # ← pas de table créée


# ── Models ─────────────────────────────────────────────────
class Category(TimeStampMixin):  # ← hérite du mixin
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    icon        = models.CharField(max_length=100, default='laptop', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Brand(TimeStampMixin):
    name    = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True, null=True)
    logo    = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Location(TimeStampMixin):
    name        = models.CharField(max_length=100)
    type        = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    parent      = models.ForeignKey('self', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='children')

    class Meta:
        unique_together = ['name', 'type']

    def __str__(self):
        return f"{self.name} ({self.type})"


class Tag(TimeStampMixin):
    name        = models.CharField(max_length=100, unique=True)
    color       = models.CharField(max_length=7, default='#3498db')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Asset(TimeStampMixin):
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    CONDITION_CHOICES = [
        ('new',     'New'),
        ('used',    'Used'),
        ('damaged', 'Damaged'),
    ]

    name             = models.CharField(max_length=100)
    category         = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                         null=True, related_name='assets')
    brand            = models.ForeignKey(Brand, on_delete=models.SET_NULL,
                                         null=True, related_name='assets')
    model            = models.CharField(max_length=100)
    serial_number    = models.CharField(max_length=150, unique=True)
    description      = models.TextField(blank=True, null=True)
    purchase_date    = models.DateField(blank=True, null=True)
    purchase_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    warranty_end     = models.DateField(blank=True, null=True)
    current_location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                         null=True, related_name='assets')
    assigned_to      = models.CharField(max_length=100, blank=True, null=True)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    condition_state  = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
    tags             = models.ManyToManyField(Tag, blank=True)
    photo            = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} [{self.serial_number}]"


class AssetMovement(TimeStampMixin):
    asset         = models.ForeignKey(Asset, on_delete=models.CASCADE,
                                      related_name='movements')
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                      null=True, related_name='movements_from')
    to_location   = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                      null=True, related_name='movements_to')
    moved_by      = models.CharField(max_length=100)
    moved_at      = models.DateTimeField(default=timezone.now)
    notes         = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-moved_at']

    def __str__(self):
        return f"{self.asset.name} → {self.to_location} ({self.moved_at:%Y-%m-%d})"
