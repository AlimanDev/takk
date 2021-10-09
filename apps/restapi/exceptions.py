from rest_framework.exceptions import APIException
from rest_framework import status


class RefundInvalidItem(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid order item'


class RefundAmountInvalid(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Refund amount should not be more than the order amount'


class CustomException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
