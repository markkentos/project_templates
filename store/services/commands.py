from abc import ABC, abstractmethod

from django.shortcuts import get_object_or_404

from store.models import Cart, CartItem, Order, Product

from .processes import StandardOrderProcess
from .states import OrderStateMachine
from .singletons import SingletonMeta


class Command(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError

    def undo(self):
        pass


def get_open_cart(request):
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        status=Cart.Status.OPEN,
    )
    return cart


def transfer_open_cart(old_session_key, new_session_key):
    if not old_session_key or not new_session_key or old_session_key == new_session_key:
        return

    source_cart = Cart.objects.filter(
        session_key=old_session_key,
        status=Cart.Status.OPEN,
    ).first()
    if not source_cart:
        return

    target_cart, _ = Cart.objects.get_or_create(
        session_key=new_session_key,
        status=Cart.Status.OPEN,
    )

    if source_cart.pk == target_cart.pk:
        return

    for source_item in source_cart.items.select_related("product"):
        target_item, item_created = CartItem.objects.get_or_create(
            cart=target_cart,
            product=source_item.product,
            defaults={"quantity": source_item.quantity},
        )
        if not item_created:
            target_item.quantity = min(
                target_item.quantity + source_item.quantity,
                source_item.product.stock,
            )
            target_item.save(update_fields=["quantity", "updated_at"])
    source_cart.delete()


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

    def undo(self):
        product = get_object_or_404(Product, slug=self.product_slug)
        cart = get_open_cart(self.request)
        item = CartItem.objects.filter(cart=cart, product=product).first()
        if item:
            if item.quantity <= self.quantity:
                item.delete()
            else:
                item.quantity -= self.quantity
                item.save(update_fields=["quantity", "updated_at"])
        return cart


class UpdateCartItemCommand(Command):
    def __init__(self, request, item_id, quantity):
        self.request = request
        self.item_id = item_id
        self.quantity = int(quantity)
        self.old_quantity = None
        self.product = None

    def execute(self):
        cart = get_open_cart(self.request)
        item = get_object_or_404(CartItem, pk=self.item_id, cart=cart)
        self.old_quantity = item.quantity
        self.product = item.product
        if self.quantity <= 0:
            item.delete()
            return cart
        if self.quantity > item.product.stock:
            raise ValueError("Количество превышает остаток на складе.")
        item.quantity = self.quantity
        item.save(update_fields=["quantity", "updated_at"])
        return cart

    def undo(self):
        if self.old_quantity is not None and self.product is not None:
            cart = get_open_cart(self.request)
            item, _ = CartItem.objects.get_or_create(
                cart=cart,
                product=self.product,
                defaults={"quantity": self.old_quantity}
            )
            item.quantity = self.old_quantity
            item.save(update_fields=["quantity", "updated_at"])
            return cart


class RemoveCartItemCommand(Command):
    def __init__(self, request, item_id):
        self.request = request
        self.item_id = item_id
        self.product = None
        self.old_quantity = None

    def execute(self):
        cart = get_open_cart(self.request)
        item = get_object_or_404(CartItem, pk=self.item_id, cart=cart)
        self.product = item.product
        self.old_quantity = item.quantity
        item.delete()
        return cart

    def undo(self):
        if self.product is not None and self.old_quantity is not None:
            cart = get_open_cart(self.request)
            item, _ = CartItem.objects.get_or_create(
                cart=cart,
                product=self.product,
                defaults={"quantity": self.old_quantity}
            )
            item.quantity = self.old_quantity
            item.save(update_fields=["quantity", "updated_at"])
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


class CommandHistoryRegistry(metaclass=SingletonMeta):
    """Синглтон реестр для отмены команд в текущей сессии."""
    def __init__(self):
        self._history = {}  # session_key -> stack of Command objects

    def push(self, session_key, command):
        if not session_key:
            return
        self._history.setdefault(session_key, []).append(command)

    def pop(self, session_key):
        if not session_key:
            return None
        stack = self._history.get(session_key, [])
        if stack:
            return stack.pop()
        return None

    def has_history(self, session_key):
        if not session_key:
            return False
        return len(self._history.get(session_key, [])) > 0

    def transfer_history(self, old_session_key, new_session_key):
        if not old_session_key or not new_session_key or old_session_key == new_session_key:
            return
        old_history = self._history.pop(old_session_key, [])
        if not old_history:
            return
        self._history.setdefault(new_session_key, []).extend(old_history)
