from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to="products/")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ClerkUserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="clerk_profile",
    )

    clerk_user_id = models.CharField(
        max_length=255,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.clerk_user_id}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    highlights = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
class Order(models.Model):

    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    ORDER_STATUS = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Packed", "Packed"),
        ("Shipped", "Shipped"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders",
)
    order_number = models.CharField(max_length=20, unique=True)

    customer_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    email = models.EmailField(blank=True)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    subtotal = models.IntegerField()

    delivery_charge = models.IntegerField(default=40)

    total = models.IntegerField()

    razorpay_order_id = models.CharField(max_length=200)

    payment_id = models.CharField(max_length=200, blank=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="Pending",
    )

    order_status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS,
        default="Pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class UserAddress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    is_default = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.city} - {self.pincode}"