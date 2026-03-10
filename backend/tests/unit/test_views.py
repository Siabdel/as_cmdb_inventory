from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from inventory.models import Asset, Location, MaintenanceType, MaintenanceRecord
from inventory.serializers import (
    AssetSerializer,
    LocationSerializer,
    MaintenanceTypeSerializer,
    MaintenanceRecordSerializer,
)


class AssetViewTest(APITestCase):
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

    def test_get_assets(self):
        url = reverse("asset-list")
        response = self.client.get(url)
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_asset(self):
        url = reverse("asset-list")
        data = {
            "name": "New Asset",
            "serial_number": "789012",
            "location": self.location.id,
            "purchase_date": "2023-01-01",
            "purchase_price": 150.00,
            "warranty_end": "2025-01-01",
            "condition_state": "neuf",
            "notes": "This is a new asset",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.count(), 2)

    def test_update_asset(self):
        url = reverse("asset-detail", args=[self.asset.id])
        data = {
            "name": "Updated Asset",
            "serial_number": "123456",
            "location": self.location.id,
            "purchase_date": "2023-01-01",
            "purchase_price": 100.00,
            "warranty_end": "2025-01-01",
            "condition_state": "neuf",
            "notes": "This is an updated asset",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.name, "Updated Asset")

    def test_delete_asset(self):
        url = reverse("asset-detail", args=[self.asset.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.count(), 0)


class LocationViewTest(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            type="placard",
            color="#FF0000",
            condition_state="neuf",
        )

    def test_get_locations(self):
        url = reverse("location-list")
        response = self.client.get(url)
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_location(self):
        url = reverse("location-list")
        data = {
            "name": "New Location",
            "type": "placard",
            "color": "#FF0000",
            "condition_state": "neuf",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 2)

    def test_update_location(self):
        url = reverse("location-detail", args=[self.location.id])
        data = {
            "name": "Updated Location",
            "type": "placard",
            "color": "#FF0000",
            "condition_state": "neuf",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, "Updated Location")

    def test_delete_location(self):
        url = reverse("location-detail", args=[self.location.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Location.objects.count(), 0)


class MaintenanceTypeViewTest(APITestCase):
    def setUp(self):
        self.maintenance_type = MaintenanceType.objects.create(
            name="Test Maintenance Type", description="This is a test maintenance type"
        )

    def test_get_maintenance_types(self):
        url = reverse("maintenance-type-list")
        response = self.client.get(url)
        maintenance_types = MaintenanceType.objects.all()
        serializer = MaintenanceTypeSerializer(maintenance_types, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_maintenance_type(self):
        url = reverse("maintenance-type-list")
        data = {
            "name": "New Maintenance Type",
            "description": "This is a new maintenance type",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaintenanceType.objects.count(), 2)

    def test_update_maintenance_type(self):
        url = reverse("maintenance-type-detail", args=[self.maintenance_type.id])
        data = {
            "name": "Updated Maintenance Type",
            "description": "This is an updated maintenance type",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.maintenance_type.refresh_from_db()
        self.assertEqual(self.maintenance_type.name, "Updated Maintenance Type")

    def test_delete_maintenance_type(self):
        url = reverse("maintenance-type-detail", args=[self.maintenance_type.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MaintenanceType.objects.count(), 0)


class MaintenanceRecordViewTest(APITestCase):
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

    def test_get_maintenance_records(self):
        url = reverse("maintenance-record-list")
        response = self.client.get(url)
        maintenance_records = MaintenanceRecord.objects.all()
        serializer = MaintenanceRecordSerializer(maintenance_records, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_maintenance_record(self):
        url = reverse("maintenance-record-list")
        data = {
            "asset": self.asset.id,
            "maintenance_type": self.maintenance_type.id,
            "date": "2023-01-01",
            "notes": "This is a new maintenance record",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaintenanceRecord.objects.count(), 2)

    def test_update_maintenance_record(self):
        url = reverse("maintenance-record-detail", args=[self.maintenance_record.id])
        data = {
            "asset": self.asset.id,
            "maintenance_type": self.maintenance_type.id,
            "date": "2023-01-01",
            "notes": "This is an updated maintenance record",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.maintenance_record.refresh_from_db()
        self.assertEqual(
            self.maintenance_record.notes, "This is an updated maintenance record"
        )

    def test_delete_maintenance_record(self):
        url = reverse("maintenance-record-detail", args=[self.maintenance_record.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MaintenanceRecord.objects.count(), 0)
