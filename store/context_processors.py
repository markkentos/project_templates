from .models import Cart


def cart_summary(request):
    is_manager = request.user.is_authenticated and request.user.is_staff
    context = {"is_manager": is_manager}
    if not request.session.session_key:

        context["cart_items_count"] = 0
        return context
    cart = Cart.objects.filter(session_key=request.session.session_key, status=Cart.Status.OPEN).first()
    if not cart:
        context["cart_items_count"] = 0
        return context
    context["cart_items_count"] = sum(item.quantity for item in cart.items.all())
    return context

