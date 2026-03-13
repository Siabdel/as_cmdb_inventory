import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from inventory.models import Asset, Category, Brand, Location, Tag, AssetMovement
from faker import Faker

fake = Faker('fr_FR')
# Ajouter en haut du fichier, après ASSET_MODELS

# URLs d'images produits réelles (Wikipedia / images publiques)
ASSET_PHOTOS = {
    # ── Dell ──────────────────────────────────────────────
    'Dell': {
        'OptiPlex 7090':    'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/desktops/optiplex-desktops/optiplex-7090/media-gallery/optiplex-7090-desktop-gallery-4.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=402',
        'Latitude 5520':    'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/latitude-notebooks/latitude-15-5520/media-gallery/notebook-latitude-15-5520-gallery-4.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=402',
        'PowerEdge R740':   'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/servers/poweredge/poweredge-r740/media-gallery/server-poweredge-r740-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1',
        'UltraSharp U2722': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/peripherals/monitors/u-series/u2722/media-gallery/monitor-u2722-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1',
    },
    # ── HP ────────────────────────────────────────────────
    'HP': {
        'EliteBook 840 G8': 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/knowledgebase/c08055652.png',
        'ProDesk 600':      'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/knowledgebase/c07195013.png',
        'ProLiant DL380':   'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/knowledgebase/c04128830.png',
        'LaserJet Pro':     'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/knowledgebase/c07627866.png',
    },
    # ── Cisco ─────────────────────────────────────────────
    'Cisco': {
        'Catalyst 9200':    'https://www.cisco.com/c/dam/en/us/products/switches/catalyst-9200-series-switches/index/jcr:content/Grid/category_atl/layout-category-atl/anchor_info/image.img.jpg/1588266977086.jpg',
        'ISR 4331':         'https://www.cisco.com/c/dam/en/us/products/routers/4000-series-integrated-services-routers-isr/index/jcr:content/Grid/category_atl/layout-category-atl/anchor_info_127906950/image.img.jpg/1588267010029.jpg',
        'ASA 5506-X':       'https://www.cisco.com/c/dam/en/us/products/security/asa-5500-x-series-firewalls/index/jcr:content/Grid/category_atl/layout-category-atl/anchor_info/image.img.jpg/1519940808892.jpg',
        'Meraki MX68':      'https://meraki.cisco.com/wp-content/uploads/2020/01/mx68-front.png',
    },
    # ── Lenovo ────────────────────────────────────────────
    'Lenovo': {
        'ThinkPad X1 Carbon':   'https://p1-ofp.static.pub/medias/bWFzdGVyfHJvb3R8MjQ2NzQ5fGltYWdlL3BuZ3xoNTYvaGZhLzE0NjE3NzY1NzI5NTY2LnBuZw/lenovo-laptop-thinkpad-x1-carbon-gen-11-14-hero.png',
        'ThinkCentre M90':      'https://p1-ofp.static.pub/medias/bWFzdGVyfHJvb3R8MTIzNTUyfGltYWdlL3BuZ3xoMTYvaGNiLzE0NjIxMzI1NTI4OTI2LnBuZw/lenovo-desktops-thinkcentre-m90t-gen3-hero.png',
        'ThinkSystem SR650':    'https://lenovopress.lenovo.com/assets/images/LP0955/ThinkSystem%20SR650%20V2%20server.jpg',
    },
    # ── Apple ─────────────────────────────────────────────
    'Apple': {
        'MacBook Pro M3':   'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spacegray-select-202310?wid=400&hei=400&fmt=jpeg&qlt=90',
        'Mac Mini M2':      'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mac-mini-hero-202301?wid=400&hei=400&fmt=jpeg&qlt=90',
        'iPhone 15 Pro':    'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-1inch-naturaltitanium?wid=400&hei=400&fmt=jpeg&qlt=90',
    },
    # ── Synology ──────────────────────────────────────────
    'Synology': {
        'DS923+':   'https://global.download.synology.com/download/Document/Hardware/HIG/DiskStation/23-year/DS923+/enu/Syno_HIG_DS923_Plus_enu.pdf',
        'RS1221+':  'https://www.synology.com/img/products/detail/RS1221plus/heading.png',
        'DS220+':   'https://www.synology.com/img/products/detail/DS220plus/heading.png',
    },
    # ── APC ───────────────────────────────────────────────
    'APC': {
        'Smart-UPS 1500':   'https://download.schneider-electric.com/files?p_Reference=SMT1500I&p_EnDocType=Product%20image&p_File_Id=7900001516',
        'Back-UPS 650':     'https://download.schneider-electric.com/files?p_Reference=BE650G2-FR&p_EnDocType=Product%20image',
        'Smart-UPS 3000':   'https://download.schneider-electric.com/files?p_Reference=SMT3000I&p_EnDocType=Product%20image',
    },
    # ── Brother ───────────────────────────────────────────
    'Brother': {
        'MFC-L8900CDW': 'https://www.brother.fr/-/media/Brother/Products/MFC-L8900CDW/MFC-L8900CDW_main.ashx',
        'HL-L6400DW':   'https://www.brother.fr/-/media/Brother/Products/HL-L6400DW/HL-L6400DW_main.ashx',
        'DCP-L2550DN':  'https://www.brother.fr/-/media/Brother/Products/DCP-L2550DN/DCP-L2550DN_main.ashx',
    },
    # ── Samsung ───────────────────────────────────────────
    'Samsung': {
        'Galaxy Tab S9':    'https://image-us.samsung.com/SamsungUS/home/mobile/galaxy-tab/all-galaxy-tabs/07132023/tab-s9-wifi-graphite-400x400.jpg',
        'Odyssey G7':       'https://image-us.samsung.com/SamsungUS/home/computing/monitors/all-monitors/06112020/lc32g75tqsnxza-400x400.jpg',
        'T7 Shield SSD':    'https://image-us.samsung.com/SamsungUS/home/computing/memory-storage/portable-ssd/06062022/mu-pe2t0s-400x400.jpg',
    },
    # ── Asus ──────────────────────────────────────────────
    'Asus': {
        'ZenBook 14':       'https://dlcdnwebimgs.asus.com/gain/B9560CB6-4EB1-4EC6-B6A9-C09E05C8BB1A/w800',
        'ExpertCenter D7':  'https://dlcdnwebimgs.asus.com/gain/B1E4A4F3-B1AC-4A7D-B3E7-F6A7B1E4A4F3/w800',
        'RT-AX88U':         'https://dlcdnwebimgs.asus.com/gain/E7E6E5E4-E3E2-E1E0-DFDE-DDDCDBDAD9D8/w800',
    },
}

# Fallback par catégorie si le modèle exact n'est pas trouvé
CATEGORY_FALLBACK_PHOTOS = {
    'laptop':     'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Laptop_600.jpg/320px-Laptop_600.jpg',
    'desktop':    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Computer-aj_aj_ashton_01.svg/320px-Computer-aj_aj_ashton_01.svg.png',
    'server':     'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg',
    'monitor':    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Eink_shades.png/320px-Eink_shades.png',
    'router':     'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Cisco_router.jpg/320px-Cisco_router.jpg',
    'switch':     'https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Cisco_Catalyst_702x.jpg/320px-Cisco_Catalyst_702x.jpg',
    'printer':    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/HP_LaserJet_1020.jpg/320px-HP_LaserJet_1020.jpg',
    'nas':        'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Synology_DS216play.jpg/320px-Synology_DS216play.jpg',
    'ups':        'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/APC_Back-UPS_CS_350.jpg/320px-APC_Back-UPS_CS_350.jpg',
    'phone':      'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Cisco_IP_Phone_7960.jpg/320px-Cisco_IP_Phone_7960.jpg',
}


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

def get_asset_photo(brand_name: str, model_name: str, category_icon: str) -> str:
    """Retourne une URL photo réaliste pour un asset IT."""
    # 1. Cherche l'image exacte marque+modèle
    brand_photos = ASSET_PHOTOS.get(brand_name, {})
    if model_name in brand_photos:
        return brand_photos[model_name]

    # 2. Fallback sur la première image disponible de la marque
    if brand_photos:
        return next(iter(brand_photos.values()))

    # 3. Fallback sur la catégorie
    return CATEGORY_FALLBACK_PHOTOS.get(category_icon, '')


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

            # Supprimer d'abord les tables dépendantes de Asset
            try:
                from maintenance.models import MaintenanceTicket, TicketPart, TicketComment
                TicketComment.objects.all().delete()
                TicketPart.objects.all().delete()
                MaintenanceTicket.objects.all().delete()
            except Exception:
                pass  # app maintenance pas encore installée

            try:
                from scanner.models import QRCode, ScanLog
                ScanLog.objects.all().delete()
                QRCode.objects.all().delete()
            except Exception:
                pass  # app scanner pas encore installée

            # Ensuite les tables inventory
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

                    # ✅ Retourne une URL photo réaliste pour un asset IT
                    photo=get_asset_photo(brand.name, model_name, asset.category.icon if hasattr(asset, 'category') and asset.category else ''),

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