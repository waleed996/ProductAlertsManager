from rest_framework.response import Response


class ResponseHelper:

    @staticmethod
    def create_response(data: object, status_code: int = 200) -> Response:
        return Response(data={'data': data}, status=status_code)
