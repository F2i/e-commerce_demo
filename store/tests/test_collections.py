from store.models import Collection
from rest_framework.test import APIClient
from rest_framework import status
from store_core.models import User
import pytest
from model_bakery import baker

@pytest.fixture
def create_collection(api_client):
    def perform_create(collection):
        return api_client.post('/store/collections/', collection)
    return perform_create

@pytest.mark.django_db
class TestCreateCollection:
    # @pytest.mark.skip
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        # Arrange
        # Act
        response = create_collection({'title': 'a'})
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    # @pytest.mark.skip
    def test_if_user_is_authenticaed_but_not_admin_returns_403(self, authenticate_user, create_collection):
        # Act
        authenticate_user(is_staff=False)
        response = create_collection({'title': 'a'})
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    # @pytest.mark.skip
    def test_if_user_is_admin_but_data_invalid_returns_400(self, authenticate_user, create_collection):
        # Arrange
        # Act
        authenticate_user(is_staff=True)
        response = create_collection({'title': ''})
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
        
    # @pytest.mark.skip
    def test_if_user_is_admin_and_data_valid_returns_201(self, authenticate_user, create_collection):
        # Arrange
        input_collection = {'title': 'a'}
        # Act
        authenticate_user(is_staff=True)
        response = create_collection(input_collection)
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
        for key in input_collection:
            assert response.data[key] == input_collection[key]


@pytest.fixture
def get_collection(api_client):
    def perform_get(collection_id):
        return api_client.get(f'/store/collections/{collection_id}/')
    return perform_get

@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_return_200(self, get_collection):
        collection = baker.make(Collection)

        response = get_collection(collection.id)

        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'product_count': 0,
        }

    def test_if_collection_not_exists_return_404(self, get_collection):
        response = get_collection(0)

        assert response.status_code == status.HTTP_404_NOT_FOUND