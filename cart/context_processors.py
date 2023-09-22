from .cart_utils import get_cart


def cart_processor(request):
    """
    Add cart information to context for all templates.
    """
    cart = get_cart(request)
    total_items = len(cart)
    return {'cart_total_items': total_items, 'cart': cart}
