from django.contrib import admin
from .models import Product, Contact, Cart, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "phone",
        "payment_status",
        "order_status",
        "total",
        "created_at",
    )

    list_filter = (
        "payment_status",
        "order_status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "customer_name",
        "phone",
    )

    inlines = [OrderItemInline]


admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Cart)
admin.site.register(OrderItem)