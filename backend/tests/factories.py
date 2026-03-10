"""
Factories pour générer des données de test avec factory-boy
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.auth.models import User

from inventory.models import (
    Location, Category, Brand, Tag, Asset, AssetMovement
)

fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory pour User"""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = "testpass123"


class LocationFactory(DjangoModelFactory):
    """Factory pour Location"""
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: f"Location {n}")
    type = factory.Iterator([
        'placard', 'salle', 'bureau', 'entrepot', 'batiment'
    ])
    parent = None


class CategoryFactory(DjangoModelFactory):
    """Factory pour Category"""
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Catégorie {n}")
    slug = factory.Sequence(lambda n: f"categorie-{n}")
    parent = None


class BrandFactory(DjangoModelFactory):
    """Factory pour Brand"""
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f"Marque {n}")
    logo = None


class TagFactory(DjangoModelFactory):
    """Factory pour Tag"""
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")
    color = factory.Iterator([
        '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'
    ])


class AssetFactory(DjangoModelFactory):
    """Factory pour Asset"""
    class Meta:
        model = Asset

    name = factory.Sequence(lambda n: f"Asset {n}")
    internal_code = factory.Sequence(lambda n: f"AST-{n:04d}")
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    current_location = factory.SubFactory(LocationFactory)
    status = factory.Iterator([
        'stock', 'en_service', 'hors_service', 'en_maintenance',
        'en_reparation', 'en_transit', 'en_attente', 'en_retour',
        'en_pret', 'en_location', 'en_garantie', 'hors_garantie'
    ])
    condition_state = factory.Iterator([
        'neuf', 'excellent', 'bon', 'moyen', 'mauvais', 'hors_service'
    ])
    purchase_date = factory.LazyFunction(
        lambda: fake.date_between(start_date='-2y', end_date='today')
    )
    purchase_price = factory.LazyFunction(
        lambda: round(fake.random_number(digits=5, fix_len=True), 2)
    )
    warranty_end = factory.LazyFunction(
        lambda: fake.date_between(start_date='today', end_date='+2y')
    )
    serial_number = factory.Sequence(lambda n: f"SN-{fake.uuid4()[:8]}-{n}")
    notes = factory.LazyFunction(
        lambda: fake.text(max_nb_chars=200) if fake.boolean(30) else None
    )
    assigned_to = None


class AssetMovementFactory(DjangoModelFactory):
    """Factory pour AssetMovement"""
    class Meta:
        model = AssetMovement

    asset = factory.SubFactory(AssetFactory)
    from_location = factory.SubFactory(LocationFactory)
    to_location = factory.SubFactory(LocationFactory)
    moved_by = factory.SubFactory(UserFactory)
    move_type = factory.Iterator([
        'move', 'entry', 'exit', 'assignment', 'return',
        'maintenance', 'disposal', 'sale', 'transfer'
    ])
    note = factory.LazyFunction(
        lambda: fake.text(max_nb_chars=100) if fake.boolean(50) else None
    )