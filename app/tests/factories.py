"""Factory to generate model objects to help in testing"""
import datetime

import factory

from app.models.user import User, UserProductSearchPhrases


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = 'test_email@test.com'
    product_alert_email_frequency = 2
    product_alert_email_last_sent = datetime.datetime.utcnow()


class UserProductSearchPhrasesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProductSearchPhrases

    user = factory.SubFactory(UserFactory)
    search_phrase = "tennis"


