import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from ..utils import generate_product_description


@patch("store.utils.OpenAI")
def test_generate_ai_product_description(mock_openai):
    """
    Test for the generate_product_description function.

    - Mocks the OpenAI client using unittest.mock.
    - Simulates a response with a sample AI-generated product description.
    - Calls the function with test input data (product name, description, price, etc.).
    - Asserts that the returned result contains the expected AI-generated content.
    - Verifies that the OpenAI client's `response.create()` method is called exactly once.

    Ensures that the integration with OpenAI works as expected and returns usable output.
    """
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Title: Example\nHook: ...")]

    mock_response = MagicMock()
    mock_response.output = [mock_message]

    mock_client.responses.create.return_value = mock_response

    result = generate_product_description(
        product_name="Test Product",
        product_description="This is a test product.",
        price=Decimal("100.50"),
        category="Electronics",
        vendor="TestVendor",
        industry=["Retail"],
        product_type=["Gadget"]
    )

    assert "Title: Example" in result
    mock_client.responses.create.assert_called_once()


@patch("store.utils.OpenAI")
def test_generate_ai_product_description_empty_choices(mock_openai):
    """
    Tests generate_product_description when OpenAI returns an empty 'choices' list.

    - Mocks the OpenAI client to simulate an API response with no choices.
    - Calls the function with minimal test input.
    - Asserts that the function returns the fallback error message.

    This test ensures proper error handling when the LLM returns an empty or invalid response.
    """
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.responses.create.return_value = {"choices": []}

    result = generate_product_description(
        product_name="Test Product",
        product_description="Test desc.",
        price=Decimal("1"),
        category="A",
        vendor="B",
        industry=[],
        product_type=[]
    )

    assert result == "An error occurred during sale product description generation"


@patch("store.utils.OpenAI")
def test_generate_ai_product_description_no_message(mock_openai):
    """
    Tests generate_product_description when OpenAI response lacks the 'message' key.

    - Mocks the OpenAI client to return a 'choices' list with an empty dictionary.
    - Simulates a malformed or incomplete API response.
    - Verifies that the function returns the expected error message.

    Ensures the function handles missing 'message' fields gracefully in OpenAI responses.
    """
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.output = [{}]

    mock_client.responses.create.return_value = mock_response

    result = generate_product_description(
            product_name="Test Product",
            product_description="Test desc.",
            price=Decimal("1"),
            category="A",
            vendor="B",
            industry=[],
            product_type=[]
        )

    assert result == "An error occurred during sale product description generation"


@patch("store.utils.OpenAI")
def test_generate_product_description_incomplete_response(mock_openai):
    """
    Tests generate_product_description when OpenAI returns a non-final (incomplete) response.

    - Mocks the OpenAI client to return a response with 'finish_reason' set to 'length'.
    - Calls the function with basic product input.
    - Asserts that the function returns the predefined error message.

    This test ensures that incomplete LLM outputs are properly detected and rejected.
    """
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.responses.create.return_value = {
        "choices": [
            {
                "message": {"content": "Some text"},
                "finish_reason": "length"
            }
        ]
    }

    result = generate_product_description(
        product_name="Test Product",
        product_description="Test desc.",
        price=Decimal("1"),
        category="A",
        vendor="B",
        industry=[],
        product_type=[]
    )

    assert result == "An error occurred during sale product description generation"


@patch("store.utils.OpenAI")
def test_generate_product_description_exception(mock_openai):
    """
    Tests generate_product_description when an exception is raised during the OpenAI API call.

    - Mocks the OpenAI client to raise an Exception (e.g., network failure) when calling `.create()`.
    - Verifies that the function catches the exception and returns the fallback error message.

    This test ensures that unexpected runtime errors from the LLM client are gracefully handled.
    """
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.responses.create.side_effect = Exception("Network fail")

    result = generate_product_description(
        product_name="Test Product",
        product_description="Test desc.",
        price=Decimal("1"),
        category="A",
        vendor="B",
        industry=[],
        product_type=[]
    )

    assert result == "An error occurred during sale product description generation"
