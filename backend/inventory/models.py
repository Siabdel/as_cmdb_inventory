from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# ── Mixin abstrait ─────────────────────────────────────────
class TimeStampMixin(models.Model):
    """Mixin réutilisable : created_at + updated_at sur tous les models."""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # ← pas de table créée


# ── Profile utilisateur avec rôle ─────────────────────────────────────────
class UserProfile(models.Model):
    """Profile utilisateur avec rôle personnalisé."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=50,
        choices=[
            ('technician', 'Technicien'),
            ('admin', 'Administrateur'),
            ('manager', 'Gestionnaire'),
        ],
        default='technician'
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


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
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactif'
        MAINTENANCE = 'maintenance', 'En maintenance'
        REPAIR = 'repair', 'En réparation'
        BROKEN = 'broken', 'En panne'
        ARCHIVED = 'archived', 'Archivé'
    
    class Condition(models.TextChoices):
        NEW = 'new', 'Neuf'
        USED = 'used', 'Occasion'
        DAMAGED = 'damaged', 'Endommagé'

    name             = models.CharField(max_length=100)
    internal_code    = models.CharField(max_length=50, unique=True, blank=True, null=True)
    category         = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                         null=True, related_name='assets')
    brand            = models.ForeignKey(Brand, on_delete=models.SET_NULL,
                                         null=True, related_name='assets')
    model            = models.CharField(max_length=100)
    serial_number    = models.CharField(max_length=150, unique=True, blank=True)
    description      = models.TextField(blank=True, null=True)
    purchase_date    = models.DateField(blank=True, null=True)
    purchase_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    warranty_end     = models.DateField(blank=True, null=True)
    current_location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                         null=True, related_name='assets')
    assigned_to      = models.CharField(max_length=100, blank=True, null=True)
    status           = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    condition_state  = models.CharField(max_length=10, choices=Condition.choices, default=Condition.NEW)
    tags             = models.ManyToManyField(Tag, blank=True)
    photo            = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} [{self.serial_number}]"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        import uuid
        # Générer un internal_code s'il est vide
        if not self.internal_code:
            # Format: CI-YYYYMMDD-HHMMSS-XXXX (XXXX aléatoire)
            timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
            random_suffix = uuid.uuid4().hex[:4].upper()
            self.internal_code = f"CI-{timestamp}-{random_suffix}"
        # Générer un serial_number s'il est vide
        if not self.serial_number:
            # Format: SR-YYYYMMDD-HHMMSS-XXXX
            timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
            random_suffix = uuid.uuid4().hex[:4].upper()
            self.serial_number = f"SR-{timestamp}-{random_suffix}"
        super().save(*args, **kwargs)


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
