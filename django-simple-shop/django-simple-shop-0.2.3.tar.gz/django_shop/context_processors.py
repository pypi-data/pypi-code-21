from .cart import Cart


def cart(request):
    """Add basket object to context"""
    if hasattr(request, 'session'):
        return {'cart': Cart(request.session, need_data=request.path.startswith('/cart'))}
    return {}
