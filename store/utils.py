from typing import Any
from openai import OpenAI
import logging
from decimal import Decimal

from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.conf import settings

logger = logging.getLogger("project")

def render_image_preview(obj: Any) -> str:
    """
    Returns an HTML-safe <img> tag for displaying an image preview in the Django admin.

    Escapes the image URL to prevent XSS vulnerabilities and uses `mark_safe`
    to allow HTML rendering in the admin list or detail views.

    Args:
        obj (Any): The model instance expected to have an `image` field.

    Returns:
        str: An HTML <img> tag if the image exists and has a valid URL,
             otherwise a fallback message ("No image selected").
    """
    if obj.image and hasattr(obj.image, "url"):
        return mark_safe(
            f'<img src="{escape(obj.image.url)}" '
            f'style="max-height: 100px; '
            f"display: block; "
            f'margin: 0 auto;"/>'
        )

    return "No image selected"


def short_description(obj: Any) -> str:
    """
    Returns a shortened version of the description field for the admin list view.
    """
    if obj.description:
        return obj.description[:50] + ("..." if len(obj.description) > 50 else "")
    return "No description"


def generate_product_description(product_name: str,
                                 product_description: str,
                                 price: Decimal,
                                 category: str,
                                 vendor: str,
                                 industry: list[str],
                                 product_type: list[str]) -> str:
    """
    Generates a persuasive HTML-formatted product description using an LLM (via OpenAI API).

    The function sends structured product metadata (name, description, price, category, etc.)
    to a language model with a detailed prompt, requesting a fully formatted marketing description.

    The generated output follows a strict HTML template with a title, hook, bullet-pointed features,
    a mini story, a call-to-action, and SEO keywords.

    Args:
        product_name (str): Name of the product.
        product_description (str): Raw input description or technical info.
        price (Decimal): Product price.
        category (str): Product category (e.g. Electronics, Fashion).
        vendor (str): Manufacturer or brand name.
        industry (list[str]): Related industry sector (e.g. Retail, Health).
        product_type (list[str]): Product type or subcategory (e.g. Smart Gadget, Kitchenware).

    Returns:
        str: HTML-formatted product description if successful; otherwise, an error message string.

    Raises:
        ValueError: If the LLM response is empty or malformed.
    """
    prompt: str = (
        f"""
        **Role**  
        You are an LLM copywriter. Using *raw product text*: 
        (plus optional `category`, `industry`, `brand`, `product_type`) 
        - product name: {product_name},
        - product description: {product_description},
        - product price: {price},
        - product category: {category},
        - product vendor: {vendor},
        - product industry: {industry}, 
        - product type: {product_type}
        
        you must craft a persuasive product description **in the same language as the input**.
        
        **Process**  
        1. Extract key facts: purpose, specs, pains/benefits, target audience.  
        2. Use provided optional fields; if absent, infer logically.  
        3. Produce copy in the structure below.   
        
        **Output structure (rendered in HTML)**    
        <p><strong>Title</strong></p>

        <p>Hook sentence (1–2 lines)</p>

        <ul>
        <li><strong>Feature 1</strong> — Benefit 1</li>
        <li><strong>Feature 2</strong> — Benefit 2</li>
        <li><strong>Feature 3</strong> — Benefit 3</li>
        <!-- 3 to 6 total items -->
        </ul>

        <p>Mini story: describe how this product solves a problem, 2–3 sentences</p>

        <p><strong>Call to Action</strong></p>

        <p style="font-size:0.9em; color:#777;"><em>SEO: keyword1, keyword2, keyword3, …</em></p> 
        
        **Style**  
        - Write from second person (“you”).  
        - Include concrete numbers and facts.  
        - Do **not** include vague marketing clichés (“great quality”, “best price”).  
        - Do **not** add any labels, section titles, or extra text — just the final HTML block.
        """
    )

    client = OpenAI(
        api_key=settings.OPEN_API_KEY
    )

    try:
        response = client.responses.create(
            model="gpt-4.1",
            instructions="You are a professional product copywriter.",
            input=prompt
        )

        logger.info("OpenAI raw response: %r", response)

        if not hasattr(response, "output") or not response.output:
            logger.error("OpenAI: Empty or incorrect response for product %s: %s", product_name, response)
            raise ValueError("OpenAI: Empty or incorrect response")

        message = response.output[0]
        text = message.content[0].text.strip()

        return text

    except Exception as e:
        logger.error(f"An error occurred during sale product description generation: {e}")
        return "An error occurred during sale product description generation"



