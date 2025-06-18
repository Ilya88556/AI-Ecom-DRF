import hashlib

from django.conf import settings


class SignatureVerifier:
    """
    Utility class for verifying signatures from supported payment gateways.
    """

    KEYS: dict[str, str] = {
        "fondy": settings.FONDY_SECRET_KEY,
        "liqpay": settings.LIQPAY_SECRET_KEY,
        "monobank": settings.MONOBANK_SECRET_KEY,
    }

    @staticmethod
    def verify_signature(gateway_name: str, data: str, signature: str) -> bool:
        """
        Verifies the signature for the given payment gateway.

        Constructs the expected signature using the pattern: key + data + key,
        hashed with SHA-1, and compares it to the provided signature.
        """
        key = SignatureVerifier.KEYS.get(gateway_name)

        expected_signature = hashlib.sha1((key + data + key).encode()).hexdigest()

        return signature == expected_signature
