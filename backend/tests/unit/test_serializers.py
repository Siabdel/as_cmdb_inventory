from rest_framework.test import APITestCase
from inventory.models import Asset, Location, MaintenanceType, MaintenanceRecord
from inventory.serializers import (
    AssetSerializer,
    LocationSerializer,
    MaintenanceTypeSerializer,
    MaintenanceRecordSerializer,
)


class AssetSerializerTest(APITestCase):
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

    def test_asset_serializer(self):
        serializer = AssetSerializer(instance=self.asset)
        self.assertEqual(serializer.data["name"], "Test Asset")
        self.assertEqual(serializer.data["serial_number"], "123456")
        self.assertEqual(serializer.data["location"], self.location.id)
        self.assertEqual(serializer.data["purchase_date"], "2023-01-01")
        self.assertEqual(serializer.data["purchase_price"], "100.00")
        self.assertEqual(serializer.data["warranty_end"], "2025-01-01")
        self.assertEqual(serializer.data["condition_state"], "neuf")
        self.assertEqual(serializer.data["notes"], "This is a test asset")


class LocationSerializerTest(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            type="placard",
            color="#FF0000",
            condition_state="neuf",
        )

    def test_location_serializer(self):
        serializer = LocationSerializer(instance=self.location)
        self.assertEqual(serializer.data["name"], "Test Location")
        self.assertEqual(serializer.data["type"], "placard")
        self.assertEqual(serializer.data["color"], "#FF0000")
        self.assertEqual(serializer.data["condition_state"], "neuf")


class MaintenanceTypeSerializerTest(APITestCase):
    def setUp(self):
        self.maintenance_type = MaintenanceType.objects.create(
            name="Test Maintenance Type", description="This is a test maintenance type"
        )

    def test_maintenance_type_serializer(self):
        serializer = MaintenanceTypeSerializer(instance=self.maintenance_type)
        self.assertEqual(serializer.data["name"], "Test Maintenance Type")
        self.assertEqual(
            serializer.data["description"], "This is a test maintenance type"
        )


class MaintenanceRecordSerializerTest(APITestCase):
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

    def test_maintenance_record_serializer(self):
        serializer = MaintenanceRecordSerializer(instance=self.maintenance_record)
        self.assertEqual(serializer.data["asset"], self.asset.id)
        self.assertEqual(serializer.data["maintenance_type"], self.maintenance_type.id)
        self.assertEqual(serializer.data["date"], "2023-01-01")
        self.assertEqual(serializer.data["notes"], "This is a test maintenance record")
