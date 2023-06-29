from typing import List
from decimal import Decimal

from config.celery import celery

from shared_data_app.models import EbayProductInformation


@celery.task
def save_ebay_products_to_shared_db(products_data: List[dict]) -> None:
    """
    Save products data to products shared database, task enqueued by send_user_product_email_task
    :param products_data: list(dict), data from ebay
    :return: None

    products_data format

    [
        {
            'itemId': 'v1|110554141352|410108936098',
            'title': 'Iphone',
            'price': {'value': '10.99', 'currency': 'USD'},
            'condition': 'New',
            'listingMarketplaceId': 'EBAY_US'
        }, ...
    ]
    """

    instances = [EbayProductInformation(ebay_item_id=product.get('itemId'), title=product.get('title'),
                                        price=Decimal(product.get('price', {}).get('value', None)),
                                        price_currency=product.get('price', {}).get('currency', None),
                                        condition=product.get('condition'),
                                        listing_market_place_ebay_id=product.get('listingMarketplaceId')) for product in
                 products_data]
    if instances:
        EbayProductInformation.objects.db_manager('products_shared_db').bulk_create(instances)
