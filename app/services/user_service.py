"""
For code separation, scalability, extensibility and re-usability only service layer interacts with the
repository layers.
"""
import json
from typing import List

from django.conf import settings

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.serializers.user_serializers import UserSerializer
from app.services import BaseService
from app.services.external.redis_service import RedisQueueService


class UserService(BaseService):
    """Service layer for user related logic"""

    def get_user_by_user_id(self, user_id: int, load_search_phrases: bool = False, serialize: bool = True):
        """
        Get user by user id

        :param user_id: int, user id of the user
        :param load_search_phrases: bool, load search phrases or not
        :param serialize: bool, serialize object or not
        :return: User or dict
        """

        user = UserRepository.get(user_id=user_id, load_search_phrases=load_search_phrases)

        if user and serialize:
            return UserSerializer(user).data

        return user if user else {}

    def get_user_by_email(self, email: str, load_search_phrases: bool = False, serialize: bool = True):
        """
        Get user by email

        :param email: str, email of the user
        :param load_search_phrases: bool, load search phrases or not
        :param serialize: bool, serialize object or not
        :return: User or dict
        """

        user = UserRepository.get(email=email, load_search_phrases=load_search_phrases)

        if user and serialize:
            return UserSerializer(user).data

        return user if user else {}

    def create_user(self, email: str, product_alert_email_frequency: int, search_phrases: List[str] = None) -> User:
        """
        Create user along with search phrases (optional)

        :param email: user's email
        :param product_alert_email_frequency: user alert frequency
        :param search_phrases: (optional) list of user's search phrases
        :return: User object
        """

        user, new_search_phrases = UserRepository.create(email=email,
                                                         product_alert_email_frequency=product_alert_email_frequency,
                                                         search_phrases=search_phrases)
        # Send new user configuration to the other service via a queue
        message = {
            'user_id': user.id,
            'email': user.email,
            'product_alert_email_frequency': product_alert_email_frequency,
            'search_phrases': [phrase.search_phrase for phrase in new_search_phrases]
        }
        RedisQueueService().push(queue_name=settings.REDIS_USER_SETTINGS_QUEUE, message=json.dumps(message))

        return user
