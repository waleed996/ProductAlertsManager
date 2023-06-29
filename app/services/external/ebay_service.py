import logging
from functools import wraps
from typing import List

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from app.exceptions import EbayUnauthorizedException
from app.services.external import BaseExternalService
from app.services.external.redis_service import RedisCacheService

logger = logging.getLogger(__name__)


def retry_with_new_access_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EbayUnauthorizedException:
            ebay_service = args[0]
            ebay_service.access_token = ebay_service.get_ebay_access_token()
            try:
                response = func(*args, **kwargs)
                ebay_service.save_updated_access_token(access_token=ebay_service.access_token)
                return response
            except EbayUnauthorizedException as err:
                logger.error(f'Ebay unauthorized error retry failed')
                raise err

    return wrapper


class EbayService(BaseExternalService):
    class Urls:
        OAUTH_ACCESS_TOKEN_URL = '/identity/v1/oauth2/token'
        SEARCH_PRODUCTS_URL = '/buy/browse/v1/item_summary/search'

    class EbaySearchAPISortOptions:
        PRICE = 'price'
        DISTANCE = 'distance'
        NEWLY_LISTED = 'newlyListed'
        ENDING_SOONEST = 'endingSoonest'

    def __init__(self):
        self.redis_cache = RedisCacheService()
        self.access_token = self.redis_cache.get_key(settings.REDIS_EBAY_ACCESS_TOKEN_KEY_NAME)
        if not self.access_token:
            self.access_token = self.get_ebay_access_token()
            self.save_updated_access_token(access_token=self.access_token)

    def get_ebay_access_token(self) -> str or None:
        """
        Get access token from ebay auth endpoint
        :return: str or None
        """

        url = settings.EBAY_ENDPOINT_BASE_URL + EbayService.Urls.OAUTH_ACCESS_TOKEN_URL
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"  # Full access scope
        }
        response = requests.post(url=url, auth=HTTPBasicAuth(username=settings.EBAY_BASIC_AUTH_USERNAME,
                                                             password=settings.EBAY_BASIC_AUTH_PASSWORD),
                                 headers=headers, data=data)
        response_data = self._handle_response(response=response)
        return response_data['access_token'] if response_data else None

    @retry_with_new_access_token
    def get_ebay_products_by_search_phrase(self, search_phrase: str, sort: str, num_of_products: int = 20) -> List[dict]:
        """
        Get list of products containing search phrase.
        :param search_phrase: phrase to search for
        :param num_of_products: number of products to fetch from ebay
        :param sort: sort the products by 'price', 'distance', 'newlyListed' or 'endingSoonest'
        :return: List[dict]

        return list format:
        {
            'itemSummaries':
                [
                    {
                        'itemId': 'v1|110554141352|410108936098',
                        'title': 'Iphone'
                        'price': {'value': '10.99', 'currency': 'USD'},
                        'condition': 'New',
                        'listingMarketplaceId': 'EBAY_US'
                    }, ... (Omitting some properties that are not needed)
                ]
        }   ... (Omitting some properties that are not needed)
        """

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        query_params = {
            'q': search_phrase,
            'limit': num_of_products if num_of_products else 20,
            'sort': sort
        }
        response = requests.get(url=settings.EBAY_ENDPOINT_BASE_URL + EbayService.Urls.SEARCH_PRODUCTS_URL,
                                params=query_params, headers=headers)
        data = self._handle_response(response)
        return data.get('itemSummaries', []) if data else []

    def _handle_response(self, response) -> dict or list:
        """
        Handle ebay api responses
        :param response: requests library response object
        :return: response dict or empty list in case of unhandled error
        :raises EbayUnauthorizedException: for 401 ebay response
        """

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise EbayUnauthorizedException('Unauthorized')
        else:
            logger.error(f'Ebay search api error, status_code: {response.status_code}, response: {response.text}')
            return []

    def save_updated_access_token(self, access_token: str) -> None:
        """
        Save updated ebay access token to redis cache
        :param access_token: str
        :return: None
        """
        try:
            self.redis_cache.create_or_update_key(key_name=settings.REDIS_EBAY_ACCESS_TOKEN_KEY_NAME,
                                                  new_value=access_token)
        except Exception as err:
            logger.error(err)
