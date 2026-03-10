from django.test import TestCase
from inventory.models import Asset, Location, MaintenanceType, MaintenanceRecord


class AssetModelTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            type="placard",
            color="#FF0000",
            condition_state="neuf",
        )
        self.asset = Asset.objects.create(
            name="Test Asset",
            serial_number="123456",
            location=self.location,
            purchase_date="2023-01-01",
            purchase_price=100.00,
            warranty_end="2025-01-01",
            condition_state="neuf",
            notes="This is a test asset",
        )

    def test_asset_str(self):
        self.assertEqual(str(self.asset), "Test Asset")

    def test_asset_purchase_date(self):
        self.assertEqual(self.asset.purchase_date, "2023-01-01")

    def test_asset_purchase_price(self):
        self.assertEqual(self.asset.purchase_price, 100.00)

    def test_asset_warranty_end(self):
        self.assertEqual(self.asset.warranty_end, "2025-01-01")

    def test_asset_condition_state(self):
        self.assertEqual(self.asset.condition_state, "neuf")

    def test_asset_notes(self):
        self.assertEqual(self.asset.notes, "This is a test asset")


class LocationModelTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            type="placard",
            color="#FF0000",
            condition_state="neuf",
        )

    def test_location_str(self):
        self.assertEqual(str(self.location), "Test Location")

    def test_location_type(self):
        self.assertEqual(self.location.type, "placard")

    def test_location_color(self):
        self.assertEqual(self.location.color, "#FF0000")

    def test_location_condition_state(self):
        self.assertEqual(self.location.condition_state, "neuf")


class MaintenanceTypeModelTest(TestCase):
    def setUp(self):
        self.maintenance_type = MaintenanceType.objects.create(
            name="Test Maintenance Type", description="This is a test maintenance type"
        )

    def test_maintenance_type_str(self):
        self.assertEqual(str(self.maintenance_type), "Test Maintenance Type")

    def test_maintenance_type_description(self):
        self.assertEqual(
            self.maintenance_type.description, "This is a test maintenance type"
        )


class MaintenanceRecordModelTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            type="placard",
            color="#FF0000",
            condition_state="neuf",
        )
        self.asset = Asset.objects.create(
            name="Test Asset",
            serial_number="123456",
            location=self.location,
            purchase_date="2023-01-01",
            purchase_price=100.00,
            warranty_end="2025-01-01",
            condition_state="neuf",
            notes="This is a test asset",
        )
        self.maintenance_type = MaintenanceType.objects.create(
            name="Test Maintenance Type", description="This is a test maintenance type"
        )
        self.maintenance_record = MaintenanceRecord.objects.create(
            asset=self.asset,
            maintenance_type=self.maintenance_type,
            date="2023-01-01",
            notes="This is a test maintenance record",
        )

    def test_maintenance_record_str(self):
        self.assertEqual(
            str(self.maintenance_record),
            "Test Asset - Test Maintenance Type - 2023-01-01",
        )

    def test_maintenance_record_date(self):
        self.assertEqual(self.maintenance_record.date, "2023-01-01")

    def test_maintenance_record_notes(self):
        self.assertEqual(
            self.maintenance_record.notes, "This is a test maintenance record"
        )
