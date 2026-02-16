"""
Modèles Django pour l'application CMDB Inventory
"""

import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
from PIL import Image


class Location(models.Model):
    """Modèle pour les emplacements physiques"""
    
    LOCATION_TYPES = [
        ('placard', 'Placard'),
        ('salle', 'Salle'),
        ('bureau', 'Bureau'),
        ('entrepot', 'Entrepôt'),
        ('externe', 'Externe'),
        ('vehicule', 'Véhicule'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    type = models.CharField(
        max_length=50, 
        choices=LOCATION_TYPES, 
        verbose_name="Type"
    )
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Emplacement parent"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Emplacement"
        verbose_name_plural = "Emplacements"
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """Retourne le chemin complet de l'emplacement"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(path)


class Category(models.Model):
    """Modèle pour les catégories d'équipements"""
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Catégorie parent"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Modèle pour les marques d'équipements"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    website = models.URLField(blank=True, verbose_name="Site web")
    logo = models.ImageField(
        upload_to='brands/', 
        blank=True, 
        null=True, 
        verbose_name="Logo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Modèle pour les étiquettes/tags"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    color = models.CharField(
        max_length=7, 
        default='#007bff', 
        verbose_name="Couleur",
        help_text="Code couleur hexadécimal (ex: #007bff)"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Étiquette"
        verbose_name_plural = "Étiquettes"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Asset(models.Model):
    """Modèle principal pour les équipements/actifs"""
    
    STATUS_CHOICES = [
        ('neuf', 'Neuf'),
        ('stock', 'En stock'),
        ('installe', 'Installé'),
        ('use', 'En utilisation'),
        ('broken', 'En panne'),
        ('maintenance', 'En maintenance'),
        ('reparation', 'En réparation'),
        ('ok', 'OK'),
        ('occasion', 'Occasion'),
        ('sold', 'Vendu'),
        ('disposed', 'Mis au rebut/Jeté'),
        ('lost', 'Perdu'),
        ('hs', 'Hors service'),
    ]
    
    CONDITION_CHOICES = [
        ('NEUF', 'Neuf'),
        ('EXCELLENT', 'Excellent'),
        ('BON', 'Bon'),
        ('MOYEN', 'Moyen'),
        ('POUR_PIECES', 'Pour pièces'),
        ('HS', 'Hors service'),
    ]
    
    # Identifiants
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name="ID"
    )
    internal_code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Code interne",
        help_text="Code unique interne (ex: PC-001)"
    )
    
    # Informations de base
    name = models.CharField(max_length=200, verbose_name="Nom")
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assets',
        verbose_name="Catégorie"
    )
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assets',
        verbose_name="Marque"
    )
    model = models.CharField(max_length=100, blank=True, verbose_name="Modèle")
    serial_number = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Numéro de série"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Informations financières
    purchase_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Date d'achat"
    )
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Prix d'achat"
    )
    warranty_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin de garantie"
    )
    
    # Valorisation et état
    price_new_euros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Prix neuf (€)"
    )
    price_occasion_euros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Prix occasion (€)"
    )
    condition_state = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='NEUF',
        verbose_name="État"
    )
    
    # Statut et localisation
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='stock',
        verbose_name="Statut"
    )
    current_location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assets',
        verbose_name="Emplacement actuel"
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_assets',
        verbose_name="Assigné à"
    )
    
    # Relations et métadonnées
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='assets',
        verbose_name="Étiquettes"
    )
    qr_code_image = models.ImageField(
        upload_to='qr_codes/', 
        blank=True, 
        null=True,
        verbose_name="QR Code"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['internal_code']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.internal_code} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Générer le code interne si pas défini
        if not self.internal_code:
            self.internal_code = self.generate_internal_code()
        
        super().save(*args, **kwargs)
        
        # Générer le QR code après la sauvegarde
        if not self.qr_code_image:
            self.generate_qr_code()
    
    def generate_internal_code(self):
        """Génère un code interne unique"""
        if self.category:
            prefix = self.category.name[:3].upper()
        else:
            prefix = "AST"
        
        # Trouver le prochain numéro disponible
        last_asset = Asset.objects.filter(
            internal_code__startswith=prefix
        ).order_by('internal_code').last()
        
        if last_asset:
            try:
                last_number = int(last_asset.internal_code.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{prefix}-{next_number:03d}"
    
    def generate_qr_code(self):
        """Génère le QR code pour l'asset"""
        if not self.id:
            return
        
        # URL vers la page de détail de l'asset
        qr_data = f"{settings.QR_CODE_BASE_URL}/{self.id}/"
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Créer l'image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder dans un buffer
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Créer le fichier Django
        filename = f"qr_{self.internal_code}.png"
        self.qr_code_image.save(
            filename,
            File(buffer),
            save=False
        )
        
        # Sauvegarder sans déclencher une nouvelle génération
        Asset.objects.filter(id=self.id).update(
            qr_code_image=self.qr_code_image
        )
    
    @property
    def is_warranty_expired(self):
        """Vérifie si la garantie est expirée"""
        if not self.warranty_end:
            return None
        from django.utils import timezone
        return self.warranty_end < timezone.now().date()
    
    @property
    def warranty_status(self):
        """Retourne le statut de la garantie"""
        if not self.warranty_end:
            return "Non définie"
        
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        days_remaining = (self.warranty_end - today).days
        
        if days_remaining < 0:
            return "Expirée"
        elif days_remaining <= 30:
            return "Expire bientôt"
        else:
            return "Valide"


class AssetMovement(models.Model):
    """Modèle pour l'historique des mouvements d'équipements"""
    
    MOVE_TYPES = [
        ('move', 'Déplacement'),
        ('entry', 'Entrée en stock'),
        ('assignment', 'Attribution'),
        ('return', 'Retour'),
        ('maintenance', 'Envoi en maintenance'),
        ('disposal', 'Mise au rebut'),
        ('sale', 'Vente'),
    ]
    
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="Équipement"
    )
    from_location = models.ForeignKey(
        Location, 
        related_name='movements_from', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Emplacement source"
    )
    to_location = models.ForeignKey(
        Location, 
        related_name='movements_to',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Emplacement destination"
    )
    moved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='movements_made',
        verbose_name="Déplacé par"
    )
    move_type = models.CharField(
        max_length=20, 
        choices=MOVE_TYPES, 
        default='move',
        verbose_name="Type de mouvement"
    )
    note = models.TextField(blank=True, verbose_name="Note")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    
    class Meta:
        verbose_name = "Mouvement d'équipement"
        verbose_name_plural = "Mouvements d'équipements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', '-created_at']),
            models.Index(fields=['move_type']),
        ]
    
    def __str__(self):
        return f"{self.asset.internal_code} - {self.get_move_type_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Mettre à jour l'emplacement de l'asset si nécessaire
        if self.to_location and self.asset.current_location != self.to_location:
            Asset.objects.filter(id=self.asset.id).update(
                current_location=self.to_location
            )