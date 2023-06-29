from django.db import models


class EbayProductInformation(models.Model):
    ebay_item_id = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    price_currency = models.CharField(max_length=10, null=True, blank=True)
    condition = models.CharField(max_length=50, null=True, blank=True)
    listing_market_place_ebay_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'ebay_product_information'
