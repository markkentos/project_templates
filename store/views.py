from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, ReviewForm
from .models import Cart, Category, Product, Review, SalesPoint
from .services.adapter import AnimeTrendAdapter
from .services.commands import (
    AddToCartCommand,
    AdvanceOrderStateCommand,
    CheckoutCommand,
    RemoveCartItemCommand,
    UpdateCartItemCommand,
    get_open_cart,
)
from .services.composite import CatalogIterator, ProductLeaf, build_catalog_tree
from .services.math_models import SalesTrendModel
from .services.pricing import get_pricing_strategy, pricing_choices
from .services.proxy import ProductCatalogProxy
from .services.shipping import get_shipping_strategy, shipping_choices
from .services.singletons import StoreSettings
from .services.states import OrderStateMachine


def cart_totals(cart, pricing_code="regular", shipping_code="courier"):
    subtotal = cart.subtotal
    price = get_pricing_strategy(pricing_code).calculate(subtotal)
    shipping = get_shipping_strategy(shipping_code).calculate(price.total)
    return {
        "subtotal": subtotal,
        "price": price,
        "shipping": shipping,
        "total": price.total + shipping.price,
    }


def home(request):
    proxy = ProductCatalogProxy()
    products = proxy.list_products()[:8]
    trend_product = Product.objects.filter(sales_points__isnull=False).distinct().order_by("-sales_count").first()
    trend = None
    if trend_product:
        trend = SalesTrendModel().calculate(trend_product.sales_points.all())
    return render(
        request,
        "store/product_list.html",
        {
            "title": "Каталог аниме атрибутики",
            "products": products,
            "categories": Category.objects.filter(parent__isnull=True),
            "featured_categories": Category.objects.filter(parent__isnull=True)[:4],
            "recommendations": AnimeTrendAdapter().recommended_products(),
            "trend_product": trend_product,
            "trend": trend,
            "query": "",
            "current_category": None,
        },
    )


def product_list(request, category_slug=None):
    query = request.GET.get("q", "").strip()
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
    products = ProductCatalogProxy().list_products(category_slug=category_slug, query=query)
    return render(
        request,
        "store/product_list.html",
        {
            "title": current_category.name if current_category else "Все товары",
            "products": products,
            "categories": Category.objects.filter(parent__isnull=True),
            "featured_categories": Category.objects.filter(parent__isnull=True)[:4],
            "recommendations": AnimeTrendAdapter().recommended_products(),
            "query": query,
            "current_category": current_category,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(product=product, **form.cleaned_data)
            messages.success(request, "Отзыв добавлен.")
            return redirect(product)
    else:
        form = ReviewForm()

    trend = SalesTrendModel().calculate(product.sales_points.all())
    return render(
        request,
        "store/product_detail.html",
        {"product": product, "form": form, "trend": trend},
    )


@require_POST
def add_to_cart(request, slug):
    try:
        AddToCartCommand(request, slug, request.POST.get("quantity", 1)).execute()
        messages.success(request, "Товар добавлен в корзину.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect(request.POST.get("next") or "store:cart")


def cart_view(request):
    cart = get_open_cart(request)
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "update":
                UpdateCartItemCommand(request, request.POST["item_id"], request.POST["quantity"]).execute()
                messages.success(request, "Корзина обновлена.")
            elif action == "remove":
                RemoveCartItemCommand(request, request.POST["item_id"]).execute()
                messages.success(request, "Позиция удалена.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("store:cart")

    pricing_code = request.GET.get("pricing", "regular")
    shipping_code = request.GET.get("shipping", "courier")
    return render(
        request,
        "store/cart.html",
        {
            "cart": cart,
            "totals": cart_totals(cart, pricing_code, shipping_code),
            "pricing_code": pricing_code,
            "shipping_code": shipping_code,
            "pricing_choices": pricing_choices(),
            "shipping_choices": shipping_choices(),
        },
    )


def checkout(request):
    cart = get_open_cart(request)
    if not cart.items.exists():
        messages.warning(request, "Добавьте товары перед оформлением заказа.")
        return redirect("store:cart")

    initial = {
        "pricing_strategy": request.GET.get("pricing", "regular"),
        "delivery_method": request.GET.get("shipping", "courier"),
    }
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = CheckoutCommand(request, form.cleaned_data).execute()
                messages.success(request, f"Заказ #{order.pk} создан.")
                return redirect(order)
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "store/checkout.html",
        {"form": form, "cart": cart, "totals": cart_totals(cart, initial["pricing_strategy"], initial["delivery_method"])},
    )


def order_detail(request, pk):
    from .models import Order

    order = get_object_or_404(Order.objects.prefetch_related("items", "logs"), pk=pk)
    machine = OrderStateMachine()
    if request.method == "POST":
        try:
            AdvanceOrderStateCommand(order.pk, request.POST["action"]).execute()
            messages.success(request, "Статус заказа обновлен.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect(order)

    return render(
        request,
        "store/order_detail.html",
        {"order": order, "transitions": machine.allowed_transitions(order)},
    )


def catalog_tree(request):
    roots = build_catalog_tree()
    flat_items = list(CatalogIterator(roots))
    return render(request, "store/catalog_tree.html", {"roots": roots, "flat_items": flat_items, "product_leaf": ProductLeaf})


def patterns_demo(request):
    settings = StoreSettings()
    singleton_ids = (id(StoreSettings()), id(StoreSettings()))
    sample_subtotal = 6000
    pricing_results = [strategy.calculate(sample_subtotal) for strategy in [get_pricing_strategy(code) for code, _ in pricing_choices()]]
    shipping_results = [get_shipping_strategy(code).calculate(sample_subtotal) for code, _ in shipping_choices()]
    trend_product = Product.objects.filter(sales_points__isnull=False).distinct().first()
    trend = SalesTrendModel().calculate(trend_product.sales_points.all()) if trend_product else None
    flat_tree = list(CatalogIterator(build_catalog_tree()))
    return render(
        request,
        "store/patterns_demo.html",
        {
            "settings": settings,
            "singleton_ids": singleton_ids,
            "pricing_results": pricing_results,
            "shipping_results": shipping_results,
            "trend_product": trend_product,
            "trend": trend,
            "adapter_titles": AnimeTrendAdapter().labels(),
            "tree_count": len(flat_tree),
            "sales_points_count": SalesPoint.objects.count(),
        },
    )
