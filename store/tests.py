from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, ProcessLog, Product, SalesPoint
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
        self.assertEqual(result.forecast, 11.0)

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

# Create your tests here.
