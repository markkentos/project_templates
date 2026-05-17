from abc import ABC, abstractmethod

from django.db import transaction
from django.utils.text import slugify

from store.models import Cart, Customer, Order, OrderItem, Product

from .factories import GiftWrapDecorator, LimitedEditionDecorator, factory_for_merch_type
from .observers import DomainEvent, configure_default_observers
from .pricing import get_pricing_strategy
from .shipping import get_shipping_strategy


class OrderProcessTemplate(ABC):
    """Шаблонный метод оформления заказа."""

    @transaction.atomic
    def execute(self, cart, customer_data, pricing_code="regular", shipping_code="courier", comment=""):
        self.validate_cart(cart)
        customer = self.resolve_customer(customer_data)
        order = self.create_order(customer, pricing_code, shipping_code, self.prepare_comment(comment))
        self.copy_items(cart, order)
        self.apply_totals(order, pricing_code, shipping_code)
        self.reserve_stock(order)
        self.close_cart(cart)
        self.after_success(order)
        return order

    def validate_cart(self, cart):
        items = list(cart.items.select_related("product"))
        if not items:
            raise ValueError("Корзина пуста.")
        for item in items:
            if item.quantity > item.product.stock:
                raise ValueError(f"Недостаточно товара '{item.product.name}' на складе.")

    def resolve_customer(self, data):
        customer, _ = Customer.objects.get_or_create(
            email=data["email"],
            defaults={
                "name": data["name"],
                "phone": data.get("phone", ""),
                "city": data.get("city", ""),
            },
        )
        changed = False
        for field in ["name", "phone", "city"]:
            value = data.get(field, "")
            if value and getattr(customer, field) != value:
                setattr(customer, field, value)
                changed = True
        if changed:
            customer.save(update_fields=["name", "phone", "city", "updated_at"])
        return customer

    def create_order(self, customer, pricing_code, shipping_code, comment):
        return Order.objects.create(
            customer=customer,
            pricing_strategy=pricing_code,
            delivery_method=shipping_code,
            comment=comment,
        )

    def copy_items(self, cart, order):
        for item in cart.items.select_related("product"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
            )

    def apply_totals(self, order, pricing_code, shipping_code):
        subtotal = sum(item.line_total for item in order.items.select_related("product"))
        price = get_pricing_strategy(pricing_code).calculate(subtotal)
        shipping = get_shipping_strategy(shipping_code).calculate(price.total)
        order.subtotal = price.subtotal
        order.discount = price.discount
        order.shipping_price = shipping.price
        order.total = price.total + shipping.price
        order.save(update_fields=["subtotal", "discount", "shipping_price", "total", "updated_at"])

    def reserve_stock(self, order):
        for item in order.items.select_related("product"):
            product = Product.objects.select_for_update().get(pk=item.product_id)
            product.stock -= item.quantity
            product.sales_count += item.quantity
            product.save(update_fields=["stock", "sales_count", "updated_at"])

    def close_cart(self, cart):
        cart.status = Cart.Status.CHECKED_OUT
        cart.save(update_fields=["status", "updated_at"])

    def after_success(self, order):
        configure_default_observers().publish(
            DomainEvent(
                event_type="order.created",
                order_id=order.pk,
                message=f"Создан заказ #{order.pk} на сумму {order.total} руб.",
            )
        )

    @abstractmethod
    def prepare_comment(self, comment):
        raise NotImplementedError


class StandardOrderProcess(OrderProcessTemplate):
    def prepare_comment(self, comment):
        return comment


class GiftOrderProcess(OrderProcessTemplate):
    def prepare_comment(self, comment):
        return f"Подарочный заказ. {comment}".strip()


class ProductGenerationTemplate:
    """Шаблонный метод генерации товаров для каталога."""

    def generate(self, rows, category_resolver):
        created = []
        for row in rows:
            factory = self.select_factory(row)
            payload = factory.create_product_data(row)
            payload = self.decorate_payload(row, payload)
            category = category_resolver(row["category"])
            created.append(self.persist(row, payload, category))
        return created

    def select_factory(self, row):
        return factory_for_merch_type(row["merch_type"])

    def decorate_payload(self, row, payload):
        if row.get("limited"):
            payload = LimitedEditionDecorator(payload).decorate()
        if row.get("gift_wrap"):
            payload = GiftWrapDecorator(payload).decorate()
        return payload

    def persist(self, row, payload, category):
        slug = row.get("slug") or slugify(payload["name"], allow_unicode=False)
        product, _ = Product.objects.update_or_create(
            slug=slug,
            defaults={
                **payload,
                "category": category,
                "is_active": True,
            },
        )
        return product


class DemoCatalogGenerationTemplate(ProductGenerationTemplate):
    def decorate_payload(self, row, payload):
        payload = super().decorate_payload(row, payload)
        if row.get("popularity_score", 0) >= 90 and not row.get("limited"):
            payload["description"] += " Популярная позиция для главной витрины."
        return payload
