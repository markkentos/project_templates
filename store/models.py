from decimal import Decimal

from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_list_by_category", kwargs={"category_slug": self.slug})


class Product(TimeStampedModel):
    class MerchType(models.TextChoices):
        FIGURE = "figure", "Фигурка"
        POSTER = "poster", "Постер"
        COSPLAY = "cosplay", "Косплей"
        CLOTHES = "clothes", "Одежда"
        MANGA = "manga", "Манга"
        ACCESSORY = "accessory", "Аксессуар"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    anime_title = models.CharField(max_length=140)
    merch_type = models.CharField(max_length=20, choices=MerchType.choices)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("4.50"))
    popularity_score = models.PositiveIntegerField(default=50)
    sales_count = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-popularity_score", "name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.anime_title})"

    def get_absolute_url(self):
        return reverse("store:product_detail", kwargs={"slug": self.slug})

    @property
    def is_available(self):
        return self.is_active and self.stock > 0


class Customer(TimeStampedModel):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
    )
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]

        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Cart(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Открыта"
        CHECKED_OUT = "checked_out", "Оформлена"

    session_key = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.session_key[:8]} ({self.get_status_display()})"

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.select_related("product")), Decimal("0.00"))


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_product_in_cart"),
        ]
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.product.price * self.quantity


class Promotion(TimeStampedModel):
    name = models.CharField(max_length=140)
    code = models.SlugField(max_length=40, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Промоакция"
        verbose_name_plural = "Промоакции"

    def __str__(self):
        return f"{self.name}: {self.discount_percent}%"


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        CREATED = "created", "Создан"
        PAID = "paid", "Оплачен"
        PACKED = "packed", "Упакован"
        SHIPPED = "shipped", "Отправлен"
        DELIVERED = "delivered", "Доставлен"
        CANCELLED = "cancelled", "Отменен"

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    delivery_method = models.CharField(max_length=40, default="courier")
    pricing_strategy = models.CharField(max_length=40, default="regular")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.pk} - {self.customer.name}"

    def get_absolute_url(self):
        return reverse("store:order_detail", kwargs={"pk": self.pk})

    @property
    def allowed_transitions(self):
        from store.services.states import OrderStateMachine
        return OrderStateMachine().allowed_transitions(self)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(default=5)
    text = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.customer_name}: {self.rating}/5"


class SalesPoint(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales_points")
    week_number = models.PositiveIntegerField()
    units_sold = models.PositiveIntegerField()

    class Meta:
        ordering = ["product", "week_number"]
        constraints = [
            models.UniqueConstraint(fields=["product", "week_number"], name="unique_product_week_sales"),
        ]
        verbose_name = "Точка продаж"
        verbose_name_plural = "Точки продаж"

    def __str__(self):
        return f"{self.product.name}: неделя {self.week_number}, {self.units_sold} шт."


class ProcessLog(models.Model):
    class Level(models.TextChoices):
        INFO = "info", "Информация"
        WARNING = "warning", "Предупреждение"
        ERROR = "error", "Ошибка"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name="logs")
    event_type = models.CharField(max_length=80)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Журнал процесса"
        verbose_name_plural = "Журнал процессов"

    def __str__(self):
        return f"{self.event_type}: {self.message[:60]}"
