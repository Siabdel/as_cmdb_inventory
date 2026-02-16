"""
Tests unitaires pour l'application CMDB Inventory
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Location, Category, Brand, Tag, Asset, AssetMovement


class LocationModelTest(TestCase):
    """Tests pour le modèle Location"""
    
    def setUp(self):
        self.parent_location = Location.objects.create(
            name="Bâtiment A",
            type="salle"
        )
        self.child_location = Location.objects.create(
            name="Salle 101",
            type="salle",
            parent=self.parent_location
        )
    
    def test_location_str(self):
        """Test de la représentation string d'une location"""
        self.assertEqual(str(self.parent_location), "Bâtiment A")
        self.assertEqual(str(self.child_location), "Bâtiment A > Salle 101")
    
    def test_full_path_property(self):
        """Test de la propriété full_path"""
        self.assertEqual(self.parent_location.full_path, "Bâtiment A")
        self.assertEqual(self.child_location.full_path, "Bâtiment A > Salle 101")


class CategoryModelTest(TestCase):
    """Tests pour le modèle Category"""
    
    def setUp(self):
        self.parent_category = Category.objects.create(
            name="Informatique",
            slug="informatique"
        )
        self.child_category = Category.objects.create(
            name="Ordinateurs",
            slug="ordinateurs",
            parent=self.parent_category
        )
    
    def test_category_str(self):
        """Test de la représentation string d'une catégorie"""
        self.assertEqual(str(self.parent_category), "Informatique")
        self.assertEqual(str(self.child_category), "Informatique > Ordinateurs")
    
    def test_slug_auto_generation(self):
        """Test de la génération automatique du slug"""
        category = Category.objects.create(name="Test Catégorie")
        self.assertEqual(category.slug, "test-categorie")


class AssetModelTest(TestCase):
    """Tests pour le modèle Asset"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="PC",
            slug="pc"
        )
        self.brand = Brand.objects.create(name="Dell")
        self.location = Location.objects.create(
            name="Bureau 1",
            type="bureau"
        )
        self.asset = Asset.objects.create(
            name="PC Dell OptiPlex",
            category=self.category,
            brand=self.brand,
            current_location=self.location,
            status="stock"
        )
    
    def test_asset_str(self):
        """Test de la représentation string d'un asset"""
        self.assertTrue(str(self.asset).startswith("PC-"))
        self.assertTrue("PC Dell OptiPlex" in str(self.asset))
    
    def test_internal_code_generation(self):
        """Test de la génération automatique du code interne"""
        self.assertTrue(self.asset.internal_code.startswith("PC-"))
        self.assertEqual(len(self.asset.internal_code), 6)  # PC-001
    
    def test_warranty_status_property(self):
        """Test de la propriété warranty_status"""
        # Sans date de garantie
        self.assertEqual(self.asset.warranty_status, "Non définie")
        
        # Avec garantie valide
        from django.utils import timezone
        from datetime import timedelta
        future_date = timezone.now().date() + timedelta(days=100)
        self.asset.warranty_end = future_date
        self.asset.save()
        self.assertEqual(self.asset.warranty_status, "Valide")


class AssetMovementModelTest(TestCase):
    """Tests pour le modèle AssetMovement"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.location1 = Location.objects.create(
            name="Stock",
            type="entrepot"
        )
        self.location2 = Location.objects.create(
            name="Bureau 1",
            type="bureau"
        )
        self.asset = Asset.objects.create(
            name="Test Asset",
            current_location=self.location1,
            status="stock"
        )
    
    def test_movement_creation(self):
        """Test de la création d'un mouvement"""
        movement = AssetMovement.objects.create(
            asset=self.asset,
            from_location=self.location1,
            to_location=self.location2,
            moved_by=self.user,
            move_type="move"
        )
        
        self.assertEqual(movement.asset, self.asset)
        self.assertEqual(movement.from_location, self.location1)
        self.assertEqual(movement.to_location, self.location2)
        self.assertEqual(movement.moved_by, self.user)
    
    def test_asset_location_update(self):
        """Test de la mise à jour automatique de l'emplacement de l'asset"""
        # L'asset est initialement dans location1
        self.assertEqual(self.asset.current_location, self.location1)
        
        # Créer un mouvement vers location2
        AssetMovement.objects.create(
            asset=self.asset,
            from_location=self.location1,
            to_location=self.location2,
            moved_by=self.user,
            move_type="move"
        )
        
        # Vérifier que l'emplacement de l'asset a été mis à jour
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.current_location, self.location2)


class AssetAPITest(APITestCase):
    """Tests pour l'API des assets"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.category = Category.objects.create(
            name="PC",
            slug="pc"
        )
        self.brand = Brand.objects.create(name="Dell")
        self.location = Location.objects.create(
            name="Bureau 1",
            type="bureau"
        )
        self.asset = Asset.objects.create(
            name="PC Dell OptiPlex",
            category=self.category,
            brand=self.brand,
            current_location=self.location,
            status="stock"
        )
    
    def test_get_assets_list(self):
        """Test de récupération de la liste des assets"""
        url = reverse('asset-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "PC Dell OptiPlex")
    
    def test_get_asset_detail(self):
        """Test de récupération du détail d'un asset"""
        url = reverse('asset-detail', kwargs={'pk': self.asset.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "PC Dell OptiPlex")
        self.assertEqual(response.data['category'], self.category.id)
    
    def test_create_asset(self):
        """Test de création d'un asset"""
        url = reverse('asset-list')
        data = {
            'name': 'Nouvel Asset',
            'category': self.category.id,
            'brand': self.brand.id,
            'current_location': self.location.id,
            'status': 'stock'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.count(), 2)
        
        new_asset = Asset.objects.get(name='Nouvel Asset')
        self.assertEqual(new_asset.category, self.category)
        self.assertEqual(new_asset.brand, self.brand)
    
    def test_move_asset_from_scan(self):
        """Test de déplacement d'asset via scan"""
        new_location = Location.objects.create(
            name="Bureau 2",
            type="bureau"
        )
        
        url = reverse('asset-move-from-scan')
        data = {
            'asset_id': str(self.asset.id),
            'target_location_id': new_location.id,
            'note': 'Déplacement via scan'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que l'asset a été déplacé
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.current_location, new_location)
        
        # Vérifier qu'un mouvement a été créé
        movement = AssetMovement.objects.get(asset=self.asset)
        self.assertEqual(movement.to_location, new_location)
        self.assertEqual(movement.note, 'Déplacement via scan')
    
    def test_unauthorized_access(self):
        """Test d'accès non autorisé"""
        self.client.credentials()  # Supprimer les credentials
        
        url = reverse('asset-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardAPITest(APITestCase):
    """Tests pour l'API du dashboard"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Créer quelques données de test
        self.category = Category.objects.create(name="PC", slug="pc")
        self.location = Location.objects.create(name="Bureau 1", type="bureau")
        
        for i in range(5):
            Asset.objects.create(
                name=f"Asset {i}",
                category=self.category,
                current_location=self.location,
                status="stock"
            )
    
    def test_dashboard_summary(self):
        """Test du résumé du dashboard"""
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_assets'], 5)
        self.assertIn('assets_by_status', data)
        self.assertIn('assets_by_location', data)
        self.assertIn('assets_by_category', data)
        self.assertEqual(data['assets_by_status']['stock'], 5)