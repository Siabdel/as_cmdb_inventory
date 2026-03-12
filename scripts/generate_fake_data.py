import random
import factory
from faker import Faker
from backend.inventory.models import Asset

fake = Faker()

class Command:
    help = 'Generate fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of assets to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        for _ in range(total):
            self.create_fake_asset()

    @staticmethod
    def create_fake_asset():
        asset_types = ['Laptop', 'Desktop', 'Server', 'Printer', 'Monitor', 'Router', 'Switch', 'UPS', 'Phone']
        asset = Asset(
            name=fake.company(),
            asset_type=random.choice(asset_types),
            serial_number=fake.uuid4(),
            purchase_date=fake.date_this_decade(),
            warranty_expiration=fake.future_date(end_date='+3y'),
            location=fake.address()
        )
        asset.save()
        print(f'Created asset: {asset.name}')