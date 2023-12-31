# Generated by Django 4.1 on 2023-06-28 10:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shared_data_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ebayproductinformation",
            name="condition",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="ebayproductinformation",
            name="ebay_item_id",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="ebayproductinformation",
            name="listing_market_place_ebay_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="ebayproductinformation",
            name="price_currency",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="ebayproductinformation",
            name="title",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
