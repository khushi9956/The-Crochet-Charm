import requests
import os
import razorpay
import hmac
import random
import hashlib
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import (
    Product,
    Contact,
    Order,
    OrderItem,
    UserAddress,
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
@renderer_classes([JSONRenderer])
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

    Contact.objects.create(
        name=name,
        email=email,
        message=message
    )

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": os.environ.get("BREVO_API_KEY"),
                "content-type": "application/json",
            },
            json={
                "sender": {
                    "name": "The Crochet Charm",
                    "email": "thecrochetcharms@gmail.com"
                },
                "to": [
                    {
                        "email": "thecrochetcharms@gmail.com",
                        "name": "Khushi"
                    }
                ],
                "subject": f"🌸 New Contact Form Submission - {name}",
                "htmlContent": f"""
                <h2>New Contact Form Submission</h2>

                <p><b>Name:</b> {name}</p>

                <p><b>Email:</b> {email}</p>

                <p><b>Message:</b></p>

                <p>{message}</p>
                """
            },
            timeout=20,
        )

        print("BREVO STATUS:", response.status_code)
        print("BREVO RESPONSE:", response.text)

    except Exception as e:
        print("BREVO ERROR:", str(e))

    return Response({
        "success": True,
        "message": "Message sent successfully."
    })
@api_view(["POST"])
def create_order(request):
    try:
        amount = request.data.get("amount")

        if not amount:
            return Response(
                {"error": "Amount is required"},
                status=400
            )

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
        return Response(
            {"error": str(e)},
            status=500
        )
@api_view(["POST"])
@permission_classes([IsAuthenticated])
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

        order_number = f"TCC{random.randint(100000, 999999)}"

        while Order.objects.filter(order_number=order_number).exists():
            order_number = f"TCC{random.randint(100000, 999999)}"

        with transaction.atomic():
          
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
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
            items_html = ""

            for item in products:
             items_html += f"""
    <tr>
        <td>{item.get('name', 'Product')}</td>
        <td>{item.get('quantity', 1)}</td>
        <td>₹{item.get('price', 0)}</td>
    </tr>
    """

    
            for item in products:
                product = Product.objects.get(id=item["id"])

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.get("quantity", 1),
                    price=item.get("price", product.price),
                )

        # -----------------------------
        # Send Order Confirmation Email
        # -----------------------------
        try:
            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "accept": "application/json",
                    "api-key": os.environ.get("BREVO_API_KEY"),
                    "content-type": "application/json",
                },
                json={
                    "sender": {
                        "name": "The Crochet Charm",
                        "email": "thecrochetcharms@gmail.com",
                    },
                    "to": [
                        {
                            "email": order.email,
                            "name": order.customer_name,
                        }
                    ],
                    "cc": [
                        {
                            "email": "thecrochetcharms@gmail.com",
                            "name": "The Crochet Charm Admin"
                        }
                    ], 
                    
                    "subject": f"🌸 Order Confirmed - {order.order_number}",
                    "htmlContent": f"""
                        <h2>Thank you for shopping with The Crochet Charm ❤️</h2>

                        <p>Hello <b>{order.customer_name}</b>,</p>

                        <p>Your order has been placed successfully.</p>

                        <p><b>Order Number:</b> {order.order_number}</p>
                        <p><b>Total:</b> ₹{order.total}</p>
                        <h3>Your Items</h3>

<table border="1" cellpadding="8" cellspacing="0" width="100%">
<tr>
<th>Product</th>
<th>Qty</th>
<th>Price</th>
</tr>

{items_html}

</table>
                        <p><b>Payment Status:</b> {order.payment_status}</p>

                        <p>We will start preparing your order soon.</p>

                        <br>

                        <p>Thank you for supporting handmade creations! 🌸</p>
                    """,
                },
                timeout=20,
            )

            print("ORDER EMAIL STATUS:", response.status_code)
            print("ORDER EMAIL RESPONSE:", response.text)

        except Exception as email_error:
            print("ORDER EMAIL ERROR:", email_error)

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
@permission_classes([IsAuthenticated])
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
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
@permission_classes([IsAuthenticated])
def order_detail(request, order_number):

    try:
        order = Order.objects.prefetch_related(
            "items__product"
        ).get(
            order_number=order_number,
            user=request.user,
        )

    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=404,
        )

    items = []

    for item in order.items.all():
        items.append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.price,
            "image": (
                item.product.image.url
                if item.product.image
                else None
            ),
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
        "razorpay_order_id": order.razorpay_order_id,
        "payment_id": order.payment_id,
        "created_at": order.created_at,
        "items": items,
    })
@api_view(["GET"])
def clerk_test(request):
    if not request.user or not request.user.is_authenticated:
        return Response(
            {"authenticated": False},
            status=401
        )

    return Response({
        "authenticated": True,
        "django_user_id": request.user.id,
        "django_username": request.user.username,
    })
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_api(request):

    user = request.user

    # GET SAVED ADDRESSES
    if request.method == "GET":

        addresses = UserAddress.objects.filter(
            user=user
        ).order_by("-is_default", "-created_at")

        data = []

        for address in addresses:
            data.append({
                "id": address.id,
                "name": address.name,
                "phone": address.phone,
                "address": address.address,
                "city": address.city,
                "state": address.state,
                "pincode": address.pincode,
                "is_default": address.is_default,
            })

        return Response(data)

    # ADD ADDRESS
    name = request.data.get("name", "").strip()
    phone = request.data.get("phone", "").strip()
    address_text = request.data.get("address", "").strip()
    city = request.data.get("city", "").strip()
    state = request.data.get("state", "").strip()
    pincode = request.data.get("pincode", "").strip()

    if not name:
        return Response(
            {"error": "Name is required"},
            status=400
        )

    if not phone:
        return Response(
            {"error": "Phone number is required"},
            status=400
        )

    if not address_text:
        return Response(
            {"error": "Address is required"},
            status=400
        )

    if not city:
        return Response(
            {"error": "City is required"},
            status=400
        )

    if not state:
        return Response(
            {"error": "State is required"},
            status=400
        )

    if not pincode:
        return Response(
            {"error": "Pincode is required"},
            status=400
        )

    # If this is the first address, make it default
    has_address = UserAddress.objects.filter(
        user=user
    ).exists()

    new_address = UserAddress.objects.create(
        user=user,
        name=name,
        phone=phone,
        address=address_text,
        city=city,
        state=state,
        pincode=pincode,
        is_default=not has_address,
    )

    return Response({
        "success": True,
        "message": "Address saved successfully.",
        "address": {
            "id": new_address.id,
            "name": new_address.name,
            "phone": new_address.phone,
            "address": new_address.address,
            "city": new_address.city,
            "state": new_address.state,
            "pincode": new_address.pincode,
            "is_default": new_address.is_default,
        }
    }, status=201)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def address_detail(request, address_id):

    try:
        address = UserAddress.objects.get(
            id=address_id,
            user=request.user
        )
    except UserAddress.DoesNotExist:
        return Response(
            {"error": "Address not found"},
            status=404
        )

    # UPDATE ADDRESS
    if request.method == "PUT":

        address.name = request.data.get(
            "name",
            address.name
        ).strip()

        address.phone = request.data.get(
            "phone",
            address.phone
        ).strip()

        address.address = request.data.get(
            "address",
            address.address
        ).strip()

        address.city = request.data.get(
            "city",
            address.city
        ).strip()

        address.state = request.data.get(
            "state",
            address.state
        ).strip()

        address.pincode = request.data.get(
            "pincode",
            address.pincode
        ).strip()

        address.save()

        return Response({
            "success": True,
            "message": "Address updated successfully.",
            "address": {
                "id": address.id,
                "name": address.name,
                "phone": address.phone,
                "address": address.address,
                "city": address.city,
                "state": address.state,
                "pincode": address.pincode,
                "is_default": address.is_default,
            }
        })

    # DELETE ADDRESS
    address.delete()

    return Response({
        "success": True,
        "message": "Address deleted successfully."
    })
