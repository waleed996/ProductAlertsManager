import logging

import redis
from django.conf import settings


logger = logging.getLogger(__name__)


class RedisCacheService:

    def __init__(self):
        self.redis_client = redis.from_url(url=settings.REDIS_CACHE_URL)

    def get_key(self, key_name: str) -> object:
        """
        Get a value for key_name from redis cache
        :param key_name: name of the key
        :return: value stored against the key
        """
        return self.redis_client.get(name=key_name)

    def create_or_update_key(self, key_name: str, new_value: object) -> None:
        """
        Update if exists or create the key with key name in redis cache
        :param key_name: Name of the key
        :param new_value: Value of key
        :return: None
        """
        self.redis_client.set(name=key_name, value=new_value)


class RedisQueueService:

    def __init__(self):
        self.redis_client = redis.from_url(url=settings.REDIS_QUEUE_URL)

    def push(self, queue_name: str, message: str) -> None:
        """
        Push a message to the redis queue
        :param queue_name: Name of the queue to push the message to.
        :param message: The message to push
        :return: None
        """
        self.redis_client.rpush(queue_name, message)

