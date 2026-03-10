import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(db):
    user = User.objects.create_user(username="testuser", password="testpassword")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(db):
    user = User.objects.create_superuser(username="adminuser", password="adminpassword")
    client = APIClient()
    client.force_authenticate(user=user)
    return client
