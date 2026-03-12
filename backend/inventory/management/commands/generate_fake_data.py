from django.core.management.base import BaseCommand
from faker import Faker
from inventory.models import Asset, Category, Brand, Location, Tag
import random

fake = Faker()


class Command(BaseCommand):
    help = 'Generate fake data for testing the CMDB'

    def add_arguments(self, parser):
        parser.add_argument('--num_assets', type=int, default=100, help='Number of assets to create')

    def handle(self, *args, **options):
        num_assets = options['num_assets']

        # Create some categories
        categories = [
            Category.objects.create(name='Ordinateurs', slug='ordinateurs'),
            Category.objects.create(name='Serveurs', slug='serveurs'),
            Category.objects.create(name='Réseaux', slug='reseaux'),
            Category.objects.create(name='Périphériques', slug='peripheriques'),
        ]

        # Create some brands
        brands = [
            Brand.objects.create(name='Dell'),
            Brand.objects.create(name='HP'),
            Brand.objects.create(name='Lenovo'),
            Brand.objects.create(name='Apple'),
        ]

        # Create some locations
        locations = [
            Location.objects.create(name='Bureau 1', type='bureau'),
            Location.objects.create(name='Salle de serveurs', type='salle'),
            Location.objects.create(name='Placard 1', type='placard'),
        ]

        # Create some tags
        tags = [
            Tag.objects.create(name='Critique', color='#FF0000'),
            Tag.objects.create(name='Maintenance', color='#FFA500'),
            Tag.objects.create(name='Stock', color='#008000'),
        ]

        # Generate fake assets
        for _ in range(num_assets):
            category = random.choice(categories)
            brand = random.choice(brands)
            location = random.choice(locations)
            tags_for_asset = random.sample(tags, random.randint(0, len(tags)))

            asset = Asset.objects.create(
                name=fake.company(),
                category=category,
                brand=brand,
                model=fake.word(),
                serial_number=fake.bothify(text='????-######'),
                description=fake.text(max_nb_chars=200),
                purchase_date=fake.date_between(start_date='-5y', end_date='today'),
                purchase_price=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
                warranty_end=fake.date_between(start_date='today', end_date='+5y'),
                current_location=location,
                assigned_to=None,
                status=random.choice(Asset.STATUS_CHOICES)[0],
                condition_state=random.choice(Asset.CONDITION_CHOICES)[0],
            )

            asset.tags.set(tags_for_asset)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_assets} assets'))