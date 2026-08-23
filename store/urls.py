from django.urls import path

from .views import (
    home,
    my_orders,
    order_detail,
    products,
    robots_txt,
    product_list,
    product_detail,
    contact_api,
    create_order,
    verify_payment,
    clerk_test,
    address_api,
    address_detail,
)

urlpatterns = [
    path("", home, name="home"),
    path("products/", products, name="products"),

    path("api/products/", product_list, name="api-products"),
    path("api/products/<int:id>/", product_detail),

    path("api/contact/", contact_api, name="contact-api"),

    path("api/create-order/", create_order),
    path("api/verify-payment/", verify_payment),
    path("api/my-orders/", my_orders),
    path("robots.txt", robots_txt),
    path(
    "api/order/<str:order_number>/",
    order_detail,
    ),
    path("api/clerk-test/", clerk_test, name="clerk-test"),
    path("api/address/", address_api, name="api-address"),

path(
    "api/address/<int:address_id>/",
    address_detail,
    name="api-address-detail",
),


]
