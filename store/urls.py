from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.product_list, name="product_list"),
    path("catalog/category/<slug:category_slug>/", views.product_list, name="product_list_by_category"),
    path("catalog/<slug:slug>/", views.product_detail, name="product_detail"),
    path("catalog/<slug:slug>/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("patterns/", views.patterns_demo, name="patterns_demo"),
    path("tree/", views.catalog_tree, name="catalog_tree"),
]
