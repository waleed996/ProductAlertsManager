"""Runs before executing tests, registering test resources"""
import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from app.tests.factories import UserFactory, UserProductSearchPhrasesFactory

# Register object factories
register(UserFactory)
register(UserProductSearchPhrasesFactory)


# Client for endpoint testing
@pytest.fixture
def api_client():
    return APIClient
