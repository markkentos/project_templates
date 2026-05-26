from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .forms import CheckoutForm, ReviewForm
from .models import Review, Order
from .services.facade import StoreFacade
from .services.composite import ProductLeaf


def home(request):
    facade = StoreFacade()
    products = facade.list_products(limit=8)
    
    context = {
        "title": "Каталог аниме атрибутики",
        "products": products,
        "categories": facade.get_all_categories(),
        "featured_categories": facade.get_featured_categories(limit=4),
        "recommendations": facade.get_recommendations(limit=4),
        "query": "",
        "current_category": None,
    }
    return render(request, "store/product_list.html", context)


def product_list(request, category_slug=None):
    facade = StoreFacade()
    query = request.GET.get("q", "").strip()
    current_category = None
    if category_slug:
        from django.shortcuts import get_object_or_404
        from .models import Category
        current_category = get_object_or_404(Category, slug=category_slug)
    
    products = facade.list_products(category_slug=category_slug, query=query)
    return render(
        request,
        "store/product_list.html",
        {
            "title": current_category.name if current_category else "Все товары",
            "products": products,
            "categories": facade.get_all_categories(),
            "featured_categories": facade.get_featured_categories(limit=4),
            "recommendations": facade.get_recommendations(limit=4),
            "query": query,
            "current_category": current_category,
        },
    )


def product_detail(request, slug):
    facade = StoreFacade()
    detail = facade.get_product_detail(slug)
    product = detail["product"]
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(product=product, **form.cleaned_data)
            messages.success(request, "Отзыв добавлен.")
            return redirect(product)
    else:
        form = ReviewForm()

    return render(
        request,
        "store/product_detail.html",
        {"product": product, "form": form},
    )


@login_required
def manager_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен. Требуются права менеджера.")
        return redirect("store:home")
        
    facade = StoreFacade()
    active_tab = request.GET.get("tab", "orders")
    
    context = {
        "title": "Панель Менеджера",
        "active_tab": active_tab,
    }
    
    if active_tab == "orders":
        context["orders"] = facade.get_all_orders()
    elif active_tab == "logs":
        context["logs"] = facade.get_all_logs()
    elif active_tab == "forecast":
        from .models import Product
        products = Product.objects.all().order_by("name")
        context["products"] = products
        
        selected_product_id = request.GET.get("product_id")
        selected_product = None
        trend = None
        if selected_product_id:
            try:
                selected_product = Product.objects.get(id=selected_product_id)
                detail = facade.get_product_detail(selected_product.slug)
                trend = detail["trend"]
            except Product.DoesNotExist:
                pass
        
        context["selected_product"] = selected_product
        context["trend"] = trend
        
    return render(request, "store/manager_dashboard.html", context)


@require_POST
def add_to_cart(request, slug):
    facade = StoreFacade()
    try:
        facade.add_to_cart(request, slug, request.POST.get("quantity", 1))
        messages.success(request, "Товар добавлен в корзину.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect(request.POST.get("next") or "store:cart")


def cart_view(request):
    facade = StoreFacade()
    cart = facade.get_open_cart(request)
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "update":
                facade.update_cart_item(request, request.POST["item_id"], request.POST["quantity"])
                messages.success(request, "Корзина обновлена.")
            elif action == "remove":
                facade.remove_cart_item(request, request.POST["item_id"])
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
            "totals": facade.get_cart_totals(cart, pricing_code, shipping_code),
            "pricing_code": pricing_code,
            "shipping_code": shipping_code,
            "pricing_choices": facade.get_pricing_choices(),
            "shipping_choices": facade.get_shipping_choices(),
            "has_history": facade.has_command_history(request),
        },
    )


@login_required
def checkout(request):
    facade = StoreFacade()
    cart = facade.get_open_cart(request)
    if not cart.items.exists():
        messages.warning(request, "Добавьте товары перед оформлением заказа.")
        return redirect("store:cart")

    initial = {
        "pricing_strategy": request.GET.get("pricing", "regular"),
        "delivery_method": request.GET.get("shipping", "courier"),
    }
    
    # Предзаполнение данных из профиля покупателя (если они есть)
    customer_profile = getattr(request.user, "customer_profile", None)
    if customer_profile:
        initial["name"] = customer_profile.name
        initial["email"] = customer_profile.email
        initial["phone"] = customer_profile.phone
        initial["city"] = customer_profile.city
    else:
        # Если профиля нет, подгружаем базовую почту
        initial["email"] = request.user.email

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                # Оформление заказа
                order = facade.checkout_cart(request, form.cleaned_data)
                
                # Связываем Customer с User, если он еще не связан!
                if customer_profile:
                    order.customer = customer_profile
                    order.save(update_fields=["customer"])
                else:
                    from store.models import Customer
                    customer, _ = Customer.objects.get_or_create(
                        email=request.user.email,
                        defaults={
                            "user": request.user,
                            "name": form.cleaned_data["name"],
                            "email": form.cleaned_data["email"],
                            "phone": form.cleaned_data.get("phone", ""),
                            "city": form.cleaned_data.get("city", "")
                        }
                    )
                    if not customer.user:
                        customer.user = request.user
                        customer.save(update_fields=["user"])
                    order.customer = customer
                    order.save(update_fields=["customer"])
                
                messages.success(request, f"Заказ #{order.pk} создан.")
                return redirect(order)
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "store/checkout.html",
        {"form": form, "cart": cart, "totals": facade.get_cart_totals(cart, initial["pricing_strategy"], initial["delivery_method"])},
    )


@login_required
def order_detail(request, pk):
    facade = StoreFacade()
    detail = facade.get_order_detail(pk)
    order = detail["order"]
    transitions = detail["transitions"]
    
    # Разграничение прав доступа (RBAC)!
    if not request.user.is_staff:
        # Обычный покупатель видит только свои собственные заказы
        if order.customer.user != request.user and order.customer.email != request.user.email:
            messages.error(request, "У вас нет прав для просмотра этого заказа.")
            return redirect("store:home")
    
    if request.method == "POST":
        action = request.POST.get("action")
        # Покупателю разрешено самостоятельно отменить свой заказ, если он на стадии "Создан" (created)
        is_customer_cancel = (
            not request.user.is_staff
            and action == "cancel"
            and order.status == Order.Status.CREATED
        )
        
        if not request.user.is_staff and not is_customer_cancel:
            messages.error(request, "Только менеджеры могут изменять статус этого заказа.")
            return redirect(order)
            
        try:
            facade.advance_order_state(order.pk, action)
            messages.success(request, "Статус заказа обновлен.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect(order)

    return render(
        request,
        "store/order_detail.html",
        {"order": order, "transitions": transitions},
    )


@login_required
def profile_view(request):
    from decimal import Decimal
    from store.models import Order
    facade = StoreFacade()
    
    # Получаем профиль покупателя, связанный с текущим пользователем
    customer_profile = getattr(request.user, "customer_profile", None)
    
    orders = []
    total_spent = Decimal("0.00")
    orders_count = 0
    
    if customer_profile:
        # Выбираем все заказы данного покупателя
        orders = Order.objects.filter(customer=customer_profile).order_by("-created_at")
        orders_count = orders.count()
        
        # Считаем общую сумму успешных (не отмененных) заказов
        successful_orders = orders.exclude(status=Order.Status.CANCELLED)
        total_spent = sum((o.total for o in successful_orders), Decimal("0.00"))
        
    context = {
        "title": "Личный кабинет",
        "customer": customer_profile,
        "orders": orders,
        "orders_count": orders_count,
        "total_spent": total_spent,
    }
    return render(request, "store/profile.html", context)


def catalog_tree(request):
    facade = StoreFacade()
    tree = facade.get_catalog_tree_and_flat()
    return render(
        request, 
        "store/catalog_tree.html", 
        {
            "roots": tree["roots"], 
            "flat_items": tree["flat_items"], 
            "product_leaf": ProductLeaf
        }
    )


def patterns_demo(request):
    facade = StoreFacade()
    demo_data = facade.get_patterns_demo_data()
    return render(
        request,
        "store/patterns_demo.html",
        {
            "settings": demo_data["settings"],
            "singleton_ids": demo_data["singleton_ids"],
            "pricing_results": demo_data["pricing_results"],
            "shipping_results": demo_data["shipping_results"],
            "trend_product": demo_data["trend_product"],
            "trend": demo_data["trend"],
            "adapter_titles": demo_data["adapter_titles"],
            "tree_count": demo_data["tree_count"],
            "sales_points_count": demo_data["sales_points_count"],
        },
    )


def undo_cart_action(request):
    facade = StoreFacade()
    if facade.undo_last_action(request):
        messages.success(request, "Последнее действие в корзине отменено.")
    else:
        messages.warning(request, "Нечего отменять.")
    return redirect("store:cart")
