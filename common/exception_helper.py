import logging
import traceback

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from common.response_helper import ResponseHelper


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context) -> Response:
    """Custom exception handler for this service"""

    if isinstance(exc, APIException):
        status_code = exc.status_code
    elif isinstance(exc, Http404):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    response_data = dict()
    if settings.ENV in ('dev', 'local'):
        response_data['msg'] = str(exc)
        response_data['traceback'] = str(traceback.format_exc())
    else:
        response_data['msg'] = 'error'

    # Log all errors
    logging.exception(exc)

    return ResponseHelper.create_response(data=response_data, status_code=status_code)

