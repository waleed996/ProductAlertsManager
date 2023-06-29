import logging

from django.db.models import Model


logger = logging.getLogger(__name__)


class SharedDbRouter:
    """Router to return db alias to use key from DATABASES dict in settings"""
    route_app_labels = {'shared_data_app'}

    def db_for_read(self, model: Model, **hints) -> str or None:
        """
        Select alias for read operation
        :param model: Model the read operation is being performed on
        :return:
        """
        if model._meta.app_label in self.route_app_labels:
            return 'products_shared_db'
        return None

    def db_for_write(self, model: Model, **hints) -> str or None:
        """
        Select alias for write operation
        :param model: Model the write operation is being performed on
        :return:
        """
        if model._meta.app_label in self.route_app_labels:
            return 'products_shared_db'
        return None

    def allow_relation(self, obj1: Model, obj2: Model, **hints) -> str or None:
        """
        Allow relations between two models or not
        :param obj1:
        :param obj2:
        :return:
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True

        return None

    def allow_migrate(self, db: str, app_label: str, model_name: str = None, **hints) -> str or None:
        """
        Allow migration or not
        :param db: Name of the db alias
        :param app_label: label of the app
        :param model_name: Name of the model
        :return:
        """
        if app_label in self.route_app_labels:
            return db == 'products_shared_db'
        return None

