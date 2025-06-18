from rest_framework.exceptions import APIException


class PaymentGatewayException(APIException):
    """
    Payment system gateway error
    """


class PaymentProcessingException(APIException):
    """
    Payment system processing error
    """

    status_code = 400
    default_detail = "Payment processing error"
    default_code = "payment_error"
