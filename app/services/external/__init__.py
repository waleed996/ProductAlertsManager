

class BaseExternalService:
    """
    Base service for all external/third party services.
    """

    def _handle_response(self, response):
        """
        Override to handle service response
        :param response: requests library response object
        :return:
        """
        pass

