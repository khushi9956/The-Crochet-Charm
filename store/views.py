import os
import razorpay
import hmac
import random
import hashlib
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import (
    Product,
    Contact,
    Order,
    OrderItem,
)
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from .models import Product
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer


def home(request):
    featured_products = Product.objects.all()[:4]

    return render(
        request,
        'index.html',
        {'featured_products': featured_products}
    )

def products(request):
    products = Product.objects.all()

    return render(
        request,
        'products.html',
        {'products': products}
    )

    print("HOME VIEW HIT")

    if request.method == "POST":

        print("POST RECEIVED")

        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            message=request.POST['message']
        )

        print("CONTACT SAVED")
        messages.success(
            request,
            "Thank you! Your message has been sent successfully. 💖"
        )

        return redirect('/')

    products = Product.objects.all()

    search = request.GET.get('search')

    if search:
        products = products.filter(
            name__icontains=search
        )

    return render(
        request,
        'index.html',
        {'products': products}
    )
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://the-crochet-charm.onrender.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

@api_view(["GET"])
def product_list(request):
    products = Product.objects.all()

    print("=" * 50)
    print("PRODUCT COUNT:", products.count())
    print("DATABASE:", settings.DATABASES["default"]["ENGINE"])
    print("DB NAME:", settings.DATABASES["default"]["NAME"])
    print("=" * 50)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
@api_view(["GET"])
def product_detail(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    serializer = ProductSerializer(product)
    return Response(serializer.data)
@api_view(["POST"])
def contact_api(request):

    name = request.data.get("name")
    email = request.data.get("email")
    message = request.data.get("message")

    # Save to Database
    Contact.objects.create(
        name=name,
        email=email,
        message=message
    )

    send_mail(
    subject=f"🌸 New Contact Form Submission - {name}",
    message=(
        f"New message from The Crochet Charm Website\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        f"Message:\n{message}"
    ),
    from_email=settings.EMAIL_HOST_USER,
    recipient_list=[settings.EMAIL_HOST_USER],
    fail_silently=False,
)
    return Response({
        "success": True,
        "message": "Message sent successfully."
    })

@api_view(["POST"])
def create_order(request):
    try:
        amount = request.data.get("amount")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

        order = client.order.create({
            "amount": int(amount),
            "currency": "INR",
            "payment_capture": 1,
        })

        return Response(order)

    except Exception as e:
        import traceback
        print(traceback.format_exc())   # Full error Render Logs me aayega
        return Response({"error": str(e)}, status=500)
@api_view(["POST"])
def verify_payment(request):

    razorpay_order_id = request.data.get("razorpay_order_id")
    razorpay_payment_id = request.data.get("razorpay_payment_id")
    razorpay_signature = request.data.get("razorpay_signature")

    customer = request.data.get("customer", {})
    products = request.data.get("products", [])

    subtotal = request.data.get("subtotal", 0)
    delivery_charge = request.data.get("delivery_charge", 40)
    total = request.data.get("total", 0)

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        order_number = f"TCC{random.randint(100000,999999)}"

        while Order.objects.filter(order_number=order_number).exists():
            order_number = f"TCC{random.randint(100000,999999)}"

        with transaction.atomic():

            order = Order.objects.create(
                order_number=order_number,

                customer_name=customer.get("name", ""),
                phone=customer.get("phone", ""),
                email=customer.get("email", ""),

                address=customer.get("address", ""),
                city=customer.get("city", ""),
                state=customer.get("state", ""),
                pincode=customer.get("pincode", ""),

                subtotal=subtotal,
                delivery_charge=delivery_charge,
                total=total,

                razorpay_order_id=razorpay_order_id,
                payment_id=razorpay_payment_id,

                payment_status="Paid",
                order_status="Confirmed",
            )

            for item in products:

                product = Product.objects.get(id=item["id"])

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.get("quantity", 1),
                    price=item.get("price", product.price),
                )

        return JsonResponse({
            "success": True,
            "order_number": order.order_number,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=400)
@api_view(["GET"])
def my_orders(request):

    email = request.GET.get("email")

    if not email:
        return Response(
            {"error": "Email is required"},
            status=400
        )

    orders = Order.objects.filter(
        email=email
    ).order_by("-created_at")

    data = []

    for order in orders:

        data.append({

            "order_number": order.order_number,

            "customer_name": order.customer_name,

            "total": order.total,

            "payment_status": order.payment_status,

            "order_status": order.order_status,

            "created_at": order.created_at,

        })

    return Response(data)
@api_view(["GET"])
def order_detail(request, order_number):

    try:
        order = Order.objects.get(order_number=order_number)

    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=404
        )

    items = []

    for item in order.items.all():

        items.append({
            "name": item.product.name,
            "image": item.product.image.url,
            "price": item.price,
            "quantity": item.quantity,
        })

    return Response({

        "order_number": order.order_number,

        "customer_name": order.customer_name,

        "phone": order.phone,

        "email": order.email,

        "address": order.address,

        "city": order.city,

        "state": order.state,

        "pincode": order.pincode,

        "subtotal": order.subtotal,

        "delivery_charge": order.delivery_charge,

        "total": order.total,

        "payment_status": order.payment_status,

        "order_status": order.order_status,

        "items": items,
    })

from django.contrib.auth.models import User
from django.http import JsonResponse


def create_render_superuser(request):
    try:
        username = "admin"
        email = "khushishukl185@gmail.com"
        password = "Admin@12345"

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "message": "Superuser already exists"
            })

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        return JsonResponse({
            "message": "Superuser created successfully"
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)