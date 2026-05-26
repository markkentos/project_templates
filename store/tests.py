from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Category, Order, ProcessLog, Product, SalesPoint, Customer
from .services.commands import AdvanceOrderStateCommand
from .services.math_models import SalesTrendModel
from .services.pricing import get_pricing_strategy


class StoreWorkflowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Фигурки", slug="figures")
        self.product = Product.objects.create(
            category=self.category,
            name="Фигурка тестовая",
            slug="test-figure",
            anime_title="Test Anime",
            merch_type=Product.MerchType.FIGURE,
            description="Тестовый товар",
            price=Decimal("1000.00"),
            stock=10,
            popularity_score=80,
        )
        for week, units in enumerate([3, 5, 7, 9], start=1):
            SalesPoint.objects.create(product=self.product, week_number=week, units_sold=units)

        # Создаем и авторизуем пользователя для прохождения проверок RBAC
        self.user = User.objects.create_user(
            username="testuser",
            email="demo@example.com",
            password="password123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name="Demo Buyer",
            email="demo@example.com"
        )
        self.client.force_login(self.user)

    def create_order_through_checkout(self):
        self.client.post(
            reverse("store:add_to_cart", args=[self.product.slug]),
            {"quantity": 2, "next": reverse("store:cart")},
        )
        return self.client.post(
            reverse("store:checkout"),
            {
                "name": "Demo Buyer",
                "email": "demo@example.com",
                "phone": "",
                "city": "Moscow",
                "delivery_method": "pickup",
                "pricing_strategy": "regular",
                "comment": "",
            },
        )

    def test_sales_trend_model_forecasts_next_week(self):
        result = SalesTrendModel().calculate(self.product.sales_points.all())

        self.assertEqual(result.direction, "растущий спрос")
        self.assertEqual(result.demand_forecast, 11.0)
        self.assertEqual(result.supply_forecast, 10.0)
        self.assertEqual(result.forecast, 10.0)
        self.assertEqual(result.supply_direction, "предложение ниже спроса")

    def test_pricing_strategy_applies_otaku_discount(self):
        result = get_pricing_strategy("otaku").calculate(Decimal("2000.00"))

        self.assertEqual(result.discount, Decimal("200.00"))
        self.assertEqual(result.total, Decimal("1800.00"))

    def test_checkout_creates_order_and_observer_logs(self):
        response = self.create_order_through_checkout()

        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(order.total, Decimal("2000.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        self.assertGreaterEqual(ProcessLog.objects.filter(order=order).count(), 2)

    def test_state_command_advances_order(self):
        self.create_order_through_checkout()
        order = Order.objects.get()

        AdvanceOrderStateCommand(order.id, "pay").execute()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)

    def test_factory_method_returns_correct_factory(self):
        from .services.factories import MerchFactoryProvider, FigureFactory, ApparelFactory
        
        fig_factory = MerchFactoryProvider.get_factory("figure")
        self.assertIsInstance(fig_factory, FigureFactory)
        
        cloth_factory = MerchFactoryProvider.get_factory("clothes")
        self.assertIsInstance(cloth_factory, ApparelFactory)

    def test_add_to_cart_undo(self):
        # Добавляем товар в корзину
        self.client.post(
            reverse("store:add_to_cart", args=[self.product.slug]),
            {"quantity": 3, "next": reverse("store:cart")},
        )
        
        # Вызываем отмену последнего действия (Undo)
        self.client.get(reverse("store:undo_cart_action"))
        
        # Проверяем, что корзина пуста после отмены
        session = self.client.session
        from .models import Cart
        cart = Cart.objects.filter(session_key=session.session_key, status=Cart.Status.OPEN).first()
        self.assertTrue(cart is None or not cart.items.exists())

    def test_optional_review_text(self):
        from .models import Review
        # Отправляем отзыв без текста (только имя и оценка)
        response = self.client.post(
            reverse("store:product_detail", args=[self.product.slug]),
            {"customer_name": "Test Reviewer", "rating": 5, "text": ""}
        )
        self.assertEqual(response.status_code, 302)  # Должен перенаправить на страницу товара
        review = Review.objects.get(customer_name="Test Reviewer")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "")

    def test_customer_can_cancel_created_order(self):
        self.create_order_through_checkout()
        order = Order.objects.get()
        self.assertEqual(order.status, Order.Status.CREATED)

        # Клиент отправляет POST-запрос с действием отмены
        response = self.client.post(
            reverse("store:order_detail", args=[order.id]),
            {"action": "cancel"}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)


# Create your tests here.
