import pytest
from rest_framework.test import APIClient
from store_core.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticate_user(api_client):
    def perform_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return perform_authenticate