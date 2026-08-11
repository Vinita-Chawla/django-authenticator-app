# utils/response.py
from rest_framework.response import Response
from rest_framework import status

class CustomResponse:
    @staticmethod
    def success(message="Success", data=None, status_code=status.HTTP_200_OK):
        response_data = {
            "status": status_code,
            "message": message,
            "data": data or {},
            "errors": None
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def error(message="Error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        response_data = {
            "status": status_code,
            "message": message,
            "data": None,
            "errors": errors or {}
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def validation_error(errors, message="Validation failed", status_code=status.HTTP_400_BAD_REQUEST):
        response_data = {
            "status": status_code,
            "message": message,
            "data": None,
            "errors": errors
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def not_found(message="Resource not found", status_code=status.HTTP_404_NOT_FOUND):
        response_data = {
            "status": status_code,
            "message": message,
            "data": None,
            "errors": None
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def unauthorized(message="Authentication required", status_code=status.HTTP_401_UNAUTHORIZED):
        response_data = {
            "status": status_code,
            "message": message,
            "data": None,
            "errors": None
        }
        return Response(response_data, status=status_code)