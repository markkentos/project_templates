from django.urls import path
from django.contrib.auth import views as auth_views

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
    path("profile/", views.profile_view, name="profile"),
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("patterns/", views.patterns_demo, name="patterns_demo"),
    path("tree/", views.catalog_tree, name="catalog_tree"),
    path("cart/undo/", views.undo_cart_action, name="undo_cart_action"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="store/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="store:home"), name="logout"),
]
