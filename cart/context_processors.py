from .cart import Cart

def cart(request):
    """
    Context processor to share the active session Cart object across all HTML templates.
    """
    return {'cart': Cart(request)}
