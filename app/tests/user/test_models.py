import pytest


# Allows tests to access test database
pytestmark = pytest.mark.django_db


class TestUserModel:

    def test_user_create(self, user_factory) -> None:
        """
        :param user_factory:  factory of User from app.tests.conftest
        :return: None
        """
        # Arrange, Act
        user = user_factory(email='test@abc.com', product_alert_email_frequency=2, product_alert_email_last_sent=None)
        # Assert
        assert user.email == 'test@abc.com'
        assert user.product_alert_email_frequency == 2
        assert user.product_alert_email_last_sent is None

    # test any custom methods in the model here


class TestUserProductSearchPhrasesModel:

    def test_user_product_search_phrases_create(self, user_factory, user_product_search_phrases_factory) -> None:
        """
        :param user_factory:  factory of User from app.tests.conftest
        :param user_product_search_phrases_factory: factory of UserProductSearchPhrases from app.tests.conftest
        :return: None
        """
        # Arrange, Act
        user = user_factory(email='test@abc.com', product_alert_email_frequency=2, product_alert_email_last_sent=None)
        user_search_phrase = user_product_search_phrases_factory(search_phrase='tennis', user=user)
        # Assert
        assert user_search_phrase.search_phrase == 'tennis'
        assert user_search_phrase.user is user

    # test any custom methods in the model here

