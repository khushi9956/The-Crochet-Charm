import os
import razorpay
import hmac
import hashlib
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Contact
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
    except:

        return JsonResponse({
            "success": False
        }, status=400)