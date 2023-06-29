from django.db import models


class User(models.Model):
    email = models.EmailField(null=False, blank=False, unique=True)
    product_alert_email_frequency = models.IntegerField(null=False, blank=False)
    product_alert_email_last_sent = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'


class UserProductSearchPhrases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_phrase = models.CharField(max_length=200, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_product_search_phrases'

