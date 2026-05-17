from .models import Cart


def cart_summary(request):
    if not request.session.session_key:
        return {"cart_items_count": 0}
    cart = Cart.objects.filter(session_key=request.session.session_key, status=Cart.Status.OPEN).first()
    if not cart:
        return {"cart_items_count": 0}
    return {"cart_items_count": sum(item.quantity for item in cart.items.all())}
