from django.urls import path
from .views import (
    home,
    products,
    robots_txt,
    product_list,
    product_detail,
    contact_api,
    create_order,
    verify_payment,
)
urlpatterns = [
    path("", home, name="home"),
    path("products/", products, name="products"),
    path("api/products/", product_list, name="api-products"),
    path("robots.txt", robots_txt),
    path("api/contact/", contact_api, name="contact-api"),
    path("api/products/<int:id>/", product_detail),
    path("api/create-order/", create_order),
    path(
    "api/verify-payment/",
    verify_payment
),
]