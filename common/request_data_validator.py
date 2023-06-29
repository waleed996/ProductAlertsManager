from typing import List


class RequestDataValidationHelper:
    """
    Generic request data validation helper utility
    """

    def validate(self, data: dict, validation_schema: dict) -> List[str] or None:
        """
        Validates rules defined in "request_data_validation_schema" on all APIViews

        :param data: dict , data to validate
        :param validation_schema: dict , schema to validate the request data
        :return: list(str) OR True , returns list of errors or None if validation passes
        """

        validation_errors = list()
        for field, rules in validation_schema.items():

            for rule in rules:
                rule_method = 'validate_rule_' + rule
                if not hasattr(self, rule_method):
                    return validation_errors.append(f"Rule: {rule} is not implemented")

                result = getattr(self, rule_method)(field, data.get(field))

                if isinstance(result, str):
                    validation_errors.append(result)

        return validation_errors if validation_errors else None

    def validate_rule_int(self, field: str, value: object) -> None or str:
        """
        Validate if value is int
        :param field: field name being checked
        :param value: object to check
        :return: str OR None , returns error message or None if no error
        """
        return f"{field} should be a integer" if not isinstance(value, int) else None

    def validate_rule_str(self, field: str, value: object) -> None or str:
        """
        Validate if value is str
        :param field: field name being checked
        :param value: object to check
        :return: str OR None , returns error message or None if no error
        """
        return f"{field} should be a string" if not isinstance(value, str) else None

    def validate_rule_required(self, field: str, value: object) -> None or str:
        """
        Validate if value is not None
        :param field: field name being checked
        :param value: object to check
        :return: str OR None , returns error message or None if no error
        """
        return f"{field} should have a value" if value is None else None

    def validate_rule_list_of_str(self, field: str, value: object) -> None or str:
        """
        Validate if value is a list of string
        :param field: field name being checked
        :param value: object to check
        :return: str OR None , returns error message or None if no error
        """
        return f"{field} should be a list of str" if not isinstance(value, list) or not all \
            ([isinstance(_, str) for _ in value]) else None

