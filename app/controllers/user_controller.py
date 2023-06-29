from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from common.request_data_validator import RequestDataValidationHelper
from common.response_helper import ResponseHelper

from app.services.user_service import UserService


class UserController(ViewSet):
    """CRUD APIs for the 'User' model"""

    request_data_validation_schema = {
        'create': {
            'email': ['required', 'str'],
            'product_alert_email_frequency': ['required', 'int'],
            'search_phrases': ['required', 'list_of_str']
        }
    }

    def list(self, request) -> Response:
        """
        Get user object using user_id or email query param

        :param request: client Request containing user_id or email query param
        :return: Response
        """

        user_id = request.query_params.get('user_id')
        email = request.query_params.get('email')

        user_service = UserService()
        if user_id:
            return ResponseHelper.create_response(
                user_service.get_user_by_user_id(user_id=user_id, load_search_phrases=True, serialize=True))
        elif email:
            return ResponseHelper.create_response(
                user_service.get_user_by_email(email=email, load_search_phrases=True, serialize=True))
        else:
            return ResponseHelper.create_response(data={'errors': ['user_id or email query param required']},
                                                  status_code=400)

    def create(self, request) -> Response:
        """
        Create user object along with search phrases (just to keep it simple)

        :param request: client Request with payload data

        format:
        {
            'email': 'test@abc.com',
            'product_alert_email_frequency': 2 | 10 | 20,
            'search_phrases': ['gym', 'fitness', 'music' ...]
        }

        :return: Response
        """

        # Validate request payload
        errors = RequestDataValidationHelper().validate(data=request.data,
                                                        validation_schema=self.request_data_validation_schema['create'])
        if errors:
            return ResponseHelper.create_response(data={'errors': errors}, status_code=400)

        user_service = UserService()
        user_service.create_user(email=request.data['email'],
                                 product_alert_email_frequency=request.data['product_alert_email_frequency'],
                                 search_phrases=request.data['search_phrases'])

        return ResponseHelper.create_response(data="User created successfully")


