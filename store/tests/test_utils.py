import pytest
from django.utils.safestring import SafeString

from ..utils import render_image_preview, short_description
from .conftest import DummyObj


# render_image_preview
def test_render_image_preview_with_valid_image(dummy_obj_with_image) -> None:
    """
    Test that render_image_preview returns SafeString <img> tag
    when object has a valid image.
    """
    result = render_image_preview(dummy_obj_with_image)
    assert isinstance(result, SafeString)
    assert '<img src="http://example.com/default.png"' in str(result)


def test_render_image_preview_no_image(dummy_obj_no_image) -> None:
    """
    Test that render_image_preview returns fallback message
    when image is None.
    """
    assert render_image_preview(dummy_obj_no_image) == "No image selected"


def test_render_image_preview_invalid_image(dummy_obj_invalid_image) -> None:
    """
    Test that render_image_preview returns fallback message
    when image has no .url.
    """
    assert render_image_preview(dummy_obj_invalid_image) == "No image selected"


# short_description
def test_short_description_truncates_long_text() -> None:
    """
    Test that short_description truncates text longer than 50 chars
    and appends '...'.
    """
    long_text = "x" * 60
    obj = DummyObj(image=None, description=long_text)
    result = short_description(obj)
    assert len(result) == 53
    assert result.endswith("...")
    assert result.startswith("x" * 50)


def test_short_description_full_or_empty() -> None:
    """
    Test that short_description returns full text when ≤50 chars,
    and 'No description' when description is empty or None.
    """

    exact = "y" * 50
    assert short_description(DummyObj(image=None, description=exact)) == exact
    assert short_description(DummyObj(image=None, description="")) == "No description"
    assert short_description(DummyObj(image=None, description=None)) == "No description"
