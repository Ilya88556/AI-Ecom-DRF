from rest_framework import serializers


class PaymentProcessingSerializer(serializers.Serializer):
    """
    Serializer for processing payment requests.

    Validates that the selected payment gateway is one of the supported options:
    'liqpay', 'monobank', or 'fondy'. Raises a custom error message for invalid choices.
    """

    gateway = serializers.ChoiceField(
        choices=["liqpay", "monobank", "fondy"],
        error_messages={"invalid_choice": "Gateway not supported"},
    )


class CallbackSerializer(serializers.Serializer):
    """
    Serializer for handling payment gateway callbacks.

    Validates the presence and correctness of the gateway name, base64-encoded data,
    and signature required for verifying the callback's authenticity.
    """

    gateway = serializers.ChoiceField(
        choices=["liqpay", "monobank", "fondy"],
        error_messages={"invalid_choice": "Gateway not supported"},
    )
    data = serializers.CharField()
    signature = serializers.CharField()
