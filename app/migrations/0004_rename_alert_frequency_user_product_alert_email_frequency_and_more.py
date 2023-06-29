# Generated by Django 4.1 on 2023-06-24 05:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_rename_user_id_userproductsearchphrases_user"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="alert_frequency",
            new_name="product_alert_email_frequency",
        ),
        migrations.AddField(
            model_name="user",
            name="product_alert_email_last_sent",
            field=models.DateTimeField(null=True),
        ),
    ]
