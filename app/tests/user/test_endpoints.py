import json

import pytest

from app.models.user import User

# Allows tests to access test database
pytestmark = pytest.mark.django_db


class TestUserControllerEndpoints:

    get_user_endpoint = '/product-alerts-manager/api/v1/user'
    create_user_endpoint = '/product-alerts-manager/api/v1/user'

    def test_get_user_by_email_endpoint_without_search_phrases(self, api_client, user_factory) -> None:
        """
        :param api_client: Rest framework APIClient
        :param user_factory:  factory of User from app.tests.conftest
        :return: None
        """
        # Arrange
        user_factory(email='test@abc.com', product_alert_email_frequency=2, product_alert_email_last_sent=None)
        # Act
        response = api_client().get(self.get_user_endpoint + '?email=test@abc.com')
        # Assert
        assert response.status_code == 200
        assert json.loads(response.content)['data']['email'] == 'test@abc.com'
        assert json.loads(response.content)['data']['product_alert_email_frequency'] == 2
        assert json.loads(response.content)['data']['product_alert_email_last_sent'] is None
        assert len(json.loads(response.content)['data']['search_phrases']) == 0

    def test_get_user_by_email_endpoint_with_search_phrases(self, api_client, user_factory, user_product_search_phrases_factory) -> None:
        """
        :param api_client:
        :param user_factory:  factory of User from app.tests.conftest
        :param user_product_search_phrases_factory: factory of UserProductSearchPhrases from app.tests.conftest
        :return: None
        """
        # Arrange
        user = user_factory(email='test@abc.com', product_alert_email_frequency=2, product_alert_email_last_sent=None)
        user_search_phrase = user_product_search_phrases_factory(search_phrase='tennis', user=user)
        # Act
        response = api_client().get(self.get_user_endpoint + '?email=test@abc.com')
        # Assert
        assert response.status_code == 200
        assert json.loads(response.content)['data']['email'] == 'test@abc.com'
        assert json.loads(response.content)['data']['product_alert_email_frequency'] == 2
        assert json.loads(response.content)['data']['product_alert_email_last_sent'] is None
        assert len(json.loads(response.content)['data']['search_phrases']) == 1

    def test_get_user_by_id_endpoint(self, api_client, user_factory, user_product_search_phrases_factory) -> None:
        """
        :param api_client: Rest framework APIClient
        :param user_factory:  factory of User from app.tests.conftest
        :param user_product_search_phrases_factory: factory of UserProductSearchPhrases from app.tests.conftest
        :return: None
        """
        # Arrange
        user = user_factory(email='test@abc.com', product_alert_email_frequency=10, product_alert_email_last_sent=None)
        user_search_phrase = user_product_search_phrases_factory(search_phrase='tennis', user=user)
        # Act
        response = api_client().get(self.get_user_endpoint + f'?user_id={user.id}')
        # Assert
        assert response.status_code == 200
        assert json.loads(response.content)['data']['email'] == 'test@abc.com'
        assert json.loads(response.content)['data']['product_alert_email_frequency'] == 10
        assert json.loads(response.content)['data']['product_alert_email_last_sent'] is None
        assert len(json.loads(response.content)['data']['search_phrases']) == 1

    def test_get_user_with_incorrect_email(self, api_client, user_factory) -> None:
        """
        :param api_client: Rest framework APIClient
        :param user_factory:  factory of User from app.tests.conftest
        :return: None
        """
        # Arrange, Act
        response = api_client().get(self.get_user_endpoint + '?email=test@abc.com')
        # Assert
        assert response.status_code == 200
        assert len(json.loads(response.content)['data'].keys()) == 0

    def test_create_user_without_search_phrases(self, api_client, user_factory) -> None:
        """
        :param api_client: Rest framework APIClient
        :param user_factory:  factory of User from app.tests.conftest
        :return: None
        """
        # Arrange
        request_data = {
            "email": "test@abc.com",
            "product_alert_email_frequency": 2,
            "search_phrases": []
        }

        # Act
        response = api_client().post(path=self.create_user_endpoint, data=request_data, format='json')
        user = User.objects.filter(email='test@abc.com').first()
        # Assert
        assert response.status_code == 200
        assert json.loads(response.content)['data'] == "User created successfully"
        assert user is not None
        assert user.email == request_data['email']
