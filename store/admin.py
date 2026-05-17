from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Category,
    Customer,
    Order,
    OrderItem,
    ProcessLog,
    Product,
    Promotion,
    Review,
    SalesPoint,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "anime_title", "category", "price", "stock", "is_active")
    list_filter = ("category", "merch_type", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "anime_title")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("session_key", "status", "updated_at")
    list_filter = ("status",)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total", "delivery_method", "created_at")
    list_filter = ("status", "delivery_method", "pricing_strategy")
    inlines = [OrderItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "city", "created_at")
    search_fields = ("name", "email")


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "discount_percent", "is_active")
    list_filter = ("is_active",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "customer_name", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(SalesPoint)
class SalesPointAdmin(admin.ModelAdmin):
    list_display = ("product", "week_number", "units_sold")
    list_filter = ("product",)


@admin.register(ProcessLog)
class ProcessLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "level", "order", "created_at")
    list_filter = ("level", "event_type")
