from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from cart.models import Cart, CartItem
from store.models import Product
from users.models import AuthUser


def get_or_create_user_cart(user: AuthUser) -> tuple[Cart, bool]:
    """
    Retrieve or create an active cart for the given user.
    """
    return Cart.objects.get_or_create(user=user, status="active")


def add_item_to_cart(user: AuthUser, product: Product, quantity: int = 1) -> Cart:
    """
    Add a product to the user's active cart.
    If the cart item exists, its quantity is incremented; otherwise, a new cart item is created.
    """
    try:
        with transaction.atomic():
            cart, _ = get_or_create_user_cart(user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product
            )
    except IntegrityError:
        raise ValueError("Multiple active carts exist")

    cart_item.quantity = cart_item.quantity + quantity if not created else quantity
    cart_item.save()

    return cart


def update_item_quantity(user: AuthUser, product: Product, quantity: int) -> Cart:
    """
    Update the quantity of a specific product in the user's active cart.
    """
    cart = Cart.objects.active_for(user)

    if cart:
        cart = (
            Cart.objects.filter(pk=cart.pk).prefetch_related("items__product").first()
        )

    if not cart:
        raise ValueError("No active cart")

    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.quantity = quantity
    cart_item.save()

    return cart


def remove_item_from_cart(user: AuthUser, product_id: int) -> Cart:
    """
    Remove a product from the user's active cart by its product ID.
    """
    cart = Cart.objects.active_for(user)
    if cart:
        cart = (
            Cart.objects.filter(pk=cart.pk).prefetch_related("items__product").first()
        )

    if not cart:
        raise ValueError("No active cart")

    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    if not cart_item:
        raise ValueError("Product not found in cart")

    cart_item.delete()
    return cart
