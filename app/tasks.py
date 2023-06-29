"""
Task definitions for celery workers.

Note: Initially I had this in 'tasks' package in 'app' inside a class, but celery is not able to find the task, I am
short on time so putting this here in functions for now. Ideally I would like to do a class based implementation
for this.
"""

import datetime
import json
import logging
import math
from collections import namedtuple, defaultdict
from typing import List

from django.core.mail import send_mass_mail
from django.conf import settings

from app.repositories.user_repo import UserRepository
from app.services.external.ebay_service import EbayService
from config.celery import celery
from shared_data_app.tasks import save_ebay_products_to_shared_db

UserEmailConfiguration = namedtuple('UserEmailConfiguration', ['email', 'alert_frequency', 'last_sent'])
UserEmail = namedtuple('UserEmail', ['subject', 'message', 'sender_email', 'receiver_email_list'])
BatchIndexes = namedtuple('BatchIndexes', ['start_index', 'end_index'])


logger = logging.getLogger(__name__)


@celery.task
def user_product_email_task_distributor() -> None:
    """
    Celery task for sending emails to users in a scalable way. This is the distributor task which will add subtasks
    with celery. Each subtask will process a batch/part of the total users to be processed for sending emails.

    :return: None
    """
    logger.debug(f'Celery task distributor started')

    # get last user id
    last_user_id = UserRepository.get_last_user_id()
    if last_user_id == 0:
        return

    # get start, end indexes of all parts
    records_batch_size = settings.CELERY_USER_PRODUCT_EMAIL_WORKER_BATCH_SIZE
    parts_indexes_list = get_start_end_indexes_n_parts(records_batch_size=records_batch_size,
                                                       total_records=last_user_id)
    # start subtasks
    for batch_indexes in parts_indexes_list:
        logger.debug(f"Creating subtask for user records, "
                     f"start_user_id = {batch_indexes.start_index}, end_user_id = {batch_indexes.end_index}")
        send_user_product_email_task.delay(batch_indexes.start_index, batch_indexes.end_index)


@celery.task
def send_user_product_email_task(user_id_start_idx: int, user_id_end_idx: int) -> None:
    """
    Process the user records between user_id_start_idx and user_id_end_idx

    :param user_id_start_idx: int, start batch index
    :param user_id_end_idx: int, end batch index
    :return: None
    """
    # Get data for this subtask to process
    users_records = UserRepository.get_users_with_search_phrases_in_range(start_user_id=user_id_start_idx,
                                                                          end_user_id=user_id_end_idx,
                                                                          user_columns=['id', 'email',
                                                                                        'product_alert_email_frequency',
                                                                                        'product_alert_email_last_sent'],
                                                                          user_product_search_phrases_columns=['search_phrase'])
    # Transform to a dict - key = namedtuple(email, alert_frequency, last_sent) : value = list(search_phrases)
    user_configuration_search_phrases_map = defaultdict(list)
    for record in users_records:
        user_config = UserEmailConfiguration(email=record['email'], alert_frequency=record['product_alert_email_frequency'],
                                             last_sent=record['product_alert_email_last_sent'])
        user_configuration_search_phrases_map[user_config].append(record['userproductsearchphrases__search_phrase'])

    # Check product_alert_email_last_sent and product_alert_email_frequency for user and send email
    ebay_service = EbayService()
    update_last_sent_emails = list()
    for user_config, search_phrases in user_configuration_search_phrases_map.items():
        send_email = False
        if user_config.last_sent:
            difference_total_seconds = (datetime.datetime.utcnow() - user_config.last_sent).seconds
            difference_mins, remaining_seconds = difference_total_seconds // 60, difference_total_seconds % 60
            # if mins are greater than alert frequency or there is a difference of <= 30 seconds, send email
            if difference_mins >= user_config.alert_frequency or (not difference_mins and remaining_seconds <= 30):
                send_email = True
        else:
            send_email = True

        if send_email:
            emails = list()
            collected_products_data = list()
            for phrase in search_phrases:
                try:
                    products_data = ebay_service.get_ebay_products_by_search_phrase(search_phrase=phrase,
                                                                                    sort=EbayService.EbaySearchAPISortOptions.PRICE)
                    collected_products_data += products_data
                except Exception as err:
                    logger.error(f'Unable to get products data from ebay err: {err}')
                    continue
                if products_data:
                    emails.append(UserEmail(subject='Ebay Product Alerts',
                                            message=create_email_content(products_data=products_data),
                                            sender_email=settings.EMAIL_HOST_USER,
                                            receiver_email_list=[user_config.email]))
            # Enqueue separate task to save data to shared db for insights phase 2
            if collected_products_data:
                save_ebay_products_to_shared_db.delay(products_data=collected_products_data)

            # Send email in bulk
            is_email_configured = is_email_settings_configured()
            if is_email_configured and emails:
                try:
                    logger.debug(f'Sending emails to {user_config.email}')
                    successfully_delivered_count = send_mass_mail(emails, fail_silently=False)
                except Exception as err:
                    logger.error(f'Email sending failed for {user_config.email}, error: {err}')
                    continue
                logger.debug(f'Successfully sent {successfully_delivered_count} out of {len(emails)} email messages')
            elif not is_email_configured:
                logger.debug(f'Email settings are not properly configured, skipping')

            # Collect emails to update product_alert_email_last_sent
            update_last_sent_emails.append(user_config.email)
    if update_last_sent_emails:
        UserRepository.update_product_alert_email_last_sent(emails=update_last_sent_emails)


def create_email_content(products_data: List[dict]) -> str:
    """
    Create a string in the correct format to be sent in the email content. check ebay service method for format.
    :param products_data: list of dict containing product data
    :return: str, the email content
    """
    # Format data here
    return json.dumps(products_data)


def get_start_end_indexes_n_parts(records_batch_size: int, total_records: int) -> List[BatchIndexes]:
    """
    Get a list of start, end indexes of n parts

    Note: Parts will be roughly equal, can be minor differences because of hard deleted records

    :param records_batch_size: int, number of records in each part
    :param total_records: int, total number of records
    :return: List[BatchIndexes] , BatchIndexes = namedtuple('BatchIndexes', ['start_index', 'end_index'])
    """
    number_of_parts = math.ceil(total_records / records_batch_size)
    start_id, end_id, i = 1, 0, 0
    all_parts_indexes = list()
    while i < number_of_parts:
        end_id = start_id + records_batch_size - 1
        all_parts_indexes.append(BatchIndexes(start_index=start_id, end_index=end_id))
        start_id = end_id
        i += 1

    return all_parts_indexes


def is_email_settings_configured() -> bool:
    """
    Check if required settings for email are configured in settings
    :return: bool
    """
    return all([getattr(settings, email_setting, None) for email_setting in
                ['EMAIL_BACKEND', 'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USE_TLS', 'EMAIL_HOST_USER',
                 'EMAIL_HOST_PASSWORD']])
