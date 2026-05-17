from abc import ABC, abstractmethod

from django.shortcuts import get_object_or_404

from store.models import Cart, CartItem, Order, Product

from .processes import StandardOrderProcess
from .states import OrderStateMachine


class Command(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError


def get_open_cart(request):
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        status=Cart.Status.OPEN,
    )
    return cart


class AddToCartCommand(Command):
    def __init__(self, request, product_slug, quantity=1):
        self.request = request
        self.product_slug = product_slug
        self.quantity = max(1, int(quantity))

    def execute(self):
        product = get_object_or_404(Product, slug=self.product_slug, is_active=True)
        if not product.is_available:
            raise ValueError("Товар недоступен.")
        cart = get_open_cart(self.request)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        new_quantity = self.quantity if created else item.quantity + self.quantity
        if new_quantity > product.stock:
            raise ValueError("Нельзя добавить больше, чем есть на складе.")
        item.quantity = new_quantity
        item.save(update_fields=["quantity", "updated_at"])
        return cart


class UpdateCartItemCommand(Command):
    def __init__(self, request, item_id, quantity):
        self.request = request
        self.item_id = item_id
        self.quantity = int(quantity)

    def execute(self):
        cart = get_open_cart(self.request)
        item = get_object_or_404(CartItem, pk=self.item_id, cart=cart)
        if self.quantity <= 0:
            item.delete()
            return cart
        if self.quantity > item.product.stock:
            raise ValueError("Количество превышает остаток на складе.")
        item.quantity = self.quantity
        item.save(update_fields=["quantity", "updated_at"])
        return cart


class RemoveCartItemCommand(Command):
    def __init__(self, request, item_id):
        self.request = request
        self.item_id = item_id

    def execute(self):
        cart = get_open_cart(self.request)
        get_object_or_404(CartItem, pk=self.item_id, cart=cart).delete()
        return cart


class CheckoutCommand(Command):
    def __init__(self, request, form_data):
        self.request = request
        self.form_data = form_data

    def execute(self):
        cart = get_open_cart(self.request)
        process = StandardOrderProcess()
        return process.execute(
            cart=cart,
            customer_data={
                "name": self.form_data["name"],
                "email": self.form_data["email"],
                "phone": self.form_data.get("phone", ""),
                "city": self.form_data.get("city", ""),
            },
            pricing_code=self.form_data.get("pricing_strategy", "regular"),
            shipping_code=self.form_data.get("delivery_method", "courier"),
            comment=self.form_data.get("comment", ""),
        )


class AdvanceOrderStateCommand(Command):
    def __init__(self, order_id, action):
        self.order_id = order_id
        self.action = action

    def execute(self):
        order = get_object_or_404(Order, pk=self.order_id)
        return OrderStateMachine().apply(order, self.action)
