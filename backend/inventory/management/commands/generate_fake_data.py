import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from inventory.models import Asset, Category, Brand, Location, Tag, AssetMovement
from faker import Faker

fake = Faker('fr_FR')

CATEGORIES = [
    ('Serveur', 'server'),
    ('PC Portable', 'laptop'),
    ('PC Fixe', 'desktop'),
    ('Routeur', 'router'),
    ('Switch', 'switch'),
    ('Écran', 'monitor'),
    ('Imprimante', 'printer'),
    ('Téléphone IP', 'phone'),
    ('NAS', 'nas'),
    ('Onduleur', 'ups'),
]

BRANDS = [
    ('Dell', 'https://dell.com'),
    ('HP', 'https://hp.com'),
    ('Cisco', 'https://cisco.com'),
    ('Lenovo', 'https://lenovo.com'),
    ('Asus', 'https://asus.com'),
    ('Brother', 'https://brother.com'),
    ('Apple', 'https://apple.com'),
    ('Samsung', 'https://samsung.com'),
    ('Synology', 'https://synology.com'),
    ('APC', 'https://apc.com'),
]

LOCATIONS = [
    ('DataCenter Lyon',   'datacenter'),
    ('Bureau Direction',  'office'),
    ('Salle Réunion A',   'office'),
    ('Salle Réunion B',   'office'),
    ('Stock IT',          'warehouse'),
    ('Agence Casablanca', 'office'),
    ('Salle Serveurs',    'datacenter'),
    ('Open Space Dev',    'office'),
    ('Reception',         'office'),
    ('Stockage Archive',  'warehouse'),
]

TAGS = [
    ('Prod',     '#e74c3c'),
    ('Test',     '#3498db'),
    ('Critical', '#e67e22'),
    ('Legacy',   '#95a5a6'),
    ('Hot',      '#e91e63'),
    ('Cold',     '#00bcd4'),
    ('Spare',    '#8e44ad'),
    ('EOL',      '#c0392b'),
]

ASSET_MODELS = {
    'Dell':     ['OptiPlex 7090', 'Latitude 5520', 'PowerEdge R740', 'UltraSharp U2722'],
    'HP':       ['EliteBook 840 G8', 'ProDesk 600', 'ProLiant DL380', 'LaserJet Pro'],
    'Cisco':    ['Catalyst 9200', 'ISR 4331', 'ASA 5506-X', 'Meraki MX68'],
    'Lenovo':   ['ThinkPad X1 Carbon', 'ThinkCentre M90', 'ThinkSystem SR650'],
    'Asus':     ['ZenBook 14', 'ExpertCenter D7', 'RT-AX88U'],
    'Brother':  ['MFC-L8900CDW', 'HL-L6400DW', 'DCP-L2550DN'],
    'Apple':    ['MacBook Pro M3', 'Mac Mini M2', 'iPhone 15 Pro'],
    'Samsung':  ['Galaxy Tab S9', 'Odyssey G7', 'T7 Shield SSD'],
    'Synology': ['DS923+', 'RS1221+', 'DS220+'],
    'APC':      ['Smart-UPS 1500', 'Back-UPS 650', 'Smart-UPS 3000'],
}
tags = []
for name, color in TAGS:
    obj, _ = Tag.objects.get_or_create(
        name=name,
        defaults={
            'color': color,
            'description': fake.sentence()  # ← ajouté
        }
    )
    tags.append(obj)


class Command(BaseCommand):
    help = "Génère données fake réalistes pour l'inventaire IT"

    def add_arguments(self, parser):
        parser.add_argument('--assets',    type=int, default=100)
        parser.add_argument('--movements', type=int, default=200)
        parser.add_argument('--flush',     action='store_true',
                            help='Vider les tables avant génération')

    def handle(self, *args, **options):  # ← TOUT ce qui suit doit être indenté ici

        if options['flush']:
            self.stdout.write(self.style.WARNING('🗑️  Flush...'))
            AssetMovement.objects.all().delete()
            Asset.objects.all().delete()
            Tag.objects.all().delete()
            Location.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write('✅ Tables vidées')

        self.stdout.write('🚀 Génération données fake...\n')

        # ── 1. Categories ──────────────────────────────
        categories = []
        for name, icon in CATEGORIES:
            obj, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': fake.sentence(nb_words=8),
                    'icon': icon,
                }
            )
            categories.append(obj)
        self.stdout.write(f'  📁 {len(categories)} catégories')

        # ── 2. Brands ──────────────────────────────────
        brands = []
        for name, website in BRANDS:
            obj, _ = Brand.objects.get_or_create(
                name=name,
                defaults={'website': website}
            )
            brands.append(obj)
        self.stdout.write(f'  🏷️  {len(brands)} marques')

        # ── 3. Locations ───────────────────────────────
        locations = []
        for name, ltype in LOCATIONS:
            obj, _ = Location.objects.get_or_create(
                name=name,
                type=ltype,
                defaults={'description': fake.sentence()}
            )
            locations.append(obj)
        self.stdout.write(f'  📍 {len(locations)} emplacements')

        # ── 4. Tags ────────────────────────────────────
        tags = []
        for name, color in TAGS:
            obj, _ = Tag.objects.get_or_create(
                name=name,
                defaults={'color': color}
            )
            tags.append(obj)
        self.stdout.write(f'  🔖 {len(tags)} tags')

        # ── 5. Assets ──────────────────────────────────
        created_count = 0
        skipped_count = 0

        for _ in range(options['assets']):
            brand = random.choice(brands)
            model_name = random.choice(ASSET_MODELS.get(brand.name, ['Modèle Générique']))
            serial = fake.bothify(text='SN-????-########').upper()

            try:
                asset = Asset.objects.create(
                    name=f"{brand.name} {model_name}",
                    category=random.choice(categories),
                    brand=brand,
                    model=model_name,
                    serial_number=serial,
                    description=fake.text(max_nb_chars=200),
                    purchase_date=fake.date_between(start_date='-4y', end_date='today'),
                    purchase_price=fake.pydecimal(
                        left_digits=4, right_digits=2, positive=True,
                        min_value=50, max_value=8000
                    ),
                    warranty_end=fake.date_between(start_date='today', end_date='+3y'),
                    current_location=random.choice(locations),
                    assigned_to=fake.name() if random.random() > 0.3 else None,
                    status=random.choices(
                        ['active', 'inactive', 'archived'],
                        weights=[70, 20, 10]
                    )[0],
                    condition_state=random.choices(
                        ['new', 'used', 'damaged'],
                        weights=[20, 70, 10]
                    )[0],
                    photo=fake.image_url(width=200, height=200),
                )
                asset.tags.set(random.sample(tags, random.randint(1, 3)))
                created_count += 1

            except Exception as e:
                if 'UNIQUE' in str(e):
                    skipped_count += 1
                else:
                    raise

        self.stdout.write(
            self.style.SUCCESS(f'  💻 {created_count} assets créés')
            + (f' ({skipped_count} doublons ignorés)' if skipped_count else '')
        )

        # ── 6. Movements ───────────────────────────────
        all_assets = list(Asset.objects.select_related('current_location').all())
        mv_count = 0

        for _ in range(options['movements']):
            asset = random.choice(all_assets)
            AssetMovement.objects.create(
                asset=asset,
                from_location=asset.current_location,
                to_location=random.choice(locations),
                moved_by=fake.name(),
                moved_at=fake.date_time_between(
                    start_date='-2y',
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                ),
                notes=fake.sentence() if random.random() > 0.5 else None,
            )
            mv_count += 1

        self.stdout.write(self.style.SUCCESS(f'  🔄 {mv_count} mouvements'))
        self.stdout.write('\n' + self.style.SUCCESS('🎉 Inventaire fake prêt !'))