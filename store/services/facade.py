from decimal import Decimal
from django.shortcuts import get_object_or_404
from store.models import Category, Order, Product, SalesPoint

from .singletons import SingletonMeta, StoreSettings
from .proxy import ProductCatalogProxy
from .adapter import AnimeTrendAdapter
from .math_models import SalesTrendModel
from .pricing import get_pricing_strategy, pricing_choices
from .shipping import get_shipping_strategy, shipping_choices
from .commands import (
    AddToCartCommand,
    UpdateCartItemCommand,
    RemoveCartItemCommand,
    CheckoutCommand,
    AdvanceOrderStateCommand,
    get_open_cart,
)
from .states import OrderStateMachine
from .composite import build_catalog_tree, CatalogIterator


class StoreFacade(metaclass=SingletonMeta):
    """Фасад для доступа к бизнес-логике и паттернам магазина.

    Служит единой точкой входа для представлений (views.py).
    """

    def get_open_cart(self, request):
        return get_open_cart(request)

    def get_cart_totals(self, cart, pricing_code="regular", shipping_code="courier"):
        subtotal = cart.subtotal
        price = get_pricing_strategy(pricing_code).calculate(subtotal)
        shipping = get_shipping_strategy(shipping_code).calculate(price.total)
        return {
            "subtotal": subtotal,
            "price": price,
            "shipping": shipping,
            "total": price.total + shipping.price,
        }

    def list_products(self, category_slug=None, query=None, limit=None):
        products = ProductCatalogProxy().list_products(category_slug=category_slug, query=query)
        if limit:
            return products[:limit]
        return products

    def get_product_detail(self, slug):
        product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
        trend = SalesTrendModel().calculate(product.sales_points.all(), supply_units=product.stock)
        return {
            "product": product,
            "trend": trend,
        }

    def get_top_trend_product_and_trend(self):
        trend_product = Product.objects.filter(sales_points__isnull=False).distinct().order_by("-sales_count").first()
        trend = None
        if trend_product:
            trend = SalesTrendModel().calculate(trend_product.sales_points.all(), supply_units=trend_product.stock)
        return {
            "product": trend_product,
            "trend": trend,
        }


    def get_featured_categories(self, limit=4):
        return Category.objects.filter(parent__isnull=True)[:limit]

    def get_all_categories(self):
        return Category.objects.filter(parent__isnull=True)

    def get_recommendations(self, limit=4):
        return AnimeTrendAdapter().recommended_products(limit=limit)

    def add_to_cart(self, request, product_slug, quantity=1):
        from .commands import CommandHistoryRegistry
        cmd = AddToCartCommand(request, product_slug, quantity)
        result = cmd.execute()
        CommandHistoryRegistry().push(request.session.session_key, cmd)
        return result

    def update_cart_item(self, request, item_id, quantity):
        from .commands import CommandHistoryRegistry
        cmd = UpdateCartItemCommand(request, item_id, quantity)
        result = cmd.execute()
        CommandHistoryRegistry().push(request.session.session_key, cmd)
        return result

    def remove_cart_item(self, request, item_id):
        from .commands import CommandHistoryRegistry
        cmd = RemoveCartItemCommand(request, item_id)
        result = cmd.execute()
        CommandHistoryRegistry().push(request.session.session_key, cmd)
        return result

    def undo_last_action(self, request):
        from .commands import CommandHistoryRegistry
        cmd = CommandHistoryRegistry().pop(request.session.session_key)
        if cmd:
            cmd.undo()
            return True
        return False

    def has_command_history(self, request):
        from .commands import CommandHistoryRegistry
        return CommandHistoryRegistry().has_history(request.session.session_key)

    def get_all_orders(self):
        return Order.objects.prefetch_related("items", "logs", "customer").all().order_by("-created_at")

    def get_all_logs(self):
        from store.models import ProcessLog
        return ProcessLog.objects.select_related("order").all().order_by("-created_at")[:30]

    def get_all_products_trends(self):
        products = Product.objects.filter(is_active=True).prefetch_related("sales_points").all()
        trends = []
        for product in products:
            trend = SalesTrendModel().calculate(product.sales_points.all(), supply_units=product.stock)
            trends.append({
                "product": product,
                "trend": trend
            })
        return trends


    def checkout_cart(self, request, form_data):
        return CheckoutCommand(request, form_data).execute()

    def get_order_detail(self, pk):
        order = get_object_or_404(Order.objects.prefetch_related("items", "logs"), pk=pk)
        machine = OrderStateMachine()
        return {
            "order": order,
            "transitions": machine.allowed_transitions(order),
        }

    def advance_order_state(self, order_id, action):
        return AdvanceOrderStateCommand(order_id, action).execute()

    def get_catalog_tree_and_flat(self):
        roots = build_catalog_tree()
        flat_items = list(CatalogIterator(roots))
        return {
            "roots": roots,
            "flat_items": flat_items,
        }

    def get_pricing_choices(self):
        return pricing_choices()

    def get_shipping_choices(self):
        return shipping_choices()

    def get_patterns_demo_data(self):
        settings = StoreSettings()
        singleton_ids = (id(StoreSettings()), id(StoreSettings()))
        sample_subtotal = Decimal("6000.00")
        
        pricing_results = [
            get_pricing_strategy(code).calculate(sample_subtotal) 
            for code, _ in pricing_choices()
        ]
        shipping_results = [
            get_shipping_strategy(code).calculate(sample_subtotal) 
            for code, _ in shipping_choices()
        ]
        
        trend_product = Product.objects.filter(sales_points__isnull=False).distinct().first()
        trend = SalesTrendModel().calculate(trend_product.sales_points.all(), supply_units=trend_product.stock) if trend_product else None
        
        flat_tree = list(CatalogIterator(build_catalog_tree()))
        
        return {
            "settings": settings,
            "singleton_ids": singleton_ids,
            "pricing_results": pricing_results,
            "shipping_results": shipping_results,
            "trend_product": trend_product,
            "trend": trend,
            "adapter_titles": AnimeTrendAdapter().labels(),
            "tree_count": len(flat_tree),
            "sales_points_count": SalesPoint.objects.count(),
        }

