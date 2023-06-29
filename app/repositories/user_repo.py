import datetime
from typing import List

from django.db import transaction
from django.db.models import Max, Prefetch

from app.models.user import UserProductSearchPhrases, User


class UserRepository:
    """Database interaction methods for 'User' model"""

    @staticmethod
    def get(user_id: int = None, email: str = None, load_search_phrases: bool = False) -> User:
        """
        Get User object

        :param user_id: pk of the user record
        :param email: email of the user
        :param load_search_phrases: load related user_product_search_phrases if True
        :return: User
        """

        records_filter = dict()
        if user_id:
            records_filter['pk'] = user_id
        if email:
            records_filter['email'] = email

        if load_search_phrases:
            return User.objects.prefetch_related('userproductsearchphrases_set').filter(**records_filter).first()

        return User.objects.filter(**records_filter).first()

    @staticmethod
    def create(email: str, product_alert_email_frequency: int, search_phrases: List[str] = None) -> tuple[User,
                                                                                                          List[UserProductSearchPhrases]]:
        """
        Create User record and UserProductSearchPhrases records

        :param email:
        :param product_alert_email_frequency:
        :param search_phrases: list of search phrase strings
        :return: (User, UserProductSearchPhrases) tuple
        """

        with transaction.atomic():
            user, created = User.objects.get_or_create(email=email,
                                                       product_alert_email_frequency=product_alert_email_frequency)

            existing_search_phrases = set()
            if not created:
                existing_search_phrases = {existing_phrase.search_phrase for existing_phrase in
                                           user.userproductsearchphrases_set.all()}

            new_search_phrases = list()
            if search_phrases:
                new_search_phrases = [UserProductSearchPhrases(user_id=user.id, search_phrase=phrase) for phrase in
                                      search_phrases if phrase not in existing_search_phrases]
                UserProductSearchPhrases.objects.bulk_create(new_search_phrases)

        return user, new_search_phrases

    @staticmethod
    def get_last_user_id() -> int:
        """
        Get the last user_id in user table
        :return: int
        """

        last_id = User.objects.aggregate(max_id=Max('id'))['max_id']
        return last_id if last_id else 0

    @staticmethod
    def get_users_with_search_phrases_in_range(start_user_id: int, end_user_id: int, user_columns: list,
                                               user_product_search_phrases_columns: list) -> List[dict]:
        """
        Get list of records in the index range

        :param start_user_id: int
        :param end_user_id: int
        :param user_columns: List[str] the columns to fetch from User table
        :param user_product_search_phrases_columns: List[str] the columns to fetch from UserProductSearchPhrases table
        :return: List[dict]
        """

        return User.objects.filter(id__range=(start_user_id, end_user_id)).select_related('userproductsearchphrases').values(
            *user_columns, *[f'userproductsearchphrases__{col}' for col in user_product_search_phrases_columns]
        )

    @staticmethod
    def update_product_alert_email_last_sent(emails: List[str]) -> None:
        """
        Update product_alert_email_last_sent for emails

        :param emails: the emails to update product_alert_email_last_sent
        :return: None
        """

        User.objects.filter(email__in=emails).update(product_alert_email_last_sent=datetime.datetime.utcnow())
